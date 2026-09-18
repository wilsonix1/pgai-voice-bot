from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime, timezone

from dotenv import load_dotenv
from livekit import api

from pgai_voice_bot.config import ASSESSMENT_NUMBER, assert_allowed_destination
from pgai_voice_bot.scenarios import load_scenarios


AGENT_NAME = "pgai-patient-bot"


async def dispatch_call(lkapi: api.LiveKitAPI, scenario_id: str, index: int) -> None:
    call_id = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{index:02d}-{scenario_id}"
    room_name = f"pgai-assessment-{call_id}"
    metadata = {
        "phone_number": assert_allowed_destination(ASSESSMENT_NUMBER),
        "scenario_id": scenario_id,
        "call_id": call_id,
    }
    await lkapi.agent_dispatch.create_dispatch(
        api.CreateAgentDispatchRequest(
            agent_name=AGENT_NAME,
            room=room_name,
            metadata=json.dumps(metadata),
        )
    )
    print(f"Dispatched {scenario_id} as {call_id} in room {room_name}")


async def main() -> None:
    load_dotenv(".env")
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--delay-seconds", type=int, default=150)
    parser.add_argument("--scenario", action="append", help="Run only the named scenario id; may repeat.")
    args = parser.parse_args()

    scenarios = load_scenarios()
    scenario_ids = args.scenario or [scenario.id for scenario in scenarios[: args.count]]
    if len(scenario_ids) < args.count:
        scenario_ids = (scenario_ids * ((args.count // len(scenario_ids)) + 1))[: args.count]

    lkapi = api.LiveKitAPI()
    try:
        for index, scenario_id in enumerate(scenario_ids[: args.count], start=1):
            await dispatch_call(lkapi, scenario_id, index)
            if index < args.count:
                await asyncio.sleep(args.delay_seconds)
    finally:
        await lkapi.aclose()


if __name__ == "__main__":
    asyncio.run(main())
