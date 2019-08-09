# wpb-bot

## Development

### praw.ini file

You'll need a `praw.ini` file in the root of this repo. Copy over the `praw.ini.example` file and fill in the details. Use your own username and password, and get the client_id and client_secret from the Reddit application

### the virtualenv way

The following instructions should be run from the repo root

#### Create the virtualenv (only have to do this once)

`python3 -m venv env`

#### Activate the virtualenv (once per terminal window)

`source env/bin/activate`

#### Install dependencies

`pip install -r requirements.txt`

#### Run the bot

To run the bot _without_ making actual replies:

`python src/main.py`

To run the bot and make actual replies:

`python src/main.py --send-replies` <--- be careful if you do this, you could end up spamming reddit

or set the env var `SEND_REPLIES=true`

By default, the bot will track which files it replied to. To skip tracking,

`python src/main.py --skip-track`

or set the env var `TRACK_REPLIES=false`

To change which file is used to track posts replied to

`python src/main.py --replied-to-path [my_new_file.txt]`

or set the env var `REPLIED_TO_PATH=[my_new_file.txt]`

To update the number of posts considered for reply, change `--limit`

`python src/main.py --limit=20`

or update the env var `LIMIT`

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

You'll need to get the key from @joegoldbeck. You should only need it if you're actively managing the dev deployment

#### All necessary Terraform modules

`terraform init`

### Update deployment

To update the deployment, simply run

`terraform apply`