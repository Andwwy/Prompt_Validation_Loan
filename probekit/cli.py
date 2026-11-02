"""
  python -m probekit list                                   scenarios
  python -m probekit agents                                 agent settings you can pick
  python -m probekit show SCENARIO [--agent ID] [--arm ARM] [--rep K] [--full]
                                                            what the agent would see (no model call)
  python -m probekit run SCENARIO --model MODEL [--agent ID] [--n 5] [--arms A B] [--workers 4]
                                  [--temperature 1] [--price IN,OUT]
  python -m probekit score [SCENARIO ...] [--agent ID] [--model MODEL] [--out FILE]
  python -m probekit prompts [WORD ...] [--id ID]            search your private prompt files (chat history)
  python -m probekit check                                  leak check before sharing

MODEL is mock (no call), gemini:<name>, openai:<name>, anthropic:<name>, mantle:<name>, or a bare name for the
configured default.
"""

import argparse
import json
import sys

from . import agents, check, config, prompts, run, scenarios, score


def cmd_list(a):
    print(f"{'scenario':22} {'family':6} {'status':8} {'agent':22} arms  title")
    for sid in scenarios.ids():
        sc = scenarios.load(sid)
        print(f"{sid:22} {sc.get('family', ''):6} {sc.get('status', ''):8} {sc['agent']:22} {len(sc['arms']):4}  "
              f"{sc.get('title', '')}")


def cmd_agents(a):
    for aid, source, name in agents.available():
        print(f"{aid:48} {source:18} {name}")


def cmd_show(a):
    sc = scenarios.load(a.scenario)
    agent = agents.resolve(a.agent or sc["agent"])
    arm = a.arm or scenarios.baseline(sc)
    system = scenarios.system_prompt(sc, agent)
    msgs, order = scenarios.messages(sc, arm, a.rep)
    print(f"# {sc['id']}: {sc.get('title', '')}\nfamily {sc.get('family', '')}, status {sc.get('status', '')}")
    print(f"agent {agent.id} ({agent.source}, {agent.name}, sha {agent.sha}); arm {arm}, rep {a.rep}")
    print("arms (baseline first; only these slots differ):")
    for name, cue in sorted(sc["arms"].items(), key=lambda x: x[0] != scenarios.baseline(sc)):
        tag = " [control]" if name in sc.get("controls", []) else ""
        print(f"  {name}{tag}: {json.dumps(cue, ensure_ascii=False)}")
    print(f"gold: {sc['gold']}\n\n## System prompt ({len(system)} chars)\n")
    print(system if a.full or len(system) <= 1500 else system[:1500] + f"\n... [{len(system) - 1500} more chars; --full]")
    for i, m in enumerate(msgs, 1):
        print(f"\n## Loan officer, turn {i}\n\n{m}")


def cmd_prompts(a):
    """Prompts from the private prompt files, with a PII note, to pick one for a scenario ({"prompt": "<id>"})."""
    if not config.load()["prompt_files"]:
        sys.exit("No prompt files: put them in probekit/private/ and register them in its config.json (README).")
    hits = [(a.id, prompts.text(a.id))] if a.id else list(prompts.search(a.words))
    for pid, t in hits[:a.limit]:
        pii = check.pii(check.words(t))
        print(f"{pid:9} {'[possible PII: ' + ', '.join(pii) + '] ' if pii else ''}{t if a.id else ' '.join(t.split())[:160]}")
    print(f"({len(hits)} prompts)", file=sys.stderr)


def cmd_run(a):
    price = tuple(float(x) for x in a.price.split(",")) if a.price else None
    run.run(a.scenario, a.model, a.agent, a.n, a.arms, a.temperature, a.workers, price)


def cmd_score(a):
    md = score.report(a.scenarios or scenarios.ids(), a.agent, a.model, a.temperature)
    if a.out:
        open(a.out, "w").write(md)
    print(md)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="probekit", description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(f=cmd_list)
    sub.add_parser("agents").set_defaults(f=cmd_agents)
    s = sub.add_parser("show")
    s.add_argument("scenario", choices=scenarios.ids())
    s.add_argument("--agent")
    s.add_argument("--arm")
    s.add_argument("--rep", type=int, default=0)
    s.add_argument("--full", action="store_true")
    s.set_defaults(f=cmd_show)
    r = sub.add_parser("run")
    r.add_argument("scenario", choices=scenarios.ids())
    r.add_argument("--model", required=True)
    r.add_argument("--agent")
    r.add_argument("--n", type=int, default=1)
    r.add_argument("--arms", nargs="+")
    r.add_argument("--temperature", type=float, default=1.0)
    r.add_argument("--workers", type=int, default=1)
    r.add_argument("--price", help="USD per 1M tokens, input,output (needed for models without a known price)")
    r.set_defaults(f=cmd_run)
    c = sub.add_parser("score")
    c.add_argument("scenarios", nargs="*")
    c.add_argument("--agent")
    c.add_argument("--model")
    c.add_argument("--temperature", type=float, default=1.0)
    c.add_argument("--out")
    c.set_defaults(f=cmd_score)
    p = sub.add_parser("prompts")
    p.add_argument("words", nargs="*")
    p.add_argument("--id", help="one prompt in full, e.g. 'NV 559'")
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(f=cmd_prompts)
    sub.add_parser("check").set_defaults(f=lambda a: sys.exit(check.main()))
    a = ap.parse_args(argv)
    a.f(a)
    if config.load()["private"] and a.cmd in ("show", "run"):
        print(f"\n(private config: {config.load()['private']})", file=sys.stderr)
