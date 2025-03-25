# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0


import os.path
from typing import Optional

from .....import_utils import optional_import_block, require_optional_import

with optional_import_block():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from sqlmodel import Field, SQLModel, Session, create_engine, select

    # This class needs to be defined here because SQLModel is optional
    class UserCredentials(SQLModel, table=True):  # type: ignore
        id: Optional[int] = Field(default=None, primary_key=True)
        user_id: int
        refresh_token: str
        client_id: str
        client_secret: str


__all__ = [
    "UserCredentials",
    "get_credentials_from_db",
    "get_credentials_from_json",
]


@require_optional_import(
    [
        "google_auth_httplib2",
        "google_auth_oauthlib",
    ],
    "google-api",
)
def _refresh_or_get_new_credentials_from_localhost(
    client_secret_file: str, scopes: list[str], creds: Optional["Credentials"]
) -> "Credentials":
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())  # type: ignore[no-untyped-call]
    else:
        flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)
        creds = flow.run_local_server(port=8080)
    return creds  # type: ignore[return-value]


# Refactored example from:
# https://developers.google.com/sheets/api/quickstart/python#configure_the_sample
@require_optional_import(
    [
        "google_auth_httplib2",
        "google_auth_oauthlib",
    ],
    "google-api",
)
def get_credentials_from_json(
    client_secret_file: str,
    scopes: list[str],
    users_token_file: str = "token.json",
) -> "Credentials":
    # The users_token_file stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    creds = None
    if os.path.exists(users_token_file):
        creds = Credentials.from_authorized_user_file(users_token_file, scopes)  # type: ignore[no-untyped-call]
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        creds = _refresh_or_get_new_credentials_from_localhost(client_secret_file, scopes, creds)

        # Save the credentials for the next run
        with open(users_token_file, "w") as token:
            token.write(creds.to_json())  # type: ignore[no-untyped-call]

    return creds  # type: ignore[no-any-return]


@require_optional_import(
    [
        "google_auth_httplib2",
        "google_auth_oauthlib",
        "sqlmodel",
    ],
    "google-api",
)
def _get_user_credentials_from_db(
    user_id: int,
    db_engine_url: str = "sqlite:///database.db",
) -> Optional["UserCredentials"]:
    engine = create_engine(db_engine_url)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        statement = (
            select(UserCredentials).where(UserCredentials.user_id == user_id).order_by(UserCredentials.id.desc())  # type: ignore[union-attr]
        )
        user_creds = session.exec(statement).first()

    return user_creds  # type: ignore[no-any-return]


@require_optional_import(
    [
        "google_auth_httplib2",
        "google_auth_oauthlib",
        "sqlmodel",
    ],
    "google-api",
)
def _set_user_credentials_to_db(
    user_creds: "UserCredentials",
    db_engine_url: str = "sqlite:///database.db",
) -> None:
    engine = create_engine(db_engine_url)
    SQLModel.metadata.create_all(engine)

    with Session(engine, expire_on_commit=False) as session:
        session.add(user_creds)
        session.commit()


@require_optional_import(
    [
        "google_auth_httplib2",
        "google_auth_oauthlib",
        "sqlmodel",
    ],
    "google-api",
)
def get_credentials_from_db(
    client_secret_file: str,
    scopes: list[str],
    user_id: int,
    db_engine_url: str = "sqlite:///database.db",
) -> "Credentials":
    user_creds = _get_user_credentials_from_db(user_id=user_id, db_engine_url=db_engine_url)

    if user_creds:
        creds = Credentials.from_authorized_user_info(  # type: ignore[no-untyped-call]
            info={
                "refresh_token": user_creds.refresh_token,
                "client_id": user_creds.client_id,
                "client_secret": user_creds.client_secret,
            },
            scopes=scopes,
        )
    else:
        creds = None

    if not creds or not creds.valid:
        creds = _refresh_or_get_new_credentials_from_localhost(
            client_secret_file=client_secret_file, scopes=scopes, creds=creds
        )

        if not user_creds:
            user_creds = UserCredentials(
                user_id=user_id,
                refresh_token=creds.refresh_token,
                client_id=creds.client_id,
                client_secret=creds.client_secret,
            )
        _set_user_credentials_to_db(user_creds=user_creds, db_engine_url=db_engine_url)
    return creds  # type: ignore[no-any-return]
