# Ghost Hunters of South Florida: website

**Live site: https://ghosthunters.michaelbarcelo.com**
(Cloudflare Pages project `ghsf`. Also served at https://ghsf-f2i.pages.dev)

| Folder | Holds |
|---|---|
| `site/` | The website: plain HTML and CSS, deployed as-is |
| `brand/` | Logo sources: `logo/*.svg` built by `build_logo.py` |
| `tests/check_site.py` | Link, nav and contact-form checks |
| `docs/superpowers/` | Design spec and build plan |

## Deploy

```
python tests/check_site.py
npx wrangler@3 pages deploy site --project-name ghsf --branch main
```

Use wrangler **3**: wrangler 4 turns `pages` commands into Workers deploys. The account is Michael's
personal Cloudflare account (`npx wrangler@3 login`). GitHub Actions is disabled on the MBarc
account, so there's no CI deploy.
