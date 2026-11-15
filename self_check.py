#!/usr/bin/env python3
"""Offline checks for the Emergency Roof Repair CT static site.
Run: python self_check.py   (needs: pip install beautifulsoup4)
Exits non-zero if any check fails."""
from pathlib import Path
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup
import json, re, sys, collections

ROOT = Path(__file__).resolve().parent
DOMAIN = "emergencyroofrepairct.com"
BRAND = "Emergency Roof Repair CT"
KEYWORD = "Emergency Roof Repair in Connecticut"
BANNED = re.compile(r"referral|TOWN_FACTS|Wave [0-9]|first-pass|\{\{[A-Z_]+\}\}|lawyer|Draft -", re.I)
issues = []
html = sorted(ROOT.rglob("*.html"))
titles = collections.Counter()
route_urls = set()

def route_of(p):
    rel = p.relative_to(ROOT).as_posix()
    if rel == "index.html": return "/"
    if rel == "404.html": return None
    return "/" + rel[:-len("index.html")]

for p in html:
    rel = p.relative_to(ROOT).as_posix()
    text = p.read_text(encoding="utf-8")
    soup = BeautifulSoup(text, "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else ""
    titles[title] += 1
    desc = (soup.find("meta", attrs={"name": "description"}) or {}).get("content", "")
    if not title: issues.append(f"{rel}: missing title")
    if not desc: issues.append(f"{rel}: missing meta description")
    if len(desc) > 165: issues.append(f"{rel}: meta description long ({len(desc)})")
    if len(soup.find_all("h1")) != 1: issues.append(f"{rel}: expected exactly one H1")
    # copy checks (visible text, meta, JSON-LD)
    visible = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    m = BANNED.search(visible)
    if m: issues.append(f"{rel}: banned wording '{m.group(0)}'")
    stripped = visible.replace(f"<h1>{KEYWORD}</h1>", "").replace(f"{KEYWORD} | {BRAND}", "")
    if KEYWORD in stripped and rel == "index.html" and False: pass
    if "Emergency Roof Repair in Connecticut" in stripped and rel == "index.html":
        pass  # keyword may appear in body copy/meta on the home page
    elif re.search(r"Emergency Roof Repair in Connecticut", stripped) and rel != "index.html":
        issues.append(f"{rel}: old brand string")
    # canonical
    route = route_of(p)
    can = soup.find("link", rel="canonical")
    if route is None:
        if can: issues.append("404: should not have a canonical")
    else:
        route_urls.add(f"https://{DOMAIN}{route}")
        if not can or can.get("href") != f"https://{DOMAIN}{route}":
            issues.append(f"{rel}: canonical wrong ({can.get('href') if can else None})")
    # logo / alt text
    for img in soup.find_all("img"):
        if img.get("alt") is None: issues.append(f"{rel}: <img> without alt attribute")
    # json-ld
    for s in soup.find_all("script", type="application/ld+json"):
        try: json.loads(s.string)
        except Exception as e: issues.append(f"{rel}: bad JSON-LD ({e})")
    # local links / assets
    for tag, attr in (("a", "href"), ("link", "href"), ("script", "src"), ("img", "src"), ("source", "src")):
        for el in soup.find_all(tag):
            v = el.get(attr)
            if not v or v.startswith(("mailto:", "tel:", "#", "data:")): continue
            u = urlparse(v)
            if u.scheme in ("http", "https"):
                if tag == "link" and el.get("rel") and "canonical" in el["rel"]: continue
                if u.netloc in ("fonts.googleapis.com", "fonts.gstatic.com"): continue
                if u.netloc.endswith(DOMAIN): continue
                issues.append(f"{rel}: unapproved external {tag} {v}")
                continue
            path = unquote(u.path)
            target = ROOT / path.lstrip("/")
            if path.endswith("/"): target = target / "index.html"
            if not target.exists(): issues.append(f"{rel}: broken local path {v}")

for t, n in titles.items():
    if n > 1: issues.append(f"duplicate title x{n}: {t}")

home = (ROOT / "index.html").read_text(encoding="utf-8")
if f"<h1>{KEYWORD}</h1>" not in home: issues.append("home H1 must be 'Emergency Roof Repair in Connecticut'")
if "hero-art-wrap" in home: issues.append("home still has the hero house illustration")
if "hero-note" in home: issues.append("home still has the hero disclaimer note")

# sitemap
sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
sm_urls = set(re.findall(r"<loc>(.*?)</loc>", sm))
if sm_urls != route_urls: issues.append(f"sitemap mismatch: missing {sorted(route_urls - sm_urls)[:3]} extra {sorted(sm_urls - route_urls)[:3]}")

# staging flag consistency
robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
noindex = sum('STAGING-NOINDEX' in p.read_text(encoding="utf-8") for p in html)
mode = "STAGING" if "Disallow: /" in robots else "LIVE"
if mode == "STAGING" and noindex != len(html): issues.append(f"staging robots.txt but only {noindex}/{len(html)} pages have noindex")
if mode == "LIVE" and noindex: issues.append(f"LIVE robots.txt but {noindex} pages still noindex")

print(json.dumps({"mode": mode, "html_files": len(html), "noindex_pages": noindex,
                  "sitemap_urls": len(sm_urls), "issues": issues, "status": "FAIL" if issues else "PASS"}, indent=2))
sys.exit(1 if issues else 0)
