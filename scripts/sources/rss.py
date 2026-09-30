"""RSS sources. Keep this module independent so one broken feed cannot stop updates."""
import calendar, email.utils, time
import urllib.request
import xml.etree.ElementTree as ET
try:
    import feedparser
except ImportError:
    feedparser = None

RSS_SOURCES = {
    "Hacker News (RSS)": "https://news.ycombinator.com/rss",
    "Zenn": "https://zenn.dev/feed",
    "GitHub Blog": "https://github.blog/feed/",
    "Cloudflare Blog": "https://blog.cloudflare.com/rss/",
    "AWS Blog": "https://aws.amazon.com/blogs/aws/feed/",
    "MDN": "https://developer.mozilla.org/en-US/blog/rss.xml",
}

def _date(entry):
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed: return time.strftime("%Y-%m-%dT%H:%M:%SZ", parsed)
    raw = entry.get("published") or entry.get("updated")
    if raw:
        try: return email.utils.formatdate(calendar.timegm(email.utils.parsedate(raw)), usegmt=True)
        except (TypeError, ValueError): pass
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def fetch_rss(timeout=20):
    items=[]
    for source,url in RSS_SOURCES.items():
        try:
            if feedparser:
                entries=feedparser.parse(url, request_headers={"User-Agent":"TechCatchup/1.0"}).entries[:20]
                for entry in entries:
                    link=entry.get("link") or (entry.get("links") or [{}])[0].get("href")
                    if link and entry.get("title"):
                        items.append({"type":"article","title":entry.title.strip(),"url":link,"source":source,"published_at":_date(entry),"description":entry.get("summary","")})
            else:
                request=urllib.request.Request(url,headers={"User-Agent":"TechCatchup/1.0"})
                root=ET.fromstring(urllib.request.urlopen(request,timeout=timeout).read())
                for node in root.findall(".//item")[:20]:
                    title=(node.findtext("title") or "").strip(); link=(node.findtext("link") or "").strip()
                    if title and link: items.append({"type":"article","title":title,"url":link,"source":source,"published_at":node.findtext("pubDate") or time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"description":node.findtext("description") or ""})
        except Exception as exc:
            print(f"[rss] {source}: {exc}")
    return items
