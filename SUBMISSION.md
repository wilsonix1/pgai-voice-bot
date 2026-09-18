# Submission Helper

Use this file while filling out the Pretty Good AI submission form.

## Form Fields

First and Last name:

```text
Wilson Mugabo
```

Email:

```text
wilsonix1@gmail.com
```

GitHub Repository Link:

```text
TODO: paste the public GitHub repo URL after pushing this project
```

Did you make GitHub Repository PUBLIC:

```text
YES
```

AI BOT Phone number:

```text
TODO: paste the outbound caller ID used by your LiveKit SIP trunk, in E.164 format, for example +12065550123
```

Do not enter `+18054398008` here. That is the assessment destination number, not your bot's caller ID.

2 Loom Links:

```text
1) TODO: public Loom walkthrough link
2) TODO: public Loom AI-debugging session link
```

Did you make BOTH Loom links PUBLIC:

```text
YES
```

US Work Authorization:

```text
TODO: choose Yes/No/Other truthfully
```

Ready to start immediately:

```text
TODO: choose Yes/No/Other truthfully
```

## Written Answer Draft

Prompt: Tell us something you went from near-zero to genuinely capable at in the last six months. How did you learn it, where did you get stuck, and how do you know you're actually there?

```text
In the last six months, I went from having limited hands-on experience with production-style AI voice systems to being able to build and reason through a working voice-agent pipeline. I learned by breaking the problem into smaller pieces: telephony, LiveKit rooms, SIP outbound calling, speech-to-text, LLM response generation, text-to-speech, transcript capture, and post-call analysis.

The hardest part was understanding how voice systems behave differently from normal chat apps. Turn-taking, interruptions, latency, and audio quality all matter, and a bot that looks good in code can still feel awkward on a real phone call. I got stuck around connecting the outbound call flow cleanly and making sure the system stayed within the challenge rules by using a pipeline architecture instead of realtime speech-to-speech.

I know I am genuinely capable now because I can explain the architecture, make tradeoff decisions between providers, run multiple realistic test scenarios, inspect transcripts, identify product-quality bugs, and package the work into a repo another engineer can understand and run.
```

## Walkthrough Loom Outline

Target length: 2-3 minutes.

```text
Hi, I'm Wilson. This is my Pretty Good AI engineering challenge submission.

I built a Python LiveKit Agents bot that calls the assessment line as a patient simulator. The important constraint was to use pipeline mode, so the call uses Deepgram for STT, OpenAI for the LLM, and Cartesia for TTS rather than a realtime speech-to-speech model.

The code is organized around scenarios. scenarios.json defines ten patient cases covering scheduling, rescheduling, cancellation, medication refills, insurance questions, location confusion, urgent symptoms, interruptions, and vague requests. The dispatcher sends each scenario into a fresh LiveKit room and the agent is hard-coded to call only +1-805-439-8008.

The worker starts the LiveKit AgentSession before dialing so it is ready as soon as the assessment line answers. During each call I save transcript events to artifacts/transcripts. Afterward I run the transcript analyzer to draft a bug report, then manually review for the highest-signal product issues.

The main tradeoff I made was keeping the system simple and inspectable. Rather than overbuilding a test harness, I focused on coherent calls, good scenario coverage, clear transcripts, and a bug report a reviewer can verify against recordings.
```

## AI Debugging Loom Outline

Target length: 2-3 minutes. Record yourself showing one real fix or iteration.

```text
For the debugging video, I'm showing how I used AI to iterate on the bot after finding an implementation issue.

The first version could make outbound calls, but the submission also needed evidence: transcripts and recordings. I asked the AI to inspect the LiveKit session event model and then added a TranscriptWriter that listens for final user_input_transcribed events and assistant conversation_item_added events.

Then I ran local validation: JSON formatting for scenarios and Python compile checks. That caught packaging friction from the src layout, so I added pyproject.toml and updated the README to include pip install -e .

This is the loop I used throughout: read the requirement, implement the smallest runnable version, verify locally, then improve the artifact path so the final submission is easy to review.
```

## Final Checklist

- [ ] Add real credentials to local `.env` only
- [ ] Run the worker
- [ ] Dispatch 10 calls
- [ ] Save 10 transcripts
- [ ] Export or collect 10 OGG/MP3 recordings
- [ ] Run transcript analysis and edit the final bug report
- [ ] Push public GitHub repo
- [ ] Record public walkthrough Loom
- [ ] Record public AI-debugging Loom
- [ ] Upload resume in the form
- [ ] Paste the outbound caller ID, not the assessment number
