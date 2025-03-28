# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

from typing import Annotated, Literal

from pydantic import BaseModel, Field

__all__ = [
    "CreateDocsFile",
]

class CreateDocsFile(BaseModel):
    name: Annotated[str, Field(description="The name of the file.")]
    content: Annotated[str, Field(description="The content of the file.")]
    content_type: Annotated[Literal["html", "markdown"], Field(description="The type of content.")]
