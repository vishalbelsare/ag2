# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0


from typing import Optional, Protocol, runtime_checkable

from .....import_utils import optional_import_block

with optional_import_block():
    from google.oauth2.credentials import Credentials


__all__ = ["GoogleCredentialsProvider"]


@runtime_checkable
class GoogleCredentialsProvider(Protocol):
    def get_credentials(self) -> Optional["Credentials"]: ...

    @property
    def host(self) -> str: ...

    @property
    def port(self) -> int: ...
