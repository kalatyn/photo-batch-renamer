<div align="center">

<img src="assets/icon.png" width="128" alt="Photo Batch Renamer Symbol">

# Photo Batch Renamer

**Kamerafotos von Standardnamen in eigene Namen umbenennen: `DSC0001.JPG` → `Your Name_1.jpg`**

Kostenlose Desktop-App für Windows, macOS und Linux. Python oder andere Software muss nicht installiert werden.

[![Build](https://github.com/kalatyn/photo-batch-renamer/actions/workflows/build.yml/badge.svg)](https://github.com/kalatyn/photo-batch-renamer/actions/workflows/build.yml)
[![Latest release](https://img.shields.io/github/v/release/kalatyn/photo-batch-renamer)](https://github.com/kalatyn/photo-batch-renamer/releases/latest)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
![Platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

[English](README.md) · **Deutsch**

<img src="docs/screenshot.png" width="660" alt="Fenster von Photo Batch Renamer: Ordner, neuer Name, Vorschau der alten und neuen Dateinamen">

</div>

## Wozu

Sie kommen aus dem Urlaub zurück und haben 500 Fotos mit Namen wie `DSC0001.JPG`, `DSC0002.JPG`, `IMG_4711.HEIC`…
Kopieren Sie sie in einen Ordner, öffnen Sie Photo Batch Renamer, geben Sie einen Namen ein, und jede Datei
bekommt einen klaren, nummerierten Namen: `Your Name_1.jpg`, `Your Name_2.jpg`, `Your Name_3.mp4`.

Die App selbst ist auf Englisch, Namen können Sie aber in jeder Sprache eingeben, auch mit Umlauten.

## Funktionen

- **Live-Vorschau.** Für jede Datei sehen Sie „vorher → nachher“, bevor etwas geändert wird.
- **Sortieren nach Aufnahmedatum.** Bei JPEG und TIFF wird das im Foto gespeicherte Datum (EXIF) verwendet, bei allen anderen Dateien das Dateidatum. Praktisch, wenn ein Ordner Fotos von Kamera und Handy mischt.
- **Rückgängig.** Doch anders entschieden? Ein Klick stellt die ursprünglichen Namen wieder her.
- **Sicher.** Es wird nie eine Datei überschrieben. Geht mittendrin etwas schief, werden alle Namen zurückgesetzt.
- **Führende Nullen (optional).** `001, 002, …`, damit Dateien überall richtig sortiert werden.
- **Dateitypen bleiben erhalten.** Fotos, Videos und RAW-Dateien (`.cr2`, `.nef`, `.arw`, …) behalten ihre Endung.
- **Drag & Drop.** Ziehen Sie einen Ordner einfach ins Fenster.
- **Dateien auswählen.** Jede Datei hat ein Häkchen. Umbenannt werden nur die angehakten, oder Sie wählen mit **All / None / Photos / Videos** per Klick: zuerst die Fotos in `Your Name photo`, dann die Videos in `Your Name video`.
- **Nur Fotos und Videos.** Angezeigt werden JPEG, PNG, HEIC, WebP, RAW-Dateien von Kameras und alle gängigen Videoformate. Dokumente, Programme, Musik und andere Dateien im Ordner werden ausgeblendet und nie verändert.
- **Updates in der App.** Mit **Check for updates** wird eine neue Version direkt installiert, ohne manuellen Download oder Neuinstallation.
- **Überall gleich.** Identisches Fenster unter Windows, macOS und Linux.

## Download

Die neueste Version gibt es auf der **[Releases-Seite](https://github.com/kalatyn/photo-batch-renamer/releases/latest)**:

| System | Datei |
|---|---|
| Windows 10 / 11 | `PhotoBatchRenamer-…-Windows-Setup.exe` |
| macOS, Apple Silicon (M1 und neuer) | `PhotoBatchRenamer-…-macOS-arm64.dmg` |
| macOS, Intel | `PhotoBatchRenamer-…-macOS-intel.dmg` |
| Ubuntu, Debian, Linux Mint | `photo-batch-renamer_…_amd64.deb` |
| Anderes Linux (portabel) | `PhotoBatchRenamer-…-Linux-x86_64.tar.gz` |

Welchen Mac haben Sie? Apple-Menü → **Über diesen Mac**: „Apple M…“ bedeutet Apple Silicon, „Intel“ bedeutet Intel.

## Installation

Die App ist kostenlos und nicht mit einem kostenpflichtigen Entwicklerzertifikat signiert. Deshalb zeigen
Windows und macOS beim ersten Start eine Warnung. Das ist normal.

<details>
<summary><b>Windows</b></summary>

1. Starten Sie `PhotoBatchRenamer-…-Windows-Setup.exe`.
2. Erscheint **„Der Computer wurde durch Windows geschützt“**, klicken Sie auf **Weitere Informationen → Trotzdem ausführen**.
3. Folgen Sie dem Installationsassistenten. Administratorrechte sind nicht nötig.

Die App erscheint im Startmenü (und auf dem Desktop, wenn Sie das ausgewählt haben).
Deinstallieren wie jede andere App: **Einstellungen → Apps**.
</details>

<details>
<summary><b>macOS</b></summary>

1. Öffnen Sie die `.dmg`-Datei und ziehen Sie **Photo Batch Renamer** in den Ordner **Programme**.
2. Öffnen Sie die App. macOS meldet, dass der Entwickler nicht überprüft werden kann. Klicken Sie auf **Fertig** (oder **OK**).
3. Öffnen Sie **Systemeinstellungen → Datenschutz & Sicherheit**, scrollen Sie nach unten und klicken Sie neben Photo Batch Renamer auf **Trotzdem öffnen**.

Das ist nur einmal nötig.
</details>

<details>
<summary><b>Linux (Ubuntu, Debian, Mint)</b></summary>

Installieren Sie die `.deb`-Datei per Doppelklick oder mit:

```bash
sudo apt install ./photo-batch-renamer_*_amd64.deb
```

Die App erscheint im Anwendungsmenü. Benötigte Systembibliotheken werden automatisch installiert.

**Andere Distributionen:** Entpacken Sie die `.tar.gz`-Datei und starten Sie `PhotoBatchRenamer/Photo Batch Renamer`.
</details>

## Bedienung

1. Klicken Sie auf **Browse…** und wählen Sie den Ordner mit Ihren Fotos (oder ziehen Sie den Ordner ins Fenster).
2. Geben Sie den neuen Namen ein, z. B. `Your Name`. Der Ordnername wird automatisch vorgeschlagen.
3. Wählen Sie die Reihenfolge: **by file name** (nach Dateiname, also in der Reihenfolge der Kamera), **by date taken** (nach Aufnahmedatum) oder **by type** (erst Fotos, dann Videos).
4. Entfernen Sie das Häkchen bei Dateien, die nicht umbenannt werden sollen, oder nutzen Sie **All / None / Photos / Videos**.
5. Prüfen Sie die Vorschau und klicken Sie auf **Rename**. Nur angehakte Dateien werden umbenannt und nummeriert.

> [!IMPORTANT]
> Umbenannt werden nur **angehakte Foto- und Videodateien** im gewählten Ordner, Unterordner nicht. Andere Dateien (Dokumente, Programme, Musik …) werden nicht angezeigt und nie verändert.

## Häufige Fragen

**Verändert die App meine Fotos?**
Nein. Nur die Dateinamen ändern sich. Bilddaten, EXIF und Dateidaten bleiben unverändert.

**Kann ich das rückgängig machen?**
Ja, mit der Schaltfläche **Undo**, solange die App geöffnet ist. Danach sind die alten Namen nicht mehr gespeichert.

**Woher kommt das „Aufnahmedatum“?**
Bei JPEG und TIFF aus den EXIF-Daten. Bei anderen Dateien (HEIC, RAW, Videos) wird das Änderungsdatum der Datei verwendet, das Kameras und Kopierprogramme normalerweise beibehalten.

**Welche Dateien werden angezeigt?**
Fotos: JPEG, PNG, GIF, BMP, TIFF, WebP, HEIC/HEIF, AVIF, JPEG XL und RAW-Dateien von Canon, Nikon, Sony, Fujifilm, Olympus/OM System, Panasonic, Leica, Pentax, Samsung, Sigma, Hasselblad, Phase One sowie DNG.
Videos: MP4, MOV, AVI, MKV, WMV, WebM, MTS/M2TS, MPG, 3GP, DV, GoPro- und Insta360-Dateien, Blackmagic RAW, RED und MXF.

**Wie funktionieren Updates?**
Klicken Sie oben rechts auf **Check for updates**. Gibt es eine neue Version, klicken Sie auf **Install**: Die App lädt sie von dieser GitHub-Seite, prüft, ob die Datei vollständig und unverändert ist (SHA-256-Prüfsumme), installiert sie über die aktuelle Version und startet neu. Einstellungen und Verknüpfungen bleiben erhalten. Unter Linux (.deb) werden Sie nach Ihrem Passwort gefragt, wie bei jeder Paketinstallation.
Beim Start fragt die App GitHub unauffällig nach der neuesten Versionsnummer. Dabei werden keine Daten über Sie oder Ihre Dateien gesendet.

**Warum ist der Download so groß (etwa 50 MB)?**
Der Installer enthält alles, was die App braucht. So müssen Sie weder Python noch andere Software installieren.

## Aus dem Quellcode bauen

Benötigt Python 3.10 oder neuer.

```bash
git clone https://github.com/kalatyn/photo-batch-renamer.git
cd photo-batch-renamer
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-build.txt

python -m pytest                                      # Tests ausführen
PYTHONPATH=src python -m photo_batch_renamer          # App starten
python packaging/build.py                             # Installer für Ihr System bauen
```

`packaging/build.py` erstellt unter Windows einen `.exe`-Installer (benötigt [Inno Setup 6](https://jrsoftware.org/isinfo.php)),
unter macOS eine `.dmg` und unter Linux eine `.deb` sowie eine `.tar.gz`, alles in `dist/`.

Releases werden automatisch mit [GitHub Actions](.github/workflows/build.yml) gebaut:
Ein Tag wie `v1.0.2` baut alle Installer und veröffentlicht sie auf der Releases-Seite.

## Mitmachen

Fehlerberichte und Ideen sind in den [Issues](https://github.com/kalatyn/photo-batch-renamer/issues) willkommen (gern auf Deutsch).
Pull Requests ebenfalls: Bitte vorher `python -m pytest` ausführen.

## Lizenz

[MIT](LICENSE). Kostenlos für private und berufliche Nutzung.
