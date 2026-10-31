import pytest
from app.core.security import hash_password
from app.models.user import User, Role, Permission

def test_auth_full_flow(client, db_session):
    # 1. Setup Role, Permission, and User
    perm = Permission(code="quotations:read", description="Read quotations")
    db_session.add(perm)
    db_session.flush()

    role = Role(name="Sales Manager", description="Manages sales and quotations")
    role.permissions.append(perm)
    db_session.add(role)
    db_session.flush()

    hashed_pw = hash_password("SuperSecure123!")
    user = User(
        role_id=role.id,
        full_name="Alice Sales",
        email="alice@brightloop.io",
        password_hash=hashed_pw,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    # 2. Login with valid credentials
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@brightloop.io", "password": "SuperSecure123!"}
    )
    assert login_resp.status_code == 200, login_resp.text
    token_data = login_resp.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert token_data["user"]["email"] == "alice@brightloop.io"
    assert token_data["user"]["role"]["name"] == "Sales Manager"
    assert "quotations:read" in token_data["user"]["permissions"]

    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]

    # 3. Test Invalid Credentials
    bad_login = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@brightloop.io", "password": "WrongPassword"}
    )
    assert bad_login.status_code == 401

    # 4. Access protected /me endpoint with access token
    me_resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "alice@brightloop.io"
    assert me_resp.json()["full_name"] == "Alice Sales"

    # 5. Refresh token flow
    refresh_resp = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_resp.status_code == 200
    refreshed_data = refresh_resp.json()
    assert "access_token" in refreshed_data
    assert "refresh_token" in refreshed_data
    new_access_token = refreshed_data["access_token"]
    new_refresh_token = refreshed_data["refresh_token"]

    # 6. Verify new access token works on /me
    me2_resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {new_access_token}"}
    )
    assert me2_resp.status_code == 200

    # 7. Logout flow
    logout_resp = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": new_refresh_token}
    )
    assert logout_resp.status_code == 200
    assert logout_resp.json()["success"] is True

    # 8. Re-using revoked refresh token should fail with 401
    reuse_resp = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": new_refresh_token}
    )
    assert reuse_resp.status_code == 401
