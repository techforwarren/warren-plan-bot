Warren Plan Bot
==================

[![Build Status](https://travis-ci.org/techforwarren/warren-plan-bot.svg?branch=master)](https://travis-ci.org/techforwarren/warren-plan-bot)

Reddit bot to help you learn about Senator Elizabeth Warren's plans

Currently active on the following subreddits
- [/r/ElizabethWarren](https://www.reddit.com/r/ElizabethWarren/)

The bot can be summoned by making a comment of the form `!WarrenPlanBot plan_topic_goes_here. any_other_questions_here`

## Development

### praw.ini file

You'll need a `praw.ini` file in the '/src' folder of this repo. Copy over the `praw.ini.example` file and fill in the details. You'll need to get the client_id and client_secret from the owners of the project.

In order to test in development, you will need to [create your own reddit dev app](https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example#first-steps). Then use the credentials to populate your `praw.ini` file for dev.

Also please see how to [run the app in dev safely](#run-the-bot)

### .env file

You'll need a `.env` file in the top-level this repo to test the LLM responses.

Copy over the `.env.example` file and fill in the details. You'll need an OpenAI API key.

### Option 1: The Docker way (recommended)

There are many ways to set this bot up for local development. A super simple way is to make a docker environment

#### Updating dependencies

When you update dependencies, you'll need to rebuild the container

`docker compose build`

#### Run commands from within the docker container

This will allow you to run all the commands below 

`docker compose run -it planbot`

### Option 2: the virtualenv way

The following instructions should be run from the repo root, and require Python 3.11

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

### Useful commands

#### Run tests

`pytest`

#### Format code

`./scripts/autoformat.sh`

#### Add a new plan

First, add the plan to `plans.json`, then

##### Download plans

`python scripts/download_plans.py`

##### Extract plan text

`python scripts/parse_plans.py`

##### Regenerate models

`./scripts/update_models.sh`

#### Test out strategies for matching

`python scripts/score_strategies.py`

This tests matching strategies against labeled posts in `labeled_posts.json`

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

#### Add the latest trigger posts from subreddit to labeled_posts.json

This requires valid praw credentials

`python scripts/download_recent_trigger_posts.py --praw-site prod`

will pull down up to 100 recent posts where someone has triggered the bot.

This can be used to help update the `labeled_posts.json` file with real user queries. You'll still need to determine the desired matches by hand.

#### Test out LLM responses

`python scripts/try_llm.py '[TEXT OF POST]'`

This can be used to test the behavior of the LLM and tweak the prompts.

for ex

`python scripts/try_llm.py '!warrenplanbot child care. how many kids can we help?'`

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

### Migrations

1) Updating plan ids

To run a dry-run on dev
`GOOGLE_APPLICATION_CREDENTIALS=~/.gcloud/***** python migrations/plans_ids_1.py --project wpb-dev --dry-run`

To run a dry-run on dev
`GOOGLE_APPLICATION_CREDENTIALS=~/.gcloud/***** python migrations/plans_ids_1.py --project wpb-prod --dry-run`

To run the migration, simply remove `--dry-run`  

### Pushshift Samples URL

https://api.pushshift.io/reddit/search/?q=elizabeth%20warren%20plan&dataviz=false&aggs=false&subreddit=elizabethwarren&searchtype=posts,comments&search=true&start=1565112951&end=1565717751&size=100

## Contributing

A good place to start is to join our Slack channel #warren-plan-bot and introduce yourself!

This README should also contain all the info you should need to know to get up and running, and otherwise operate the bot locally. 
If there's any info you find missing or incorrect, please make a PR to update it :D

If you're looking for good issues to start tackling as you get familiar with the repo, 
look for those tagged with [help wanted](https://github.com/techforwarren/warren-plan-bot/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22) and/or [good first issue](https://github.com/techforwarren/warren-plan-bot/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)

If you want to start with one of those issues, you're welcome to go ahead and just get started, but if you'd like further clarity, 
want to bite off something larger, or have new ideas for contribution, start a conversation with the projects leads 
@joegoldbeck and @Hucxley in the project slack channel!

### Development workflow

1. Create a branch off of `master` using the naming convention `[your_initials]/[topic]-[issue_number_if_applicable]` (e.g. `jg/create-readme-1`). 
(You'll first need to [fork the repo](https://help.github.com/en/articles/fork-a-repo) entirely if you're not an existing contributor) 

1. Follow the [development instructions above](#development) to set up your working environment, if you haven't already.

1. You can test out any code changes you've made by [running the tests](#run-tests) or [running the bot in safe mode](#safely-and-statelessly)

1. If you've added code that should be tested, add tests.

1. If you've changed or created any new scripts or major functionality, remember to update the documentation in this file.

1. Submit a [pull request](https://github.com/techforwarren/warren-plan-bot/compare)

### Code style

All code that's submitted for a PR should be autoformatted using

- `black`
- `isort`

You can set up your editor however you'd like, or you can just run `./scripts/autoformat.sh`