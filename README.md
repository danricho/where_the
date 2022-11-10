<div align="center">

<img src="static/logo_md.png"/>

# Where The ?!?

A simple Python Flask web application which helps keep track of your stored items.

<a href="https://danricho.com"><img src="https://img.shields.io/static/v1?label=built by&message=danricho&style=flat&color=C0A890&labelColor=a0a0a0" alt="Built with Python3"></a> <a href="https://en.wikipedia.org/wiki/2022"><img src="https://img.shields.io/static/v1?label=built in&message=2022&style=flat&color=C0A890&labelColor=a0a0a0" alt="Built in 2022"></a> <a href="https://choosealicense.com/licenses/gpl-3.0/"><img src="https://img.shields.io/static/v1?label=released under&message=GNU GPLv3&style=flat&color=C0A890&labelColor=a0a0a0" alt="Released under GNU GPLv3"></a>
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/built using-Python 3-C0A890?labelColor=a0a0a0&style=flat" alt="Built using Python3"></a> <a href="https://flask.palletsprojects.com/"><img src="https://img.shields.io/badge/built using-Flask-C0A890?labelColor=a0a0a0&style=flat" alt="Built using Flask"></a> <a href="https://flask-login.readthedocs.io/en/latest/"><img src="https://img.shields.io/badge/built using-Flask Login-C0A890?labelColor=a0a0a0&style=flat" alt="Built using Flask Login"></a> <a href="https://marcoagner.github.io/Flask-QRcode/"><img src="https://img.shields.io/badge/built using-Flask QRCode-C0A890?labelColor=a0a0a0&style=flat" alt="Built using Flask QRCode"></a> <a href="https://github.com/mebjas/html5-qrcode"><img src="https://img.shields.io/badge/built using-HTML5 QRCode-C0A890?labelColor=a0a0a0&style=flat" alt="Built using HTML5 QRCode"></a> <a href="https://jquery.com/"><img src="https://img.shields.io/badge/built using-JQuery 3.5.1-C0A890?labelColor=a0a0a0&style=flat" alt="Built using JQuery 3.5.1"></a> <a href="https://jenil.github.io/chota/"><img src="https://img.shields.io/badge/built using-Chota CSS-C0A890?labelColor=a0a0a0&style=flat" alt="Built using Chota CSS"></a>

</div>

## Features

- Responsive web-based user interface
- Easy, simple location editing
- Search by stored item
- Sort locations by different attributes:
   - description
   - location (eg. Office, Garage, etc)
   - type (eg. Shelf, Plastic Box, etc)
   - recently edited
   - unique ID
   - how used (% full)
- QR codes to assist location tracking based on unique ID
- Print QR code labels from website
- Simple JSON storage (pros & cons)

## Screenshots - Out of date already!

**Does anyone know a quick way to generate this type of demo image?**

See [this page](static/screenshots/screenshots.md) for example screenshots.

## Installation - Native Python

*These steps describe how I set it up. I use a linux terminal so under Windows there may be minor step inaccuracies.*

1.  Clone repo to a local directory.
    eg: `git clone https://github.com/danricho/where_the.git where_the`

1.  Create a Python Virtual Environment (venv).
    eg: `python3 -m venv venv`

1.  Install dependencies via pip into your venv.
    eg: `venv/bin/pip install -r requirements.txt` or activate venv then `pip install -r requirements.txt` 

1.  Create `config.yml` and update according it to your setup - see the [Configuration section](#configuration-configyml).

1.  Run `main.py` in your venv.
    eg: `venv/bin/python main.py` or activate venv then `python main.py` 

## Installation - Docker Compose

*Running in Docker is a quick way to get this to run as a service (launches on boot etc).*

1. Clone repo to a local directory.
   eg: `git clone https://github.com/danricho/where_the.git where_the`

1. Create `config.yml` and update according to the [Configuration section](#configuration-configyml). This file is mounted within the docker image but saved here outside it (to keep data between docker sessions)

1. Create `data.json` and set the content to `{}`. This file is mounted within the docker image but saved here outside it (to keep data between docker sessions)

1. Run the docker container using the command `docker-compose up -d`. 

1. To troubleshoot the container it may help to see it's logs: `docker logs where_the`

## Updating to the latest GitHub version

To update, all that shoule be needed is to run the command `git pull` in your Where The ?!? directory.

If you get a message about local file changes which would be overwritten by merge, this means you have modified one of the tracked files. The config and data files (as made during installation) are not the files git is talking about. 

The command `git diff` will tell you what is different about the files. Running `git reset --hard HEAD` will reset the uncommited file changes, but **NOTE THAT** you may lose work if you do this. Only do this if you understand what you are doing. And once your Repo is clean, the `git pull` whould work.

There are many resources available online to learn more about Git operations.

## Configuration (config.yml)

```yaml
# DO NOT ADD COMMENTS YOU WANT KEPT TO THIS YML AS IT IS REWRITTEN BY THE APP AND COMMENTS ARE LOST.

SITE: 
  BASE_URL: http://localhost # THIS IS YOUR DOMAIN OR START OF YOUR URL - USED IN QR CODE
  PATH_PREFIX: / # THIS IS USEFUL IF YOU WANT A PREFIX ON THE URL PATH - USED IN QR CODE AND FLASK

# THE MAIN COLOR. 
# THE DEFAULT #C0A890 IS BASED ON A CARBOARD BOX COLOR :)
# CAN BE ANY VALID CSS COLOR STRING - EG: rgb(128,128,128)
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

I plan to start using it more to identify the holes I haven't found yet!  
I do have a few ideas that I'd like to add while maintaining the current simplicity as much as possible.  

Please propose and discuss ideas [here](https://github.com/danricho/where_the/discussions)!

My ideas so far (most would be choosen via a `config.yml` option):​
- Add `Dark Mode` to Chota CSS, which is very easy (as per the Chota webpage) and a toggle for it in the fixed header
- Add additional storage options other than raw JSON file  - [discussion](https://github.com/danricho/where_the/discussions/3)
- UI improvements - [discussion](https://github.com/danricho/where_the/discussions/9)
- Code improvements - [discussion](https://github.com/danricho/where_the/discussions/7)

I welcome contributions to these with Pull requests!

## Change Log

See [changelog](changelog.md) for a history of changes.
