# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0


import os.path
from typing import Literal

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Add more services
ServiceType = Literal["spreadsheets", "documents"]
ServiceScopes = Literal["readonly", "write", "metadata"]


# Refactored example from:
# https://developers.google.com/sheets/api/quickstart/python#configure_the_sample
def get_credentials(
    client_secret_file: str,
    service: ServiceType,
    users_token_file: str = "token.json",
    scopes: set[ServiceScopes] = {"readonly"},
) -> Credentials:
    # The users_token_file stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    service_scopes = {f"https://www.googleapis.com/auth/{service}.{scope}" for scope in scopes}
    creds = None
    if os.path.exists(users_token_file):
        creds = Credentials.from_authorized_user_file(users_token_file, service_scopes)  # type: ignore[no-untyped-call]
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # type: ignore[no-untyped-call]
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, service_scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(users_token_file, "w") as token:
            token.write(creds.to_json())

    return creds  # type: ignore[no-any-return]
