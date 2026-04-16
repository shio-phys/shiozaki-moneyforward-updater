variable "project_id" {
  default = "shiozaki-moneyforward-updater"
}

variable "region" {
  default = "asia-northeast1"
}

variable "image_tag" {
  description = "デプロイするコンテナイメージのタグ"
  default     = "latest"
}

variable "schedule" {
  description = "Cloud Scheduler の cron 式 (JST)"
  default     = "0 * * * *" # 毎時0分
}
