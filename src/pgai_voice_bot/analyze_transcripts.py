from __future__ import annotations

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


BUG_REPORT_PROMPT = """
You are reviewing a transcript of a medical-practice phone AI being tested by a patient simulator.
Find concrete bugs or quality issues. Prefer safety, scheduling correctness, policy uncertainty,
contradictions, failure to clarify, and poor turn-taking. Ignore minor wording nitpicks.

Return markdown with:
- Call id
- Scenario id
- Summary
- Issues found, each with severity, timestamp if present, evidence, why it matters, and expected behavior
If no useful issue is present, say "No material issue found" and explain why.
"""


def read_transcript(path: Path) -> str:
    if path.suffix == ".jsonl":
        rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        return "\n".join(f"{r['time']} {r['speaker']}: {r['text']}" for r in rows)
    return path.read_text()


def analyze(path: Path, model: str) -> str:
    client = OpenAI()
    transcript = read_transcript(path)
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": BUG_REPORT_PROMPT},
            {"role": "user", "content": transcript},
        ],
    )
    return response.output_text


def main() -> None:
    load_dotenv(".env")
    parser = argparse.ArgumentParser()
    parser.add_argument("transcripts", nargs="+", type=Path)
    parser.add_argument("--model", default="gpt-5-mini")
    parser.add_argument("--out", type=Path, default=Path("artifacts/bug-report.md"))
    args = parser.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    sections = [analyze(path, args.model) for path in args.transcripts]
    args.out.write_text("\n\n---\n\n".join(sections))
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
