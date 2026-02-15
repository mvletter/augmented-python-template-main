import os
import re
from collections import defaultdict
from functools import lru_cache

from opentelemetry.context import Context
from opentelemetry.sdk.trace import ReadableSpan, Span
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv._incubating.attributes.peer_attributes import PEER_SERVICE


class SpanChildCountProcessorMixin:
    """
    Track "child_span_count" which adds an attribute with the number of
    local child spans. This can be used to query big traces in Tempo.
    """

    _span_counts: dict[int, int] = defaultdict(int)

    def on_start(self, span: Span, parent_context: Context | None) -> None:
        if span.parent and not span.parent.is_remote:
            self._span_counts[span.context.trace_id] += 1
        super().on_start(span)

    def on_end(self, span: ReadableSpan) -> None:
        if span.parent is None or span.parent.is_remote:
            span_count = self._span_counts.pop(span.context.trace_id, 0)
            if span_count:
                # `set_attribute` doesn't work in `on_end`.
                span._attributes["child_span_count"] = span_count

        super().on_end(span)


class PeerSpanProcessor(SpanChildCountProcessorMixin, BatchSpanProcessor):
    EXCLUDED_SPAN_NAMES = ["PING"]
    EXCLUDED_NONE_PARENT_SPAN_NAMES = ["connect", "SELECT.*"]

    def on_start(self, span: Span, parent_context: Context | None = None) -> None:
        """
        Add peer service attribute to spans when they are intrumented by sqlachemy or redis.
        This is needed by tempo to generate the service graph properly.
        """
        if span.instrumentation_scope.name == "opentelemetry.instrumentation.sqlalchemy":
            span.set_attribute(PEER_SERVICE, f"{span.resource.attributes['service.name']}-db")
        elif span.instrumentation_scope.name == "opentelemetry.instrumentation.redis":
            span.set_attribute(PEER_SERVICE, f"{span.resource.attributes['service.name']}-redis")
        super().on_start(span, parent_context)

    @lru_cache
    def _get_excluded_span_names(self) -> list[str]:
        """
        Get a list of span names to exclude from tracing.
        List of spans found in the `TRACING_EXCLUDED_SPAN_NAMES` environment variable will be appended to the
        default values.
        The value of the environment variable must be a comma separated list of regexes.
        """
        env_excluded_names = os.getenv("TRACING_EXCLUDED_SPAN_NAMES", "")
        if not env_excluded_names:
            return self.EXCLUDED_SPAN_NAMES
        if env_excluded_names.endswith(","):
            env_excluded_names = env_excluded_names[:-1]
        list_of_excluded = self.EXCLUDED_SPAN_NAMES + env_excluded_names.split(",")
        return list_of_excluded

    @lru_cache
    def _get_excluded_none_parent_span_names(self) -> list[str]:
        """
        Get a list of span names which will be excluded from tracing if they don't have a parent.
        List of spans found in the `TRACING_EXCLUDED_NONE_PARENT_SPAN_NAMES` environment variable will be appended to
        the default values.
        The value of the environment variable must be a comma separated list of regexes.
        """
        env_excluded_names = os.getenv("TRACING_EXCLUDED_NONE_PARENT_SPAN_NAMES", "")
        if not env_excluded_names:
            return self.EXCLUDED_NONE_PARENT_SPAN_NAMES
        if env_excluded_names.endswith(","):
            env_excluded_names = env_excluded_names[:-1]
        list_of_excluded = self.EXCLUDED_NONE_PARENT_SPAN_NAMES + env_excluded_names.split(",")
        return list_of_excluded

    def on_end(self, span: ReadableSpan) -> None:
        """
        Exclude spans from tracing based on their name.
        Spans which name is matching the regex list from `_get_excluded_span_names` will be excluded.
        Spans which name is matching the regex list from `_get_excluded_none_parent_span_names` and don't have
        a parent will also be excluded.
        """
        for regex in self._get_excluded_span_names():
            if re.match(regex, span.name):
                return
        for regex in self._get_excluded_none_parent_span_names():
            if re.match(regex, span.name) and span.parent is None:
                return
        super().on_end(span)
