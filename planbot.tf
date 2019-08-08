variable "region" {
  type = string
  default = "us-central"
}

variable "project_id" {
  type = string
  default = "wpb-dev"
}

variable "credentials_file" {
  type = string
  default = "~/.gcloud/wpb-dev-terraform-key.json"
}

variable "function_name" {
  type = string
  default = "run-plan-bot-3"
}

variable "function_storage_bucket" {
  type = string
  default = "wpb-cloud-function-dev"
}

variable "function_storage_bucket_object" {
  type = string
  default = "plan_bot.zip"
}

provider "google" {
  credentials = file(var.credentials_file)
  project = var.project_id
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
  schedule = "* * * * *"

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

# create the storage bucket
resource "google_storage_bucket" "plan_bot_function_storage" {
  name = var.function_storage_bucket
}


# place the zip-ed code in the bucket
resource "google_storage_bucket_object" "plan_bot_zip" {
  name = var.function_storage_bucket_object
  bucket = google_storage_bucket.plan_bot_function_storage.name
  source = "${path.root}/dist/plan_bot.zip"
  depends_on = [
    data.archive_file.plan_bot_zip
  ]

}
output "blag" {
  value = google_pubsub_topic.run_plan_bot.id
}
resource "google_cloudfunctions_function" "run_plan_bot" {
  name = var.function_name
  description = "Run the plan bot"
  runtime = "python37"

  available_memory_mb = 256

  event_trigger {
    event_type = "providers/cloud.pubsub/eventTypes/topic.publish"
    resource = google_pubsub_topic.run_plan_bot.name
  }
  source_archive_bucket = google_storage_bucket.plan_bot_function_storage.name
  source_archive_object = google_storage_bucket_object.plan_bot_zip.name
  timeout = 60
  entry_point = "run_plan_bot"
  max_instances = 1
  labels = {
    // Here so that the deploy trick above keeps working
    deployment-tool = "cli-gcloud"
  }

  environment_variables = {
  }
}

resource "null_resource" "update_cloud_function" {
  depends_on = [
    google_cloudfunctions_function.run_plan_bot,
    google_storage_bucket_object.plan_bot_zip
  ]
  triggers = {
    uploaded_function_code = google_storage_bucket_object.plan_bot_zip.crc32c
  }

  provisioner "local-exec" {
    command = "GOOGLE_APPLICATION_CREDENTIALS=${var.credentials_file} gcloud functions deploy ${var.function_name} --source gs://${google_storage_bucket.plan_bot_function_storage.name}/${google_storage_bucket_object.plan_bot_zip.name}"
  }
}