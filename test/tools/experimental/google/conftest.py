# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

import os
import tempfile
from typing import Generator

import pytest


@pytest.fixture
def tmp_db_engine_url() -> Generator[str, None, None]:
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test_database.db")
        yield f"sqlite:///{db_path}"
