# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0


import os
from typing import Optional

from .....import_utils import optional_import_block, require_optional_import

with optional_import_block():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    from .credentials_provider import GoogleCredentialsProvider


__all__ = ["GoogleCredentialsLocalProvider"]


class GoogleCredentialsLocalProvider(GoogleCredentialsProvider):
    def __init__(
        self,
        client_secret_file: str,
        scopes: list[str],  # e.g. ['https://www.googleapis.com/auth/drive/readonly']
        service_name: str,  # e.g. 'sheets', 'drive', etc.
        version: str,  # e.g. 'v4'
        users_token_file: Optional[str] = None,
        port: int = 8080,
    ) -> None:
        self.client_secret_file = client_secret_file
        self.scopes = scopes
        self.service_name = service_name  # TODO: maybe not needed
        self.version = version  # TODO: maybe not needed
        self.users_token_file = users_token_file
        self._port = port

    @property
    def host(self) -> str:
        return "localhost"

    @property
    def port(self) -> int:
        return self._port

    @require_optional_import(
        [
            "google_auth_httplib2",
            "google_auth_oauthlib",
        ],
        "google-api",
    )
    def _refresh_or_get_new_credentials(self, creds: Optional["Credentials"]) -> "Credentials":
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # type: ignore[no-untyped-call]
        else:
            flow = InstalledAppFlow.from_client_secrets_file(self.client_secret_file, self.scopes)
            creds = flow.run_local_server(host=self.host, port=self.port)
        return creds  # type: ignore[return-value]

    @require_optional_import(
        [
            "google_auth_httplib2",
            "google_auth_oauthlib",
        ],
        "google-api",
    )
    def get_credentials(self) -> Optional["Credentials"]:
        creds = None
        if self.users_token_file and os.path.exists(self.users_token_file):
            creds = Credentials.from_authorized_user_file(self.users_token_file)  # type: ignore[no-untyped-call]

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            creds = self._refresh_or_get_new_credentials(creds)

            if self.users_token_file:
                # Save the credentials for the next run
                with open(self.users_token_file, "w") as token:
                    token.write(creds.to_json())  # type: ignore[no-untyped-call]

        return creds  # type: ignore[no-any-return]
