# Organisationen verwalten (Multi-Org)

← [Zurück zur Startseite](Home)

> Verfügbar ab **Version 2.0.0**. Erfordert die Rolle `system_admin`.

## Konzept

In einer Instanz dieser App können mehrere Feuerwehren (Organisationen) verwaltet werden. Jede Organisation:

- hat eigene Benutzer, Mitglieder und Fahrzeuge
- kann ihre eigene Org selbst verwalten (Org-Admin)
- kann bei Einsätzen als Kollaborator hinzugefügt werden

## Organisations-Übersicht aufrufen

**Admin-Menü** → **Organisationen** (nur `system_admin`)  
URL: `/admin/organisations`

## Neue Organisation anlegen

**+ Neue Organisation** → Formular:

| Feld | Beschreibung |
|------|-------------|
| Kürzel (slug) | Eindeutig, nur Kleinbuchstaben/Ziffern/Bindestriche (z.B. `lauterach`) |
| Name | Vollständiger Ortsname (z.B. `FF Lauterach`) |
| Farbe | Hex-Farbcode — wird als linker Streifen auf Fahrzeugkarten angezeigt |
| Kontakt E-Mail | Optional |

Nach Anlage kann ein Org-Admin-Benutzer erstellt werden, der die Org selbst verwaltet.

## Org-Admin einrichten

1. `/admin/benutzer` → **+ Neuer Benutzer**
2. `org_id` der neuen Organisation auswählen
3. Rolle `org_admin` zuweisen

Dieser Benutzer kann sich einloggen und seine Organisation selbst verwalten (Mitglieder, Fahrzeuge, Einstellungen), hat aber keinen Zugriff auf andere Organisationen.

## Rollen und Zugriff

| Rolle | Zugriff |
|-------|---------|
| `system_admin` | Alle Organisationen, alle Einsätze, System-Einstellungen |
| `org_admin` / `admin` | Nur eigene Organisation |
| Andere Rollen | Eigene Org + Einsätze, an denen ihre Org beteiligt ist |

## Multi-Org-Einsatz

Wenn Org A einen Einsatz erstellt, kann sie Org B als Kollaborator hinzufügen:

1. Im Einsatz-Board: **Org hinzufügen** (Einsatzleiter oder Admin)
2. Org aus Liste auswählen
3. Benutzer von Org B sehen den Einsatz sofort (WebSocket-Benachrichtigung)
4. Fahrzeuge von Org B sind im Board sichtbar (mit Org-B-Farbe)

## Organisation deaktivieren

In der Organisations-Liste → **Deaktivieren**

Deaktivierte Orgs können sich nicht einloggen, ihre Daten bleiben erhalten. Die Heimwehr kann nicht deaktiviert werden.

## Heimwehr

Die Organisation, die die App-Instanz betreibt, ist als **Heimwehr** markiert (`is_home_org = true`). Sie kann nicht deaktiviert werden und ist beim API-Einsatzanlage die Standard-Organisation.
