from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class TranscriptWriter:
    def __init__(self, call_id: str, scenario_id: str, out_dir: Path = Path("artifacts/transcripts")):
        self.call_id = call_id
        self.scenario_id = scenario_id
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.jsonl_path = self.out_dir / f"{call_id}.jsonl"
        self.txt_path = self.out_dir / f"{call_id}.txt"

    def event(self, speaker: str, text: str, **extra: Any) -> None:
        text = (text or "").strip()
        if not text:
            return
        row = {
            "time": datetime.now(timezone.utc).isoformat(),
            "call_id": self.call_id,
            "scenario_id": self.scenario_id,
            "speaker": speaker,
            "text": text,
            **extra,
        }
        with self.jsonl_path.open("a") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        with self.txt_path.open("a") as f:
            f.write(f"[{row['time']}] {speaker}: {text}\n")

    def attach_to_session(self, session: Any) -> None:
        @session.on("user_input_transcribed")
        def on_user_input(event: Any) -> None:
            if getattr(event, "is_final", False):
                self.event("practice_agent", getattr(event, "transcript", ""))

        @session.on("conversation_item_added")
        def on_conversation_item(event: Any) -> None:
            item = getattr(event, "item", None)
            role = getattr(item, "role", None)
            content = getattr(item, "content", None)
            if role != "assistant":
                return
            if isinstance(content, list):
                text = " ".join(str(part) for part in content)
            else:
                text = str(content or "")
            self.event("patient_bot", text)
