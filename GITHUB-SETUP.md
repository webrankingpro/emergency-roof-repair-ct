# GitHub setup

Repository: https://github.com/webrankingpro/emergency-roof-repair-ct

```bash
git init
git branch -M main
git add .
git commit -m "Emergency Roof Repair CT: rebrand, new logo, Cloudflare Pages ready"
git remote add origin https://github.com/webrankingpro/emergency-roof-repair-ct.git
git push -u origin main
```

If the repository already has commits, use `git pull --rebase origin main` first (or `git push -u origin main --force` only if you intend to replace what is there).

Then connect the repository in Cloudflare Pages as described in `README.md`.
