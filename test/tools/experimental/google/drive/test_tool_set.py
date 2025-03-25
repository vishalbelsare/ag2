# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0


import unittest
from unittest.mock import MagicMock

from autogen.import_utils import optional_import_block, skip_on_missing_imports
from autogen.tools import ToolSet

with optional_import_block():
    from autogen.tools.experimental.google.drive import GoogleDriveToolSet


@skip_on_missing_imports(
    [
        "googleapiclient",
        "google_auth_httplib2",
        "google_auth_oauthlib",
    ],
    "google-api",
)
class TestGoogleDriveToolSet:
    def test_init(self) -> None:
        with unittest.mock.patch(
            "autogen.tools.experimental.google.drive.tool_set.build",
            return_value=MagicMock(),
        ) as mock_build:
            tool_set = GoogleDriveToolSet(
                credentials=MagicMock(),
                download_folder="download_folder",
            )

            mock_build.assert_called_once()
            assert isinstance(tool_set, ToolSet)

            assert len(tool_set.tools) == 1
