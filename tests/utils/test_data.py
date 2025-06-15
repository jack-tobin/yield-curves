from unittest.mock import MagicMock, patch

from pydantic.main import BaseModel

from src.utils.data import Extractor, Loader, Transformer, run_pipeline


class MyExtractor(Extractor):
    class Extracted(BaseModel):
        data: str

    def extract(self):
        return self.Extracted(data="extracted")


class MyTransformer(Transformer):
    class Transformed(BaseModel):
        data: str

    def transform(self, data):
        return self.Transformed(data="transformed")


class MyLoader(Loader):
    def load(self, data):
        return


@patch.object(MyLoader, "load")
@patch.object(MyTransformer, "transform")
@patch.object(MyExtractor, "extract")
def test_run_pipeline(mock_extract: MagicMock, mock_transform: MagicMock, mock_load: MagicMock):
    mock_extracted = MagicMock()
    mock_extract.return_value = mock_extracted

    mock_transformed = MagicMock()
    mock_transform.return_value = mock_transformed

    extractor = MyExtractor()
    transformer = MyTransformer()
    loader = MyLoader()

    run_pipeline(extractor, transformer, loader)

    assert mock_extract.called
    mock_transform.assert_called_once_with(mock_extracted)
    mock_load.assert_called_once_with(mock_transformed)
