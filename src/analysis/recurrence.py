from ..statements.statements import AbstractStatement, AbstractStatements
from collections import defaultdict
import statistics, datetime
import math

def recurrence_score(statements: list[AbstractStatement]) -> float:
        
    if len(statements) < 3:
        return 0.0
    
    WEEKLY = 7
    BIWEEKLY = 14
    MONTHLY = 30

    MIN_COUNT = 4
    AMT_VARIANCE_TOLERANCE = 0.12
    CADENCE_DELTA_TOLERANCE = 12 # Scales quadratically exp(-v/10)
    CADENCE_TOLERANCE = 4 # days

    CADENCE_WEIGHT = 0.3
    AMOUNT_WEIGHT = 0.3
    COUNT_WEIGHT = 0.4

    # --- sort by date ---
    statements = sorted(statements, key=lambda s: s.get_date())

    # --- cadence score ---
    dates = [s.get_date() for s in statements]
    deltas = [(dates[i+1] - dates[i]).days for i in range(len(dates) - 1)]

    median_delta = statistics.median(deltas)
    delta_variance = statistics.pvariance(deltas)

    # expected candences (days)
    expected = [WEEKLY, BIWEEKLY, MONTHLY]

    cadence_error = min(abs(median_delta - e) for e in expected)
    cadence_score = math.exp(-cadence_error / CADENCE_TOLERANCE) * math.exp(-delta_variance / CADENCE_DELTA_TOLERANCE)

    # ---- Amount stability score ----
    amounts = [abs(s.get_amount()) for s in statements]
    mean_amt = statistics.mean(amounts)
    std = statistics.pstdev(amounts)

    cv = std / (mean_amt + 1e-6)

    amount_score = math.exp(-cv / AMT_VARIANCE_TOLERANCE)

    # count confidence
    count_score = min(len(statements) / MIN_COUNT, 1.0)

    return (
        CADENCE_WEIGHT * cadence_score +
        AMOUNT_WEIGHT * amount_score + 
        COUNT_WEIGHT * count_score
    )

def is_recurring(statements: list[AbstractStatement], threshold: float=0.75) -> bool:
    return recurrence_score(statements=statements) >= threshold


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