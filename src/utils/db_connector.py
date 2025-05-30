
from django.utils.connection import cached_property
from src.utils.configuration import conf
from sqlalchemy import create_engine
from sqlalchemy.sql.expression import Select
import pandas as pd


class DBConnector:
    def __init__(self, name: str):
        self.name = name
        self._config = conf.get(name)

    @cached_property
    def _url(self):
        return (
            "postgresql://"
            f"{self._config['name']}:{self._config['password']}"
            f"@{self._config['host']}:{self._config['port']}"
            f"/{self._config['name']}"
        )

    @cached_property
    def engine(self):
        return create_engine(self._url)

    def get_data(self, select: Select) -> pd.DataFrame:
        return pd.read_sql(self, self.engine)
