from collections import defaultdict
from abc import ABC, abstractmethod
import datetime
from typing import Callable
from pathlib import Path

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


class AbstractStatements(ABC):

    def __init__(self, statements: dict[datetime.date, list[AbstractStatement]]):
        self._statements:       dict[datetime.date, list[AbstractStatement]] = statements
        self._withdrawls_view:  dict[datetime.date, list[AbstractStatement]] = self._create_view(self._withdrawl_filter)
        self._deposits_view:    dict[datetime.date, list[AbstractStatement]] = self._create_view(self._deposit_filter)

        self._discovered_withdrawl_signals: dict[str, list[AbstractStatement]] = defaultdict(list)
        self._discovered_deposit_signals:   dict[str, list[AbstractStatement]] = defaultdict(list)

        self._average_monthly_expendature:  dict[datetime.date, float] = defaultdict(float)
        self._average_monthly_deposits:     dict[datetime.date, float] = defaultdict(float)

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
     
   

    @abstractmethod
    def _discover_signals(self, comparator: Callable[[any], bool], label: str) -> dict[str, list[AbstractStatement]]:
        pass

    

