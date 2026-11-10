# ethglobal-judge

A Claude Code skill for judging hackathon projects (built for ETHGlobal, works anywhere).

You watch the pitch. Claude reads the repo, checks git history and onchain
state, and writes a scored report in about 3 minutes:

- Was the code written at the event, or before? (older repos, faked commit
  history, big dumps)
- What's really onchain vs stubbed (fake tx hashes, `setTimeout` payments,
  team-key "oracles")
- How deep each sponsor integration really is
- Scores on the ETHGlobal criteria, calibrated against a real human judge
- 2–3 sharp questions to ask the team, tied to `file:line`

Optional **scribe**: use your phone as a mic, transcribe each pitch locally
with whisper, and Claude reads the transcript as evidence.

## Install

```bash
git clone https://github.com/<owner>/ethglobal-judge
# use it in any folder:
ln -s "$PWD/ethglobal-judge/skill" ~/.claude/skills/ethglobal-judge
```
Or just run `claude` inside this repo (it ships the skill in `.claude/skills/`).

Needs: `git`, `gh` (logged in), `cast` (Foundry) and an RPC key
(e.g. Alchemy) in `.env` as `ALCHEMY_API_KEY` or `RPC_URL`.

## Use

Make a folder for the event and start Claude there:
```bash
mkdir my-event && cd my-event && claude
```
Then:
```
judge https://ethglobal.com/showcase/<project>
```
Claude creates `projects/<slug>/report.md` and a `SCOREBOARD.md` line.
Ask follow-ups while the team pitches: "what did they build here?",
"how does the code look?", "why does this need a blockchain?",
"rank everything".

## Scribe (optional)

```bash
brew install ffmpeg whisper-cpp
mkdir -p ~/whisper-models && curl -L -o ~/whisper-models/ggml-small.en.bin \
  https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en.bin
cd my-event && python3 /path/to/ethglobal-judge/scribe/server.py
```
Open the printed `https://<ip>:8844` on your phone (accept the self-signed
cert), pick or add a project, hit record. Transcripts land in
`projects/<slug>/transcript.md`; quick notes in `notes.md`.
Venue wifi often blocks phone↔laptop traffic; put the laptop on your phone's
hotspot if so.

Env: `WHISPER_MODEL` (model path), `SCRIBE_PORT` (default 8844),
`WORKSPACE` (default current folder). Optional auto-detect of new projects
from the judging page needs `BROWSER_BRIDGE` + `JUDGE_URL`.

## Files

```
skill/SKILL.md            workflow
skill/rubric.md           criteria + "built at the event" rule
skill/calibration.md      score levels from a real judging room (anonymized)
skill/lessons.md          how pre-built / faked / stubbed work got caught
skill/report-template.md  report format
skill/scripts/scan.sh     read-only repo scan
skill/scripts/read-form.js  read score inputs off a judging form (browser)
scribe/                   phone mic → local whisper transcripts
```

## Safety

Project code is untrusted. The skill never installs or runs it; it only reads.
It never submits scores or posts anything.

## License

MIT
