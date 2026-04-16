resource "google_secret_manager_secret" "passkey_credentials" {
  secret_id = "${local.app_name}-passkey-credentials"

  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}
