#!/usr/bin/env python3
"""Render six full translations of the existing English support/privacy pages.

Editorial source: support.html and privacy.html as published on 2026-09-23.
Policy effective date remains 2026-09-16; translation date is shown separately.
No client-side translation, language detection, cookies or external services.
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://openmusic.performarc.app/"
LANGUAGES = {"en": "English", "ru": "Русский", "de": "Deutsch", "fr": "Français", "es": "Español", "it": "Italiano", "ja": "日本語", "zh-Hans": "简体中文"}
SECTION_IDS = {
    "support": ["add-music", "clear-library", "playback", "recognition", "feedback", "diagnostics"],
    "privacy": ["controller", "local-data", "files", "recognition", "platforms", "feedback", "processors", "tracking", "deletion", "contact"],
}

def filename(kind, lang):
    return f"{kind}{'' if lang == 'en' else '-' + lang}.html"

def alternates(kind):
    return "\n".join(f'<link rel="alternate" hreflang="{lang}" href="{ORIGIN}{filename(kind, lang)}">' for lang in LANGUAGES) + f'\n<link rel="alternate" hreflang="x-default" href="{ORIGIN}{filename(kind, "en")}">'

def switcher(kind, current, label):
    links = []
    for lang, name in LANGUAGES.items():
        state = ' aria-current="page"' if lang == current else ""
        links.append(f'<a href="{filename(kind, lang)}" lang="{lang}" hreflang="{lang}"{state}>{name}</a>')
    return f'<nav class="page-languages" aria-label="{html.escape(label, quote=True)}">' + "".join(links) + '</nav>'

def render(lang, data, kind):
    ui, page = data["ui"], data[kind]
    support, privacy = filename("support", lang), filename("privacy", lang)
    news = "news/" + filename("version-1-2-2", lang)
    def content(text):
        for key, value in {"privacy": privacy, "support": support, "news": news, "email": "support-openmusic@performarc.app"}.items():
            text = text.replace("{" + key + "}", value)
        return text
    def e(text):
        return html.escape(text, quote=True)
    ids = SECTION_IDS[kind]
    assert len(page["sections"]) == len(ids), (lang, kind, "incomplete sections")
    sections = "\n".join(f'<section id="{sid}"><h2>{e(section["heading"])}</h2>{content(section["html"])}</section>' for sid, section in zip(ids, page["sections"]))
    aside = "".join(f'<a href="#{sid}">{e(section["heading"])}</a>' for sid, section in zip(ids, page["sections"]))
    if kind == "support":
        extra = f'<p class="page-release-note">{content(page["availability"])} {content(page["notes"])}</p>'
        sections += f'<div class="contact-panel" id="contact"><div><h2>{e(page["contact"])}</h2><p>{e(page["contactText"])}</p></div><a class="button button-primary" href="mailto:support-openmusic@performarc.app">{e(ui["email"])}</a></div>'
        aside += f'<a href="#contact">{e(page["contact"])}</a>'
    else:
        extra = f'<div class="page-meta"><span>{e(page["updated"])}</span><span>{e(page["translated"])}</span></div>'
        sections = f'<div class="callout"><p>{e(page["notice"])}</p></div>\n' + sections
    other_kind, other_file = ("privacy", privacy) if kind == "support" else ("support", support)
    language_nav = switcher(kind, lang, ui['language'])
    intro_extra = language_nav + extra if kind == "support" else extra + language_nav
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{e(page['description'])}">
<meta name="theme-color" content="#07120e">
<link rel="canonical" href="{ORIGIN}{filename(kind, lang)}">
{alternates(kind)}
<link rel="icon" type="image/png" href="app-icon.png">
<link rel="stylesheet" href="styles.css">
<link rel="stylesheet" href="pages.css?v=20260924">
<title>{e(ui[kind])} — Open Music Player</title>
</head>
<body class="page-body">
<a class="skip-link" href="#main">{e(ui['skip'])}</a>
<header class="page-header"><div class="shell header-inner"><a class="brand page-nav-home" href="./"><img src="app-icon.png" alt=""><span>Open Music Player</span></a><nav aria-label="{e(ui['navigation'])}"><a href="./#features">{e(ui['features'])}</a><a href="{news}">{e(ui['news'])}</a><a href="{other_file}">{e(ui[other_kind])}</a></nav><a class="header-cta" href="https://apps.apple.com/app/id6808717551">App Store <span aria-hidden="true">↗</span></a></div></header>
<main class="page-main" id="main"><div class="shell">
<div class="page-intro"><p class="kicker">{e(ui[kind])}</p><h1>{e(page['title'])}</h1><p>{e(page['intro'])}</p>{intro_extra}</div>
<div class="article-layout"><article class="article">{sections}</article><aside class="article-aside" aria-label="{e(ui['toc'])}"><strong>{e(ui['toc'])}</strong>{aside}</aside></div>
</div></main>
<footer><div class="shell footer-inner"><a class="brand footer-brand" href="./"><img src="app-icon.png" alt=""><span>Open Music Player</span></a><p>{e(ui['tagline'])}<br>{e(ui['by'])}</p><div class="footer-links"><a href="{news}">{e(ui['news'])}</a><a href="{other_file}">{e(ui[other_kind])}</a><a href="mailto:support-openmusic@performarc.app">{e(ui['email'])}</a></div><small>© 2026 Performarc</small></div></footer>
</body>
</html>
'''

if __name__ == "__main__":
    for lang in list(LANGUAGES)[2:]:
        data = json.loads((ROOT / "locales" / f"{lang}.json").read_text())
        for kind in SECTION_IDS:
            (ROOT / filename(kind, lang)).write_text(render(lang, data, kind))
    print("Rendered 12 localized support/privacy pages.")
