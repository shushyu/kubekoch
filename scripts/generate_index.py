#!/usr/bin/env python3
"""KubeKoch – Index-Generator.

Scannt rezepte/*.html, liest Titel + optionale Meta-Tags und baut
daraus index.html mit einer Karte pro Rezept. Ergebnis landet in _site/
(fertig für GitHub Pages). Keine Abhängigkeiten außer der Stdlib.

Optionale Meta-Tags in jeder Rezept-HTML (alles hat Defaults):
  <meta name="rezept-kategorie"   content="observability">
  <meta name="rezept-beschreibung" content="Ein Satz für die Karte">
  <meta name="rezept-stand"        content="Logging 6.6 · 07/2026">
  <meta name="rezept-suche"        content="loki lokistack vector">
"""

import html
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REZEPTE = ROOT / "rezepte"
SITE = ROOT / "_site"

KATEGORIEN = [
    "observability", "storage", "netzwerk", "security",
    "cluster-ops", "gitops", "troubleshooting", "allgemein",
]


def meta(quelle: str, name: str) -> str:
    m = re.search(
        rf'<meta\s+name=["\']{name}["\']\s+content=["\'](.*?)["\']', quelle, re.I | re.S
    )
    return html.unescape(m.group(1)).strip() if m else ""


def titel(quelle: str, fallback: str) -> str:
    m = re.search(r"<title>(.*?)</title>", quelle, re.I | re.S)
    return html.unescape(m.group(1)).strip() if m else fallback


def lede(quelle: str) -> str:
    """Erster Absatz mit class="lede" als Beschreibungs-Fallback (ohne Tags, gekürzt)."""
    m = re.search(r'<p\s+class=["\']lede["\']\s*>(.*?)</p>', quelle, re.I | re.S)
    if not m:
        return ""
    text = re.sub(r"<[^>]+>", "", m.group(1))
    text = html.unescape(re.sub(r"\s+", " ", text)).strip()
    return text[:180] + "…" if len(text) > 180 else text


def stationen(quelle: str) -> int:
    return len(re.findall(r"<section\s+id=", quelle, re.I))


def git_datum(pfad: Path) -> str:
    """Letztes Commit-Datum der Datei, Fallback: Datei-Änderungsdatum."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(pfad)],
            capture_output=True, text=True, cwd=ROOT, check=True,
        ).stdout.strip()
        if out:
            return datetime.strptime(out, "%Y-%m-%d").strftime("%m/%Y")
    except Exception:
        pass
    return datetime.fromtimestamp(pfad.stat().st_mtime).strftime("%m/%Y")


def karte(pfad: Path) -> dict:
    quelle = pfad.read_text(encoding="utf-8", errors="replace")
    kategorie = meta(quelle, "rezept-kategorie").lower() or "allgemein"
    if kategorie not in KATEGORIEN:
        kategorie = "allgemein"
    return {
        "datei": f"rezepte/{pfad.name}",
        "titel": titel(quelle, pfad.stem),
        "kategorie": kategorie,
        "beschreibung": meta(quelle, "rezept-beschreibung") or lede(quelle),
        "stand": meta(quelle, "rezept-stand") or git_datum(pfad),
        "suche": meta(quelle, "rezept-suche"),
        "stationen": stationen(quelle),
    }


def strecke_html(n: int) -> str:
    if n < 2:
        return ""
    punkte = "<b></b>".join("<i></i>" for _ in range(min(n, 12)))
    return (
        f'<div class="strecke" aria-label="{n} Schritte">{punkte}'
        f"<span>{n} Schritte</span></div>"
    )


def karten_html(karten: list[dict]) -> str:
    teile = []
    for k in karten:
        teile.append(f'''
    <a class="plan" href="{k["datei"]}" data-linie="{k["kategorie"]}"
       data-suche="{html.escape(k["suche"])}">
      <div class="plan-top">
        <span class="linie">{k["kategorie"].replace("-", "-&#8203;").title()}</span>
        <span class="stand">{html.escape(k["stand"])}</span>
      </div>
      <h2>{html.escape(k["titel"])}</h2>
      <p>{html.escape(k["beschreibung"])}</p>
      {strecke_html(k["stationen"])}
    </a>''')
    return "\n".join(teile)


def main() -> None:
    dateien = sorted(REZEPTE.glob("*.html"))
    karten = sorted((karte(p) for p in dateien), key=lambda k: k["titel"].lower())

    vorlage = (ROOT / "scripts" / "index_vorlage.html").read_text(encoding="utf-8")
    index = vorlage.replace("<!--KARTEN-->", karten_html(karten))

    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    (SITE / "index.html").write_text(index, encoding="utf-8")
    shutil.copytree(REZEPTE, SITE / "rezepte")
    cname = ROOT / "CNAME"
    if cname.exists():
        shutil.copy(cname, SITE / "CNAME")

    print(f"{len(karten)} Rezept(e) → _site/index.html")


if __name__ == "__main__":
    main()
