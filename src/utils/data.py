"""Data utils."""

from abc import ABC, abstractmethod
from pydantic import BaseModel

from src.utils.logger import logger


class Extractor(ABC):
    class Extracted(BaseModel): ...

    @abstractmethod
    def extract(self) -> Extracted: ...


class Transformer(ABC):
    class Transformed(BaseModel): ...

    @abstractmethod
    def transform(self, extracted: Extractor.Extracted) -> Transformed: ...


class Loader(ABC):
    @abstractmethod
    def load(self, transformed: Transformer.Transformed) -> None: ...


def run_pipeline(
    extractor: Extractor,
    transformer: Transformer,
    loader: Loader,
):
    logger.info("Starting data pipeline")
    logger.info("Extracting data...")
    extracted = extractor.extract()

    logger.info("Transforming data...")
    transformed = transformer.transform(extracted)

    logger.info("Loading data...")
    loader.load(transformed)
