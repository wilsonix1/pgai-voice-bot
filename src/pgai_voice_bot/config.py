from __future__ import annotations

import os
from dataclasses import dataclass


ASSESSMENT_NUMBER = "+18054398008"


@dataclass(frozen=True)
class Settings:
    livekit_url: str
    livekit_api_key: str
    livekit_api_secret: str
    sip_outbound_trunk_id: str
    assessment_number: str = ASSESSMENT_NUMBER


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def load_settings() -> Settings:
    configured_number = os.getenv("PGAI_TEST_NUMBER", ASSESSMENT_NUMBER)
    if normalize_phone(configured_number) != ASSESSMENT_NUMBER:
        raise RuntimeError(
            f"PGAI_TEST_NUMBER must stay pinned to {ASSESSMENT_NUMBER}; got {configured_number}"
        )

    return Settings(
        livekit_url=require_env("LIVEKIT_URL"),
        livekit_api_key=require_env("LIVEKIT_API_KEY"),
        livekit_api_secret=require_env("LIVEKIT_API_SECRET"),
        sip_outbound_trunk_id=require_env("SIP_OUTBOUND_TRUNK_ID"),
    )


def normalize_phone(phone: str) -> str:
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) == 10:
        digits = f"1{digits}"
    return f"+{digits}"


def assert_allowed_destination(phone: str) -> str:
    normalized = normalize_phone(phone)
    if normalized != ASSESSMENT_NUMBER:
        raise ValueError(f"Refusing to call {phone}; only {ASSESSMENT_NUMBER} is allowed")
    return normalized
