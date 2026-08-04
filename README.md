# KubeKoch

Deutschsprachige Schritt-für-Schritt-Rezepte für Kubernetes und OpenShift.
Statisch, ohne Build-Framework – GitHub Pages baut und deployt alles.

## Neues Rezept veröffentlichen

1. HTML-Datei nach `rezepte/` legen (selbstenthaltend, Styles inline).
2. Optional Meta-Tags in den `<head>` setzen – alles hat Defaults:

```html
<meta name="rezept-kategorie"    content="observability">
<meta name="rezept-beschreibung" content="Ein Satz für die Karte">
<meta name="rezept-stand"        content="Logging 6.6 · 07/2026">
<meta name="rezept-suche"        content="loki lokistack vector">
```

Kategorien: `observability`, `storage`, `netzwerk`, `security`,
`cluster-ops`, `gitops`, `troubleshooting` – sonst `allgemein`.

3. `git add . && git commit && git push` – fertig. Die Action generiert
   die Startseite (Titel aus `<title>`, Stationen aus den `<section id=…>`,
   Datum aus dem Git-Commit) und deployt nach GitHub Pages.

## Einmalige Einrichtung

1. Repo auf GitHub anlegen, diesen Inhalt pushen.
2. Settings → Pages → Source: **GitHub Actions**.
3. Domain: `CNAME`-Datei enthält `kubekoch.de`. Beim Registrar:
   - 4 A-Records auf `185.199.108.153` … `185.199.111.153`
   - CNAME `www` → `DEINUSER.github.io`
4. In den Pages-Settings die Domain eintragen, „Enforce HTTPS“ aktivieren.

## Lokal testen

```bash
python3 scripts/generate_index.py
python3 -m http.server -d _site
```
