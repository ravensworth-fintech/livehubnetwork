#!/usr/bin/env python3
"""Build a public discovery index for authorized/free live-TV sources.
Community posts and repositories are indexed as leads only, never as playable feeds.
Direct playlist entries are admitted only when their host is explicitly allowlisted.
"""
import json, os, re, time, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

OUT=Path("data/discovery.json")
UA="LIVEHUB-Discovery/1.0 (personal free-TV source index)"
TIMEOUT=20
# Explicit allowlist: official/public provider domains only. Extend after verifying rights.
ALLOWED_HOSTS={x.strip().lower() for x in os.getenv("LIVEHUB_ALLOWED_HOSTS", "").split(",") if x.strip()}
REDDIT_QUERIES=["free official live tv", "official free live sports stream", "public live television stream", "free legal live channels"]
NEWS_QUERIES=["official free live sports streaming", "free live television channels official", "broadcaster free live stream"]
GITHUB_QUERIES=["official free live tv streams", "public domain live stream", "free ad supported live tv official"]

def get(url, headers=None):
    req=urllib.request.Request(url,headers={"User-Agent":UA,**(headers or {})})
    with urllib.request.urlopen(req,timeout=TIMEOUT) as r:return r.read()

def host_allowed(url):
    try: host=urllib.parse.urlparse(url).hostname.lower()
    except Exception:return False
    return any(host==d or host.endswith("."+d) for d in ALLOWED_HOSTS)

def reddit_items():
    out=[]; checked=0
    for q in REDDIT_QUERIES:
        url="https://www.reddit.com/search.rss?"+urllib.parse.urlencode({"q":q,"sort":"new","t":"month","limit":25})
        try:
            root=ET.fromstring(get(url,{"Accept":"application/rss+xml, application/xml"})); checked+=1
            ns={"a":"http://www.w3.org/2005/Atom"}
            for e in root.findall("a:entry",ns):
                title=e.findtext("a:title",default="",namespaces=ns)
                link=e.find("a:link",ns)
                href=link.attrib.get("href","") if link is not None else ""
                summary=re.sub("<[^>]+>"," ",e.findtext("a:content",default="",namespaces=ns))
                if href and "reddit.com" in urllib.parse.urlparse(href).netloc:
                    out.append({"id":"reddit:"+href,"title":title[:180],"description":re.sub(r"\s+"," ",summary)[:420],"url":href,"source":"Reddit","kind":"Community discussion","category":"Community lead","status":"Review listing; not a verified stream","playback":"External listing"})
        except Exception as e: print("reddit search failed",q,str(e)[:160])
        time.sleep(1)
    return out,checked

def news_items():
    out=[]; checked=0
    for q in NEWS_QUERIES:
        url="https://news.google.com/rss/search?"+urllib.parse.urlencode({"q":q,"hl":"en-US","gl":"US","ceid":"US:en"})
        try:
            root=ET.fromstring(get(url,{"Accept":"application/rss+xml, application/xml"})); checked+=1
            for item in root.findall("./channel/item"):
                title=item.findtext("title",default=""); href=item.findtext("link",default="")
                desc=re.sub("<[^>]+>"," ",item.findtext("description",default=""))
                if href:
                    out.append({"id":"news:"+href,"title":title[:180],"description":re.sub(r"\s+"," ",desc)[:420],"url":href,"source":"Google News","kind":"News/search result","category":"Web discovery","status":"Article lead; verify original broadcaster source","playback":"External listing"})
        except Exception as e: print("news search failed",q,str(e)[:160])
        time.sleep(1)
    return out,checked

def github_items():
    out=[]; checked=0
    for q in GITHUB_QUERIES:
        url="https://api.github.com/search/repositories?"+urllib.parse.urlencode({"q":q,"sort":"updated","per_page":15})
        try:
            data=json.loads(get(url,{"Accept":"application/vnd.github+json"})); checked+=1
            for r in data.get("items",[]):
                html=r.get("html_url","")
                if not html:continue
                out.append({"id":"github:"+str(r.get("id")),"title":r.get("full_name","Public repository"),"description":(r.get("description") or "Public repository; inspect its license and source provenance before use")[:420],"url":html,"source":"GitHub","kind":"Repository","category":"Open-source project","status":"Repository lead; stream rights not verified","playback":"External listing"})
        except Exception as e: print("github search failed",q,str(e)[:160])
        time.sleep(1)
    return out,checked

def playlist_items():
    # Public catalogue is treated as untrusted input. Only explicitly approved hosts pass.
    if not ALLOWED_HOSTS:return [],0
    out=[]; checked=0
    try:
        raw=get("https://iptv-org.github.io/iptv/index.m3u").decode("utf-8","replace"); checked=1
        name="Unknown channel"; group="Live TV"
        for line in raw.splitlines():
            line=line.strip()
            if line.startswith("#EXTINF:"):
                m=re.search(r",([^,]+)$",line); name=m.group(1).strip() if m else "Unknown channel"
                g=re.search(r'group-title="([^"]+)"',line); group=g.group(1) if g else "Live TV"
            elif line.startswith("http") and host_allowed(line):
                out.append({"id":"allowlisted:"+line,"title":name[:160],"description":"Playlist entry hosted on a domain you explicitly allowlisted. Confirm the broadcaster's redistribution permission before playback.","url":line,"source":"Approved-domain playlist filter","kind":"Candidate stream","category":group[:80],"status":"Host allowlisted; rights still require confirmation","playback":"Direct stream candidate"})
    except Exception as e: print("playlist fetch failed",str(e)[:160])
    return out,checked

def main():
    items=[]; sources=0
    for fn in (reddit_items,news_items,github_items,playlist_items):
        found,n=fn(); items.extend(found); sources+=n
    # Deduplicate by URL and keep the most recent/first indexed record.
    dedup={}
    for x in items: dedup.setdefault(x["url"],x)
    result={"generated_at":datetime.now(timezone.utc).isoformat(),"sources_checked":sources,"items":list(dedup.values())[:1500],"notice":"Community and repository records are discovery leads, not endorsements or verified streams. Direct stream candidates require explicit host allowlisting and independent rights confirmation."}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(f"Wrote {len(result['items'])} discovery records from {sources} successful source checks")
if __name__=="__main__":main()
