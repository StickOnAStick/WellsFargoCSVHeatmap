from abc import ABC, abstractmethod
from pathlib import Path
from ..statements.statements import AbstractStatement
import datetime

class AbstractStatementParser(ABC):

    def __init__(self, file_path: Path):
        self._source_file: Path = file_path
    
    @abstractmethod
    def get_statements(self) -> dict[datetime.date, list[AbstractStatement]]:
        pass

