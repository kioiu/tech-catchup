"""Build data/news.json. RSS/HN always run even when optional X fails."""
import hashlib, json, re, sys, time
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from sources.rss import fetch_rss
from sources.hackernews import fetch_hackernews
from sources.x import fetch_x

# Edit these lists to tune the beginner audience without changing the pipeline.
BEGINNER_KEYWORDS={"github":4,"git":3,"docker":3,"python":3,"javascript":3,"typescript":3,"react":2,"html":2,"css":2,"sql":3,"database":3,"api":3,"http":2,"linux":2,"aws":2,"cloudflare":2,"security":2,"vscode":2,"beginner":5,"tutorial":4,"guide":3,"how to":3,"ai coding":3,"copilot":2}
CATEGORIES={"AI":["ai","llm","copilot","agent","machine learning"],"Cloud":["aws","cloud","cloudflare","kubernetes","serverless"],"Security":["security","vulnerability","cve","privacy","auth"],"Web":["html","css","javascript","typescript","react","web","http","browser"],"Tools":["vscode","docker","github actions","gitlab","terminal","cli","tool"],"Development":["python","java","rust","go","api","database","sql","linux","git"]}
def score(item):
    text=f"{item['title']} {item.get('description','')}".lower(); return min(10,sum(weight for word,weight in BEGINNER_KEYWORDS.items() if word in text))
def category(item):
    text=f"{item['title']} {item.get('description','')}".lower()
    for name,words in CATEGORIES.items():
        if any(word in text for word in words): return name
    return "Beginner" if score(item)>=6 else "Other"
def normalize(items):
    now=datetime.now(timezone.utc); output=[]; seen=set()
    for item in items:
        url=item.get("url","").split("#")[0].rstrip("/"); title=re.sub(r"\s+"," ",item.get("title","")).strip()
        key=hashlib.sha1((url.lower() or title.lower()).encode()).hexdigest()
        if not title or key in seen: continue
        seen.add(key); item.update({"url":url,"title":title,"category":category(item),"beginner_score":score(item)})
        try: age=max(0,(now-datetime.fromisoformat(item["published_at"].replace("Z","+00:00"))).total_seconds()/3600)
        except Exception: age=72
        item["description"]=re.sub(r"<[^>]+>"," ",item.get("description","")).strip()[:240]; item["rank_score"]=item["beginner_score"]*10+max(0,24-age)/3
        output.append(item)
    return sorted(output,key=lambda x:x["rank_score"],reverse=True)[:80]
def main():
    all_items=[]
    for name,fn in (("rss",fetch_rss),("hackernews",fetch_hackernews),("x",fetch_x)):
        try: all_items.extend(fn())
        except Exception as exc: print(f"[{name}] isolated failure: {exc}")
    output=normalize(all_items); target=Path(__file__).parents[1]/"data/news.json"; target.parent.mkdir(exist_ok=True)
    if not output:
        print("No stories fetched; keeping existing data/news.json.")
        return
    target.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(f"Wrote {len(output)} stories to {target}")
if __name__=="__main__": main()
