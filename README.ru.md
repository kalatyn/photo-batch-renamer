<div align="center">

<img src="assets/icon.png" width="128" alt="Значок Photo Batch Renamer">

# Photo Batch Renamer

**Переименуйте фото с камеры из стандартных имён в свои: `DSC0001.JPG` → `Your Name_1.jpg`**

Бесплатная программа для Windows, macOS и Linux. Python и другие программы ставить не нужно.

[![Build](https://github.com/kalatyn/photo-batch-renamer/actions/workflows/build.yml/badge.svg)](https://github.com/kalatyn/photo-batch-renamer/actions/workflows/build.yml)
[![Latest release](https://img.shields.io/github/v/release/kalatyn/photo-batch-renamer)](https://github.com/kalatyn/photo-batch-renamer/releases/latest)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
![Platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

[English](README.md) · **Русский**

<img src="docs/screenshot.png" width="660" alt="Окно Photo Batch Renamer: папка, новое название, старые и новые имена файлов">

</div>

## Зачем

Вы вернулись из поездки, и у вас 500 фотографий с именами `DSC0001.JPG`, `DSC0002.JPG`, `IMG_4711.HEIC`…
Скопируйте их в папку, откройте Photo Batch Renamer, введите название, и каждый файл получит понятное
имя с номером: `Your Name_1.jpg`, `Your Name_2.jpg`, `Your Name_3.mp4`.

Сама программа на английском, но названия можно писать на любом языке, в том числе по-русски.

## Возможности

- **Предпросмотр.** До переименования видно, как каждый файл назывался и как будет называться.
- **Порядок по дате съёмки.** Для JPEG и TIFF берётся дата, записанная в самой фотографии (EXIF), для остальных файлов — дата файла. Удобно, если в одной папке снимки с фотоаппарата и с телефона.
- **Отмена.** Передумали — одно нажатие возвращает прежние имена.
- **Безопасность.** Программа никогда не перезаписывает файлы. Если что-то пойдёт не так посреди работы, все имена вернутся как были.
- **Нули впереди (по желанию).** `001, 002, …`, чтобы файлы правильно сортировались везде.
- **Расширения сохраняются.** У фото, видео и RAW-файлов (`.cr2`, `.nef`, `.arw`, …) тип не меняется.
- **Перетаскивание.** Папку можно бросить прямо в окно.
- **Служебные файлы не трогаются:** `Thumbs.db`, `desktop.ini`, `.DS_Store` и скрытые файлы.
- **Одинаково везде.** Окно одинаковое в Windows, macOS и Linux.

## Скачать

Последняя версия — на **[странице релизов](https://github.com/kalatyn/photo-batch-renamer/releases/latest)**:

| Система | Файл |
|---|---|
| Windows 10 / 11 | `PhotoBatchRenamer-…-Windows-Setup.exe` |
| macOS, Apple Silicon (M1 и новее) | `PhotoBatchRenamer-…-macOS-arm64.dmg` |
| macOS, Intel | `PhotoBatchRenamer-…-macOS-intel.dmg` |
| Ubuntu, Debian, Linux Mint | `photo-batch-renamer_…_amd64.deb` |
| Другой Linux (без установки) | `PhotoBatchRenamer-…-Linux-x86_64.tar.gz` |

Какой у вас Mac? Меню Apple → **Об этом Mac**: «Apple M…» — это Apple Silicon, «Intel» — Intel.

## Установка

Программа бесплатная и не подписана платным сертификатом разработчика, поэтому при первом запуске
Windows и macOS покажут предупреждение. Это нормально.

<details>
<summary><b>Windows</b></summary>

1. Запустите `PhotoBatchRenamer-…-Windows-Setup.exe`.
2. Если появится окно **«Windows защитила ваш компьютер»**, нажмите **Подробнее → Выполнить в любом случае**.
3. Пройдите шаги установки. Права администратора не нужны.

Программа появится в меню «Пуск» (и на рабочем столе, если вы это выбрали).
Удаляется как обычно: **Параметры → Приложения**.
</details>

<details>
<summary><b>macOS</b></summary>

1. Откройте `.dmg` и перетащите **Photo Batch Renamer** в папку **Программы**.
2. Откройте программу. macOS напишет, что не может проверить разработчика. Нажмите **Готово** (или **OK**).
3. Откройте **Системные настройки → Конфиденциальность и безопасность**, прокрутите вниз и нажмите **Всё равно открыть** рядом с Photo Batch Renamer.

Это нужно сделать только один раз.
</details>

<details>
<summary><b>Linux (Ubuntu, Debian, Mint)</b></summary>

Откройте `.deb` двойным щелчком или выполните:

```bash
sudo apt install ./photo-batch-renamer_*_amd64.deb
```

Программа появится в меню приложений. Нужные системные библиотеки установятся сами.

**Другие дистрибутивы:** распакуйте `.tar.gz` и запустите `PhotoBatchRenamer/Photo Batch Renamer`.
</details>

## Как пользоваться

1. Нажмите **Browse…** и выберите папку с фотографиями (или перетащите папку в окно).
2. Введите новое название, например `Your Name`. Имя папки подставляется само.
3. Выберите порядок: **by file name** (по имени файла — в том порядке, как снимала камера) или **by date taken** (по дате съёмки).
4. Проверьте предпросмотр и нажмите **Rename**.

> [!IMPORTANT]
> Программа переименовывает **все файлы** в выбранной папке (вложенные папки не трогает). Кладите туда только те фото, которые хотите переименовать.

## Вопросы и ответы

**Программа меняет сами фотографии?**
Нет. Меняются только имена файлов. Изображение, EXIF и даты файлов остаются прежними.

**Можно отменить?**
Да, кнопкой **Undo**, пока программа открыта. После закрытия прежние имена не сохраняются.

**Откуда берётся «дата съёмки»?**
Для JPEG и TIFF — из EXIF. Для остальных файлов (HEIC, RAW, видео) — дата изменения файла, которую фотоаппараты и программы копирования обычно сохраняют.

**Почему установщик такой большой (около 50 МБ)?**
В нём уже есть всё, что нужно программе, чтобы вам не пришлось ставить Python и другие программы.

## Сборка из исходников

Нужен Python 3.10 или новее.

```bash
git clone https://github.com/kalatyn/photo-batch-renamer.git
cd photo-batch-renamer
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-build.txt

python -m pytest                                      # тесты
PYTHONPATH=src python -m photo_batch_renamer          # запуск программы
python packaging/build.py                             # установщик для вашей системы
```

`packaging/build.py` собирает установщик `.exe` в Windows (нужен [Inno Setup 6](https://jrsoftware.org/isinfo.php)),
`.dmg` в macOS и `.deb` с `.tar.gz` в Linux. Всё складывается в `dist/`.

Релизы собираются автоматически через [GitHub Actions](.github/workflows/build.yml):
после отправки тега вроде `v1.0.1` собираются все установщики и публикуются на странице релизов.

## Участие

Ошибки и идеи пишите в [Issues](https://github.com/kalatyn/photo-batch-renamer/issues) (можно по-русски).
Pull request’ы тоже приветствуются: перед отправкой запустите `python -m pytest`.

## Лицензия

[MIT](LICENSE). Можно бесплатно использовать для себя и в работе.
