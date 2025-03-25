# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

from typing import TYPE_CHECKING, Any, Callable, Optional, Union

from ..agentchat.groupchat import GroupChat, GroupChatManager
from ..doc_utils import export_module

if TYPE_CHECKING:
    from ..agentchat import Agent, ChatResult, LLMMessageType
    from .run_pattern import RunPatternProtocol


@export_module("autogen.run_patterns")
class RoundRobinRunPattern(GroupChatManager):
    def __init__(
        self,
    ) -> None:
        super().__init__()

    def run(
        self,
        *agents: "Agent",
        message: str,
        messages: list["LLMMessageType"],
        max_turns: int,
        summary_method: Optional[Union[str, Callable[..., Any]]],
    ) -> "ChatResult":
        groupchat = GroupChat(
            agents=agents,
            messages=messages,
            max_round=max_turns,
            speaker_selection_method="round_robin",
        )

        self.initialize_groupchat(groupchat)

        return agents[0].initiate_chat(
            recipient=self,
            message=message,
            summary_method=summary_method,
        )

    async def a_run(
        self,
        *agents: "Agent",
        message: str,
        messages: list["LLMMessageType"],
        max_turns: int,
        summary_method: Optional[Union[str, Callable[..., Any]]],
    ) -> "ChatResult":
        groupchat = GroupChat(
            agents=agents,
            messages=messages,
            max_round=max_turns,
            speaker_selection_method="round_robin",
        )

        self.initialize_groupchat(groupchat)

        return await agents[0].a_initiate_chat(
            recipient=self,
            message=message,
            summary_method=summary_method,
        )


if TYPE_CHECKING:

    def check_group_run_pattern_implements_run_pattern_protocol(x: RoundRobinRunPattern) -> RunPatternProtocol:
        return x
