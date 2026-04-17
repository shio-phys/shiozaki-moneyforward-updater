# MoneyForward 一括更新自動化

MoneyForward の「一括更新」ボタンをパスキー認証で自動クリックするスクリプトです。  
GCP Cloud Run Job + Cloud Scheduler により毎時自動実行されます。

## 仕組み

1. Playwright の CDP (Chrome DevTools Protocol) で仮想 WebAuthn 認証器を作成
2. 事前に登録したパスキー認証情報をロードしてログイン
3. `/accounts` ページの「一括更新」ボタンをクリック

## ファイル構成

```
.
├── main.py                  # 本番用: パスキーでログインして一括更新
├── register.py              # 初回のみ: メール/パスワードでログインしてパスキーを登録
├── Dockerfile               # Cloud Run Job 用コンテナ
├── deploy.sh                # イメージビルド・プッシュ・Job 更新
├── pyproject.toml
├── uv.lock
└── terraform/               # GCP インフラ (Cloud Run Job, Cloud Scheduler, etc.)
```

## セットアップ

### 前提

- [uv](https://github.com/astral-sh/uv) がインストール済み
- Python 3.13+

### インストール

```bash
uv sync
uv run playwright install chromium
```

### 環境変数

`.env.example` をコピーして `.env` を作成します。

```bash
cp .env.example .env
```

```env
MF_EMAIL=your-email@example.com
MF_PASSWORD=your-password
```

### パスキー登録（初回のみ）

```bash
uv run register.py
```

ヘッドありブラウザが開き、メール/パスワードでログイン後にパスキーを登録します。  
認証情報は `passkey_credentials.json` に保存されます（`.gitignore` 済み）。

### 動作確認

```bash
uv run main.py
```

## デプロイ (GCP)

### インフラ構築（初回のみ）

```bash
cd terraform
terraform init
terraform apply
```

パスキー認証情報を Secret Manager に登録します。

```bash
gcloud secrets versions add moneyforward-passkey-credentials \
  --data-file=passkey_credentials.json \
  --project=shiozaki-moneyforward-updater
```

### アプリ更新

```bash
./deploy.sh
```

Docker イメージをビルド・プッシュし、Cloud Run Job を更新します。

## スケジュール

Cloud Scheduler により毎時0分 (JST) に自動実行されます。  
`terraform/variables.tf` の `schedule` 変数で変更可能です。
