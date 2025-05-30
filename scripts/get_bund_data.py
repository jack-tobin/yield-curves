"""Fetch Bund data from bundesbank."""

import datetime as dt
import os
import re
import sys
from pathlib import Path
from typing import Any, NamedTuple
from django.db.models import Max
from pydantic import BaseModel
import pandas as pd
import requests
from bs4 import BeautifulSoup
import argparse
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import pdb

from src.utils.logger import logger
from src.apps.yield_curves.models import BondMetric


@dataclass(frozen=True)
class BundDataArgs:
    date: dt.date | None = None
    backfill: bool = False


def parse_args(args: tuple[str, ...]) -> BundDataArgs:
    validated_args = {}
    for arg in args:
        key, value = arg.split("=")
        if value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False
        elif value.isdigit():
            value = int(value)
        elif value.lower() == "none":
            value = None
        validated_args[key] = value
    return BundDataArgs(**validated_args)


def run(
    *args: tuple[str, ...],
):
    parsed = parse_args(args)

    pipeline = BundesbankDataPipeline(
        date=parsed.date,
        backfill=parsed.backfill,
    )
    df = pipeline.execute()


class Pipeline(ABC):
    class Extracted(BaseModel):
        data: Any

    class Transformed(BaseModel):
        data: Any

    @abstractmethod
    def extract(self) -> Extracted:
        ...

    @abstractmethod
    def transform(self, data: Extracted) -> Transformed:
        ...

    @abstractmethod
    def load(self, data: Transformed) -> None:
        ...


@dataclass(frozen=True)
class File:
    url: str = field(repr=False)
    month: int
    year: int
    text: str


class BundesbankDataPipeline(Pipeline):
    def __init__(
        self,
        date: dt.date | None = None,
        backfill: bool = False,
    ):
        if date is None:
            date = dt.date.today()
        self.date = date
        self.backfill = backfill
        self.base_url = "https://www.bundesbank.de/en/service/federal-securities/prices-and-yields"

    class Extracted(BaseModel):
        class Config:
            arbitrary_types_allowed = True

        max_date_in_table: dt.date | None
        available_files: list[File]
        excel_files: list[pd.ExcelFile]

    class Transformed(BaseModel):
        class Config:
            arbitrary_types_allowed = True

        data: Any

    def execute(self) -> pd.DataFrame:
        raw_data = self.extract()
        clean_df = self.transform(raw_data)
        return clean_df

    def extract(self) -> Extracted:
        max_date_in_table = self._get_max_date_in_table()
        files = self._get_available_files()
        selected_files = self._select_files(files, max_date_in_table)

        raw_data = []
        for file in selected_files:
            logger.info(f"Downloading {file}")
            raw_data.append(self._download_and_parse_excel(file))

        if not raw_data:
            raise ValueError("No data found")

        pdb.set_trace()

        return self.Extracted(
            max_date_in_table=max_date_in_table,
            available_files=files,
            excel_files=raw_data,
        )

    def _get_max_date_in_table(self) -> dt.date | None:
        return BondMetric.objects.aggregate(Max("date"))["date__max"]

    def _get_available_files(self) -> list[File]:
        response = requests.get(self.base_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        files = []
        for link in soup.find_all('a', href=True):
            text = link.get_text(strip=True)
            if (
                'XLSX' not in text
                or 'Prices and yields of listed Federal securities' not in text
            ):
                continue

            href = f"https://www.bundesbank.de{link['href']}"

            date_match = re.search(r'(\w+)\s+(\d{4})', text)
            if not date_match:
                continue
            month_name, year = date_match.groups()
            month_num = dt.datetime.strptime(month_name, "%B").month

            files.append(
                File(
                    url=href,
                    month=month_num,
                    year=int(year),
                    text=text,
                )
            )

        return files

    def _select_files(
        self,
        files: list[File],
        max_date_in_table: dt.date | None = None,
    ) -> list[File]:
        if not files:
            raise ValueError("No files found on the Bundesbank website")

        # Sort files by date (newest first)
        sorted_files = sorted(
            files,
            key=lambda x: (x.year, x.month),
            reverse=True,
        )

        if self.backfill:
            # If no date specified, return all files after latest date
            if max_date_in_table is not None:
                return [
                    file for file in sorted_files
                    if (file.year, file.month) >= (max_date_in_table.year, max_date_in_table.month)
                ]
            return sorted_files

        # Find the closest file date
        target_year_month = (self.date.year, self.date.month)

        for file in sorted_files:
            file_year_month = (file.year, file.month)
            if file_year_month <= target_year_month:
                return [file]

        raise ValueError(f"No files found for date {self.date}")

    def _download_and_parse_excel(self, file: File) -> dict[str, pd.DataFrame]:
        response = requests.get(file.url)
        response.raise_for_status()

        with tempfile.TemporaryDirectory() as tempdir:
            filename = file.url.split('/')[-1]
            if not filename.endswith('.xlsx'):
                filename = f"bundesbank_bonds_{dt.datetime.now().strftime('%Y%m%d')}.xlsx"

            filepath = Path(tempdir) / filename
            with filepath.open("wb") as f:
                f.write(response.content)

            # Read from the saved file
            return pd.read_excel(filepath, engine='openpyxl', sheet_name=None)

    def transform(self, extracted: Extracted) -> Transformed:
        df = extracted.data.copy()

        pdb.set_trace()

        # The Bundesbank files might have different structures
        # First, try to identify the actual data rows by looking for common column names

        # Common column names in Bundesbank files
        possible_headers = [
            'Security name', 'Maturity date', 'Coupon', 'ISIN',
            'Standard price', 'Yield', 'Duration', 'Macaulay duration',
            'Clean price', 'Dirty price'
        ]

        # Find rows that might contain headers
        header_rows = []
        for idx, row in df.iterrows():
            matches = sum(1 for val in row if isinstance(val, str) and val in possible_headers)
            if matches >= 3:  # If at least 3 matches, likely a header row
                header_rows.append(idx)

        if header_rows:
            # Use the first identified header row
            header_row = header_rows[0]

            # Set this row as the header
            headers = df.iloc[header_row].values
            df = df.iloc[header_row+1:].copy()
            df.columns = headers

            # Remove rows with all NaN
            df = df.dropna(how='all')

            # Ensure ISIN is treated as string
            if 'ISIN' in df.columns:
                df['ISIN'] = df['ISIN'].astype(str)

            # Convert date columns to datetime
            date_columns = [col for col in df.columns if 'date' in str(col).lower()]
            for col in date_columns:
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    # If conversion fails, keep as is
                    pass

            # Convert numeric columns
            numeric_columns = ['Coupon', 'Standard price', 'Yield', 'Duration',
                              'Macaulay duration', 'Clean price', 'Dirty price']
            for col in [c for c in numeric_columns if c in df.columns]:
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except:
                    # If conversion fails, keep as is
                    pass

        else:
            # If headers weren't found, try to infer based on content
            # This is a fallback approach and might need adjustment

            # Drop rows where all values are NaN
            df = df.dropna(how='all')

            # Try to identify the header row based on common column names
            for idx, row in df.iterrows():
                row_str = ' '.join([str(x).lower() for x in row if x is not None])
                if 'isin' in row_str and ('coupon' in row_str or 'yield' in row_str):
                    # This is likely a header row
                    headers = df.iloc[idx].values
                    df = df.iloc[idx+1:].copy()
                    df.columns = headers
                    break

        # Add metadata
        df['fetch_date'] = dt.datetime.now().date()

        return self.Transformed(data=df)

    def load(self, data: pd.DataFrame) -> None:
        ...
