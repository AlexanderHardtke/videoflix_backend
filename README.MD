# Videoflix Backend

## Requirements

- Videoflix-Frontend must be installed (`https://github.com/AlexanderHardtke/videoflix_frontend`)
- Docker must be installed [Docker](https://docs.docker.com/compose/install/)
- git must be installed [git](https://git-scm.com/downloads)

## Installation

IMPORTANT NOTE: Use the .env-template to generate an .env file in the same folder, follow the instructions in the.env-template.
Then run `docker-compose up --build -d`

# Upload Videos

To upload videos go to your `BACKEND_URL/api/upload` and login with the superuser account, from there you can upload the videos.
Or alternatively you can  go to `BACKEND_URL/admin` and do the same in the admin panel of Django.

# Videoflix Backend

## Vorraussetzungen

- Videoflix-Frontend muss installiert sein (`https://github.com/AlexanderHardtke/videoflix_frontend`)
- Docker muss installiert sein [Docker](https://docs.docker.com/compose/install/)
- git muss installiert sein [git](https://git-scm.com/downloads)

# Installation

WICHTIGER HINWEIS: Benutze die .env-template, um deine eigene .env-Datei zu erstellen. Lege sie im gleichen Verzeichnis ab und befolge die Anweisungen in der Vorlage.
Dann führe `docker-compose up --build -d`

# Videos hochladen

Um Videos hochzuladen, rufe auf: `BACKEND_URL/api/upload`
Melde dich mit deinem Superuser-Account an, mit diesem kannst du Videos direkt hochladen.
Alternativ kannst du auch das Django-Admin-Panel verwenden unter: `BACKEND_URL/admin`
