from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv
from livekit import api
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RoomInputOptions,
    RunContext,
    WorkerOptions,
    cli,
    function_tool,
    get_job_context,
)
from livekit.plugins import cartesia, deepgram, noise_cancellation, openai, silero
from livekit.plugins.turn_detector.english import EnglishModel

from pgai_voice_bot.config import assert_allowed_destination, load_settings
from pgai_voice_bot.scenarios import get_scenario
from pgai_voice_bot.transcript import TranscriptWriter


load_dotenv(".env")
logger = logging.getLogger("pgai-patient-bot")
logger.setLevel(logging.INFO)


class PatientBot(Agent):
    def __init__(self, instructions: str):
        super().__init__(instructions=instructions)

    async def hangup(self) -> None:
        job_ctx = get_job_context()
        await job_ctx.api.room.delete_room(api.DeleteRoomRequest(room=job_ctx.room.name))

    @function_tool()
    async def end_call(self, ctx: RunContext) -> str:
        """End the call after the scenario goal is complete or the practice agent cannot proceed."""
        current_speech = ctx.session.current_speech
        if current_speech:
            await current_speech.wait_for_playout()
        await self.hangup()
        return "Call ended."


def build_call_id(scenario_id: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{scenario_id}"


async def entrypoint(ctx: JobContext) -> None:
    settings = load_settings()
    metadata: dict[str, Any] = json.loads(ctx.job.metadata or "{}")
    scenario_id = metadata.get("scenario_id", "schedule_new_patient")
    scenario = get_scenario(scenario_id)
    phone_number = assert_allowed_destination(metadata.get("phone_number", settings.assessment_number))
    call_id = metadata.get("call_id") or build_call_id(scenario_id)
    participant_identity = f"pgai-test-line-{call_id}"

    logger.info("connecting to room %s for scenario %s", ctx.room.name, scenario_id)
    await ctx.connect()

    transcript = TranscriptWriter(call_id=call_id, scenario_id=scenario_id)
    agent = PatientBot(instructions=scenario.instructions())
    session = AgentSession(
        turn_detection=EnglishModel(),
        vad=silero.VAD.load(),
        stt=deepgram.STT(),
        llm=openai.LLM(model=metadata.get("llm_model", "gpt-4o-mini")),
        tts=cartesia.TTS(),
    )
    transcript.attach_to_session(session)

    session_started = asyncio.create_task(
        session.start(
            agent=agent,
            room=ctx.room,
            room_input_options=RoomInputOptions(
                noise_cancellation=noise_cancellation.BVCTelephony(),
            ),
        )
    )

    try:
        await ctx.api.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                room_name=ctx.room.name,
                sip_trunk_id=settings.sip_outbound_trunk_id,
                sip_call_to=phone_number,
                participant_identity=participant_identity,
                wait_until_answered=True,
            )
        )
        await session_started
        await ctx.wait_for_participant(identity=participant_identity)
        logger.info("assessment line answered for %s", call_id)
        transcript.event("system", f"Call connected to {phone_number}")
    except api.TwirpError as exc:
        logger.error(
            "SIP call failed: %s status=%s %s",
            exc.message,
            exc.metadata.get("sip_status_code"),
            exc.metadata.get("sip_status"),
        )
        transcript.event("system", f"SIP call failed: {exc.message}")
        ctx.shutdown()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, agent_name="pgai-patient-bot"))
