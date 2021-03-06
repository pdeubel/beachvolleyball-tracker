# Mobile Web App for Sports Players and Their Games

This is a simple web app to register, for example beachvolleyball players, and track which games they have won to track
the best player of the season.
Players get a QR code assigned, which is used in a QR code reader to start a game. All scanned players are then selected
to be either in Team 1 or Team 2. After that, the game is started and played in real life. When the game is over,
the result is entered into the web app and the winning players get points assigned.
After the season the 'Master of Desaster' (the overall winner) can be seen!

# Installation

## Setup

### Local Setup

- Create a virtual environment with Python 3 and activate it
- Install the packages with `pip install -r requirements.txt`
- TODO: Setup database
- TODO: Explain E-mail whitelist

### Deployment Setup

- TODO: Heroku setup instructions

#### HTTPS certificate

Generate a certificate by running `openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365`,
and pressing enter for everything (since we use it for development only the settings are irrelevant). Now you
only have to confirm once in the browser that you trust this self-signed certificate, when opening the application
in the browser.

## Environment Variables

The following environment variables must be defined, where the application is run:

```shell
export FLASK_APP=mod_beach
# Or set to development for local debugging (disables geolocation check)
export FLASK_ENV=production
# Must be set and kept private!
# See https://flask.palletsprojects.com/en/2.1.x/tutorial/deploy/?highlight=secret%20key#configure-the-secret-key
export SECRET_KEY=
# URL to the mail server or use localhost for a local one
export MAIL_SERVER=
# Port could also be chosen differently, though keep in mind that I set MAIL_USE_TLS to True
export MAIL_PORT=587
# Username for the mail account from which the PIN code emails shall be sent
export MAIL_USERNAME=
# Password for the mail account
export MAIL_PASSWORD=
# E-mail address in the form 'user@domain.com'. I think it does not have to match to the chosen user, but this is what
# the user will see as the sender
export MAIL_SENDER_ADDRESS=  

# If a game lasts longer (in hours) than this value (i.e. no result has been entered), then it is deleted        
export MAX_GAME_AGE_HOURS=3.5
# Specify the minimum amount of players needed to start a game. The value must be greater than 0
export MINIMUM_PLAYERS_PER_GAME=2
```

## Starting the server

### Local Start

- Run `python mod_beach.py --debug -h IP`
    - This starts the app in debug mode, and allows connection to the specified IP
    - If you want to test this in your local network for example, set IP to your local network IP (e.g. "192.168.0.20")
    - You can get your local ip by running 'ip -a' on a modern Linux OS

### Deployment

- TODO: Heroku install instructions