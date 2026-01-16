from pathlib import Path
from src.statements.statements import AbstractStatement

class App():

    def __init__(self, data_directory: str):
        self._data_dir: str = Path().from_uri(data_directory)
        self._supported_banks: list[str] = ["Wells", "Chase"]
        
    def discover_recurring(self, ):
        pass