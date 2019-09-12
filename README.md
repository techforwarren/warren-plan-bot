wpb-bot
==================

[![Build Status](https://travis-ci.com/joegoldbeck/wpb-bot.svg?branch=master)](https://travis-ci.com/joegoldbeck/wpb-bot)


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

#### Add src folder to your Python path

There are several ways to do this, one way is to extend your env/bin/activate file by running

`echo -e "\nexport PYTHONPATH=\$PYTHONPATH:$(pwd)/src" >> env/bin/activate`


#### Other requirements

##### Gcloud

`brew cask install google-cloud-sdk` on Mac

or visit https://cloud.google.com/sdk/docs/quickstarts

##### Java (if you're running the local Firestore emulator)

`brew cask install java` on Mac

or visit https://www.java.com/download/

### The Docker way

#### Start the container

`docker-compose up -d`

#### Updating dependencies

When you update dependencies, you'll need to rebuild the container

`docker-compose build`

and then start the new container

`docker-compose down && docker-compose up -d`

#### Run commands from within the docker container

This will allow you to run all the commands below 

`docker exec -it planbot bash`

### Run tests

`pytest`

### Format code

`./scripts/autoformat.sh`

### Preprocess plans (repeat every time a new plan is added)

#### Download plans

`python scripts/download_plans.py`

#### Extract plan text

`python scripts/parse_plans.py`

#### Regenerate models

`./scripts/update_models.sh`

### Test strategies for matching

`python scripts/score_strategies.py`

We can matching strategies against labeled posts in `labeled_posts.json`

Posts in that file have the form

```json
  {
    "text": "TEXT OF POST",
    "source": "WHERE WE GOT THIS POST FROM i.e. /r/warren, jg (joe goldbeck), sh (shane ham), ...",
    "match": "ID_OF_PLAN_WHICH_THIS_TEXT_SHOULD_MATCH",
    "alternate_matches": ["ID_OF_PLAN_WHICH_WOULD_ALSO_BE_SOMEWHAT_ACCEPTABLE_MATCHES", "..."]
  }
```

Strategies are defined as static methods of the Strategy class in `matching.py`


### Run the bot

#### Safely and Statelessly

- Without making actual replies
- Without checking a posts_replied_to list

`python src/main.py --skip-tracking`

#### Safely, using state from the local Firestore emulator 

##### Start local Firestore

`gcloud beta emulators firestore start --project wpb-dev --host-port localhost:8480`

##### Run the bot

- Without making actual replies
- While updating the local emulated posts database

`GOOGLE_APPLICATION_CREDENTIALS=~/.gcloud/wpb-dev-terraform-key.json FIRESTORE_EMULATOR_HOST=localhost:8480 python src/main.py --simulate-replies`

Note: this method doesn't yet work in Docker, since that container doesn't have credentials (even fake ones)

#### (Unsafe) Live, using shared tracking state

- Make actual replies
- Using the shared posts database in Firestore

(Unsafe) `GOOGLE_APPLICATION_CREDENTIALS=~/.gcloud/wpb-dev-terraform-key.json python src/main.py --send-replies`

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
  --project TEXT                gcp project where firestore db lives  [env var: GCP_PROJECT; default: wpb-dev]
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

##### And for prod

You'll also need to key for the Terraform prod service account at

`~/.gcloud/wpb-prod-terraform-key.json`

#### All necessary Terraform modules

`terraform init`

### To switch between deployments

#### Dev deployment

`terraform workspace select default`

#### Prod deployment

`terraform workspace select prod`

### Update deployment

To update the deployment, simply run

`terraform apply`

This will deploy any new infrastructure, and if anything in the `/src` folder is updated, 
will upload the that folder as a .zip archive and deploy a new version of the cloud function pointing to that archive

### Turn off the bot

To prevent the bot from running every minute, the simplest thing to do is to remove the Cloud Scheduler job

`terraform destroy -target google_cloud_scheduler_job.run_plan_bot`

Or you can do it via the UI: [dev](https://console.cloud.google.com/cloudscheduler?project=wpb-dev) [prod](https://console.cloud.google.com/cloudscheduler?project=wpb-prod)


### Pushshift Samples URL

https://api.pushshift.io/reddit/search/?q=elizabeth%20warren%20plan&dataviz=false&aggs=false&subreddit=elizabethwarren&searchtype=posts,comments&search=true&start=1565112951&end=1565717751&size=100
