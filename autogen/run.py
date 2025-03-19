# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0
#
# Portions derived from  https://github.com/microsoft/autogen are under the MIT License.
# SPDX-License-Identifier: MIT
import queue
import threading
from typing import Any, Callable, Iterable, Optional, Union
from uuid import UUID, uuid4

from .agentchat.agent import DEFAULT_SUMMARY_METHOD, Agent
from .cache import AbstractCache
from .chat_managers import ChatManagerProtocol, RoundRobinChatManager
from .doc_utils import export_module
from .io.base import IOStream
from .io.run_response import AsyncRunResponseProtocol, RunResponseProtocol
from .messages.agent_messages import TerminationMessage
from .messages.print_message import PrintMessage
from .messages.run_events import Event, InputRequestEvent, Message, TerminationEvent
from .tools.tool import Tool

__all__ = ["run"]


class ThreadIOStream:
    def __init__(self) -> None:
        self._input_stream: queue.Queue = queue.Queue()  # type: ignore[type-arg]
        self._output_stream: queue.Queue = queue.Queue()  # type: ignore[type-arg]

    def input(self, prompt: str = "", *, password: bool = False) -> str:
        # if password:
        #     return getpass.getpass(prompt if prompt != "" else "Password: ")
        self.send(InputRequestEvent(uuid=uuid4(), prompt=prompt))
        return self._output_stream.get()  # type: ignore[no-any-return]

    def print(self, *objects: Any, sep: str = " ", end: str = "\n", flush: bool = False) -> None:
        print_message = PrintMessage(*objects, sep=sep, end=end)
        self.send(print_message)

    def send(self, message: Any) -> None:
        self._input_stream.put(message)

    @property
    def input_stream(self) -> queue.Queue:  # type: ignore[type-arg]
        return self._input_stream


class RunResponse:
    def __init__(self, iostream: ThreadIOStream):
        self.iostream = iostream
        self._summary: Optional[str] = None
        self._uuid = uuid4()

    def _queue_generator(self, q: queue.Queue) -> Iterable[Event]:  # type: ignore[type-arg]
        """A generator to yield items from the queue until the termination message is found."""
        while True:
            try:
                # Get an item from the queue
                event = q.get(timeout=0.1)  # Adjust timeout as needed
                # event = get_event(item)

                if isinstance(event, InputRequestEvent):
                    event.respond = lambda response: self.iostream._output_stream.put(response)

                yield event

                if isinstance(event, TerminationMessage):
                    chat_result_message = q.get(timeout=0.1)
                    # print("?" * 100)
                    # print(chat_result_message)
                    self._summary = chat_result_message.summary
                    break
            except queue.Empty:
                continue  # Wait for more items in the queue

    @property
    def events(self) -> Iterable[Event]:
        return self._queue_generator(self.iostream.input_stream)

    @property
    def messages(self) -> Iterable[Message]:
        return []

    @property
    def summary(self) -> Optional[str]:
        return self._summary

    @property
    def above_run(self) -> Optional["RunResponseProtocol"]:
        return None

    @property
    def uuid(self) -> UUID:
        return self._uuid


def run_single_agent(agent: Agent, iostream: ThreadIOStream, message: str, **kwargs: Any) -> None:
    with IOStream.set_default(iostream):  # type: ignore[arg-type]
        chat_result = agent.run(message=message, user_input=False, **kwargs)  # type: ignore[attr-defined]
        iostream.send(TerminationEvent(uuid=uuid4(), summary=chat_result.summary))


def run_group_chat(
    *agents: Agent,
    iostream: ThreadIOStream,
    message: str,
    chat_manager: ChatManagerProtocol,
    previous_run: Optional[RunResponseProtocol],
) -> None:
    with IOStream.set_default(iostream):  # type: ignore[arg-type]
        chat_result = chat_manager.run(
            *agents,
            message=message,
            messages=previous_run.messages if previous_run else [],
        )

        iostream.send(TerminationEvent(uuid=uuid4(), summary=chat_result.summary))


@export_module("autogen")
def run(
    *agents: Agent,
    initial_message: Optional[str] = None,
    previous_run: Optional[RunResponseProtocol] = None,
    chat_manager: Optional[ChatManagerProtocol] = None,
    # What to do with this? Goes to initiate_chat but not to initiate_swarm_chat
    clear_history: bool = False,
    max_turns: Optional[int] = None,
    summary_method: Optional[Union[str, Callable[..., Any]]] = DEFAULT_SUMMARY_METHOD,
    summary_args: Optional[dict[str, Any]] = {},
    cache: Optional[AbstractCache] = None,
    # Single agent run specific arguments
    tools: Optional[Union[Tool, Iterable[Tool]]] = None,
    executor_kwargs: Optional[dict[str, Any]] = None,
    user_input: bool = True,
    **kwargs: Any,
) -> RunResponseProtocol:
    """Run the agents with the given initial message.

    Args:
        agents (Agent): The agents to run.
        initial_message (str): The initial message to send to the first agent.
        previous_run (RunResponseProtocol): The previous run to continue.
        chat_manager (ChatManagerProtocol): The chat manager to use for the group chat.
        clear_history (bool): Whether to clear the history of the agents.
        max_turns (int): The maximum number of turns to run.
        summary_method (Union[str, Callable[..., Any]]): The method to use to summarize the chat.
        summary_args (dict[str, Any]): The arguments to pass to the summary method.
        cache (AbstractCache): The cache to use.
        tools (Union[Tool, Iterable[Tool]]): The tools to use.
        executor_kwargs (dict[str, Any]): The arguments to pass to the executor.
        user_input (bool): Whether to allow user input.
        kwargs: Additional arguments to pass to the agents.
    """
    iostream = ThreadIOStream()
    response = RunResponse(iostream)

    if len(agents) == 1:
        threading.Thread(target=run_single_agent, args=(agents[0], iostream, initial_message), kwargs=kwargs).start()
    else:
        threading.Thread(
            target=run_group_chat,
            args=agents,
            kwargs={
                "iostream": iostream,
                "message": initial_message,
                "chat_manager": chat_manager if chat_manager else RoundRobinChatManager(),
                "previous_run": previous_run,
            },
        ).start()

    return response


async def a_run(  # type: ignore[empty-body]
    *agents: Agent,
    initial_message: Optional[str] = None,
    previous_run: Optional[RunResponseProtocol] = None,
    **kwargs: Any,
) -> AsyncRunResponseProtocol:
    """Run the agents with the given initial message.

    Args:
        agents (Agent): The agents to run.
        initial_message (str): The initial message to send to the first agent.
        previous_run (RunResponseProtocol): The previous run to continue.
        kwargs: Additional arguments to pass to the agents

    """
    ...
