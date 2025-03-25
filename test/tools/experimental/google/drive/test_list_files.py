# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0


import unittest
from unittest.mock import MagicMock

import pytest

from autogen.import_utils import optional_import_block, skip_on_missing_imports

with optional_import_block():
    from autogen.tools.experimental.google import ListGoogleDriveFilesTool
    from autogen.tools.experimental.google.authentication.credentials_local_provider import (
        GoogleCredentialsLocalProvider,
    )


@skip_on_missing_imports(
    [
        "googleapiclient",
        "google_auth_httplib2",
        "google_auth_oauthlib",
    ],
    "google-api",
)
class TestListGoogleDriveFilesTool:
    def test_init(self) -> None:
        with unittest.mock.patch(
            "autogen.tools.experimental.google.drive.list_files.build",
            return_value=MagicMock(),
        ) as mock_build:
            google_drive_tool = ListGoogleDriveFilesTool(
                credentials=MagicMock(),
            )

            assert google_drive_tool.name == "list_google_drive_files"
            assert google_drive_tool.description == "List files in a user's Google Drive."
            mock_build.assert_called_once()

    @pytest.mark.skip(reason="This test requires real google credentials and is not suitable for CI at the moment")
    def test_end2end(self) -> None:
        client_secret_file = "client_secret_ag2.json"

        provider = GoogleCredentialsLocalProvider(
            client_secret_file=client_secret_file,
            scopes=["https://www.googleapis.com/auth/drive.metadata.readonly"],
            service_name="drive",
            version="v4",
        )
        creds = provider.get_credentials()

        google_drive_tool = ListGoogleDriveFilesTool(
            credentials=creds,
        )

        result = google_drive_tool.func(10)
        print(f"List of files: {result}")
