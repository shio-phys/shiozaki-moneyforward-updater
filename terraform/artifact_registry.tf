resource "google_artifact_registry_repository" "app" {
  repository_id = local.app_name
  location      = var.region
  format        = "DOCKER"
  description   = "moneyforward-updater container images"

  depends_on = [google_project_service.apis]
}
