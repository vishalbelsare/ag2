# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0


import os.path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from sqlmodel import Field, SQLModel, Session, create_engine, select

__all__ = [
    "UserCredentials",
    "get_credentials_from_json",
]


# Refactored example from:
# https://developers.google.com/sheets/api/quickstart/python#configure_the_sample
def get_credentials_from_json(
    client_secret_file: str,
    scopes: list[str],
    users_token_file: str = "token.json",
) -> Credentials:
    # The users_token_file stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    creds = None
    if os.path.exists(users_token_file):
        creds = Credentials.from_authorized_user_file(users_token_file, scopes)  # type: ignore[no-untyped-call]
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # type: ignore[no-untyped-call]
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(users_token_file, "w") as token:
            token.write(creds.to_json())

    return creds  # type: ignore[no-any-return]


class UserCredentials(SQLModel, table=True):  # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    refresh_token: str
    client_id: str
    client_secret: str


def _get_user_credentials_from_db(
    user_id: int,
    db_engine_url: str = "sqlite:///database.db",
) -> Optional[UserCredentials]:
    engine = create_engine(db_engine_url)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        statement = (
            select(UserCredentials).where(UserCredentials.user_id == user_id).order_by(UserCredentials.id.desc())  # type: ignore[union-attr]
        )
        user_creds = session.exec(statement).first()
        print(user_creds)

    return user_creds  # type: ignore[no-any-return]


def _set_user_credentials_to_db(
    user_creds: UserCredentials,
    db_engine_url: str = "sqlite:///database.db",
) -> None:
    engine = create_engine(db_engine_url)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(user_creds)
        session.commit()
