"""Optional X source. Failure is intentionally isolated from the main pipeline."""
import os, time
try:
    import requests
except ImportError:
    requests = None

def fetch_x(timeout=15):
    token=os.getenv("X_BEARER_TOKEN")
    query=os.getenv("X_QUERY", "(github OR cloudflare OR aws OR vscode OR docker OR react OR python) -is:retweet lang:en")
    if not token or not requests:
        print("[x] X_BEARER_TOKEN is not set; skipping X."); return []
    try:
        response=requests.get("https://api.x.com/2/tweets/search/recent",headers={"Authorization":f"Bearer {token}"},params={"query":query,"max_results":20,"tweet.fields":"created_at,author_id,entities","expansions":"author_id","user.fields":"username,name"},timeout=timeout)
        response.raise_for_status(); payload=response.json(); users={u["id"]:u for u in payload.get("includes",{}).get("users",[])}; items=[]
        for tweet in payload.get("data",[]):
            user=users.get(tweet.get("author_id"),{}); username=user.get("username","unknown")
            items.append({"type":"social","title":tweet.get("text","").replace("\n"," ")[:120],"url":f"https://x.com/{username}/status/{tweet['id']}","source":f"X · @{username}","published_at":tweet.get("created_at",time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())),"description":tweet.get("text","")})
        return items
    except Exception as exc:
        print(f"[x] optional source failed: {exc}"); return []
