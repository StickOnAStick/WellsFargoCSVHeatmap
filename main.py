import csv
from  dataclasses import dataclass
from collections import defaultdict
import datetime
import calendar
from HTML.base_content import BASE_HTML
from HTML.injector import DivInjector
import webbrowser
from pathlib import Path

FILE_PATH = "data/some/csv_path.csv"
PAY_CHECK_DESC = "Some_bi-weekly_paycheck_description"

@dataclass
class WellsStatement:
    date:   datetime.date
    amount: float 
    desc:   str


class StatementViewer:
    def __init__(self, file_path: str):
        self.statements_by_date: dict[datetime.date, list[WellsStatement]] = self.create_statements_by_date_dict(file_path=file_path)
        self.deposits: dict[datetime.date, list[WellsStatement]] = self.create_activity_views(True)
        self.withdrawls: dict[datetime.date, list[WellsStatement]] = self.create_activity_views(False)

    def create_statements_by_date_dict(self, file_path: str) -> dict[datetime.date, list[WellsStatement]]:
        """
        returns date-ordered dict of every transaction for a given day.
        
        :param self: the class
        :param file_path: Path to the input file.
        """
        daily_statements: dict[datetime.date, list[WellsStatement]] = defaultdict(list)
        with open(file_path, "r", newline='') as statement:
            csvreader = csv.reader(statement, delimiter=",")
            for row in csvreader:
                split_date: list[int] = [int(x) for x in row[0].split("/")]
                date: datetime.date = datetime.date(
                    split_date[2],
                    split_date[0],
                    split_date[1],
                )
                val: WellsStatement = WellsStatement(
                    date=date,
                    amount=float(row[1]),
                    desc=row[-1]
                )
                daily_statements[date].append(val)
        daily_statements = dict(sorted(daily_statements.items()))
        return daily_statements
    
    def create_activity_views(self, deposit: bool):
        d = defaultdict(list)
        for day, statements in self.statements_by_date.items():
            for stmt in statements:
                if deposit and stmt.amount >= 0:
                    d[day].append(stmt)
                elif not deposit and stmt.amount <= 0:
                    d[day].append(stmt)
        return d
    

    @staticmethod
    def get_daily_totals(statements: dict[datetime.date, list[WellsStatement]]) -> dict[datetime.date, float]:
        d: dict[datetime.date, float] = defaultdict(float)
        for day, stmts in statements.items():
            for stmt in stmts:
                d[day] += stmt.amount
        return d
    
    @staticmethod
    def get_averaged_daily_totals(statements: dict[datetime.date, list[WellsStatement]]) -> dict[datetime.date, float]:
        # Find paychecks
        paychecks = []
        for day, stmts in statements.items():
            for stmt in stmts:
                if PAY_CHECK_DESC in stmt.desc and stmt.amount > 0:
                    paychecks.append((day, stmt.amount))
        paychecks.sort(key=lambda x: x[0])
        
        new_totals = defaultdict(float)
        # First, set all days to their original totals
        for day, stmts in statements.items():
            new_totals[day] = sum(stmt.amount for stmt in stmts)
        
        # Then, override for paycheck periods
        for i in range(len(paychecks)):
            date1, amount1 = paychecks[i]
            if i < len(paychecks) - 1:
                date2 = paychecks[i+1][0]
            else:
                date2 = date1 + datetime.timedelta(days=14)
            average_income = amount1 / 14
            current_date = date1
            while current_date < date2:
                negatives = sum(stmt.amount for stmt in statements.get(current_date, []) if stmt.amount < 0)
                new_totals[current_date] = negatives + average_income
                current_date += datetime.timedelta(days=1)
        return dict(new_totals)

    def gen_html_calendar(self):
        daily_totals = self.get_averaged_daily_totals(self.statements_by_date)
        vals = ColoredCalendar(daily_totals, firstweekday=6)
        html = vals.formatyear(
            theyear=2025,
            width=5
        )

        return html

class ColoredCalendar(calendar.HTMLCalendar):
    def __init__(self, daily_totals, **kwargs):
        super().__init__(**kwargs)
        self.daily_totals = daily_totals

    def formatmonth(self, theyear, themonth, withyear=True):
        self.current_year = theyear
        self.current_month = themonth
        return super().formatmonth(theyear, themonth, withyear)

    def formatday(self, theday, weekday):
        if theday == 0:
            return super().formatday(theday, weekday)
        date = datetime.date(self.current_year, self.current_month, theday)
        total = self.daily_totals.get(date, 0)
        if total > 0:
            color = 'green'
        elif total < 0:
            color = 'red'
        else:
            color = None
        html = super().formatday(theday, weekday)
        if html.strip() and color:
            html = html.replace('<td ', f'<td style="background-color: {color};" ', 1)
        return html

class HTMLCalendar:

    def __init__(self, html_str: str):
        self.in_html: str = html_str
        self.base_content: str = BASE_HTML
        self.target_id: str = "calendar"

    def generate_html(self, out_file: str):
        injector = DivInjector(
            self.target_id,
            inject_html=self.in_html
        )
        injector.feed(self.base_content)

        with open(out_file, "w", encoding="utf8") as f:
            f.write("".join(injector.output))

        webbrowser.open(Path(out_file).absolute().as_uri())


def main():

    stmtView = StatementViewer(FILE_PATH)
    html = stmtView.gen_html_calendar()

    calendar = HTMLCalendar(html)
    calendar.generate_html('test.html')

    return


if __name__ == "__main__":
    main()
