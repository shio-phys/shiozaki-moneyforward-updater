resource "google_service_account" "runner" {
  account_id   = "${local.app_name}-runner"
  display_name = "MoneyForward Updater - Cloud Run Job Runner"

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret_iam_member" "runner_secret_access" {
  secret_id = google_secret_manager_secret.passkey_credentials.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.runner.email}"
}

resource "google_service_account" "scheduler" {
  account_id   = "${local.app_name}-scheduler"
  display_name = "MoneyForward Updater - Cloud Scheduler"

  depends_on = [google_project_service.apis]
}

resource "google_project_iam_member" "scheduler_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.scheduler.email}"
}
