#!/usr/bin/env python3
"""Fetch contribution calendar + featured repo info into data/*.json (run daily by the Action)."""
import datetime, json, os, subprocess, urllib.request

USER = os.environ.get("GH_USER", "gravityyyy99")
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
FEATURED = ["youtube-watch-party", "filmox", "thestoryteller-website", "the-nose-tral-network", "onconeuro-ai"]


def token():
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    return t or subprocess.check_output(["gh", "auth", "token"], text=True).strip()


def api(url, data=None):
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None,
                                 headers={"Authorization": f"Bearer {token()}", "User-Agent": "profile-cards"})
    return json.load(urllib.request.urlopen(req))


def contributions():
    q = """query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{totalContributions
    weeks{contributionDays{date contributionCount}}}}}}"""
    cal = api("https://api.github.com/graphql", {"query": q, "variables": {"u": USER}})
    cal = cal["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    days = [{"date": d["date"], "count": d["contributionCount"]} for d in days]
    today = datetime.date.today().isoformat()
    days = [d for d in days if d["date"] <= today]
    monthly = {}
    for d in days:
        monthly[d["date"][:7]] = monthly.get(d["date"][:7], 0) + d["count"]
    run, best, cur, curs, bests = 0, 0, 0, None, None
    start = None
    for d in days:
        if d["count"]:
            run += 1
            start = start or d["date"]
            if run >= best:
                best, bests = run, start
        else:
            run, start = 0, None
    cur = 0
    for d in reversed(days):
        if d["count"]:
            cur += 1
        elif d["date"] != today:
            break
    bd = max(days, key=lambda d: d["count"])
    return {
        "username": USER, "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "total": cal["totalContributions"], "active_days": sum(1 for d in days if d["count"]),
        "current_streak": cur, "longest_streak": best, "best_day": bd,
        "monthly": [{"month": k, "total": v} for k, v in sorted(monthly.items())][-12:], "days": days,
    }


def repos():
    out = []
    for n in FEATURED:
        r = api(f"https://api.github.com/repos/{USER}/{n}")
        out.append({"name": r["name"], "description": r["description"] or "", "language": r["language"] or "",
                    "stars": r["stargazers_count"], "url": r["html_url"]})
    return out


if __name__ == "__main__":
    json.dump(contributions(), open(os.path.join(ROOT, "data", "contributions.json"), "w"), indent=1)
    json.dump(repos(), open(os.path.join(ROOT, "data", "repos.json"), "w"), indent=1)
    print("ok")
