#!/usr/bin/env python3
"""LIVEHUB public-web link discovery.

Searches public RSS/search feeds, extracts links from public pages, and crawls
only domains explicitly allowlisted by the operator. It indexes links for the
LIVEHUB UI. It does not bypass logins, DRM, paywalls, bot controls, or access
restrictions. A matching media URL is only a technical candidate; operators
must confirm they have permission to display it.
"""
from __future__ import annotations
import html, json, os, re, time, urllib.parse, urllib.request, urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

OUT = Path('data/discovery.json')
UA = 'LIVEHUB-LinkDiscovery/2.0 (+public-link-index; contact site operator)'
TIMEOUT = 15
MAX_PAGE_BYTES = 1_500_000
MAX_CRAWL_PAGES = int(os.getenv('LIVEHUB_MAX_CRAWL_PAGES', '60'))
ALLOWED_HOSTS = {x.strip().lower() for x in os.getenv('LIVEHUB_ALLOWED_HOSTS', '').split(',') if x.strip()}
# Public discovery sources. These produce leads, not assumed-authorized streams.
SEARCH_TERMS = [
    'official NFL live game watch broadcaster',
    'official college football live game watch broadcaster',
    'free official live sports stream broadcaster',
    'official free live television sports stream',
]
REDDIT_TERMS = [
    'official NFL game live stream', 'official college football live stream',
    'where to watch NFL game official', 'where to watch college football official',
]
MEDIA_EXTS = ('.m3u8', '.mp4', '.mpd')
SKIP_HOSTS = {'localhost'}


def safe_http_url(url: str) -> bool:
    try:
        p = urllib.parse.urlsplit(url)
        host = (p.hostname or '').lower()
        return p.scheme in ('http', 'https') and bool(host) and host not in SKIP_HOSTS and not host.endswith('.local')
    except Exception:
        return False


def allowed(url: str) -> bool:
    if not safe_http_url(url): return False
    host = (urllib.parse.urlsplit(url).hostname or '').lower()
    return any(host == d or host.endswith('.' + d) for d in ALLOWED_HOSTS)


def fetch(url: str, max_bytes: int = MAX_PAGE_BYTES):
    if not safe_http_url(url): raise ValueError('Unsafe URL')
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml,application/rss+xml,application/xml,*/*;q=0.7'})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        final = r.geturl()
        if not safe_http_url(final): raise ValueError('Unsafe redirect target')
        data = r.read(max_bytes + 1)
        return data[:max_bytes], r.headers.get_content_type(), final


def clean_text(s: str) -> str:
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]*>', ' ', s or ''))).strip()


def host_of(url):
    return (urllib.parse.urlsplit(url).hostname or '').lower()


def classify(url: str):
    p = urllib.parse.urlsplit(url); host = host_of(url); path = p.path.lower()
    if not allowed(url): return None
    if path.endswith('.m3u8'): return 'hls'
    if path.endswith('.mp4'): return 'mp4'
    if host in {'youtube.com','www.youtube.com','m.youtube.com','youtu.be','www.youtube-nocookie.com'}:
        return 'youtube'
    if '/embed/' in path or '/player/' in path: return 'embed'
    return None


class PageLinks(HTMLParser):
    def __init__(self, base):
        super().__init__(convert_charrefs=True); self.base=base; self.links=[]; self.title=[]; self.in_title=False
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag.lower()=='title': self.in_title=True
        for key in ('href','src','data-src','content'):
            val=a.get(key)
            if val and (key!='content' or a.get('property') in ('og:video','og:video:url','og:video:secure_url') or a.get('name') in ('twitter:player:stream','og:video')):
                u=urllib.parse.urljoin(self.base, html.unescape(val.strip()))
                if safe_http_url(u): self.links.append(u)
    def handle_endtag(self, tag):
        if tag.lower()=='title': self.in_title=False
    def handle_data(self, data):
        if self.in_title: self.title.append(data)


def extract_text_urls(text, base):
    out=[]
    for raw in re.findall(r'''(?:https?:)?//[^\s<>"'\\]+''', text or '', re.I):
        u=urllib.parse.urljoin(base, raw.rstrip(').,;]'))
        if safe_http_url(u): out.append(u)
    return out


def add_record(records, seen, *, title, description, url, source, category, playback=None, kind=None):
    if not safe_http_url(url): return
    key=url.split('#',1)[0]
    if key in seen: return
    seen.add(key)
    is_playable=bool(playback)
    records.append({
        'id': ('media:' if is_playable else 'lead:') + str(abs(hash(key))),
        'title': (title or host_of(url))[:180], 'description': (description or '')[:500],
        'url': url, 'source': source, 'kind': kind or ('Media candidate' if is_playable else 'Public web lead'),
        'category': category, 'status': ('Supported media format on an allowlisted domain; rights and actual playback still need confirmation' if is_playable else 'Public page/link lead; not represented as a playable stream'),
        'playback': playback or 'Listing only', 'playable': is_playable
    })


def parse_feed(url, records, seen, label):
    try:
        raw, _, final=fetch(url, 900_000); root=ET.fromstring(raw); count=0
        # RSS
        for item in root.findall('.//item'):
            title=item.findtext('title') or label; link=item.findtext('link') or ''; desc=clean_text(item.findtext('description') or '')
            if link and safe_http_url(link):
                add_record(records,seen,title=title,description=desc,url=link,source=label,category='Sports discovery')
                count+=1
                # Extract outbound links from public descriptions, but only index/crawl allowlisted destinations.
                for u in extract_text_urls(item.findtext('description') or '', link):
                    if allowed(u): add_record(records,seen,title=title,description='Outbound link discovered in a public listing.',url=u,source=label,category='Provider link',playback=classify(u))
        # Atom
        ns={'a':'http://www.w3.org/2005/Atom'}
        for entry in root.findall('a:entry',ns):
            title=entry.findtext('a:title',default=label,namespaces=ns); content=entry.findtext('a:content',default='',namespaces=ns)
            link_el=entry.find('a:link',ns); link=link_el.attrib.get('href','') if link_el is not None else ''
            if link and safe_http_url(link):
                add_record(records,seen,title=title,description=clean_text(content),url=link,source=label,category='Community lead')
                count+=1
            for u in extract_text_urls(content,link or final):
                if allowed(u): add_record(records,seen,title=title,description='Outbound link extracted from a public post.',url=u,source=label,category='Provider link',playback=classify(u))
        return count
    except Exception as e:
        print(f'Feed error ({label}): {str(e)[:180]}'); return 0


def crawl_allowed_pages(records, seen):
    # Seed queue only with allowlisted links already found. No arbitrary host crawling.
    queue=[]
    for rec in list(records):
        if allowed(rec['url']) and not rec['playable']:
            queue.append((rec['url'],rec['title'],rec['source']))
    crawled=set(); pages=0
    while queue and pages < MAX_CRAWL_PAGES:
        url,title,source=queue.pop(0); normalized=url.split('#',1)[0]
        if normalized in crawled or not allowed(url): continue
        crawled.add(normalized)
        try:
            raw,ctype,final=fetch(url); pages+=1
            if not allowed(final): continue
            if 'html' not in ctype and 'xml' not in ctype: continue
            text=raw.decode('utf-8','replace'); parser=PageLinks(final); parser.feed(text)
            page_title=' '.join(parser.title).strip() or title
            links=list(dict.fromkeys(parser.links + extract_text_urls(text,final)))
            # Record media and supported embeds only; keep ordinary provider links as leads.
            for u in links:
                if not allowed(u): continue
                typ=classify(u)
                if typ:
                    add_record(records,seen,title=page_title,description='Media/embed URL extracted from an allowlisted public provider page.',url=u,source=host_of(final),category='Provider media',playback=typ)
                elif host_of(u)==host_of(final) and len(queue)<MAX_CRAWL_PAGES*8:
                    path=urllib.parse.urlsplit(u).path.lower()
                    if path.endswith(('.html','.htm','/')): queue.append((u,page_title,host_of(final)))
        except Exception as e: print(f'Page crawl error ({url}): {str(e)[:140]}')
    return pages


def main():
    records=[]; seen=set(); checked=0
    for q in SEARCH_TERMS:
        url='https://news.google.com/rss/search?'+urllib.parse.urlencode({'q':q,'hl':'en-US','gl':'US','ceid':'US:en'})
        checked += parse_feed(url,records,seen,'Google News')
        time.sleep(.5)
    for q in REDDIT_TERMS:
        url='https://www.reddit.com/search.rss?'+urllib.parse.urlencode({'q':q,'sort':'new','t':'month','limit':25})
        checked += parse_feed(url,records,seen,'Reddit public posts')
        time.sleep(.5)
    crawled=crawl_allowed_pages(records,seen) if ALLOWED_HOSTS else 0
    result={'generated_at':datetime.now(timezone.utc).isoformat(),'sources_checked':checked,'pages_crawled':crawled,
            'items':records[:1500],
            'notice':'Public web leads are not necessarily playable. Media candidates are limited to operator-allowlisted domains and supported formats. Confirm distribution rights and provider embedding permission. This crawler does not bypass logins, DRM, paywalls, or access controls.'}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(f'Wrote {len(records)} link records; crawled {crawled} allowlisted pages; allowlisted hosts: {len(ALLOWED_HOSTS)}')

if __name__=='__main__': main()
