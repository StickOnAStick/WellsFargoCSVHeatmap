from ..statements.statements import AbstractStatement
from collections import defaultdict
import datetime
import statistics
import math


WEEKLY = 7
BIWEEKLY = 14
MONTHLY = 30

_default_cadences: list[int] = [WEEKLY, BIWEEKLY, MONTHLY]

def recurrence_score(
    statements: list[AbstractStatement],
    cadence_list: list[int] = _default_cadences, 
    
    min_sample_count: int = 4,

    CADENCE_TOLERANCE: float = 4.0, # days
    CADENCE_DELTA_TOLERANCE: float = 12.0, # Scales quadratically exp(-v/10)
    AMT_VARIANCE_TOLERANCE: float = 0.12,
    
    CADENCE_WEIGHT: float = 0.3,
    COUNT_WEIGHT: float = 0.3,
    AMOUNT_WEIGHT: float = 0.4,
) -> float:
        
    if len(statements) < 3:
        return 0.0

    # --- sort by date ---
    statements = sorted(statements, key=lambda s: s.get_date())

    # --- cadence score ---
    dates = [s.get_date() for s in statements]
    deltas = [(dates[i+1] - dates[i]).days for i in range(len(dates) - 1)]

    median_delta = statistics.median(deltas)
    delta_variance = statistics.pvariance(deltas)

    # expected candences (days)
    cadence_error = min(abs(median_delta - e) for e in cadence_list)
    cadence_score = math.exp(-cadence_error / CADENCE_TOLERANCE) * math.exp(-delta_variance / CADENCE_DELTA_TOLERANCE)

    # ---- Amount stability score ----
    amounts = [abs(s.get_amount()) for s in statements]
    mean_amt = statistics.mean(amounts)
    std = statistics.pstdev(amounts)

    cv = std / (mean_amt + 1e-6)

    amount_score = math.exp(-cv / AMT_VARIANCE_TOLERANCE)

    # count confidence
    count_score = min(len(statements) / min_sample_count, 1.0)

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