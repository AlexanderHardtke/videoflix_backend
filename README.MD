# Videoflix Backend

This project functions only in combination with my Videoflix-Frontend project which you can find here (`https://github.com/AlexanderHardtke/videoflix_frontend`)

# Installation

IMPORTANT NOTE: Use the .env-template to generate an .env file in the same folder, follow the instructions in the.env-template.

## Developement server

Go the the src folder and activate `"env/script/activate"`, after this you need to have Docker Desktop installed and run `docker compose up --build` in the console.

# Build on real server

Install docker on your server with `sudo apt update`, `sudo apt install docker.io docker-compose-plugin` and `sudo systemctl enable --now docker`
Go to your projects folder and clone this project with `git clone`.
Go to videoflix_backend and write your .env here (or copy it from your local PC)
Also in the videoflix_backend folder `docker-compose up --build -d`