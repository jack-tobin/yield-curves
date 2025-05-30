"""Test configuration module."""

from src.utils.configuration import Configuration
import pytest
import os


class TestConfiguration:
    @pytest.fixture(scope="class")
    def conf(self) -> Configuration:
        os.environ["CONFIG__SOME__NESTED__VALUE"] = "some_secret_password"
        return Configuration()
        
    def test_get_existing_key(self, conf: Configuration):
        assert conf.get("db.django_test.host") == "test_host"
        assert conf.get("db.django_test.port") == "test_port"

    def test_get_non_existing_key(self, conf: Configuration):
        assert conf.get("non.existing.key", default="default_value") == "default_value"

    def test_environment_variable_override(self, conf: Configuration):
        assert conf.get("some.nested.value") == "some_secret_password"