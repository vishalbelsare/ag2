# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0
#
# Portions derived from  https://github.com/microsoft/autogen are under the MIT License.
# SPDX-License-Identifier: MIT
from typing import TYPE_CHECKING

from ..groupchat import GroupChat, GroupChatManager

if TYPE_CHECKING:
    from ...agent import Agent, LLMMessageType
    from ...chat import ChatResult


class RoundRobinChatManager(GroupChatManager):
    def __init__(
        self,
    ) -> None:
        super().__init__()

    def run(
        self,
        *agents: "Agent",
        message: str,
        messages: list["LLMMessageType"],
    ) -> "ChatResult":
        groupchat = GroupChat(
            agents=agents,
            messages=messages,
            speaker_selection_method="round_robin",
        )

        self.initialize_groupchat(groupchat)

        return agents[0].initiate_chat(
            recipient=self,
            message=message,
        )

    async def a_run(
        self,
        *agents: "Agent",
        message: str,
        messages: list["LLMMessageType"],
    ) -> "ChatResult":
        groupchat = GroupChat(
            agents=agents,
            messages=messages,
            speaker_selection_method="round_robin",
        )

        self.initialize_groupchat(groupchat)

        return await agents[0].a_initiate_chat(
            recipient=self,
            message=message,
        )
