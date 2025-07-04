# Videoflix Backend

This project functions only in combination with my Videoflix-Frontend project which you can find here (`https://github.com/AlexanderHardtke/videoflix_frontend`)

# Installation

IMPORTANT NOTE: Use the .env-template to generate an .env file in the same folder, follow the instructions in the.env-template.

## Developement server

Change line 22 in docker-compose.yml to `python manage.py runserver 0.0.0.0:8000`
Go the the src folder and activate `"env/scripts/activate"`, after this you need to have Docker Desktop installed and run `docker compose up --build` in the console.

# Build on real server

Install docker on your server with `sudo apt update`, `sudo apt install docker.io docker-compose-plugin` and `sudo systemctl enable --now docker`
Go to your projects folder and clone this project with `git clone https://github.com/AlexanderHardtke/videoflix_backend.git`.
Go to videoflix_backend and write your .env here (or copy it from your local PC)
Also in the videoflix_backend folder `docker-compose up --build -d`

# Upload Videos

To upload videos go to your `BACKEND_URL/api/upload` and login with the superuser account, from there you can upload the videos.
Or alternatively you can  go to `BACKEND_URL/admin` and do the same in the admin panel of Django.

# Videoflix Backend

Dieses Projekt funktioniert nur in Kombination mit meinem Videoflix-Frontend (`https://github.com/AlexanderHardtke/videoflix_frontend`).

# Installation

WICHTIGER HINWEIS: Benutze die .env-template, um deine eigene .env-Datei zu erstellen. Lege sie im gleichen Verzeichnis ab und befolge die Anweisungen in der Vorlage.

## Entwicklungsserver

Ändere Zeile 22 in der docker-compose.yml auf: `python manage.py runserver 0.0.0.0:8000`
Wechsle in den src-Ordner und aktiviere dein virtuelles Environment: `"env/scripts/activate"`
Stelle sicher, dass Docker Desktop installiert ist.
Starte den Container mit `docker-compose up --build -d`

# Deployment auf einem echten Server

Installiere Docker auf deinem Server mit `sudo apt update`, `sudo apt install docker.io docker-compose-plugin` und `sudo systemctl enable --now docker`
Wechsle in deinen Projektordner und klone das Repository mit  `git clone https://github.com/AlexanderHardtke/videoflix_backend.git`.
Gehe ins Verzeichnis videoflix_backend und lege deine .env an (oder kopiere sie von deinem lokalen Rechner).
Baue und starte die Container im Hintergrund mit `docker-compose up --build -d`

# Videos hochladen

Um Videos hochzuladen, rufe auf: `BACKEND_URL/api/upload`
Melde dich mit deinem Superuser-Account an, mit diesem kannst du Videos direkt hochladen.
Alternativ kannst du auch das Django-Admin-Panel verwenden unter: `BACKEND_URL/admin`
