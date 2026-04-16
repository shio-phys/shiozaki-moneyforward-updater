locals {
  app_name   = "moneyforward-updater"
  image_name = "${var.region}-docker.pkg.dev/${var.project_id}/${local.app_name}/${local.app_name}"
  image_full = "${local.image_name}:${var.image_tag}"
}
