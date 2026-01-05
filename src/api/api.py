from pydantic import BaseModel
from src.statements.statements import AbstractStatement, AbstractStatements
from collections import defaultdict
import datetime

class FrontendStatementView(BaseModel):
    date:           datetime.date
    desc:           str
    amount:         float
    is_recurring:   bool

class FrontendCalendarDayView(BaseModel):
    date:           datetime.date
    net_daily_avg:  float
    status_color:   str # "green" | "red" explict, not dervied in JS
    statements:     list[FrontendStatementView]

class FrontendCalendarView(BaseModel):
    days: dict[datetime.date, FrontendCalendarDayView]


def make_amortized_frontend_statement(
    day: datetime.date,
    source_desc: str,
    daily_amount: float
) -> FrontendStatementView:
    return FrontendStatementView(
        date=day,
        desc=f"(amortized) {source_desc}",
        amount=daily_amount,
        is_recurring=True
    )

def infer_analysis_end_date(stmts: AbstractStatements) -> datetime.date:
    return max(stmts.get_daily_statements().keys())

def amoritize_signal_to_daily_map(
    signal_statements: list[AbstractStatement],
    end_date: datetime.date
) -> dict[datetime.date, float]:
    """
        Given statements for ONE recurring signal
        return date -> amortized daily contribution
    """

    # Aggregate amounts per day
    by_day = defaultdict(float)
    for s in signal_statements:
        by_day[s.get_date()] += s.get_amount()


    # Sort occurrence days
    days = sorted(by_day.keys())

    daily = defaultdict(float)

    # Spread occurrences until the next
    for i in range(len(days) - 1):
        start   = days[i]
        end     = days[i + 1]

        total = by_day[start]
        span  = (end - start).days
        if span <= 0:
            continue

        daily_rate = total / span

        d = start
        while d < end:
            daily[d] += daily_rate
            d += datetime.timedelta(days=1)

    # Insert final paycheck, abstracting out to last date in the sequence
    last = days[-1]
    total = by_day[last]
    span = (end_date - last).days

    if span > 0:
        rate = total / span
        d = last
        while d <= end_date:
            daily[d] += rate
            d += datetime.timedelta(days=1)

    return daily

def build_calendar_from_statements(
    stmts: AbstractStatements,
    recurring_signals: dict[str, list[AbstractStatement]]
) -> FrontendCalendarView:
    days: dict[datetime.date, FrontendCalendarDayView] = {}

    # Discover recurring lump-sum payments
    recurring_keys = {
        (s.get_date(), stmts._normalize_desc(s.get_desc()))
        for signal_stmts in recurring_signals.values()
        for s in signal_stmts
    }

    # Amortize recurring contributions
    amortized_daily = defaultdict(float)

    for desc, signal_stmts in recurring_signals.items():
        daily_map = amoritize_signal_to_daily_map(
            signal_stmts,
            end_date=infer_analysis_end_date(stmts=stmts)
        )
        for day, amt in daily_map.items():

            if day not in days:
                days[day] = FrontendCalendarDayView(
                    date=day,
                    net_daily_avg=0.0,
                    status_color="green",
                    statements=[],
                )

            amortized_daily[day] += amt
            days[day].statements.append(
                make_amortized_frontend_statement(
                    day=day,
                    source_desc=desc,
                    daily_amount=amt
                )
            )
    
    # Build calendar from days existing per-day storage
    for day, day_stmts in stmts.get_daily_statements().items():

        net = amortized_daily.get(day, 0.0)
        frontend_statements: list[FrontendStatementView] = []

        for s in day_stmts:
            key = (s.get_date(), stmts._normalize_desc(s.get_desc()))
            is_recurring = key in recurring_keys

            # Do NOT add recurring lump sums to the net
            if not is_recurring:
                net += s.get_amount()

            frontend_statements.append(
                FrontendStatementView(
                    date=s.get_date(),
                    desc=s.get_desc(),
                    amount=s.get_amount(),
                    is_recurring=is_recurring,
                )
            )

        if day in days:
            days[day].statements.extend(frontend_statements)
        else:
            days[day] = FrontendCalendarDayView(
                date=day,
                net_daily_avg=0.0,
                status_color="green",
                statements=frontend_statements,
            )
        
        days[day].net_daily_avg = round(net, 2)
        days[day].status_color  = "green" if net >= 0 else "red"

    # Finalize amortized-only days
    for day, view in days.items():
        if view.net_daily_avg == 0.0:
            net = amortized_daily.get(day, 0.0)
            view.net_daily_avg = round(net, 2)
            view.status_color = "green" if net >= 0 else "red"

    # Sort again
    days = dict(
        sorted(
            days.items(),
            key=lambda item: item[0],
            reverse=True
        
        )
    )

    return FrontendCalendarView(days=days)