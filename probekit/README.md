# probekit: counterfactual probes for loan-officer agents

The validator in `src/` checks a prompt before it goes to a model. probekit checks what an AI agent does with the
prompt: does the agent change what it puts in front of a loan officer (flags, conditions, documents, drafts) for a
reason no rule allows?

A loan officer asks an agent about one synthetic borrower. The arms of a probe are identical except for one changed
factor: a borrower cue (name, age, sex, disability, the destination of a transfer) or the loan officer's own framing.
The correct output is fixed by construction, so bias is the gap between arms in how often the output departs from it.
This is the measure in MortarBench (arXiv 2606.19416, §7.3).

Run every command from the repo root. No API key is needed to try it: the `mock` model makes no call.

```bash
python -m probekit list
```

```bash
python -m probekit show remittance --arm B_guadalajara
```

```bash
python -m probekit run remittance --model mock --n 2
```

```bash
python -m probekit score remittance --model mock
```

The kit itself uses only the standard library. The Gemini backend uses `google-genai` and the `validate` measure uses
`src/`, both already in `requirements.txt`. Optional: `boto3` for the Bedrock Mantle backend, `openpyxl` for the leak
check over private spreadsheets, `scipy` for one test.

## Terms

| Term | Meaning |
|---|---|
| Scenario | One probe: a JSON file in `probekit/scenarios/` |
| Arm | One version of the conversation. Arms differ only in their slots |
| Slot | A named value filled into the messages, e.g. `{cue}`, `{name}`, `{framing}` |
| Baseline | The arm every other arm is compared with |
| Control arm | An arm where the decoy answer is correct. It must differ from the baseline; it shows that the agent reads the cue |
| Gold | The correct output, fixed from a named rule before any run |
| Decoy | An answer that is correct only if the cue mattered. Picking it is a false positive |
| Measure | A true/false test on each run's output, e.g. "any decoy picked" |
| Primary | The measure the probe's conclusion rests on. Primary tests are Holm-corrected |

Three families of changed factor:

| Family | What changes between arms | Failure |
|---|---|---|
| F1 Borrower cue | One cue in the file or in the loan officer's description | The cue adds a flag, condition or document request |
| F2 Steering the agent | The loan officer's framing: neutral, or a premise or push toward a result | The agent adopts the premise: drops a required item, adds a decoy, or accepts a claim no document supports |
| F3 Steering the underwriter through the agent | The loan officer's instructions for text the underwriter reads (condition response, letter of explanation) | The draft leaves out a material fact or makes a claim the file does not support, and the agent gives no warning |

For F2 and F3: a claim backed by a document can change the correct output; an assertion alone cannot.

The 16 scenarios with status `tested` were run on real agents. `f2_p2p_pressure` and `f3_condition_response` are
drafts: not reviewed and not run.

## Choose an agent

```bash
python -m probekit agents
```

Every scenario names a default agent. Use `--agent` with `show`, `run` or `score` to try the same probe on another one:

| Agent id | What it is |
|---|---|
| `loan_structuring`, `undisclosed_liability`, `credit_summary`, `bank_statement_review` | Stand-ins in `probekit/agents/`, written for this kit |
| `bare` | The model with no system prompt |
| `export:<folder>` | Your own ChatGPT custom-GPT export folder (`configs.raw.json`; the newest instructions are used word for word) |

Results on a stand-in say nothing about any real agent. To probe a real agent, export it and pass `export:<folder>`, or
register it in a private config (below).

## Choose a model

| Model | Backend |
|---|---|
| `mock` | No call. Picks menu items at random, so the whole pipeline runs |
| `gemini:<name>` | Google Gemini through `google-genai`, as the validator's semantic tier (`GEMINI_API_KEY`, also read from `.env`) |
| `openai:<name>` | OpenAI Chat Completions (`OPENAI_API_KEY`; `OPENAI_BASE_URL` for a compatible server) |
| `anthropic:<name>` | Anthropic Messages API (`ANTHROPIC_API_KEY`) |
| `mantle:<name>` | Amazon Bedrock Mantle, signed with your AWS credentials (`PROBEKIT_MANTLE_PROJECT`) |

Spend is capped. Every paid call is logged to `probekit/results/spend.jsonl`. A call does not start if its worst case
could pass the budget (default $5; env `PROBEKIT_BUDGET_USD`), or while the file `probekit/results/SPEND_LOCK` exists.
Models without a price in `probekit/backends.py` need `--price IN,OUT` (USD per 1M tokens).

A logged run is never run again: `run` skips any arm and rep that already has a log in `probekit/results/`.

## Score with the validator

A measure can run the repo's own `PromptValidator` on the agent's text (rule and proxy tiers only, so scoring makes no
model call). It is true when the validator flags the text:

```json
{"name": "draft flagged by the fair-lending validator", "validate": "reply[-1]", "context": "mortgage_underwriting"}
```

`f3_condition_response` uses it on the draft the agent writes for the underwriter.

## Add a scenario

1. Copy `probekit/scenarios/_template.json` to `probekit/scenarios/<id>.json`. The fields are explained in
   `probekit/scenarios/README.md`.
2. Keep the file clean against the rule: nothing outside the changed factor may give a reason to flag.
3. Write the gold from a named rule. Add a control arm or a real item that must fire.
4. Read every arm: `python -m probekit show <id> --arm <arm>`.
5. Run it on `mock`, then a pilot of 1 run per arm on a real model. Read the pilot by hand before a full run.
6. A full run is 3 paraphrases × 5 or more runs per arm. `score` reports the gap, the Fisher p, and the smallest gap
   the run can detect.

## Data in this kit

All borrower data is synthetic. Names, loan and account numbers, statements and credit reports are invented. SSNs
and birth dates are masked, phone numbers are in the fictional 555-01xx range, and balances are computed by
`probekit/docs.py`. The loan officers' requests are our own wording of common request types. The agents in
`probekit/agents/` and the excerpts in `probekit/excerpts/` were written for this kit. The excerpts summarize public
rules (Fannie Mae Selling Guide, Regulation B). Check them against the current rules before you rely on them.

Run the leak check before you push:

```bash
python -m probekit check
```

It looks for personal-data patterns, keys and internal ids. With a private config it also looks for blocked terms, for
any run of 6 words copied from the private text you list, and for PII in text copied from your prompt files.

## Private mode

Set `PROBEKIT_PRIVATE` to a folder outside the repo. Its `config.json` can set:

| Key | Use |
|---|---|
| `results_dir`, `ledger`, `spend_lock`, `budget_usd` | Where runs and spend go |
| `default_backend`, `mantle` | Backend for bare model names; Mantle's `env_file`, `project_key`, `region` |
| `agents_dir`, `agents` | Real agent exports. An id equal to a stand-in's replaces it, so scenarios run unchanged |
| `excerpts_dir` | The agents' own knowledge-file excerpts, used in place of `probekit/excerpts/` |
| `corpora`, `blocked_terms` | Private text and terms for the leak check. A copy of 6+ words from `corpora` is a finding |
| `prompt_files` | Real prompt files that everyone who reads your copy already holds. Text copied from them is allowed, but `check` reports a copied run with a first name, a 7+ digit number, or an SSN or phone shape, and `run` refuses to send one |

An `overlays.json` in that folder can replace top-level fields of a scenario, for example the original prompt
wording. Paths are relative to the private folder. This repo is public: keep `prompt_files` text, real agents and
overlays out of it.

## Tests

```bash
python -m pytest tests/test_probekit.py
```
