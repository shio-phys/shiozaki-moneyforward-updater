import json
import os
import sys
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

MF_URL = "https://moneyforward.com"
CREDENTIALS_FILE = "passkey_credentials.json"


def setup_virtual_authenticator(cdp, credentials: list) -> str:
    cdp.send("WebAuthn.enable")
    result = cdp.send("WebAuthn.addVirtualAuthenticator", {
        "options": {
            "protocol": "ctap2",
            "transport": "internal",
            "hasResidentKey": True,
            "hasUserVerification": True,
            "isUserVerified": True,
            "automaticPresenceSimulation": True,
        }
    })
    authenticator_id = result["authenticatorId"]

    for cred in credentials:
        cdp.send("WebAuthn.addCredential", {
            "authenticatorId": authenticator_id,
            "credential": cred,
        })

    print(f"仮想認証器に認証情報を {len(credentials)} 件ロードしました")
    return authenticator_id


def login_with_passkey(page) -> None:
    # /accounts にアクセスすると仮想認証器が自動でパスキー認証して直接着地する
    page.goto(f"{MF_URL}/accounts", timeout=60000)
    page.wait_for_load_state("networkidle", timeout=30000)

    if not page.url.startswith(MF_URL):
        raise RuntimeError(f"ログイン失敗: {page.url}")

    print("ログイン成功")


def bulk_update(page) -> None:
    page.wait_for_timeout(3000)  # JS描画待ち
    button = page.get_by_text("一括更新").first
    button.wait_for(timeout=10000)
    button.click()
    print("「一括更新」ボタンをクリックしました")
    page.wait_for_timeout(3000)
    print("更新リクエスト送信完了")


def load_credentials() -> list:
    # 環境変数 PASSKEY_CREDENTIALS があればそちらを優先（Cloud Run用）
    env_creds = os.environ.get("PASSKEY_CREDENTIALS")
    if env_creds:
        return json.loads(env_creds)

    if not os.path.exists(CREDENTIALS_FILE):
        print(f"エラー: {CREDENTIALS_FILE} が見つかりません。先に uv run register.py を実行してください", file=sys.stderr)
        sys.exit(1)

    with open(CREDENTIALS_FILE) as f:
        return json.load(f)


MAX_RETRIES = 3


def run_once(credentials: list) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()
        cdp = context.new_cdp_session(page)

        setup_virtual_authenticator(cdp, credentials)

        try:
            login_with_passkey(page)
            bulk_update(page)
        finally:
            browser.close()


def main() -> None:
    credentials = load_credentials()

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            run_once(credentials)
            return
        except PlaywrightTimeoutError as e:
            print(f"タイムアウトエラー (試行 {attempt}/{MAX_RETRIES}): {e}", file=sys.stderr)
            if attempt == MAX_RETRIES:
                sys.exit(1)
            print("60秒待機してリトライします...")
            time.sleep(60)


if __name__ == "__main__":
    main()
