# Einstellungen

← [Zurück zur Startseite](Home)

> URL: `/admin/settings`  
> Zugänglich für: `org_admin`, `admin`, `system_admin`

## Organisations-Einstellungen

Jede Organisation kann ihre eigenen Einstellungen verwalten.

### Logo hochladen

**Einstellungen** → **Logo** → Datei auswählen (PNG, JPG, SVG, WebP — max. 2 MB)

Das Logo wird angezeigt:
- Im Header der App (neben dem Organisationsnamen)
- Auf dem Deckblatt des PDF-Einsatzberichts
- Auf der About-Seite

Hochgeladene Logos werden in `app/static/img/uploads/` gespeichert und sind beim System-Update **geschützt** (werden nicht überschrieben).

### Organisationsname

Der angezeigte Name der Organisation in der gesamten App und in Berichten.

### Primärfarbe

Die Akzentfarbe der Organisation:
- Linker Streifen auf Fahrzeugkarten im Board
- Wird auch für eigene Fahrzeuge im Multi-Org-Einsatz genutzt

### Kontaktdaten

Für Impressum und PDF-Berichte: E-Mail, Telefon, Adresse.

### Footer-Text

Erscheint im Footer jedes PDF-Einsatzberichts (z.B. „FF Wolfurt — Rathausstraße 1 — 6922 Wolfurt").

## System-Einstellungen (nur system_admin)

Auf der Einstellungsseite sieht der System-Admin zusätzlich:

- **Aktuelle App-Version**
- **Schnelllinks**: Organisationen verwalten, System-Update, About

## System-Update (nur system_admin)

Neue Versionen können über `/admin/system/update` per ZIP-Upload eingespielt werden.

Details: [System-Update](Administration-System-Update)

## About-Seite

`/admin/about` — Versions-Info, Autoren, Changelog.

Zugänglich für alle angemeldeten Benutzer.
