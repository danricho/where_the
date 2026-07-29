<div align="center">

<img src="static/logo_md.png"/>

# Where The ?!?

A simple Python Flask web application which helps keep track of your stored items.

</div>

## Features

- Responsive web-based user interface
- Easy, simple location editing
- Bulk item editor — all items of a location in one text block, one per line (fast stocktakes on a laptop; press <kbd>b</kbd> on a location page)
- Search by stored item
- Sort locations by different attributes:
  - description
  - location (eg. Office, Garage, etc)
  - type (eg. Shelf, Plastic Box, etc)
  - recently edited
  - unique ID
  - how used (fullness)
- QR codes to assist location tracking based on unique ID
- Print QR code labels from website
- Simple JSON storage (pros & cons)

## Screenshots

**Does anyone know a quick way to generate this type of demo image?**

See [this page](static/screenshots/screenshots.md) for example screenshots.

## Installation - Native Python

_These steps describe how I set it up. I use a linux terminal so under Windows there may be minor step inaccuracies._

1.  Clone repo to a local directory.
    eg: `git clone https://github.com/danricho/where_the.git where_the`

1.  Create a Python Virtual Environment (venv).
    eg: `python3 -m venv venv`

1.  Install dependencies via pip into your venv.
    eg: `venv/bin/pip install -r requirements.txt` or activate venv then `pip install -r requirements.txt`

1.  Create `config.yml` and update according it to your setup - see the [Configuration section](#configuration-configyml).

1.  Run `main.py` in your venv.
    eg: `venv/bin/python main.py` or activate venv then `python main.py`

**NOTE:**
If running the script as root (or sudo), the directory ownership may need to be changed to root using `chown -R root .`. This is due to a new ownership check in newer versions of git and Where The checks for new versions when it starts. If the check can't run (no internet, or the ownership issue above), the app still starts and simply shows "Version check unavailable" in the menu instead of the version comparison.

## Installation - Docker

_Running in Docker is a quick way to get this to run as a service (launches on boot etc)._

1. Clone repo to a local directory.
   eg: `git clone https://github.com/danricho/where_the.git where_the`

1. Create `config.yml` and update according to the [Configuration section](#configuration-configyml). This file is mounted within the docker image but saved here outside it (to keep data between docker sessions)

1. Create `data.json` and set the content to `{}`. This file is mounted within the docker image but saved here outside it (to keep data between docker sessions)

1. Run the docker container using the command `docker-compose up -d`.

1. To troubleshoot the container it may help to see it's logs: `docker logs where_the`

**NOTE:**
Networking settings are more complicated when using docker, so check the following:

- in `config.yml`:
  - `FLASK.HOST` - `0.0.0.0`
  - `FLASK.PORT` - `5000`
  - `SITE.BASE_URL` - usually host's IP or hostname
- in `docker-compose.yml`:
  - `services.web-app.ports` - `80:5000` - second number needs to match above, first is the port that docker will use. _Note: 80 may require special permission_.

### Pre-Built Docker Image

An alternative to building the docker image is now provided thanks to [@LukeEvansTech](https://github.com/LukeEvansTech).
Each push to this repo now re-builds a 'package' which is GitHub's name for pre-made Docker Images and can be used as follows:

- Using docker command to pull the image to the local machine:
  `docker pull ghcr.io/danricho/where_the:main`
- Use in docker-compose file:
  `image: ghcr.io/danricho/where_the:main`
- Use docker run, although the correct arguments will need to be provided - see `docker-compose.yml` for more information.

## Updating to the latest GitHub version

To update, all that should be needed is to run the command `git pull` in your Where The ?!? directory.

If you get a message about local file changes which would be overwritten by merge, this means you have modified one of the tracked files. The config and data files (as made during installation) are not the files git is talking about.

The command `git diff` will tell you what is different about the files. Running `git reset --hard HEAD` will reset the uncommited file changes, but **NOTE THAT** you may lose work if you do this. Only do this if you understand what you are doing. And once your Repo is clean, the `git pull` should work.

There are many resources available online to learn more about Git operations.

### Extra Update Step for Docker

After updating, the docker image needs to be rebuilt as the app files (other than those mapped in `docker-compose.yml`) are cached inside the docker image. This automatically happens the first time you bring Where The ?!? up.

This can be done by running docker-compose with a few extra commands:
`docker-compose up -d --force-recreate --build`

If using the pre-built image, ensure that you freshly pull the latest image.

## Configuration (config.yml)

```yaml
# DO NOT ADD COMMENTS YOU WANT KEPT TO THIS YML AS IT IS REWRITTEN BY THE APP AND COMMENTS ARE LOST.

SITE:
  BASE_URL: http://localhost # THIS IS YOUR DOMAIN OR START OF YOUR URL - USED IN QR CODE
  PATH_PREFIX: / # THIS IS USEFUL IF YOU WANT A PREFIX ON THE URL PATH - USED IN QR CODE AND FLASK

# THE MAIN COLOR.
# THE DEFAULT #C0A890 IS BASED ON A CARBOARD BOX COLOR :)
# CAN BE IN ONE OF THE FOLLOWING FORMATS:
#  - rgb(192, 168, 144)
#  - hsl(30, 28%, 66%)
#  - #C0A890
# NOTE: ALPHA VALUES WILL BE IGNORED
PRIMARY-COLOR: '#C0A890'

#-------------------------------------

# THESE ARE FLASK CONFIGURATION SETTINGS
FLASK:
  HOST: 0.0.0.0
  PORT: '5000'
  SECRET: abcd1234
  DEBUG: false
  TEMPLATES_AUTO_RELOAD: true
  USE_RELOADER: false

#-------------------------------------
# CAN BE ONE OF: 'NO-AUTH', 'FLASK-LOGIN', 'AUTHELIA'
AUTHENTICATION: FLASK-LOGIN

# NEXT, ADD ONE OF THE FOLLOWING TO MATCH

# USERS FOR NO AUTHENTICATION (NO-AUTH)
# THIS WILL STORE THE SETTINGS CHANGES (COMMON FOR EVERYONE)
USERS: {}

# SETTING UP USERS FOR FLASK-LOGIN AUTHENTICATION (FLASK-LOGIN)
USERS:
  user:
    password: pass
  user2:
    password: pass

# USERS FOR AUTHELIA AUTHENTICATION (AUTHELIA)
# THIS WILL BE POPULATED FROM AUTHELIA AUTHENTICATION HEADERS
USERS: {}

# FOR INFORMATION:
# AUTHELIA IS AN AUTHENTICATION MIDDLEWARE USEFUL WHEN USING TRAEFIK FOR ROUTING
# 'WHERE THE ?!?' READS THE AUTHENTICATION HEADERS AUTHELIA PROVIDES ONCE LOGGED
# IN TO KEEP TRACK OF WHO IS LOGGED IN. ACCESS CONTROL IS HANDLED PRIOR TO
# ACCESSING 'WHERE THE ?!?' WHEN USING AUTHELIA.
AUTHELIA-LOGOUT: https://auth.SAMPLE-DOMAIN.org # IF SET, HOMEPAGE WILL HAVE A LOGOUT BUTTON IN AUTHELIA MODE

#-------------------------------------
PRINT_TEMPLATE:

  ADD_DESCRIPTION_TO_LABEL: true # WHEN USING THIS, BE AWARE OF DESCRIPTION LENGTH.
  ADD_LOGO_TO_QR: true # REMOVES THE LOGO IN THE CENTRE OF THE QR CODE.
  COLORED_BACKGROUNDS: true # USE PRIMARY COLOR FOR BACKGROUND OF DESCRIPTION AND ID (DARK GREY IF FALSE)

  # BELOW ARE USED TO LAYOUT THE QR CODE LABELS. THE DEFAULT IS SHOWN
  IDENTIFIER: AVERY L7164 # JUST A NAME FOR THIS LABEL LAYOUT - CAN BE ANYTHING

  PAGE:
    WIDTH: 21cm # A4 PAGE WIDTH
    X_MARGIN: 0.7214cm # L7164 (MEASURED FROM LEFT PAGEEDGE TO FIRST LABEL)
    Y_MARGIN: 0.457cm # L7164 (MEASURED FROM TOP PAGE EDGE TO FIRST LABEL)

  LABELS_PER_PAGE: 12 # USED TO INSERT CORRECT PAGE BREAKS

  LABEL:
    HEIGHT: 7.2cm # L7164 (MEASURED HEIGHT OF THE LABELS)
    WIDTH: 6.353cm # L7164 (MEASURED WIDTH OF THE LABELS)
    X_GUTTER: 0.25cm # L7164 (SPACE BETWEEN THE LABELS HORIZONTALLY)
    Y_GUTTER: 0cm # L7164 (SPACE BETWEEN THE LABELS VERTICALLY)
    X_PADDING: 0.25cm # SPACE TO LEAVE ON SIDES OF LABEL (TOLERANCE FOR INACCURACIES WHEN PRINTING)
    Y_PADDING: 0.1cm # SPACE TO LEAVE ON TOP AND BOTTOM OF LABEL (TOLERANCE FOR INACCURACIES WHEN PRINTING)

  # USE THESE ONCE THE LABEL AND PAGE ARE SETUP TO MAKE SURE THEY FIT ON THE LABELS
  ID_FONT_SIZE: 0.8cm # HEIGHT OF ID STRING FONT
  DESCRIPTION_FONT_SIZE: 0.35cm # HEIGHT OF DESCRIPTION STRING FONT (IF ENABLED)
  QR_HEIGHT: 4.3cm # HEIGHT OF THE QR CODE
```

## What's Next / Future Improvements

The roadmap below is ordered by value-for-effort: quick wins first, big-ticket features last. Effort estimates assume familiarity with the codebase and include cursory testing.

Please propose and discuss ideas [here](https://github.com/danricho/where_the/discussions)! I would welcome any contributions to these with pull requests!

### Phase 1 — Bug fixes & hardening (quick wins)

| #   | Item                                                                                                                                   | Value | Effort   |
| --- | -------------------------------------------------------------------------------------------------------------------------------------- | ----- | -------- |
| 1   | **Harden the edit route** — normalise the ID (`.upper()`) and check it exists before saving, matching the other routes                 | Med   | ~30 min  |
| 2   | **Fix pagination with zero locations** — page count of 0 produces a negative slice                                                     | Low   | ~30 min  |
| 3   | **Proper CSV escaping on export** — use the `csv` module so commas/quotes in fields don't corrupt the file                             | Med   | ~30 min  |
| 4   | **Pin dependency versions & refresh Docker base image** — requirements.txt is unpinned and the image uses EOL Python 3.9 / Alpine 3.14 | Med   | ~1–2 hrs |

### Phase 2 — Security & login polish

| #   | Item                                                                                                                                                                                                  | Value | Effort  |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----- | ------- |
| 5   | **Hashed passwords** ([#12](https://github.com/danricho/where_the/discussions/12)) — store werkzeug password hashes in config.yml instead of plaintext (with migration of existing plaintext entries) | High  | ~2 hrs  |
| 6   | **Redirect to originally requested page after login** ([#5](https://github.com/danricho/where_the/discussions/5)) — existing TODO in main.py                                                          | Med   | ~1 hr   |
| 7   | **"Remember me" on login** ([#5](https://github.com/danricho/where_the/discussions/5))                                                                                                                | Med   | ~30 min |
| 8   | **Escape item names on the edit page** — items are appended to the DOM as raw HTML client-side                                                                                                        | Med   | ~30 min |

### Phase 3 — Storage upgrade

| #   | Item                                                                                                                                                                                                                                                              | Value | Effort   |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----- | -------- |
| 9   | **Move from data.json to TinyDB** ([#3](https://github.com/danricho/where_the/discussions/3)) — pure-Python, single-file, no server; wrap storage behind a small data-access layer, auto-migrate existing data.json on first run, keep the daily-backup behaviour | High  | ~4–6 hrs |

Doing this behind a small storage interface makes the later item-metadata and image features much easier, which is why it sits before them.

### Phase 4 — Features

| #   | Item                                                                                                                                                                                                                         | Value | Effort    |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----- | --------- |
| 10  | **User settings page** ([#12](https://github.com/danricho/where_the/discussions/12)) — currently a placeholder in the menu; expose sort/pagination prefs and password change                                                 | Med   | ~3–4 hrs  |
| 11  | **Dark mode** — CSS groundwork was done back in 2022; add a toggle + user preference                                                                                                                                         | Med   | ~2–4 hrs  |
| 12  | **CSV import** ([#17](https://github.com/danricho/where_the/discussions/17)) — round-trip the existing export, enabling migration from tools like Sortly                                                                     | Med   | ~3–4 hrs  |
| 13  | **Item metadata** ([#11](https://github.com/danricho/where_the/discussions/11)) — quantity, value, purchase date etc. as an optional per-item dict with globally defined tag names; needs schema, edit UI and search changes | High  | ~8–12 hrs |
| 14  | **Images per location** ([#19](https://github.com/danricho/where_the/discussions/19)) — photo of the box contents on the view page; per-location keeps it simple (per-item would be much larger)                             | Med   | ~4–8 hrs  |

### Ongoing / nice-to-have

- More label templates and printing tweaks ([#10](https://github.com/danricho/where_the/discussions/10))
- More code comments for casual contributors ([#7](https://github.com/danricho/where_the/discussions/7))
- Demo screenshot generation ([#16](https://github.com/danricho/where_the/discussions/16))

## Change Log

See [changelog](changelog.md) for a history of changes.
