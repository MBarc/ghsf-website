"""Static checks for site/: links resolve, nav is complete, analytics and the contact form are wired.

Run: python tests/check_site.py   (exit 0 = OK)
"""
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

SITE = Path(__file__).resolve().parent.parent / "site"
PAGES = ["index.html", "about.html", "merch.html", "contact.html"]


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.nav, self.inputs, self.forms = [], [], {}, []
        self.title, self._in_title, self._in_nav, self.text = "", False, False, ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for key in ("href", "src"):
            if a.get(key):
                self.refs.append(a[key])
        if tag == "title":
            self._in_title = True
        if tag == "nav":
            self._in_nav = True
        if tag == "a" and self._in_nav and a.get("href"):
            self.nav.append(a["href"])
        if tag == "input" and a.get("name"):
            self.inputs[a["name"]] = a
        if tag == "form":
            self.forms.append(a)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag == "nav":
            self._in_nav = False

    def handle_data(self, data):
        self.text += data
        if self._in_title:
            self.title += data


def check():
    errors = []
    if not SITE.is_dir():
        return [f"missing {SITE}"]
    for html in sorted(SITE.glob("*.html")):
        p = Page()
        p.feed(html.read_text(encoding="utf-8"))
        name = html.name
        if not p.title.strip():
            errors.append(f"{name}: no <title>")
        for ref in p.refs:
            u = urlparse(ref)
            if u.scheme or ref.startswith(("#", "//", "mailto:")):
                continue
            target = (html.parent / u.path).resolve()
            if u.path and not target.exists():
                errors.append(f"{name}: broken link {ref}")
        if name != "thanks.html" and not set(PAGES) <= set(p.nav):
            errors.append(f"{name}: nav missing {sorted(set(PAGES) - set(p.nav))}")
        if "js/analytics.js" not in p.refs:
            errors.append(f"{name}: js/analytics.js not loaded")
    analytics = SITE / "js" / "analytics.js"
    js = analytics.read_text(encoding="utf-8") if analytics.exists() else ""
    if "posthog.init" not in js or "maskAllInputs: true" not in js:
        errors.append("js/analytics.js: posthog.init with maskAllInputs: true missing")
    for name in PAGES + ["thanks.html"]:
        if not (SITE / name).exists():
            errors.append(f"missing page {name}")

    contact = SITE / "contact.html"
    if contact.exists():
        p = Page()
        p.feed(contact.read_text(encoding="utf-8"))
        if not any(f.get("action") == "https://api.web3forms.com/submit" and f.get("method", "").lower() == "post"
                   for f in p.forms):
            errors.append("contact.html: form must POST to https://api.web3forms.com/submit")
        for field in ("access_key", "botcheck", "subject", "name", "email"):
            if field not in p.inputs:
                errors.append(f"contact.html: input '{field}' missing")
        if not p.inputs.get("redirect", {}).get("value", "").endswith("thanks.html"):
            errors.append("contact.html: redirect to thanks.html missing")
    return errors


if __name__ == "__main__":
    errs = check()
    for e in errs:
        print("FAIL", e)
    print("OK" if not errs else f"{len(errs)} problem(s)")
    sys.exit(1 if errs else 0)
