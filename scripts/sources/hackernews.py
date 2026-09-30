"""Hacker News official Firebase API source."""
import json, time, urllib.request
try:
    import requests
except ImportError:
    requests = None

API="https://hacker-news.firebaseio.com/v0"
def fetch_hackernews(limit=30, timeout=15):
    try:
        if requests: ids=requests.get(f"{API}/topstories.json",timeout=timeout).json()[:limit]
        else: ids=json.load(urllib.request.urlopen(f"{API}/topstories.json",timeout=timeout))[:limit]
    except Exception as exc:
        print(f"[hackernews] top stories: {exc}"); return []
    items=[]
    for item_id in ids:
        try:
            if requests: item=requests.get(f"{API}/item/{item_id}.json",timeout=timeout).json()
            else: item=json.load(urllib.request.urlopen(f"{API}/item/{item_id}.json",timeout=timeout))
            if item and item.get("type")=="story" and item.get("title") and item.get("url"):
                items.append({"type":"article","title":item["title"],"url":item["url"],"source":"Hacker News","published_at":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(item.get("time",time.time()))),"description":f"{item.get('score',0)} points · {item.get('descendants',0)} comments on Hacker News."})
        except Exception as exc: print(f"[hackernews] {item_id}: {exc}")
    return items
