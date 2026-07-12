"""Tests that verify production high-availability defaults are set correctly."""

from __future__ import annotations

import pytest

from app.core.config.settings import Settings
from app.modules.proxy.ring_membership import RING_STALE_THRESHOLD_SECONDS

pytestmark = pytest.mark.unit


def test_ring_stale_threshold_is_30_seconds() -> None:
    assert RING_STALE_THRESHOLD_SECONDS == 30


def test_admission_wait_timeout_default_is_10_seconds() -> None:
    s = Settings()
    assert s.proxy_admission_wait_timeout_seconds == 10.0


def test_http_bridge_liveness_defaults_enable_heartbeat_and_auto_progress_timeout() -> None:
    settings = Settings()

    assert settings.proxy_upstream_websocket_heartbeat_seconds == 20.0
    assert settings.http_responses_session_bridge_response_created_timeout_seconds == 0.0
