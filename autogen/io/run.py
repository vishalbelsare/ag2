# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0
#
# Portions derived from  https://github.com/microsoft/autogen are under the MIT License.
# SPDX-License-Identifier: MIT
from typing import Any, Optional

from ..agentchat import Agent
from ..agentchat.groupchat import GroupChat, GroupChatManager
from .run_response import AsyncRunResponseProtocol, RunResponseProtocol

# class MultiprocessingIOStream:
#     def __init__(self):
#         self._input_stream = multiprocessing.Queue()
#         self._output_stream = multiprocessing.Queue()

#     def input(self, prompt: str = "", *, password: bool = False) -> str:
#         # if password:
#         #     return getpass.getpass(prompt if prompt != "" else "Password: ")
#         return self._output_stream.get()

#     def print(self, *objects: Any, sep: str = " ", end: str = "\n", flush: bool = False) -> None:
#         self._input_stream.put(objects)

#     def send(self, message: Any) -> None:
#         self._output_stream.put(message)


def run(
    *agents: Agent, message: Optional[str] = None, previous_run: Optional[RunResponseProtocol] = None, **kwargs: Any
) -> RunResponseProtocol:
    """Run the agents with the given initial message.

    Args:
        agents: The agents to run.
        message: The initial message to send to the first agent.
        previous_run: The previous run to continue.
        kwargs: Additional arguments to pass to the agents.

    """
    # Setup group chat
    groupchat = GroupChat(agents=list(agents), speaker_selection_method="auto", messages=[])

    # Create manager
    # At each turn, the manager will check if the message contains DONE! and end the chat if so
    # Otherwise, it will select the next appropriate agent using its LLM
    manager = GroupChatManager(
        name="group_manager",
        groupchat=groupchat,
        llm_config=kwargs.get("llm_config"),
        is_termination_msg=lambda x: "DONE!" in (x.get("content", "") or "").upper(),
    )

    # Start the conversation
    chat_result = agents[0].initiate_chat(  # type: ignore[attr-defined]
        recipient=manager,
        message=message,
    )

    return chat_result  # type: ignore[no-any-return]


async def a_run( # type: ignore[empty-body]
    *agents: Agent, message: Optional[str] = None, previous_run: Optional[RunResponseProtocol] = None, **kwargs: Any
) -> AsyncRunResponseProtocol:
    """Run the agents with the given initial message.

    Args:
        agents: The agents to run.
        message: The initial message to send to the first agent.
        previous_run: The previous run to continue.
        kwargs: Additional arguments to pass to the agents.

    """
    ...
