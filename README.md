# Emergency Roof Repair CT — emergencyroofrepairct.com

Static site for Cloudflare Pages. No build step. Domain: **emergencyroofrepairct.com**. Brand: **Emergency Roof Repair CT**. Homepage H1 / SEO target: **Emergency Roof Repair in Connecticut**.

## Deploy on Cloudflare Pages (Git)
1. Cloudflare dashboard → **Workers & Pages → Create → Pages → Connect to Git** → pick `webrankingpro/emergency-roof-repair-ct`.
2. Framework preset: **None**. Production branch: **main**. Build command: *(leave blank, or `exit 0` if the dashboard requires one)*. Build output directory: **`.`** (repo root).
3. Save and deploy. The `*.pages.dev` preview URL stays `noindex` (see `_headers`).
4. **Custom domain:** Pages project → *Custom domains → Set up a domain* → `emergencyroofrepairct.com` (and `www.emergencyroofrepairct.com`). The domain must be an active Cloudflare zone (nameservers pointed to Cloudflare). Add a redirect from `www` to the apex (Rules → Redirect Rules) so there is one canonical host.

### Or deploy directly from a terminal (no Git)
```bash
npx wrangler pages deploy . --project-name=emergency-roof-repair-ct --branch=main
```

## Going live (indexing on)
The site ships with staging protections so it can't be indexed with placeholder contact details: every page has `noindex, nofollow` and `robots.txt` has `Disallow: /`.

1. Open `launch_swap.py` and set in `CONFIG`:
   - `PHONE_DISPLAY` / `PHONE_TEL` → the real call-tracking number (replaces the `+92` dummy everywhere),
   - `FORM_MODE` → anything other than `DUMMY` once the real form embed (or a call-only flow) is in place,
   - `LAUNCH_MODE` → `"LIVE"`.
2. Run `python launch_swap.py`. It refuses LIVE mode while the dummy phone, `FORM_MODE = DUMMY` or the temporary-form comment remain. In LIVE mode it removes the `noindex` tags and `Disallow`, and writes the `Sitemap:` line in `robots.txt`.
3. Commit and push. Cloudflare redeploys automatically.
4. Submit `https://emergencyroofrepairct.com/sitemap.xml` in Google Search Console.

Repeat runs of the script are safe.

## Notes
- Fonts load from Google Fonts (allowed in the CSP in `_headers`). No analytics or call-tracking scripts are installed; if you add Ringba or similar, add its origin to `script-src` / `connect-src` in `_headers`.
- Logo files: `assets/img/logo-emergency-roof-repair.webp` (header), `assets/img/social-share.jpg` (1200×630 share image), plus `favicon*`, `apple-touch-icon.png`, `android-chrome-*.png`.
- See `AUDIT-NOTES.md` for what has been checked and what still needs a live check.
