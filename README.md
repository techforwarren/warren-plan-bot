# wpb-bot

## Development

### praw.ini file

You'll need a `praw.ini` file in the '/src' folder of this repo. Copy over the `praw.ini.example` file and fill in the details. You'll need to get the client_id and client_secret from the Reddit application

### the virtualenv way

There are many ways to set this bot up for local development. A super simple way is to make a virtual environment

The following instructions should be run from the repo root

#### Create the virtualenv (only have to do this once)

`python3 -m venv env`

#### Activate the virtualenv (once per terminal window)

`source env/bin/activate`

#### Install dependencies

`pip install -r requirements-dev.txt`

### Other requirements

#### Java (if you're running the local Firestore emulator)

`brew cask install java` on Mac

or visit https://www.java.com/download/

### Format code

Sort imports

`isort src/*.py`

### Run the bot

#### Safely and Statelessly

- Without making actual replies
- Without checking a posts_replied_to list

`python src/main.py --skip-tracking`

#### Safely, using state from the repo

- Without making actual replies
- Using the posts_replied_to.txt in the repo

`python src/main.py --replied-to-path posts_replied_to.txt`

#### Safely, using state from the local firestore emulator 

##### Start local firestore

(You'll need java if you don't have it: `brew cask install java`)

`gcloud beta emulators firestore start --project wpb-dev --host-port localhost:8480`

##### Start the bot
and in another terminal

--FIXME-- This ideally shouldn't need credentials...
`GOOGLE_APPLICATION_CREDENTIALS=~/.gcloud/wpb-dev-terraform-key.json FIRESTORE_EMULATOR_HOST=localhost:8480 python src/main.py --skip-tracking --simulate-replies`

#### Simulate state

- Without making actual replies
- While updating the posts_replied_to list in the repo

`python src/main.py --replied-to-path posts_replied_to.txt --simulate-replies`

#### Live, using shared tracking state

- Make actual replies
- Using the shared tracking file on google cloud storage

`GOOGLE_APPLICATION_CREDENTIALS=~/.gcloud/wpb-dev-terraform-key.json python src/main.py --send-replies`

You'll need to get this account credentials from @joegoldbeck, and put it at the appropriate location

## Bot options

`python src/main.py --help` will bring up a list of command line options and their environment variable equivalents

```
Usage: main.py [OPTIONS]

  Run a single pass of Warren Plan Bot

  - Check posts store for posts replied to (If tracking is on)
  - Search for any new comments and submissions not on that list
  - Reply to any unreplied matching comments (If replies are on)
  - Update posts store (If replies and tracking is on)

Options:
  --send-replies / --skip-send  whether to send replies  [env var: SEND_REPLIES; default: False]
  --skip-tracking               whether to check whether replies have already been posted  [default: False]
  --simulate-replies            pretend to make replies, including updating state  [default: False]
  --limit INTEGER               number of posts to return  [env var: LIMIT; default: 10]
  --praw-site [dev|prod]        section of praw file to use for reddit module configuration  [env var: PRAW_SITE; default: dev]
  --help                        Show this message and exit.
```

## Managing the Deployment

### Requirements

#### Terraform

##### Mac (with homebrew)

`brew install terraform`

##### Otherwise

Download the binary at https://www.terraform.io/downloads.html

Make sure the `terraform` binary is in your PATH

#### Service Account Key

Add the key for the Terraform service account to

`~/.gcloud/wpb-dev-terraform-key.json`

You'll need to get this key from @joegoldbeck

#### All necessary Terraform modules

`terraform init`

### Update deployment

To update the deployment, simply run

`terraform apply`

This will deploy any new infrastructure, and if anything in the `/src` folder is updated, 
will upload the that folder as a .zip archive and deploy a new version of the cloud function pointing to that archive

### Turn off the bot

To prevent the bot from running every minute, the simplest thing to do is to remove the Cloud Scheduler job

`terraform destroy -target google_cloud_scheduler_job.run_plan_bot`