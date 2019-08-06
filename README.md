# wpb-bot

## Development

### pram.ini file

You'll need a `pram.ini` file in the root of this repo. Copy over the `pram.ini.example` file and fill in the details. Use your own username and password, and get the client_id and client_secret from the Reddit application

### the virtualenv way

The following instructions should be run from the repo root

#### Create the virtualenv (only have to do this once)

`python3 -m venv env`

#### Activate the virtualenv (once per terminal window)

`source env/bin/activate`

#### Install dependencies

`pip install -r requirements.txt`

#### Run the bot

`python src/main.py`
