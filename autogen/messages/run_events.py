# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0
#
# Portions derived from  https://github.com/microsoft/autogen are under the MIT License.
# SPDX-License-Identifier: MIT
from typing import Annotated, Any, Callable, Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

__all__ = [
    "AgentMessageEvent",
    "AsyncInputRequestEvent",
    "ErrorEvent",
    "Event",
    "InputRequestEvent",
    "InputResponseEvent",
    "OutputEvent",
    "SystemEvent",
]

EventType = Literal[
    "input_request", "async_input_request", "input_response", "agent_message", "output", "system", "error", "terminate"
]
Message = dict[str, Any]


class Event(BaseModel):
    uuid: Annotated[UUID, Field(default_factory=uuid4)]

    type: EventType


class InputRequestEvent(Event):
    prompt: str
    respond: Optional[Callable[[str], None]] = None

    # def respond(self, response: "InputResponseEvent") -> None:
    #     pass

    type: EventType = "input_request"


class AsyncInputRequestEvent(Event):
    prompt: str

    async def a_respond(self, response: "InputResponseEvent") -> None:
        pass

    type: EventType = "async_input_request"


class InputResponseEvent(Event):
    type: EventType = "input_response"

    value: str


class AgentMessageEvent(Event):
    message: Message

    type: EventType = "agent_message"


class OutputEvent(Event):
    value: str

    type: EventType = "output"


class SystemEvent(Event):
    value: str

    type: EventType = "system"


class ErrorEvent(Event):
    type: EventType = "error"

    error: str


class TerminationEvent(Event):
    type: EventType = "terminate"
    summary: Optional[str] = None
