"""Usage: python -m demo.judge_mode --phase all [--dry-run]."""
import argparse
import json
from urllib.error import URLError
from .traffic_generator import TrafficGenerator


def main():
    parser = argparse.ArgumentParser(description="Replay clearly marked synthetic flow records")
    parser.add_argument("--api-url", default="http://127.0.0.1:8000")
    parser.add_argument("--phase", choices=("all",) + TrafficGenerator.PHASES, default="all")
    parser.add_argument("--dry-run", action="store_true", help="Print records without contacting the API")
    args = parser.parse_args()
    generator = TrafficGenerator(api_url=args.api_url)
    phases = generator.PHASES if args.phase == "all" else [args.phase]
    try:
        for phase in phases:
            result = {"flows": generator.generate(phase)} if args.dry_run else generator.submit(phase)
            print(json.dumps({"phase": phase, "synthetic": True, "result": result}, indent=2))
    except (URLError, TimeoutError) as exc:
        parser.exit(1, f"Cannot submit replay to {args.api_url}: {exc}\nStart the backend or use --dry-run.\n")


if __name__ == "__main__":
    main()
