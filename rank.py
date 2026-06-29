"""Main CLI entry point: produces the ranked submission CSV."""

import argparse
from ranker.pipeline import run_pipeline


def main():
    parser = argparse.ArgumentParser(description="Rank candidates against job description")
    parser.add_argument("--candidates", default="Dataset/candidates.jsonl",
                        help="Path to candidates JSONL file")
    parser.add_argument("--output", default="submission.csv",
                        help="Output CSV path")
    parser.add_argument("--precomputed", default="precomputed",
                        help="Directory with precomputed artifacts")
    parser.add_argument("--top-k", type=int, default=100,
                        help="Number of top candidates to output")
    args = parser.parse_args()

    run_pipeline(
        candidates_path=args.candidates,
        output_path=args.output,
        precomputed_dir=args.precomputed,
        top_k=args.top_k,
    )


if __name__ == "__main__":
    main()
