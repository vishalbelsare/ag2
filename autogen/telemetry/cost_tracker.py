# Copyright (c) 2023 - 2024, Owners of https://github.com/ag2ai
#
# SPDX-License-Identifier: Apache-2.0

import json
from typing import Any, Dict, Optional

from .telemetry_core import EventKind, SpanContext, SpanKind, TelemetryProvider, _is_list_of_string_dicts


class CostTrackerProvider(TelemetryProvider):
    def __init__(self):
        self.cost_history = []  # History of cost events, contains dictionary of attributes
        self.total_cost = 0.0

    def start_trace(self, name: str, attributes: Dict[str, Any] = None) -> SpanContext:
        pass

    def start_span(
        self,
        kind: SpanKind,
        core_span_id: str,
        parent_context: Optional[SpanContext] = None,
        attributes: Dict[str, Any] = None,
    ) -> SpanContext:
        pass

    def set_span_attribute(self, context: SpanContext, key: str, value: Any) -> None:
        pass

    def end_span(self, context: SpanContext) -> None:
        pass

    def record_event(self, span_context: SpanContext, event_kind: EventKind, attributes: Dict[str, Any] = None) -> None:
        if event_kind == EventKind.COST:
            cost = attributes.get("ag2.cost")

            # Convert attributes to OpenTelemetry compatible formats
            formatted_attributes = {key: self.convert_attribute_value(value) for key, value in attributes.items()}

            if cost is not None:
                self.cost_history.append(formatted_attributes)
                self.total_cost += cost

    def convert_attribute_value(self, value: Any) -> Any:
        """Convert attributes for storage in a dictionary"""
        if isinstance(value, str):
            return value
        if isinstance(value, int):
            return value
        if isinstance(value, bool):
            return value
        if _is_list_of_string_dicts(value) or isinstance(value, dict):
            # Typical messages
            return json.dumps(value)
        return str(value)
