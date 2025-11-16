terraform {
  required_version = ">= 1.4.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# --------------------------
# Pub/Sub Topic
# --------------------------
resource "google_pubsub_topic" "iot_topic" {
  name = var.topic_id
}

# --------------------------
# Cloud Run Service Account
# --------------------------
resource "google_service_account" "cloudrun_sa" {
  account_id   = "iot-bridge-sa"
  display_name = "Cloud Run SA for IoT Bridge"
}

# --------------------------
# Grant SA publish rights
# --------------------------
resource "google_pubsub_topic_iam_binding" "pub_publisher" {
  topic = google_pubsub_topic.iot_topic.name
  role  = "roles/pubsub.publisher"

  members = [
    "serviceAccount:${google_service_account.cloudrun_sa.email}",
  ]
}

# --------------------------
# Cloud Run service
# --------------------------
resource "google_cloud_run_v2_service" "iot_bridge" {
  name     = "iot-bridge"
  location = var.region

  template {
    service_account = google_service_account.cloudrun_sa.email

    containers {
      image = var.container_image

      env {
        name  = "AUTH_TOKEN"
        value = var.auth_token
      }

      env {
        name  = "TOPIC_ID"
        value = var.topic_id
      }

      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
    }
  }

  traffic {
    percent        = 100
    type           = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}


