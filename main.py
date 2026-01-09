from src.analysis.recurrence import is_recurring, recurrence_score, aggregate_daily
from src.statements.wells_fargo import WellsFargoStatements
import src.api.api as API

FILE_PATH = "data/a.csv"
JSON_OUTPUT_FILE = "frontend/calendar.json"

def main():

    statements = WellsFargoStatements(FILE_PATH)

    candidates = statements.discover_candidates(statements._deposit_filter)
    signals = statements.discover_signals(
        candidates,
        lambda stmts: is_recurring(aggregate_daily(stmts))
    )

    scored = {
        k: recurrence_score(aggregate_daily(v)) for k, v in candidates.items()
    }

    scored_signals = {
        k: recurrence_score(aggregate_daily(v)) for k, v in signals.items()
    }

    print(f"Candidates: \n{"\n".join(f"{k} - {v}" for k, v in candidates.items())}\n\n")
    print(f"Signals: \n{"\n".join(f"{k} - {v}" for k, v, in signals.items())}\n\n")

    print(f"Scored candidates: \n{"\n".join(f"{k} - {v}" for k, v in scored.items())}\n\n")
    print(f"Scored signals: \n{"\n".join(f"{k} - {v}" for k, v in scored_signals.items())}\n\n")

    calendar_view = API.build_calendar_from_statements(statements, signals)
    with open(JSON_OUTPUT_FILE, 'w+', encoding='utf-8') as f:
        f.write(calendar_view.model_dump_json())

    return


if __name__ == "__main__":
    main()
