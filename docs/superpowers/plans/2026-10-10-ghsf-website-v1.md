# GHSF Website v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the four-page static GHSF site (Home, About, Merch, Contact) to GitHub Pages.

**Architecture:** Plain HTML pages plus one stylesheet in `site/`, deployed by a GitHub Actions Pages workflow. The contact form POSTs to Web3Forms, and analytics is the PostHog snippet in each `<head>`.

**Tech Stack:** HTML, CSS, a few lines of vanilla JS, Google Fonts, Web3Forms, PostHog, GitHub Pages. Python 3.12 (stdlib only) for the site check.

**Spec:** `docs/superpowers/specs/2026-10-10-ghsf-website-design.md`

## Global Constraints

- Palette: black `#0B0D0A`, ecto lime `#8BE234`, deep green `#3F7A2A`, bone `#EDEFE6`.
- Fonts: Alfa Slab One (display), Oswald 600/700 (labels and nav), plus a body face from Google Fonts.
- Public repo: no secrets. The keys are placeholders `WEB3FORMS_ACCESS_KEY` and `POSTHOG_PROJECT_KEY` until Michael supplies them.
- No invented team members, bios or claims. Missing content is a visibly marked placeholder.
- Works at 360 px wide and respects `prefers-reduced-motion`.
- Form inputs are masked in PostHog session replay.

---

### Task 1: Site check script (the test)

**Files:** Create `tests/check_site.py`

**Produces:** `python tests/check_site.py` exits 0 when the site is valid and prints each failure otherwise.

Checks for every `site/*.html`:
- Every local `href`/`src` resolves to a file in `site/`.
- There is a `<title>` and the nav links to `index.html`, `about.html`, `merch.html` and `contact.html`.
- The PostHog snippet is present (`posthog.init`).
- `contact.html` has a form posting to `https://api.web3forms.com/submit`, an `access_key` input, a `botcheck` honeypot, and a `redirect` to `thanks.html`.

- [ ] Write the script (stdlib `html.parser`)
- [ ] Run it and expect FAIL (no `site/` yet)

### Task 2: Stylesheet, Home page and assets

**Files:** Create `site/index.html`, `site/css/site.css`, and `site/img/` (copied from `brand/logo/`, plus a favicon SVG made from the hat mark).

- [ ] Write `site.css`: tokens, header/nav, footer, hero, buttons, cards, the viewfinder-frame utility and form styles
- [ ] Write the Home page: badge hero, one-line statement, three link blocks and an investigation call to action
- [ ] Run the check; Home passes and the other pages are reported missing

### Task 3: About and Merch

**Files:** Create `site/about.html` and `site/merch.html`.

- [ ] About: what GHSF does and how it investigates, in a neutral voice with no factual claims beyond the spec, plus a marked placeholder for team bios
- [ ] Merch: an "in the works" state with the hat mark, plus a card pattern (commented example) for future CustomInk links
- [ ] Run the check

### Task 4: Contact and thanks

**Files:** Create `site/contact.html` and `site/thanks.html`.

- [ ] Form: a radio toggle between general and investigation. Investigation fields sit in a `<fieldset>` that is disabled and hidden when not selected. JS also updates the hidden `subject`. The form includes the honeypot, the redirect and a privacy note.
- [ ] Run the check and expect PASS for all pages

### Task 5: Deploy

**Files:** Create `.github/workflows/pages.yml` and `site/CNAME` (`ghosthunters.michaelbarcelo.com`).

- [ ] Workflow: `actions/checkout@v4`, then `actions/configure-pages@v5`, then `actions/upload-pages-artifact@v3` (path `site`), then `actions/deploy-pages@v4`
- [ ] Take headless Edge screenshots of each page at 390 and 1280 px and fix any problems
- [ ] Commit. Create the public repo `MBarc/ghsf-website`, push, and enable Pages (source: GitHub Actions)

### Handoff (Michael)

The Web3Forms key, the PostHog key, the Cloudflare CNAME, About copy, then the live form and PostHog tests from the spec's Testing section.
