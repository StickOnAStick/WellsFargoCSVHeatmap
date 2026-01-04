import csv
from  dataclasses import dataclass
from collections import defaultdict
import datetime

FILE_PATH = "Data/Wells/Checking2.csv"

@dataclass
class WellsStatement:
    date:   datetime.date
    amount: float 
    desc:   str

daily_statements: dict[datetime.date, list[WellsStatement]] = defaultdict(list)
with open(FILE_PATH, "r", newline='') as statement:
    csvreader = csv.reader(statement, delimiter=",")
    for row in csvreader:
        split_date: list[int] = [int(x) for x in row[0].split("/")]
        date: datetime.date = datetime.date(
            date[2],
            date[0],
            date[1],
        )
        val: WellsStatement = WellsStatement(
            date=date,
            amount=float(row[1]),
            desc=row[-1]
        )
        daily_statements[date].append(val)


views = {
    "deposits": defaultdict(list),
    "withdrawls": defaultdict(list)
}
# Sort by withdrawl / deposit
for day, statements in daily_statements.items():
    for stmt in statements:
        if stmt['amount'] >= 0:
            views["deposits"][day].append(stmt)
        else:
            views["withdrawls"][day].append(stmt)



# Discover all days where a recurring deposit occurred.
def detect_recurring_deposits(
    statements: list[Statement]
)