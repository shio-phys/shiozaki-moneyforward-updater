resource "google_cloud_run_v2_job" "app" {
  name                = local.app_name
  location            = var.region
  deletion_protection = false

  template {
    template {
      service_account = google_service_account.runner.email
      timeout         = "1800s"
      max_retries     = 0

      containers {
        image = local.image_full

        resources {
          limits = {
            cpu    = "1"
            memory = "2Gi"
          }
        }

        env {
          name = "PASSKEY_CREDENTIALS"
          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.passkey_credentials.secret_id
              version = "latest"
            }
          }
        }
      }
    }
  }

  depends_on = [
    google_artifact_registry_repository.app,
    google_secret_manager_secret.passkey_credentials,
  ]
}
