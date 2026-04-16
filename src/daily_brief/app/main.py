from __future__ import annotations

import argparse

from daily_brief.workflows.daily_brief import run_daily_brief_workflow, run_rss_brief_workflow


def main() -> None:
    parser = argparse.ArgumentParser(description="Run daily brief workflow")
    parser.add_argument("--source", choices=["mock", "rss"], default="mock")
    parser.add_argument(
        "--feed-url",
        action="append",
        default=[],
        help="RSS/Atom feed URL. Can be used multiple times.",
    )
    parser.add_argument("--limit", type=int, default=20, help="Max items to fetch")
    parser.add_argument(
        "--llm",
        choices=["mock", "none", "gemini"],
        default="mock",
        help="Select LLM backend",
    )
    parser.add_argument(
        "--gemini-model",
        default="gemini-2.5-flash",
        help="Gemini model name when --llm gemini",
    )
    args = parser.parse_args()

    try:
        if args.source == "rss":
            feed_urls = args.feed_url or ["https://hnrss.org/frontpage"]
            output = run_rss_brief_workflow(
                feed_urls=feed_urls,
                limit=args.limit,
                llm_backend=args.llm,
                gemini_model=args.gemini_model,
            )
        else:
            output = run_daily_brief_workflow(
                llm_backend=args.llm,
                gemini_model=args.gemini_model,
            )
        print(output)
    except RuntimeError as exc:
        print("Failed to run workflow.")
        print(f"Reason: {exc}")


if __name__ == "__main__":
    main()
