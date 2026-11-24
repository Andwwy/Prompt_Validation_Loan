# Probes, test by test

Every probe we ran on loan-officer agents, one folder per test. Each folder says what was tested and shows what the
agent saw. The code that runs and scores the tests is in `probekit/` (rounds 1-4) and `probes/scripts/` (rounds 5-9).

Index of the 23 tests: [tests/README.md](tests/README.md).

## Layout

```
probes/
  tests/<test>/
    setting.md         arms, turns, gold, measures, models and runs, how to run it
    profile.md         the borrower the agent sees
    user_prompts.md    the loan officer's messages
    system_prompt.md   the agent's system prompt
  tests/<round>_grossup/   also holds the round's scenario files (.json) and its code book
  scripts/             runner, scorer and builders for rounds 5-9; the card writer
  gold/                gross-up gold cases that the builders read
```

## Labels

Every card starts with one of two labels.

| Label | Meaning |
|---|---|
| SYNTHESIZED | We wrote it. No real person, loan, account, document, prompt or agent text |
| REAL | Taken from the lender's own material. It stays out of this repo; the card says what it is and how to plug in your own copy |

| Part | Label |
|---|---|
| Borrower profiles, documents, statements | SYNTHESIZED, in every test |
| Loan officer's prompts | SYNTHESIZED: our wording of kinds of requests that real loan officers make |
| System prompt in our paid runs | REAL: the lender's own agent settings (custom-GPT exports) |
| System prompt in this repo, rounds 1-4 | SYNTHESIZED: the stand-in agents in `probekit/agents/` |
| System prompt in this repo, rounds 5-9 | None. The role `income_calculator` has no stand-in |
| Gold | Fixed before any run, from named public rules (Fannie Mae Selling Guide, Regulation B) |

Not in this repo: the real agent settings, real loan-officer prompts, run logs, hand codes, result reports, and the
rule table and audits behind the gold cases. Teammates on the data agreement get them through the lab's channel.

## Rounds 1-4

These are the kit scenarios. Each test folder links to its scenario file in `probekit/scenarios/`. Run and score them
with `python -m probekit` ([probekit/README.md](../probekit/README.md)); the commands are in each `setting.md`.

## Run the gross-up rounds (5-9)

One runner serves all five rounds: `probes/scripts/grossup_probe.py --round r5 | r6 | r7 | r8 | r9`.

1. Map the role `income_calculator` to an agent export. In your private config (`probekit/private/config.json`, written
   by `python -m probekit setup --agents <exports folder>`), add the role by hand, because it takes two knowledge files:

   ```json
   {"agents": {"income_calculator": {"export": "<export folder name>*",
                                     "knowledge": ["<knowledge file 1>", "<knowledge file 2>"]}}}
   ```

2. Build the scenario files (already built in `tests/<round>_grossup/`; rebuild after you edit a builder):

   ```bash
   python probes/scripts/build_r9.py
   ```

3. Pilot, plan, full run. Spend goes through the kit's ledger, budget and lock.

   ```bash
   python probes/scripts/grossup_probe.py --round r9 run --model openai:<model> --n 1
   ```

   ```bash
   python probes/scripts/grossup_probe.py --round r9 plan --model openai:<model>
   ```

   ```bash
   python probes/scripts/grossup_probe.py --round r9 run --model openai:<model>
   ```

4. Rounds 5, 7 and 8 need a hand code of turn 1 before they score: `blind` writes the masked items, two coders and a
   settler follow `tests/<round>_grossup/codebook.md`. Round 9 needs none.

5. Score:

   ```bash
   python probes/scripts/grossup_probe.py --round r9 score --model openai:<model>
   ```

A scenario id ends in a hash of everything the agent sees, and logs are kept per id and per agent version. An edit to
any text gives new runs; old runs never mix in.

Rounds 8 and 9 refuse a paid run unless `tests/<round>_grossup/FROZEN_ANALYSIS.sha256` matches the files (paths
relative to `probes/`). After you change a builder, a scenario file or the scorer, write the manifest again before
you run:

```bash
cd probes && shasum -a 256 scripts/grossup_probe.py scripts/build_r9.py scripts/build_r7.py scripts/build_r5.py gold/gross_up_scenarios.csv gold/gold_r9_supplement.csv tests/r9_grossup/r9_gu_*.json > tests/r9_grossup/FROZEN_ANALYSIS.sha256
```

The manifests here cover this repo's copies. The paid runs were frozen under our local paths before each run.

## Score our runs again

With our logs (not in this repo), set two keys in the private config and score. No model call is made.

```json
{"results_dir": "<folder with one subfolder of logs per scenario id>",
 "grossup_work_dir": "<folder with <round>_grossup/ subfolders that hold the plan, blind items and hand codes>"}
```

```bash
python probes/scripts/grossup_probe.py --round r7 score --model openai.gpt-5.6-sol
```

To try another analysis, edit `score_log` (the measures of one run) or the table functions in `grossup_probe.py`.

## Gold

| File | What it is |
|---|---|
| `gold/gross_up_scenarios.csv` | Gold v1: 50 gross-up cases with the maximum qualifying income, tolerance and document lists. Frozen on 2026-11-06 |
| `gold/FROZEN_v1.sha256` | Hashes of the frozen v1 files. `build_r5.py` checks the cases file against it. The other files it lists (rule table, builders, audits) are not in this repo |
| `gold/gold_r9_supplement.csv` | 4 cases for round 9, built from the same frozen rules |

## Write the cards again

After a scenario changes, run this without a private config, so that the cards hold the public wording only:

```bash
python probes/scripts/make_cards.py
```

Then run the leak check, which also covers this folder:

```bash
python -m probekit check
```
