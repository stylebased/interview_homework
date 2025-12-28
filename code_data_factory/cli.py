import argparse

from .analyzer import run_analysis
from .scene1_pipeline import generate_scene1
from .scene2_pipeline import generate_scene2
from .postprocess import run_all as postprocess_all


def main():
    parser = argparse.ArgumentParser(description="Codebase Trainer Data Factory")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("analyze", help="Scan target repo and build skeleton/chunks")

    s1 = sub.add_parser("scene1", help="Generate Scene 1 (code Q&A) data")
    s1.add_argument("--limit", type=int, default=50, help="Max number of chunks")
    s1.add_argument("--qa-count", type=int, default=3, help="QAs per chunk")
    s1.add_argument("--dry-run", action="store_true")

    s2 = sub.add_parser("scene2", help="Generate Scene 2 (design) data")
    s2.add_argument("--count", type=int, default=10, help="Design samples count")
    s2.add_argument("--dry-run", action="store_true")

    sub.add_parser("postprocess", help="Run all postprocessing & merge SFT")

    args = parser.parse_args()

    if args.command == "analyze":
        run_analysis()
    elif args.command == "scene1":
        generate_scene1(limit=args.limit, qa_count=args.qa_count, dry_run=args.dry_run)
    elif args.command == "scene2":
        generate_scene2(count=args.count, dry_run=args.dry_run)
    elif args.command == "postprocess":
        postprocess_all()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
