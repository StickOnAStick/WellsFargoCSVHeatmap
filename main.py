from src.statements.recurrence import is_recurring, recurrence_score, aggregate_daily
from src.statements.wells_fargo import WellsFargoStatements

FILE_PATH = "data/asd.csv"


def main():

    statements = WellsFargoStatements(FILE_PATH)

    candidates = statements.discover_candidates(statements._deposit_filter)
    signals = statements.discover_signals(
        candidates,
        lambda stmts: is_recurring(aggregate_daily(stmts))
    )
    print(f"Signals: {signals}")

    scored = {
        k: recurrence_score(aggregate_daily(v)) for k, v in candidates.items()
    }

    scored_signals = {
        k: recurrence_score(aggregate_daily(v)) for k, v in signals.items()
    }

    print(scored)
    print("\n\n\n")
    print( "\n".join(f"{k} - {v}" for k, v in scored_signals.items()))

    withdrawl_candidates = statements.discover_candidates(statements._withdrawl_filter)
    signals = statements.discover_signals(
        candidates=withdrawl_candidates,
        detector=lambda stmts: is_recurring(aggregate_daily(stmts), threshold=0.8)
    )
    scored_signals = {
        k: recurrence_score(aggregate_daily(v)) for k, v in signals.items()
    }

    print( "\n".join(f"{k} - {v}" for k, v in scored_signals.items()))

    return


if __name__ == "__main__":
    main()
