variable "region" {
  type = string
  default = "us-central"
}

variable "send_replies" {
  type = bool
  default = true
}

locals {
  environment = terraform.workspace == "default" ? "dev" : terraform.workspace
}

locals {
  project_id = "wpb-${local.environment}"
  function_storage_bucket = "wpb-cloud-function-${local.environment}"
  credentials_file = "~/.gcloud/wpb-${local.environment}-terraform-key.json"
  function_name = "run-plan-bot"
  function_storage_bucket_object = "plan_bot.zip"
  limit = "20"
  schedule = "*/2 * * * *" // every 2 minutes
  timeout = 160 // longer than the schedule interval
  time_in_loop = 100 // shorter than the schedule interval
}

provider "google" {
  credentials = file(local.credentials_file)
  project = local.project_id
  region = "us-central1"
}

terraform {
  backend "gcs" {
    bucket = "wpb-dev-terraform-state"
    prefix = "terraform/state"
    credentials = "~/.gcloud/wpb-dev-terraform-key.json"
  }
}

resource "google_pubsub_topic" "run_plan_bot" {
  name = "run-plan-bot"
}

resource "google_cloud_scheduler_job" "run_plan_bot" {
  name = "run-plan-bot"
  description = "run the plan bot cloud function"
  schedule = local.schedule

  pubsub_target {
    topic_name = google_pubsub_topic.run_plan_bot.id
    data = base64encode("go planbot go!")
  }
}


# zip up our source code
data "archive_file" "plan_bot_zip" {
  type = "zip"
  source_dir = "${path.root}/src/"
  output_path = "${path.root}/dist/plan_bot.zip"
}

# create the storage bucket for function storage
resource "google_storage_bucket" "plan_bot_function_storage" {
  name = local.function_storage_bucket
}


# place the zip-ed code in the bucket
resource "google_storage_bucket_object" "plan_bot_zip" {
  name = local.function_storage_bucket_object
  bucket = google_storage_bucket.plan_bot_function_storage.name
  source = "${path.root}/dist/plan_bot.zip"
  depends_on = [
    data.archive_file.plan_bot_zip
  ]
}

resource "google_cloudfunctions_function" "run_plan_bot" {
  name = local.function_name
  description = "run the plan bot"
  runtime = "python311"

  available_memory_mb = 1024

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource = google_pubsub_topic.run_plan_bot.name
  }

  source_archive_bucket = google_storage_bucket.plan_bot_function_storage.name
  source_archive_object = google_storage_bucket_object.plan_bot_zip.name
  timeout = local.timeout
  entry_point = "run_plan_bot_event_handler"
  max_instances = 1
  labels = {
    // here so that the deploy trick above keeps working
    deployment-tool = "cli-gcloud"
  }

  environment_variables = {
    SEND_REPLIES = var.send_replies
    PRAW_SITE = local.environment
    LIMIT = local.limit
    TIME_IN_LOOP = local.time_in_loop
  }
}

# redeploy cloud function if code has changed
resource "null_resource" "update_cloud_function" {
  depends_on = [
    google_cloudfunctions_function.run_plan_bot,
    google_storage_bucket_object.plan_bot_zip
  ]
  triggers = {
    uploaded_function_code = google_storage_bucket_object.plan_bot_zip.crc32c
  }

  provisioner "local-exec" {
    command = "google_application_credentials=${local.credentials_file} gcloud functions deploy ${local.function_name} --source gs://${google_storage_bucket.plan_bot_function_storage.name}/${google_storage_bucket_object.plan_bot_zip.name} --project ${local.project_id}"
  }
}

output "project_id" {
  value = local.project_id
}

output "function_storage_bucket" {
  value = local.function_storage_bucket
}

output "praw_site" {
  value = google_cloudfunctions_function.run_plan_bot.environment_variables.PRAW_SITE
}