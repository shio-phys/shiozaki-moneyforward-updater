resource "google_cloud_scheduler_job" "app" {
  name      = "${local.app_name}-daily"
  region    = var.region
  schedule  = var.schedule
  time_zone = "Asia/Tokyo"

  http_target {
    http_method = "POST"
    uri         = "https://run.googleapis.com/v2/projects/${var.project_id}/locations/${var.region}/jobs/${local.app_name}:run"

    oauth_token {
      service_account_email = google_service_account.scheduler.email
    }
  }

  depends_on = [google_cloud_run_v2_job.app]
}
