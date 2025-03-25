# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0


from typing import Any

from .....import_utils import optional_import_block, require_optional_import

with optional_import_block():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

from ..authentication.credentials import get_credentials_from_db, get_credentials_from_json

__all__ = [
    "build_service",
    "build_service_from_db",
    "build_service_from_json",
]


@require_optional_import(
    [
        "googleapiclient",
        "google_auth_httplib2",
        "google_auth_oauthlib",
        "sqlmodel",
    ],
    "google-api",
)
def build_service_from_db(
    client_secret_file: str,
    scopes: list[str],
    user_id: int,
    service_name: str,
    version: str,
    db_engine_url: str = "sqlite:///database.db",
) -> Any:
    creds = get_credentials_from_db(
        client_secret_file=client_secret_file,
        scopes=scopes,
        user_id=user_id,
        db_engine_url=db_engine_url,
    )
    return build(serviceName=service_name, version=version, credentials=creds)


@require_optional_import(
    [
        "googleapiclient",
        "google_auth_httplib2",
        "google_auth_oauthlib",
    ],
    "google-api",
)
def build_service_from_json(
    client_secret_file: str,
    scopes: list[str],
    service_name: str,
    version: str,
    users_token_file: str = "token.json",
) -> Any:
    creds = get_credentials_from_json(
        client_secret_file=client_secret_file,
        scopes=scopes,
        users_token_file=users_token_file,
    )
    return build(serviceName=service_name, version=version, credentials=creds)


@require_optional_import(
    [
        "googleapiclient",
        "google_auth_httplib2",
        "google_auth_oauthlib",
    ],
    "google-api",
)
def build_service(
    credentials: "Credentials",
    service_name: str,
    version: str,
) -> Any:
    return build(serviceName=service_name, version=version, credentials=credentials)
