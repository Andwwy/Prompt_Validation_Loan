# Probes, test by test

Every probe we ran on loan-officer agents: 23 tests, one folder each. Start at the index,
[tests/README.md](tests/README.md).

```
probes/
  tests/<test>/    setting.md, profile.md, user_prompts.md, system_prompt.md
                   gross-up rounds also hold their scenario files (.json) and code book
  scripts/         runner, scorer and builders for rounds 5-9; make_cards.py writes the cards
  gold/            gross-up gold cases that the builders read (v1, frozen 2026-11-06)
```

## Labels

Every card starts with one of two labels.

| Part | Label |
|---|---|
| Borrower profiles, documents | SYNTHESIZED: we wrote them; no real person or loan |
| Loan officer's prompts | SYNTHESIZED: our wording of requests that real loan officers make |
| System prompt, our paid runs | REAL: the lender's own agent settings; not in this repo |
| System prompt, in this repo | SYNTHESIZED stand-ins for rounds 1-4 (`probekit/agents/`); none for rounds 5-9 |

Also not in this repo: real prompts, run logs, hand codes, result reports. Lab members on the data agreement get
them through the lab's channel.

## Rounds 1-4

Kit scenarios. They run on the stand-in agents with no data and no key:

```bash
python -m probekit run r3_ssdi --model mock --n 2
```

```bash
python -m probekit score r3_ssdi --model mock
```

Real agents and models: [probekit/README.md](../probekit/README.md).

## Rounds 5-9 (gross-up)

These need a real agent export: the role `income_calculator` has no stand-in.

**Where the export files go.** Keep them outside the repo, in any folder, one subfolder per agent as exported:

```
<exports folder>/
  <agent name>__g-.../
    configs.raw.json     the agent's instructions
    files/               its knowledge files
```

Then tell the kit where they are. This writes `probekit/private/config.json`, which git ignores.

```bash
python -m probekit setup --agents <exports folder>
```

```bash
python -m probekit agents
```

```bash
python -m probekit setup --map income_calculator=export/<name> --knowledge income_calculator=<file 1> income_calculator=<file 2>
```

The second command lists your agents as `export/<name>`; use the income calculator's. `<file 1>` and `<file 2>` are
file names in its `files/` folder. They are appended to the instructions in the order given.

Then run a round (`--round r5` to `r9`; `--help` lists the commands). `--model mock` makes no call:

```bash
python probes/scripts/grossup_probe.py --round r9 run --model <model> --n 1
```

```bash
python probes/scripts/grossup_probe.py --round r9 score --model <model>
```

- `--n 1` is a pilot. `plan` then picks n from the pilot's cost and the budget; `run` without `--n` uses it.
- Rounds 5, 7 and 8 need a hand code of turn 1 before `score`: `blind` writes the masked items; the procedure is
  in the round's `codebook.md`.
- To score stored logs, set `results_dir` (and `grossup_work_dir` for plans and hand codes) in the private config.
  `score` makes no model call.

## Change a test or the analysis

- **Analysis:** edit `score_log` (the measures of one run) or the table functions in `scripts/grossup_probe.py`.
- **Test:** edit `scripts/build_<round>.py` and run it. A scenario id ends in a hash of everything the agent
  sees, so an edited text gets a new id and its runs never mix with old ones.
- **Rounds 8 and 9** refuse a paid run unless `tests/<round>_grossup/FROZEN_ANALYSIS.sha256` matches the files.
  After an edit, write it again (round 8: `build_r8.py`, its `codebook.md`, and no supplement):

  ```bash
  cd probes && shasum -a 256 scripts/grossup_probe.py scripts/build_r9.py scripts/build_r7.py scripts/build_r5.py gold/gross_up_scenarios.csv gold/gold_r9_supplement.csv tests/r9_grossup/r9_gu_*.json > tests/r9_grossup/FROZEN_ANALYSIS.sha256
  ```

- **Before a push:** write the cards again without a private config, then run the leak check.

  ```bash
  python probes/scripts/make_cards.py && python -m probekit check
  ```
