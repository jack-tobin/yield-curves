"""Fetch Bund data from bundesbank."""

import datetime as dt
import re
from pathlib import Path
from django.db.models import Max
from pydantic import BaseModel as PydanticBaseModel
import pandas as pd
import requests
from bs4 import BeautifulSoup
import tempfile
from dataclasses import dataclass, field
from string import ascii_uppercase

from src.utils.logger import logger
from src.utils.data import Extractor, Transformer, Loader, run_pipeline
from src.apps.yield_curves.models import Bond, BondMetric


class ArbitraryBaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True


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

    extractor = BundesbankDataExtractor(
        date=parsed.date,
        backfill=parsed.backfill,
    )
    transformer = BundesbankDataTransformer()
    loader = BundesbankDataLoader()

    try:
        run_pipeline(
            extractor,
            transformer,
            loader,
        )
    except Exception:
        logger.exception("Error in pipeline.")
        return -1

    return 0


@dataclass(frozen=True)
class File:
    url: str = field(repr=False)
    month: int
    year: int
    text: str


@dataclass(frozen=True)
class ExcelSheet:
    name: str
    data: pd.DataFrame


@dataclass(frozen=True)
class ExcelFile:
    sheets: list[ExcelSheet]

    @classmethod
    def from_dict(cls, data: dict[str, pd.DataFrame]):
        return cls(
            sheets=[ExcelSheet(name=name, data=data) for name, data in data.items()],
        )


class BundesbankDataExtractor(Extractor):
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

    class Extracted(ArbitraryBaseModel):
        max_date_in_table: dt.date
        available_files: list[File]
        excel_files: list[ExcelFile]

    def extract(self) -> Extracted:
        max_date_in_table = self._get_max_date_in_table()
        files = self._get_available_files()
        logger.info(f"Found {len(files)} files")

        selected_files = self._select_files(files, max_date_in_table)
        logger.info(f"Selected {len(selected_files)} files")

        raw_data = []
        for file in selected_files:
            logger.info(f"Downloading {file}")
            raw_data.append(self._download_and_parse_excel(file))

        if not raw_data:
            raise ValueError("No data found")

        return self.Extracted(
            max_date_in_table=max_date_in_table,
            available_files=files,
            excel_files=raw_data,
        )

    def _get_max_date_in_table(self) -> dt.date:
        max_date = BondMetric.objects.aggregate(Max("date"))["date__max"]
        return max_date or dt.date.min

    def _get_available_files(self) -> list[File]:
        response = requests.get(self.base_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        files = []
        for link in soup.find_all("a", href=True):
            text = link.get_text(strip=True)
            if "XLSX" not in text or "Prices and yields of listed Federal securities" not in text:
                continue

            href = f"https://www.bundesbank.de{link['href']}"

            date_match = re.search(r"(\w+)\s+(\d{4})", text)
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
        max_date_in_table: dt.date,
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
            return [
                file
                for file in sorted_files
                if (file.year, file.month) >= (max_date_in_table.year, max_date_in_table.month)
            ]

        # Find the closest file date
        target_year_month = (self.date.year, self.date.month)

        for file in sorted_files:
            file_year_month = (file.year, file.month)
            if file_year_month <= target_year_month:
                return [file]

        raise ValueError(f"No files found for date {self.date}")

    def _download_and_parse_excel(self, file: File) -> ExcelFile:
        response = requests.get(file.url)
        response.raise_for_status()

        with tempfile.TemporaryDirectory() as tempdir:
            filename = file.url.split("/")[-1]
            if not filename.endswith(".xlsx"):
                filename = f"bundesbank_bonds_{dt.datetime.now().strftime('%Y%m%d')}.xlsx"

            filepath = Path(tempdir) / filename
            with filepath.open("wb") as f:
                f.write(response.content)

            excel_data = pd.read_excel(filepath, engine="openpyxl", sheet_name=None)
            return ExcelFile.from_dict(excel_data)


class BundesbankDataTransformer(Transformer):
    class Transformed(ArbitraryBaseModel):
        data: pd.DataFrame
        max_date_in_table: dt.date

    def transform(self, extracted: BundesbankDataExtractor.Extracted) -> Transformed:
        data_by_date = []
        for excel_file in extracted.excel_files:
            for sheet in excel_file.sheets:
                data = self._parse_sheet(sheet)
                data_by_date.append(data)

        if not data_by_date:
            raise ValueError("No data found")
        all_data = pd.concat(data_by_date)

        logger.info(f"Successfully parsed {len(extracted.excel_files)} Excel files")
        return self.Transformed(
            data=all_data,
            max_date_in_table=extracted.max_date_in_table,
        )

    def _parse_sheet(self, sheet: ExcelSheet) -> pd.DataFrame:
        data = sheet.data.copy()
        data = data.dropna()

        # Rename columns as A-Z.
        data.columns = list(ascii_uppercase)[: len(data.columns)]

        # Fix ISIN.
        data["isin"] = [
            f"{row[0]}{row[1]}{int(row[2])}" for row in data.loc[:, ["A", "B", "C"]].values
        ]

        # Rename
        data = data.rename(
            columns={
                "D": "coupon",
                "E": "description",
                "F": "maturity_date",
                "G": "residual_life",
                "H": "issue_volume",
                "I": "clean_price",
                "J": "yield",
                "K": "dirty_price",
            }
        )

        # Format dates
        data["maturity_date"] = [
            pd.to_datetime(date, format="%d.%m.%Y").date() for date in data["maturity_date"]
        ]

        # Floats
        float_cols = ["coupon", "issue_volume", "clean_price", "yield", "dirty_price"]
        data[float_cols] = data[float_cols].astype(float)

        # Sheet name to as-of date.
        data["date"] = pd.to_datetime(sheet.name, format="%d.%m.%Y").date()

        return data[
            [
                "date",
                "isin",
                "description",
                "coupon",
                "maturity_date",
                "issue_volume",
                "clean_price",
                "yield",
                "dirty_price",
            ]
        ]


class BundesbankDataLoader(Loader):
    def load(self, transformed: BundesbankDataTransformer.Transformed) -> None:
        bonds_to_insert = []
        metrics_to_insert = []
        for _, row in transformed.data.iterrows():
            bond = Bond(
                isin=row["isin"],
                description=row["description"],
                coupon=row["coupon"],
                maturity_date=row["maturity_date"],
                issue_volume=row["issue_volume"],
            )
            if bond not in bonds_to_insert:
                bonds_to_insert.append(bond)

            metric = BondMetric(
                date=row["date"],
                isin=row["isin"],
                clean_price=row["clean_price"],
                dirty_price=row["dirty_price"],
                _yield=row["yield"],
            )
            metric.bond = bond
            if metric.date > transformed.max_date_in_table:
                metrics_to_insert.append(metric)

        logger.info(f"Upserting {len(bonds_to_insert)} bond rows...")
        Bond.objects.bulk_create(
            bonds_to_insert,
            update_conflicts=True,
            unique_fields=["isin"],
            update_fields=["description", "coupon", "maturity_date", "issue_volume"],
        )

        logger.info(f"Inserting {len(metrics_to_insert)} bond metric rows...")
        BondMetric.objects.bulk_create(metrics_to_insert, ignore_conflicts=True)

        logger.info("Success.")
