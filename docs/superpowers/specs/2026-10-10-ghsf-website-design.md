# GHSF website: design

Date: 2026-10-10 · Status: approved in chat, pending spec review

The public website for **Ghost Hunters of South Florida (GHSF)**. Brand work came first and is
done (see Brand). This spec covers version 1 of the site.

## Goals

- Tell visitors who GHSF is, in a **balanced** tone: serious about the evidence, warm and
  playful about the team.
- Let people get in touch, and in particular **request an investigation**.
- Send fans to merch, which is sold through CustomInk and not on the site.
- Let the team see what visitors do on the site (analytics, session replay, heatmaps).

Not in v1: case files, an evidence or EVP gallery, accounts, an on-site store, a blog.

## Brand

| Item | Decision |
|---|---|
| Logo | Viewfinder badge (camera brackets, record dot) with the classic sheet ghost tilted 10°. Hat mark = brackets + ghost + "GHSF". |
| Files | `brand/logo/ghsf-{badge,mark}{,-1color,-light}.svg`, built by `brand/build_logo.py` (text outlined, transforms baked) |
| Palette | Black `#0B0D0A`, ecto lime `#8BE234`, deep green `#3F7A2A`, bone `#EDEFE6`. These are also the 4 embroidery threads. |
| Type | Alfa Slab One for display and "GHSF", Oswald 600/700 for labels and nav, plus a readable body face chosen at build time (Google Fonts) |
| Constraint | The logo is embroidery-first: no gradients or glow, ≥5 mm text at a 3.75" chest size |

## Architecture

- **Static site.** Four HTML pages, one stylesheet and the logo SVGs, with no framework and no build step.
  The header and footer are duplicated across the pages. Switch to Jekyll layouts if the site grows past about 6 pages.
- **Repo:** `MBarc/ghsf-website`. It must be **public** (GitHub Pages on a free plan), so nothing
  secret is ever committed. The Web3Forms and PostHog keys are public by design.
- **Layout:** `site/` is the website, the only thing deployed. `brand/` holds the logo sources and `docs/` holds specs and plans.
- **Deploy:** a GitHub Actions workflow (`actions/upload-pages-artifact` with path `site`, then
  `actions/deploy-pages`) on every push to `main`.
- **Domain:** `ghosthunters.michaelbarcelo.com`. A Cloudflare CNAME `ghosthunters` → `mbarc.github.io`
  (DNS-only, grey cloud), with the custom domain set in the repo's Pages settings and "Enforce HTTPS" on.
  A dedicated domain may replace it later.

```
site/
  index.html        Home
  about.html        About
  merch.html        Merch
  contact.html      Contact + investigation request
  thanks.html       form-submitted confirmation (Web3Forms redirect target)
  css/site.css
  img/              logo SVGs, favicon, photos
```

## Pages

**Home.** The badge as the hero, a one-line statement of who GHSF is, three short blocks
linking to About, Merch and Contact, and a "Request an investigation" call to action.

**About.** Who GHSF is, how the team investigates (equipment, method, respect for the
places and people involved), and team bios. **The content comes from Michael.** No team
member, bio or claim is invented. Missing content is shown as a clearly marked placeholder.

**Merch.** Cards that link out to CustomInk design pages (opened in a new tab). Until those
designs exist, the page shows an "in the works" state with the hat mark.

**Contact.** One form with a choice between *General question* and *Request an
investigation*.
- Always: name, email, message.
- Investigation adds: location type (home, business, public or historic site, other), city or
  area, what's been happening, how long it's been going on, and best way and time to reach you.
- Fields that don't apply are hidden and disabled, so they aren't submitted.
- Submissions go to **Web3Forms**, which emails them to Michael's Gmail. The page holds only the
  public access key, not the email address. A honeypot field blocks basic spam (hCaptcha
  can be added if needed). The subject line includes the request type. On success the visitor
  is redirected to `thanks.html`.
- Without JavaScript, the form still submits as a plain HTML POST; the type toggle is the only
  enhancement.

## Analytics

PostHog, as on the TaskMesh website, but in a **separate GHSF project**. The standard snippet goes in
each page's `<head>` with pageviews, autocapture, session replay and heatmaps on. Replay masks
form inputs, because contact details must not be recorded. The footer links to a short privacy note
on the Contact page.

## Look and feel

A dark site in the brand palette. Lime is reserved for actions and highlights, bone is used for text, and
deep green for quiet surfaces. The viewfinder brackets are reused to frame photos and the hero. Motion
is minimal and respects `prefers-reduced-motion`. The layout is mobile first and works at 360 px.

## What Michael provides

1. Web3Forms: verify the email address and hand over the access key.
2. PostHog: create the GHSF project and hand over the project key.
3. About copy and team bios (names, roles, photos if any).
4. Photos from investigations, if any (optional for launch).
5. A Cloudflare DNS record, or approval for Claude to add it.

Until 1 and 2 arrive, the pages ship with clearly named placeholders
(`WEB3FORMS_ACCESS_KEY`, `POSTHOG_PROJECT_KEY`), and the PostHog snippet does nothing without a key.

## Testing

- Render each page at phone (390 px) and desktop (1280 px) width, and check for overflow and
  readable contrast.
- Check that every internal link and asset path resolves (a small script).
- Submit one real form of each type and confirm both emails arrive.
- Confirm a pageview appears in PostHog live events after deploy, and that inputs are masked in replay.
- After the DNS change, confirm the site loads at the subdomain over HTTPS.
