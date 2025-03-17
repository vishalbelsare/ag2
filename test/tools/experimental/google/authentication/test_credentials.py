# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0


import os
import tempfile
import unittest
from typing import Generator
from unittest.mock import MagicMock

import pytest
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from autogen.tools.experimental.google.authentication.credentials import (
    UserCredentials,
    _check_credentials_and_update_if_needed,
    _get_user_credentials_from_db,
    _set_user_credentials_to_db,
    get_credentials_from_json,
)


class TestUserCredentials:
    @pytest.fixture
    def tmp_db_engine_url(self) -> Generator[str, None, None]:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test_database.db")
            yield f"sqlite:///{db_path}"

    def test_user_credentials(self, tmp_db_engine_url: str) -> None:
        data = {"user_id": 1, "refresh_token": "refresh", "client_id": "client", "client_secret": "secret"}
        user_credentials = UserCredentials(**data)
        _set_user_credentials_to_db(
            user_creds=user_credentials,
            db_engine_url=tmp_db_engine_url,
        )

        user_credentials_from_db = _get_user_credentials_from_db(1, tmp_db_engine_url)
        assert user_credentials_from_db == user_credentials
        assert user_credentials_from_db.model_dump(exclude={"id"}) == data

        user_credentials_from_db = _get_user_credentials_from_db(2, tmp_db_engine_url)
        assert user_credentials_from_db is None

    def test_check_credentials_and_update_if_needed_raises_exception(self) -> None:
        with pytest.raises(ValueError, match="Either user_id or user_creds must be provided"):
            _check_credentials_and_update_if_needed(
                client_secret_file="client_secret_test.json",
                scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
            )

    @pytest.mark.parametrize(
        "valid_creds",
        [
            True,
            False,
        ],
    )
    def test_check_credentials_and_update_if_needed(self, tmp_db_engine_url: str, valid_creds: bool) -> None:
        with unittest.mock.patch(
            "autogen.tools.experimental.google.authentication.credentials.Credentials.from_authorized_user_info",
        ) as mock_from_authorized_user_info:
            user_creds = MagicMock()
            user_creds.refresh_token = "refresh"
            user_creds.client_id = "client"
            user_creds.client_secret = "secret"
            user_creds.valid = valid_creds
            mock_from_authorized_user_info.return_value = user_creds

            _check_credentials_and_update_if_needed(
                client_secret_file="client_secret_ag2.json",
                scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
                user_creds=UserCredentials(
                    user_id=1, refresh_token="refresh", client_id="client", client_secret="secret"
                ),
                db_engine_url=tmp_db_engine_url,
            )

            mock_from_authorized_user_info.assert_called_once_with(
                info={
                    "refresh_token": "refresh",
                    "client_id": "client",
                    "client_secret": "secret",
                },
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets.readonly",
                ],
            )

            creds_from_db = _get_user_credentials_from_db(1, tmp_db_engine_url)

            if valid_creds:
                assert creds_from_db is None, creds_from_db
            else:
                assert creds_from_db is not None, creds_from_db


def test_end2end() -> None:
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    client_secret_file = "client_secret_ag2.json"
    creds = get_credentials_from_json(
        client_secret_file=client_secret_file,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        # The ID and range of a sample spreadsheet.
        spreadsheet_id = "1BdWBOyCAyIPE6sgtPqGPxDqrgBpvl6zmSgGRQ_I3s-Y"
        range_name = "Sheet1!A2:E"
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return

        print("Name, Major:")
        for row in values:
            print(row)
    except HttpError as err:
        print(err)
