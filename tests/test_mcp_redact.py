"""Tests for tju.mcp.redact — profile PII masking."""

from __future__ import annotations

import pytest

pytest.importorskip("mcp", reason="tju[mcp] extra not installed")

from tju.mcp.redact import (  # noqa: E402
    SENSITIVE_FIELDS,
    _partial_mask,
    mask_profile,
    should_reveal_pii,
)


# ---------------------------------------------------------------------------
# _partial_mask
# ---------------------------------------------------------------------------


def test_partial_mask_student_id():
    assert "****" in _partial_mask("2024000001")


def test_partial_mask_phone():
    masked = _partial_mask("13812345678")
    assert "****" in masked
    assert "13812345678" not in masked  # full value must not appear


def test_partial_mask_short():
    assert _partial_mask("abc") == "***"


def test_partial_mask_preserves_prefix_and_suffix():
    result = _partial_mask("2024000001")
    # Prefix and suffix of the original should still appear somewhere
    assert result.startswith("20")
    assert result.endswith("01")


# ---------------------------------------------------------------------------
# mask_profile
# ---------------------------------------------------------------------------


_SAMPLE_PROFILE = {
    "stu_id": "2024000001",
    "stu_name": "张三",
    "faculty": "计算机学院",
    "email": "zhangsan@tju.edu.cn",
    "phone": "13812345678",
    "mobile": "13900000001",
    "home_address": "天津市南开区",
    "home_address_zip": "300071",
    "home_phone": "02212345678",
    "address": "天津市北洋园校区宿舍",
}


def test_mask_profile_hides_sensitive_by_default():
    result = mask_profile(_SAMPLE_PROFILE, reveal=False)
    for field in SENSITIVE_FIELDS:
        if field in _SAMPLE_PROFILE and _SAMPLE_PROFILE[field]:
            assert result[field] != _SAMPLE_PROFILE[field], (
                f"Field '{field}' should be masked but was not"
            )


def test_mask_profile_preserves_non_sensitive():
    result = mask_profile(_SAMPLE_PROFILE, reveal=False)
    assert result["stu_name"] == "张三"
    assert result["faculty"] == "计算机学院"


def test_mask_profile_reveal_true_returns_all():
    result = mask_profile(_SAMPLE_PROFILE, reveal=True)
    assert result["stu_id"] == "2024000001"
    assert result["email"] == "zhangsan@tju.edu.cn"
    assert result["phone"] == "13812345678"


def test_mask_profile_none_values_unchanged():
    data = {"stu_id": None, "stu_name": "李四", "phone": None}
    result = mask_profile(data, reveal=False)
    assert result["stu_id"] is None
    assert result["phone"] is None
    assert result["stu_name"] == "李四"


# ---------------------------------------------------------------------------
# should_reveal_pii
# ---------------------------------------------------------------------------


def test_should_reveal_pii_default_false(monkeypatch, tmp_path):
    monkeypatch.setenv("TJU_CONFIG_DIR", str(tmp_path))
    monkeypatch.delenv("TJU_MCP_REVEAL_PII", raising=False)
    assert should_reveal_pii() is False


def test_should_reveal_pii_env_true(monkeypatch, tmp_path):
    monkeypatch.setenv("TJU_CONFIG_DIR", str(tmp_path))
    monkeypatch.setenv("TJU_MCP_REVEAL_PII", "1")
    assert should_reveal_pii() is True


def test_should_reveal_pii_env_false(monkeypatch, tmp_path):
    monkeypatch.setenv("TJU_CONFIG_DIR", str(tmp_path))
    monkeypatch.setenv("TJU_MCP_REVEAL_PII", "false")
    assert should_reveal_pii() is False


def test_should_reveal_pii_config_file(monkeypatch, tmp_path):
    monkeypatch.setenv("TJU_CONFIG_DIR", str(tmp_path))
    monkeypatch.delenv("TJU_MCP_REVEAL_PII", raising=False)
    import tju.config as cfg  # noqa: PLC0415
    cfg.set_preference("mcp_reveal_pii", True)
    assert should_reveal_pii() is True
