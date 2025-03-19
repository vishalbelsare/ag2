# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0
#
# Portions derived from  https://github.com/microsoft/autogen are under the MIT License.
# SPDX-License-Identifier: MIT

from typing import TYPE_CHECKING, Iterable, Protocol

if TYPE_CHECKING:
    from ..agentchat.agent import Agent, LLMMessageType
    from ..agentchat.chat import ChatResult


class ChatManagerProtocol(Protocol):
    def run(
        self,
        *agents: "Agent",
        message: str,
        messages: Iterable["LLMMessageType"],
    ) -> "ChatResult": ...

    async def a_run(
        self,
        *agents: "Agent",
        message: str,
        messages: Iterable["LLMMessageType"],
    ) -> "ChatResult": ...
