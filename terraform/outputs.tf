output "docker_push_commands" {
  description = "コンテナイメージをビルド&プッシュするコマンド"
  value       = <<-EOT
    gcloud auth configure-docker ${var.region}-docker.pkg.dev --project=${var.project_id}
    docker build --platform linux/amd64 -t ${local.image_full} .
    docker push ${local.image_full}
  EOT
}

output "secret_init_command" {
  description = "パスキー認証情報をSecret Managerに登録するコマンド（初回のみ）"
  value       = "cat passkey_credentials.json | gcloud secrets versions add ${local.app_name}-passkey-credentials --data-file=- --project=${var.project_id}"
}

output "manual_run_command" {
  description = "手動実行コマンド"
  value       = "gcloud run jobs execute ${local.app_name} --region=${var.region} --project=${var.project_id} --wait"
}
