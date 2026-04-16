"""
MoneyForward パスキー登録スクリプト

初回のみ実行してください。
ヘッドありブラウザで手動ログイン後、パスキーを登録し認証情報をファイルに保存します。
"""

import json
import os
import sys
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

load_dotenv()

MF_URL = "https://moneyforward.com"
LOGIN_URL = "https://id.moneyforward.com/sign_in"
PASSKEY_SETTINGS_URL = "https://id.moneyforward.com/webauthn/credentials"
CREDENTIALS_FILE = "passkey_credentials.json"


def setup_virtual_authenticator(cdp) -> str:
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
    return result["authenticatorId"]


def export_credentials(cdp, authenticator_id: str) -> list:
    result = cdp.send("WebAuthn.getCredentials", {"authenticatorId": authenticator_id})
    return result.get("credentials", [])


def login_with_password(page, email: str, password: str) -> None:
    page.goto(LOGIN_URL)
    page.get_by_label("メールアドレス").fill(email)
    page.get_by_role("button", name="ログイン").click()
    page.locator("input#mfid_user\\[password\\]").fill(password)
    page.get_by_role("button", name="ログイン").click()

    try:
        page.wait_for_url("https://id.moneyforward.com/me", timeout=8000)
    except PlaywrightTimeoutError:
        if page.get_by_placeholder("000000").is_visible():
            otp = input("追加認証コード（メールに届いた6桁）を入力してください: ").strip()
            page.get_by_placeholder("000000").fill(otp)
            page.get_by_role("button", name="認証する").click()
            page.wait_for_url("https://id.moneyforward.com/me", timeout=15000)
        else:
            raise

    print("ログイン成功")


def register_passkey(page) -> None:
    print("パスキー登録ページへ移動します...")
    page.goto(PASSKEY_SETTINGS_URL)
    page.wait_for_load_state("networkidle", timeout=10000)

    register_button = page.get_by_role("button", name="パスキーを登録する")
    register_button.wait_for(timeout=10000)
    register_button.click()
    print("パスキー登録ボタンをクリックしました")

    # 登録完了を待つ: URLが /new から外れるか、成功メッセージが出るまで
    try:
        page.wait_for_url(
            lambda url: "passkeys/new" not in url,
            timeout=15000,
        )
    except PlaywrightTimeoutError:
        pass  # URL変化がなくても認証情報が登録されていれば成功

    page.wait_for_timeout(1000)
    print("パスキー登録完了")


def main() -> None:
    email = os.environ.get("MF_EMAIL")
    password = os.environ.get("MF_PASSWORD")

    if not email or not password:
        print("エラー: .env に MF_EMAIL と MF_PASSWORD を設定してください", file=sys.stderr)
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 確認のためヘッドあり
        context = browser.new_context()
        page = context.new_page()
        cdp = context.new_cdp_session(page)

        authenticator_id = setup_virtual_authenticator(cdp)
        print(f"仮想認証器を作成しました (id: {authenticator_id})")

        try:
            login_with_password(page, email, password)
            register_passkey(page)

            credentials = export_credentials(cdp, authenticator_id)
            if not credentials:
                print("エラー: 認証情報が登録されませんでした", file=sys.stderr)
                page.screenshot(path="error.png")
                sys.exit(1)

            with open(CREDENTIALS_FILE, "w") as f:
                json.dump(credentials, f, indent=2)

            print(f"認証情報を {CREDENTIALS_FILE} に保存しました ({len(credentials)} 件)")
            print("次回から uv run main.py で自動ログインできます")

        except PlaywrightTimeoutError as e:
            print(f"タイムアウトエラー: {e}", file=sys.stderr)
            page.screenshot(path="error.png")
            print("スクリーンショットを error.png に保存しました")
            sys.exit(1)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
