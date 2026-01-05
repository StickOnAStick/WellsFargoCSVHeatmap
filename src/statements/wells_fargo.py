from .statements import AbstractStatement, AbstractStatements
from .parsers import AbstractStatementParser
from collections import defaultdict
from typing import Callable
from pathlib import Path
import datetime
import re
import csv




class WellsStatement(AbstractStatement):
    def __init__(self, date: datetime.date, amount: float, desc: str):
        super().__init__(date=date, desc=desc, amount=amount)

    def get_amount(self):
        return super().get_amount()
    
    def get_date(self):
        return super().get_date()
    
    def get_desc(self):
        return super().get_desc()

    def __repr__(self) -> str:
        return f"WellsStatement(date={self._date}, amount={self._amount}, desc={self._desc})"
    
    def __str__(self):
        return super().__str__()


class WellsCSVParser(AbstractStatementParser):
    def __init__(self, file_path, ):
        super().__init__(file_path)
    
    def get_statements(self) -> dict[datetime.date, list[AbstractStatement]]:
        d = defaultdict(list)
        with open(self._source_file, 'r', newline='', encoding='utf-8') as f:
            csv_reader = csv.DictReader(
                f, 
                fieldnames=['date', 'amount', 'unused', 'unused', 'desc'],
                delimiter=','
            )
            
            for row in csv_reader:
                split_date: list[int] = [int(x) for x in row['date'].split("/")]
                date = datetime.date(split_date[2], split_date[0], split_date[1])
                amt = float(row['amount'].strip().replace(',', '').replace('$', ''))
                statement = WellsStatement(
                    date=date,
                    amount=amt,
                    desc=row['desc']
                )
                d[date].append(statement)
                
        return d


class WellsFargoStatements(AbstractStatements):

    def __init__(self, csv_path: Path):
        parser = WellsCSVParser(csv_path)
        statements = parser.get_statements()
        super().__init__(statements=statements)

    def get_daily_statements(self):
        return super().get_daily_statements()
    
    def get_deposits_view(self):
        return super().get_deposits_view()
    
    def get_withdrawls_view(self):
        return super().get_withdrawls_view()
    
    def _withdrawl_filter(self, statement: WellsStatement) -> bool:
        return statement._amount < 0.0

    def _deposit_filter(self, statement: WellsStatement) -> bool:
        return statement._amount >= 0.0

    def _create_view(self, comparator: Callable[[AbstractStatement], bool]):
        view: dict[datetime.date, list[AbstractStatement]] = defaultdict(list)
        for day, statements in self._statements.items():
            for statement in statements:
                if comparator(statement):
                    view[day].append(statement)
        return view

    def _discover_signals(self, comparator: Callable[[AbstractStatement], bool]):
        signals = defaultdict(list)
        for day, statements in self._statements.items():
            for statement in statements:
                if comparator(statement):
                    key = self._normalize_desc(statement._desc)
                    signals[key].append(statement)
        return signals

    @staticmethod
    def _normalize_desc(s: str) -> str:
        s = s.upper()
        s = re.sub(r"\d+", "", s)
        s = re.sub(r"\s+", " ", s)
        return s.strip()