from collections import defaultdict
from abc import ABC, abstractmethod
import datetime
from typing import Callable
from pathlib import Path
import re


class AbstractStatement(ABC):

    def __init__(self, date: datetime.date, amount: float, desc: str):
        self._date:     datetime.date = date
        self._amount:   float = amount
        self._desc:     str = desc

    def get_desc(self) -> str:
        return self._desc

    def get_amount(self) -> float:
        return self._amount

    def get_date(self) -> datetime.date:
        return self._date        
    
    def __str__(self) -> str:
        return f'{self._date}, {self._amount}, {self._desc}'
    
    def __repr__(self):
        return f"AbstractStatement(date={self._date}, amount={self._amount}, desc={self._desc})"

Predicate = Callable[[AbstractStatement], bool]
SignalDetector = Callable[[list[AbstractStatement]], bool]

class AbstractStatements(ABC):

    def __init__(self, statements: dict[datetime.date, list[AbstractStatement]]):
        self._statements:       dict[datetime.date, list[AbstractStatement]] = statements
        self._withdrawls_view:  dict[datetime.date, list[AbstractStatement]] = self._create_view(self._withdrawl_filter)
        self._deposits_view:    dict[datetime.date, list[AbstractStatement]] = self._create_view(self._deposit_filter)

    @abstractmethod
    def _withdrawl_filter(statement: AbstractStatement) -> bool:
        pass

    @abstractmethod
    def _deposit_filter(statement: AbstractStatement) -> bool:
        pass
    
    def _create_view(
            self, 
            predicate: Callable[[AbstractStatement], bool]
    ) -> dict[datetime.date, list[AbstractStatement]]:
        view = defaultdict(list)
        for day, statements in self._statements.items():
            for statement in statements:
                if predicate(statement):
                    view[day].append(statement)
        
        return view

    def get_daily_statements(self) -> dict[datetime.date, list[AbstractStatement]]:
        return self._statements

    def get_withdrawls_view(self) -> dict[datetime.date, list[AbstractStatement]]:
        return self._withdrawls_view

    def get_deposits_view(self) -> dict[datetime.date, list[AbstractStatement]]:
        return self._deposits_view
     
    @staticmethod
    def _normalize_desc(s: str) -> str:
        s = s.upper()
        s = re.sub(r"\d+", "", s)
        s = re.sub(r"\s+", " ", s)
        return s.strip()

    def discover_candidates(
            self,
            predicate: Predicate
    ) -> dict[str, list[AbstractStatement]]:
        candidates = defaultdict(list)
        for _, statements in self._statements.items():
            for statement in statements:
                if predicate(statement):
                    key = self._normalize_desc(statement.get_desc())
                    candidates[key].append(statement)
        return candidates

    def discover_signals(
        self,
        candidates: dict[str, list[AbstractStatement]],
        detector: SignalDetector
    ) -> dict[str, list[AbstractStatement]]:
        signals = {}
        for key, statements in candidates.items():
            if detector(statements):
                signals[key] = statements
        
        return signals

    def aggregate_daily(
        statements: list[AbstractStatement]
    ) -> list[AbstractStatement]:
        
        totals = defaultdict(float)

        for s in statements:
            totals[s.get_date()] += s.get_amount()
        
        aggregated = []
        for date, amount in totals.items():
            aggregated.append(
                type(statements[0])(date=date, amount=amount, desc=statements[0].get_desc())
            )
        
        return aggregated
