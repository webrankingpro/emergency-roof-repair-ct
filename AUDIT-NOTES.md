# Audit notes (2026-11-15, after rebrand)

## Done
- Brand: **Emergency Roof Repair CT** everywhere (header/footer, titles, Open Graph, JSON-LD provider, TCPA text, Terms, Privacy, manifest). Homepage H1 stays **Emergency Roof Repair in Connecticut**; homepage `<title>` is "Emergency Roof Repair in Connecticut | Emergency Roof Repair CT".
- Domain: `{{DOMAIN}}` replaced with `emergencyroofrepairct.com` in canonicals, Open Graph URLs, JSON-LD and `sitemap.xml`.
- New logo (header, favicons, app icons, 1200×630 social image) built from the supplied icon with the new wordmark.
- All "referral service" wording removed (footer disclosure, About, Terms, Privacy, service and town pages, FAQs, schema `serviceType`). The homepage "…is a referral service, not the company carrying out roof work" line is gone.
- House/roof line-art under the homepage phone number removed.
- Internal/staging copy removed from public pages (Wave 1/2, TOWN_FACTS.md, "first-pass planning data", "call-routing provider", "not part of this release", Draft/lawyer banners).
- Contact email block removed (no mailbox exists); Terms/Privacy point to the phone number instead.
- `launch_swap.py` updated: no longer rewrites the brand string (it would have overwritten the H1); email no longer required.

## Still open before indexing is turned on (`launch_swap.py` blocks LIVE until set)
1. Real phone number (the `+92 304 6734508` dummy is still everywhere).
2. Real lead form / call-only decision. The form on Home and Contact still shows "This form is not connected yet". Add the provider's origin to CSP `form-action` / `frame-src` / `connect-src` in `_headers`.
3. Privacy Policy and Terms were cleaned of draft banners but have **not been reviewed by a lawyer** (legal entity, governing law, call recording/SMS consent, contractor data sharing).
4. Image licences: source/licence of the stock photos in `assets/img/` is not recorded.
5. Live checks only possible after deploy: Cloudflare headers, SSL, `www` → apex redirect, Core Web Vitals.
