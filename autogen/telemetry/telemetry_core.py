# Copyright (c) 2023 - 2024, Owners of https://github.com/ag2ai
#
# SPDX-License-Identifier: Apache-2.0
import threading
import uuid
from abc import ABC, abstractmethod
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# Number of bits for trace and span IDs
TRACE_ID_BITS = 128
SPAN_ID_BITS = 64

# Global context variable to store the current telemetry manager
_current_telemetry: ContextVar[Optional["InstrumentationManager"]] = ContextVar("current_telemetry", default=None)


def get_current_telemetry() -> Optional["InstrumentationManager"]:
    """Get the current telemetry manager from the global context.

    Used throughout the code to access the current telemetry manager (returning None if not established)

    Returns:
        Optional[InstrumentationManager]: The current telemetry manager or None if not

    E.g.
        telemetry = get_current_telemetry()
        if telemetry:
            reply_span_context = telemetry.start_span(
                kind=SpanKind.REPLY,
                ...
    """
    return _current_telemetry.get()


class SpanKind(Enum):
    """Enumeration of span kinds

    Spans represent a unit of work within a trace. Typically spans have child spans and events.

    Descriptions:
        WORKFLOW: Main workflow span
        CHATS: Multiple chats, e.g. initiate_chats
        CHAT: Single chat, e.g. initiate_chat
        NESTED_CHAT: Start of a nested chat, e.g. _summary_from_nested_chats
        ROUND: A round within a chat (where chats have max_round or max_turn)
        REPLY: Agent replying to another agent
        REPLY_FUNCTION: Functions executed during a reply, such as generate_oai_reply and check_termination_and_human_reply
        SUMMARY: Summarization of a chat
        REASONING: Agent reasoning step, for advanced agents like ReasoningAgent and CaptainAgent
        SWARM_ON_CONDITION: Swarm-specific, ON_CONDITION hand off
    """

    WORKFLOW = "workflow"
    CHATS = "chats"
    CHAT = "chat"
    NESTED_CHAT = "nested_chat"
    ROUND = "round"
    REPLY = "reply"
    REPLY_FUNCTION = "reply_function"
    SUMMARY = "summary"
    REASONING = "reasoning"
    SWARM_ON_CONDITION = "swarm_on_condition"


class EventKind(Enum):
    """Enumeration of span event kinds

    Events represent a singular point in time within a span, capturing specific moments or actions.

    Descriptions:
        AGENT_TRANSITION: Transition moved from one agent to another
        AGENT_CREATION: Creation of an Agent
        GROUPCHAT_CREATION: Creation of a GroupChat
        LLM_CREATE: LLM execution
        AGENT_SEND_MSG: Agent sending a message to another agent
        TOOL_EXECUTION: Tool or Function execution
        COST: Cost event
        CONSOLE_PRINT: Console output (TBD)
    """

    AGENT_TRANSITION = "agent_transition"
    AGENT_CREATION = "agent_creation"
    GROUPCHAT_CREATION = "groupchat_creation"
    LLM_CREATE = "llm_create"
    AGENT_SEND_MSG = "agent_send_msg"
    TOOL_EXECUTION = "tool_execution"
    COST = "cost"
    CONSOLE_PRINT = "console_print"


@dataclass
class SpanContext:
    """Data class to represent a span (a unit of work within a trace)."""

    kind: SpanKind
    trace_id: str
    timestamp: datetime = None
    parent_span_id: Optional[str] = None
    attributes: Dict[str, Any] = None
    core_span_id: Optional[str] = None

    def __post_init__(self):
        # Timestamps for ordering spans
        self.timestamp = datetime.now()

        if self.attributes is None:
            self.attributes = {}

    def set_attribute(self, key: str, value: Any) -> None:
        """Set/update an attribute."""
        self.attributes[key] = value


@dataclass
class EventContext:
    """Data class to represent a span event (point in time events occurring within a span)."""

    kind: EventKind
    attributes: Dict[str, Any] = None

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}


class TelemetryProvider(ABC):
    """Base class for telemetry providers.

    All telemetry providers are to implement this interface and then be registered
    with the InstrumentationManager.

    Telemetry follows the OpenTelemetry signals terminology of traces, spans, and events. However, it is
    not restricted to OpenTelemetry use and can be used to gather AG2 activity or represent it in other formats,
    such as diagrams or logging to files/databases.

    Trace: Full workflow, including object creations, chats, summaries, etc.
    Span: A unit of work within a trace, such as a chat, round, or agent reply. Spans typically have child spans and events.
    Event: A singular point in time within a span, such as LLM execution, agent creation, agent transition, or cost.

    Multiple providers can be attached to the InstrumentationManager for simultaneous and real-time telemetry.
    """

    @abstractmethod
    def start_trace(self, name: str, core_span_id: str, attributes: Dict[str, Any] = None) -> SpanContext:
        """Start a new trace.

        Args:
            name: User-provided name of the trace
            core_span_id: Unique ID for the trace-level span that's created with a trace
            attributes: Optional attributes for the trace

        Returns:
            SpanContext: The trace-level span
        """
        pass

    @abstractmethod
    def start_span(
        self,
        kind: SpanKind,
        core_span_id: str,
        parent_context: Optional[SpanContext] = None,
        attributes: Dict[str, Any] = None,
    ) -> SpanContext:
        """Start a new span.

        Args:
            kind (SpanKind): The kind of span
            core_span_id (str): Unique ID for the span, determined by the InstrumentationManager and common to the span across all providers
            parent_context (SpanContext or None): Optional parent span context to help maintain hierarchy
                Note: a provider, such as OpenTelemetry, may not require this to maintain hierarchy
            attributes (dict or None): Optional attributes for the span

        Returns:
            SpanContext: The created span context
        """
        pass

    @abstractmethod
    def set_span_attribute(self, context: SpanContext, key: str, value: Any) -> None:
        """Set an attribute on a span.

        Args:
            context (SpanContext): The span context
            key (str): The attribute key
            value (Any): The attribute value
        """
        pass

    @abstractmethod
    def end_span(self, context: SpanContext) -> None:
        """Ends a span.

        Note: Some telemetry providers, like OpenTelemetry, must have an end_span for every start_span to create a valid trace.

        Args:
            context (SpanContext): The span context to end"""
        pass

    @abstractmethod
    def record_event(
        self, span_context: SpanContext, event_name: str, kind: EventKind, attributes: Dict[str, Any] = None
    ) -> None:
        """Record a span event.

        Args:
            span_context (SpanContext): The span context to record the event in
            event_name (str): The name of the event
            kind (EventKind): The kind of event
            attributes (dict or None): Optional attributes for the event
        """
        pass

    @abstractmethod
    def convert_attribute_value(self, value: Any) -> Any:
        """Convert an attribute value to a format suitable for the provider.

        Args:
            value (Any): The value to convert

        Returns:
            Any: The converted value
        """
        pass


class InstrumentationManager:
    """Manager for telemetry providers.

    The InstrumentationManager is the central hub for all telemetry providers. It manages the providers
    and orchestrates the starting, ending, and recording of traces, spans, and events.

    The InstrumentationManager is to be used with the telemetry_context context manager.

    Example:
    ```python
    from autogen.telemetry.telemetry_core import InstrumentationManager, telemetry_context
    instrumentation_manager = InstrumentationManager()
    ... register providers with manager ...

    with telemetry_context(instrumentation_manager, "My Program Name", {"my_program_id": "456"}) as telemetry:
        ... AG2 workflow code here ...

    ```
    """

    def __init__(self):
        # Attached providers
        self._providers: List[TelemetryProvider] = []

        # Thread-local storage for the context stack
        self._thread_local = threading.local()

        # Master set of spans
        self._active_spans: Dict[str, SpanContext] = {}

    def register_provider(self, provider: TelemetryProvider) -> None:
        """Register a telemetry provider with the manager.

        Args:
            provider: The TelemetryProvider instance to register
        """
        self._providers.append(provider)

    def deregister_provider(self, provider: TelemetryProvider) -> bool:
        """Remove a telemetry provider from the manager.

        Args:
            provider: The TelemetryProvider instance to remove

        Returns:
            bool: True if provider was found and removed, False if not found
        """
        try:
            self._providers.remove(provider)
            return True
        except ValueError:
            return False

    def get_current_span(self) -> Optional[SpanContext]:
        """Get the current span from the thread-local stack.

        Returns:
            Optional[SpanContext]: The current span or None if not found
        """
        if not hasattr(self._thread_local, "context_stack"):
            self._thread_local.context_stack = []
        return self._thread_local.context_stack[-1] if self._thread_local.context_stack else None

    def start_trace(self, name: str, attributes: Dict[str, Any] = None) -> SpanContext:
        """Start a new trace and workflow span across all providers.

        Args:
            name: User-provided name of the trace
            attributes: Optional attributes for the trace

        Returns:
            SpanContext: The trace-level span
        """
        if attributes is None:
            attributes = {}

        # Create a single trace context
        trace_id = generate_id(TRACE_ID_BITS)
        core_span_id = generate_id(SPAN_ID_BITS)

        # Create the central span context
        context = SpanContext(
            kind=SpanKind.WORKFLOW,
            trace_id=trace_id,
            core_span_id=core_span_id,
            attributes=attributes,
        )

        # Store the span centrally
        self._active_spans[core_span_id] = context

        # Start trace with each provider
        for provider in self._providers:
            try:
                provider.start_trace(name=name, core_span_id=core_span_id, attributes=attributes)
            except Exception as e:
                print(f"Error in provider {provider.__class__.__name__}: {e}")

        # Store master context in thread local stack
        if not hasattr(self._thread_local, "context_stack"):
            self._thread_local.context_stack = []
        self._thread_local.context_stack.append(context)

        return context

    def start_span(
        self, kind: SpanKind, parent_context: Optional[SpanContext] = None, attributes: Dict[str, Any] = None
    ) -> SpanContext:
        """Start a new span,with an optional explicit parent context, across all providers.

        If parent_context is not provided, uses the current span from the stack.

        Args:
            kind (SpanKind): The kind of span
            parent_context (SpanContext): Optional parent span context
            attributes (dict): Optional attributes for the span
        """

        # DEBUGGING - FOR ENSURING CORRECT NUMBER OF SPANS - CAN BE REMOVED WHEN PR FINALISED
        _spans_started.set(_spans_started.get() + 1)

        # Use provided parent_context or get from stack
        effective_parent = parent_context if parent_context is not None else self.get_current_span()

        # Generate unified IDs
        core_span_id = generate_id(SPAN_ID_BITS)

        # Create central span context
        context = SpanContext(
            kind=kind,
            trace_id=effective_parent.trace_id if effective_parent else None,
            parent_span_id=effective_parent.core_span_id if effective_parent else None,
            attributes=attributes,
            core_span_id=core_span_id,
        )

        # Store span centrally
        self._active_spans[core_span_id] = context

        # Start span in each provider
        for provider in self._providers:
            try:
                provider.start_span(
                    kind=kind, core_span_id=core_span_id, parent_context=effective_parent, attributes=attributes
                )
            except Exception as e:
                print(f"Error in provider {provider.__class__.__name__}: {e}")

        # Add to thread local stack
        if not hasattr(self._thread_local, "context_stack"):
            self._thread_local.context_stack = []
        self._thread_local.context_stack.append(context)

        return context

    def set_attribute(self, span_context: SpanContext, key: str, value: Any) -> None:
        """Set an attribute on a span across all providers.

        Args:
            span_context: The span context to set the attribute on
            key: The attribute key
            value: The attribute value
        """
        if span_context:
            # Update master span
            span = self._active_spans.get(span_context.core_span_id)
            if span:
                span.set_attribute(key, value)

            # Propagate to each provider
            for provider in self._providers:
                try:
                    provider.set_span_attribute(span_context, key, value)
                except Exception as e:
                    print(f"Error in provider {provider.__class__.__name__}: {e}")

    def end_span(self) -> None:
        """End the current span across all providers."""
        if not hasattr(self._thread_local, "context_stack"):
            return

        # DEBUGGING - FOR ENSURING CORRECT NUMBER OF SPANS - CAN BE REMOVED WHEN PR FINALISED
        _spans_ended.set(_spans_ended.get() + 1)

        if self._thread_local.context_stack:
            context = self._thread_local.context_stack.pop()

            # Remove from central management
            if context.core_span_id in self._active_spans:
                del self._active_spans[context.core_span_id]

            # End in each provider
            for provider in self._providers:
                try:
                    provider.end_span(context)
                except Exception as e:
                    print(f"Error in provider {provider.__class__.__name__}: {e}")

    def record_event(self, event_kind: EventKind, attributes: Dict[str, Any] = None) -> None:
        """Record an event in the current span across all providers.

        Args:
            event_kind (EventKind): The kind of event
            attributes (dict): Optional attributes for the event
        """
        current_span = self.get_current_span()
        if current_span:
            for provider in self._providers:
                try:
                    provider.record_event(current_span, event_kind, attributes)
                except Exception as e:
                    print(f"Error in provider {provider.__class__.__name__}: {e}")


@contextmanager
def telemetry_context(manager: InstrumentationManager, trace_name: str = None, trace_attributes: Dict[str, Any] = None):
    """Context manager that automatically starts and ends a trace.

    Args:
        manager: The InstrumentationManager instance
        trace_name: Optional name for the trace. Defaults to 'AG2 Workflow'
        trace_attributes: Optional attributes for the trace
    """
    # Set the current telemetry manager in the context
    token = _current_telemetry.set(manager)
    try:
        # Start the trace automatically
        trace_name = trace_name or "AG2 Workflow"
        trace_attributes = trace_attributes or {}
        manager.start_trace(trace_name, trace_attributes)
        yield manager
    finally:
        # End all remaining spans in the stack
        while hasattr(manager._thread_local, "context_stack") and manager._thread_local.context_stack:
            manager.end_span()
        # Reset the context
        _current_telemetry.reset(token)


# STATIC METHODS


@staticmethod
def generate_id(bits: int) -> str:
    """Generate a random ID of specified bit length.

    Creates a random identifier by generating a UUID4 and masking it to the desired bit length.
    The result is formatted as a lowercase hex string with the appropriate number of leading zeros.

    Based on the requirement for OpenTelemetry trace and span IDs.

    Args:
        bits: Number of bits for the ID (e.g. 128 for trace ID, 64 for span ID)

    Returns:
        str: Hex string representation of the ID with appropriate length (bits/4 characters)

    Examples:
        >>> InstrumentationManager.generate_id(128)  # For trace ID
        'a1b2c3d4e5f67890a1b2c3d4e5f67890'
        >>> InstrumentationManager.generate_id(64)   # For span ID
        'a1b2c3d4e5f67890'
    """
    hex_chars = bits // 4  # Each hex char represents 4 bits
    return format(uuid.uuid4().int & ((1 << bits) - 1), f"0{hex_chars}x")


@staticmethod
def _is_list_of_string_dicts(item: Any) -> bool:
    """Check if an object is a list of dictionaries with string values, for handling messages

    Args:
        item: The object to check

    Returns:
        bool: True if the object is a list of dictionaries with string values, False otherwise
    """
    if not isinstance(item, list):
        return False
    if not all(isinstance(d, dict) for d in item):
        return False
    return all(isinstance(key, str) and isinstance(value, str) for d in item for key, value in d.items())


# DEBUG - FOR ENSURING CORRECT NUMBER OF SPANS STARTED AND ENDED - CAN BE REMOVED WHEN PR REVIEWED
_spans_started: ContextVar[int] = ContextVar("spans_started", default=0)
_spans_ended: ContextVar[int] = ContextVar("spans_ended", default=0)


def get_spans_started() -> int:
    return _spans_started.get()


def get_spans_ended() -> int:
    return _spans_ended.get()


# DEBUG
