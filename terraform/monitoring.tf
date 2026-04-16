resource "google_monitoring_notification_channel" "email" {
  display_name = "${local.app_name} alert email"
  type         = "email"

  labels = {
    email_address = "shio.phys@gmail.com"
  }

  depends_on = [google_project_service.apis]
}

resource "google_logging_metric" "job_failed" {
  name   = "${local.app_name}-job-failed"
  filter = "resource.type=\"cloud_run_job\" AND resource.labels.job_name=\"${local.app_name}\" AND textPayload=~\"Container called exit\\([^0]\""

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
  }
}

resource "google_monitoring_alert_policy" "job_failed" {
  display_name = "${local.app_name} job failed"
  combiner     = "OR"

  conditions {
    display_name = "Cloud Run Job failed"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_job\" AND metric.type=\"logging.googleapis.com/user/${google_logging_metric.job_failed.name}\""
      comparison      = "COMPARISON_GT"
      threshold_value = 0
      duration        = "0s"

      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_SUM"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  alert_strategy {
    auto_close = "86400s"
  }
}
