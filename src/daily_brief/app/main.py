from __future__ import annotations

from daily_brief.workflows.daily_brief import run_daily_brief_workflow


def main() -> None:
    try:
        output = run_daily_brief_workflow()
        print(output)
    except RuntimeError as exc:
        print("Failed to run workflow.")
        print(f"Reason: {exc}")


if __name__ == "__main__":
    main()
