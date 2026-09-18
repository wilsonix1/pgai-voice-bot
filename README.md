# Pretty Good AI Voice Bot Challenge

Python LiveKit Agents voice bot for the Pretty Good AI engineering challenge. It calls only the assessment number `+1-805-439-8008`, simulates patient scenarios, records transcripts, and helps produce a bug report from the calls.

## Requirements Summary

- Python implementation using LiveKit Agents pipeline mode
- Separate STT, LLM, and TTS components
- No realtime/speech-to-speech models and no hosted voice-agent platforms
- Minimum 10 real calls to `+1-805-439-8008`
- Submit code, README, architecture doc, transcripts, recordings, bug report, and two Loom videos

## Setup

```bash
cd pgai-voice-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
cp .env.example .env
```

Fill in `.env`:

- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- `SIP_OUTBOUND_TRUNK_ID`
- `OPENAI_API_KEY`
- `DEEPGRAM_API_KEY`
- `CARTESIA_API_KEY`

Create or configure a LiveKit SIP outbound trunk before running real calls.

## Run The Worker

In terminal 1:

```bash
source .venv/bin/activate
python -m pgai_voice_bot.agent dev
```

The worker registers as `pgai-patient-bot` and waits for dispatches.

## Make The 10 Assessment Calls

In terminal 2:

```bash
source .venv/bin/activate
python -m pgai_voice_bot.run_calls --count 10 --delay-seconds 150
```

The dispatcher rotates through the first 10 scenarios in `scenarios.json`. The code refuses to dial anything except `+1-805-439-8008`.

To run one scenario:

```bash
python -m pgai_voice_bot.run_calls --count 1 --scenario office_hours_weekend
```

## Artifacts

Transcripts are written to:

```text
artifacts/transcripts/<call-id>.txt
artifacts/transcripts/<call-id>.jsonl
```

For audio recordings, use LiveKit Cloud's session/telephony recording export or configure LiveKit Egress for your project, then place the OGG or MP3 files in:

```text
artifacts/recordings/
```

Use the same call id in the transcript and recording filenames so reviewers can pair them easily.

## Generate A Bug Report Draft

After transcripts are available:

```bash
python -m pgai_voice_bot.analyze_transcripts artifacts/transcripts/*.txt --out artifacts/bug-report.md
```

Review and edit the output manually before submission. The best final report should focus on material product issues, not wording nitpicks.

## Suggested Submission Layout

```text
ARCHITECTURE.md
BUG_REPORT.md
README.md
artifacts/
  transcripts/
  recordings/
scenarios.json
src/
```

## Loom Checklist

- Walkthrough video: explain the pipeline, scenario strategy, turn-taking decisions, and what issues were found.
- AI-debugging video: show one concrete debugging loop, such as fixing transcript capture or improving a scenario after listening to a call.
