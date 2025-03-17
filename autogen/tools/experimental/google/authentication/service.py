# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0


from typing import Any

from .....import_utils import optional_import_block

with optional_import_block():
    from googleapiclient.discovery import build

from .credentials import get_credentials_from_db, get_credentials_from_json

__all__ = [
    "build_service_from_db",
    "build_service_from_json",
]


def build_service_from_db(
    client_secret_file: str,
    scopes: list[str],
    user_id: int,
    service_name: str,
    db_engine_url: str = "sqlite:///database.db",
) -> Any:
    creds = get_credentials_from_db(
        client_secret_file=client_secret_file,
        scopes=scopes,
        user_id=user_id,
        db_engine_url=db_engine_url,
    )
    return build(serviceName=service_name, version="v3", credentials=creds)


def build_service_from_json(
    client_secret_file: str,
    scopes: list[str],
    service_name: str,
    users_token_file: str = "token.json",
) -> Any:
    creds = get_credentials_from_json(
        client_secret_file=client_secret_file,
        scopes=scopes,
        users_token_file=users_token_file,
    )
    return build(serviceName=service_name, version="v3", credentials=creds)
