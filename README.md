# Ghost Hunters of South Florida: website

**Live site: https://ghosthunters.michaelbarcelo.com**
(GitHub Pages; https://mbarc.github.io/ghsf-website/ redirects there)

| Folder | Holds |
|---|---|
| `site/` | The website: plain HTML and CSS, deployed as-is |
| `brand/` | Logo sources: `logo/*.svg` built by `build_logo.py` |
| `tests/check_site.py` | Link, nav and contact-form checks. The deploy runs it first |
| `docs/superpowers/` | Design spec and build plan |

Pushing to `main` deploys through `.github/workflows/pages.yml`.
