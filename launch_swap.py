#!/usr/bin/env python3
"""Safe, repeatable placeholder swap for the static Cloudflare Pages site.
Edit CONFIG, then run: python launch_swap.py
LIVE mode is intentionally gated; it will not remove noindex until all required launch
values are supplied and FORM_MODE is changed from DUMMY to the approved live setup.
"""
from pathlib import Path
import re, sys

ROOT = Path(__file__).resolve().parent
CONFIG = {
    "BRAND": "Emergency Roof Repair CT",
    "DOMAIN": "emergencyroofrepairct.com",   # bare hostname; no protocol or path
    "PHONE_DISPLAY": "+92 304 6734508", # TEMP dummy - replace with the final Ringba number
    "PHONE_TEL": "+923046734508",       # TEMP dummy - replace with tel-safe final number
    "CONTACT_EMAIL": "",          # optional - only used if a {{CONTACT_EMAIL}} token is added to a page
    "CLAIM_247": "OFF",
    "LAUNCH_MODE": "STAGING",     # STAGING or LIVE
    "FORM_MODE": "DUMMY",         # DUMMY until a real approved form or call-only flow is configured
}
SOURCE_PHONE_DISPLAY = "+92 304 6734508"
SOURCE_PHONE_TEL = "+923046734508"
TEXT_EXTENSIONS = {".html", ".xml", ".txt", ".js", ".css", ".webmanifest"}

def main():
    mode = str(CONFIG["LAUNCH_MODE"]).upper()
    if mode not in {"STAGING", "LIVE"}:
        raise SystemExit("LAUNCH_MODE must be STAGING or LIVE")
    domain = str(CONFIG["DOMAIN"]).strip().lower().strip('.')
    email = str(CONFIG["CONTACT_EMAIL"]).strip()
    if domain and ("/" in domain or "://" in domain or "{{" in domain):
        raise SystemExit("DOMAIN must be a bare hostname, e.g. example.com")
    if mode == "LIVE":
        problems=[]
        if not domain: problems.append("DOMAIN is empty")
        if CONFIG["PHONE_DISPLAY"] == SOURCE_PHONE_DISPLAY or CONFIG["PHONE_TEL"] == SOURCE_PHONE_TEL:
            problems.append("dummy +92 phone number is still configured")
        if str(CONFIG["FORM_MODE"]).upper() == "DUMMY":
            problems.append("FORM_MODE is still DUMMY; configure the approved form or call-only flow")
        if any("TEMP FORM, replace with the Leads Smart embed" in page.read_text(encoding="utf-8") for page in ROOT.rglob("*.html")):
            problems.append("temporary form placeholder comment remains in the HTML")
        if problems:
            raise SystemExit("Refusing LIVE launch: " + "; ".join(problems))

    changed_files=[]
    for path in ROOT.rglob('*'):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS or path.name == Path(__file__).name:
            continue
        original = path.read_text(encoding='utf-8')
        text = original
        text = text.replace('{{BRAND}}', str(CONFIG['BRAND']))
        if domain:
            text = text.replace('{{DOMAIN}}', domain)
        if email:
            text = text.replace('{{CONTACT_EMAIL}}', email)
        text = text.replace(SOURCE_PHONE_DISPLAY, str(CONFIG['PHONE_DISPLAY']))
        text = text.replace(SOURCE_PHONE_TEL, str(CONFIG['PHONE_TEL']))
        if mode == 'LIVE':
            text = re.sub(r'\s*<meta name="robots" content="noindex, nofollow">\s*<!-- STAGING-NOINDEX -->', '', text, flags=re.I)
            text = re.sub(r'(?m)^# STAGING[^\n]*\n', '', text)
            text = re.sub(r'(?m)^Disallow:\s*/\s*\n?', '', text)
            # Replace any existing Sitemap line rather than adding duplicates.
            if path.name == 'robots.txt':
                text = re.sub(r'(?m)^Sitemap:\s*.*\n?', '', text)
                if domain:
                    text = text.rstrip() + f"\nSitemap: https://{domain}/sitemap.xml\n"
        if text != original:
            path.write_text(text, encoding='utf-8')
            changed_files.append(str(path.relative_to(ROOT)))
    print(f"Mode: {mode}")
    print(f"Updated files: {len(changed_files)}")
    for item in changed_files: print(f" - {item}")
    if mode == 'STAGING': print("Staging protections retained. Noindex and robots Disallow remain enabled.")
    else: print("LIVE swaps applied. Verify domain DNS, SSL, redirects, form routing and legal approval before promotion.")

if __name__ == '__main__': main()
