# Lessons

What actually caught problems in a real judging room.

## Pre-built code
- **Look for older repos by the same people.** `gh api users/<login>/repos`
  and the org's repos. Compare file hashes: identical files in a repo created
  weeks earlier = the code is old, whatever the commit dates say.
- **Commit timing.** `git log --format='%ad' --date=iso`. Dozens of commits
  seconds apart = one dump split into fake commits by a script.
- **Big first commit.** A finished app (thousands of lines) in commit 1 or 2.
  Check `git log --stat --reverse | head`.
- **Dates inside the files.** Docs, changelogs, `package.json` versions,
  lockfiles or comments dated before the event.
- **Commits before the event start.** On existing-project tracks that's
  allowed only if disclosed. Find the commit where the event work starts and
  score from there (`git diff <start>..HEAD --stat`).
- **Exports from a private monorepo.** Paths, package names or imports that
  point to a bigger codebase that isn't in the repo.
- **Read the showcase "AI usage" and description.** Teams often say there
  what they reused. Honest disclosure is a plus.

## Fake or stubbed
- Web demo "payments" using `setTimeout` and random tx IDs, while only a CLI
  does real txs.
- The last commit swapping a real DB/API for a mock before the deadline.
- "Oracle" / "attestation" / "bridge" = a team EOA signing whatever it wants.
- "Workflow" code (oracle networks, automation) that was only simulated
  locally, never deployed.
- An "agent" that is an LLM prompt with no onchain action.
- "Liquidate", "bridge", "verify" in the pitch with no matching code. Search
  for it; say so if it's missing.

## Hidden trust
- One EOA is owner + relayer + arbiter + attester.
- Admin functions that move user funds (`simulateLoss`, `emergencyWithdraw`,
  `setPrice`). Link the exact line on GitHub; judges like a clickable link.
- Records anyone can write (shared stores with no writer filter): anyone can
  poison them.
- Verifiers that trust a user-declared value instead of checking it.
- Server holds all user keys.

## Onchain
- Deployed but 0 txs = deploy only.
- Same tx paid 3 times = one demo, replayed.
- Verified source on the explorer is a good sign. Unverified, ask why.

## Working with the judge
- They're listening to a pitch. One-line answers. Result first.
- "What did they build here?" = what's new at the event versus what existed.
- Read the live transcript. If the pitch claims something the code doesn't
  do, give the judge a question that exposes it.
- Wifi at events is bad: save the report early, use `gh api` instead of a
  full clone, retry network calls 2–3 times then move on.
- Write every score the judge gives you into the report right away, so it
  can be re-typed if the form fails to save.
