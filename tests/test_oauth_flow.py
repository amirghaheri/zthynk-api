from urllib.parse import parse_qs, urlparse


def test_login_redirects_to_cognito_with_pkce(client):
    response = client.get("/auth/login", follow_redirects=False)

    assert response.status_code == 302

    redirect_url = urlparse(response.headers["location"])
    query = parse_qs(redirect_url.query)

    assert redirect_url.path.endswith("/login")
    assert query["response_type"] == ["code"]
    assert query["client_id"]
    assert query["state"]
    assert query["code_challenge"]
    assert query["code_challenge_method"] == ["S256"]

    cookies = response.headers.get_list("set-cookie")
    cookie_text = " ".join(cookies)

    assert "zthynk_oauth_state" in cookie_text
    assert "zthynk_pkce_verifier" in cookie_text


def test_callback_rejects_invalid_state(client):
    response = client.get(
        "/auth/callback?code=fake-code&state=attacker-state",
        cookies={"zthynk_oauth_state": "legitimate-state"},
        follow_redirects=False,
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid OAuth state"}


def test_callback_rejects_missing_pkce_verifier(client):
    response = client.get(
        "/auth/callback?code=fake-code&state=legitimate-state",
        cookies={"zthynk_oauth_state": "legitimate-state"},
        follow_redirects=False,
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Missing PKCE verifier"}


def test_login_cookies_are_secure_in_production(client, monkeypatch):
    from app.config.settings import settings

    monkeypatch.setattr(settings, "environment", "production")

    response = client.get("/auth/login", follow_redirects=False)

    assert response.status_code == 302

    cookies = response.headers.get_list("set-cookie")

    assert len(cookies) >= 2

    for cookie in cookies:
        assert "secure" in cookie.lower()
        assert "httponly" in cookie.lower()
