"""ci/policy_check.py の回帰テスト。"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


def _load_policy_check_module():
    """policy_check モジュールをファイルパスから読み込む。"""
    module_path = Path(__file__).resolve().parent.parent / "ci" / "policy_check.py"
    spec = importlib.util.spec_from_file_location("policy_check", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("policy_check.py の読み込みに失敗しました")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _build_freeze_doc_text(version: str, extra_line: str = "") -> str:
    """必須要素を満たした凍結仕様ドキュメント本文を生成する。"""
    extra_block = f"\n{extra_line}\n" if extra_line else "\n"
    return (
        "# SEC系Issueトリアージ 仕様凍結版\n\n"
        "## 2. 確定仕様\n"
        "- 実装ファイル: .github/workflows/sec011-issue-triage.yml\n"
        "- 実装ファイル: .github/workflows/security-issue-triage-report.yml\n\n"
        "## 4. 凍結方針\n"
        "- シンプル運用を維持する\n\n"
        "## 5. 変更管理\n"
        "- 参照: docs/development.md\n"
        "- 参照: README.md\n"
        f"{extra_block}"
        "## 6. 変更履歴\n\n"
        f"- {version} (2026-03-05)\n"
        "  - テスト用変更履歴\n"
    )


@pytest.mark.parametrize(
    ("current_text", "previous_text", "expected_has_message"),
    [
        pytest.param(
            _build_freeze_doc_text("v1.0", "- 追加仕様A"),
            _build_freeze_doc_text("v1.0"),
            True,
            id="変更あり_版据え置きで失敗",
        ),
        pytest.param(
            _build_freeze_doc_text("v1.1", "- 追加仕様A"),
            _build_freeze_doc_text("v1.0"),
            False,
            id="変更あり_版増分で成功",
        ),
        pytest.param(
            _build_freeze_doc_text("v1.0"),
            _build_freeze_doc_text("v1.0"),
            False,
            id="変更なし_版据え置きで成功",
        ),
    ],
)
def test_scan_sec_triage_spec_freeze_版番号増分ルール(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    current_text: str,
    previous_text: str,
    expected_has_message: bool,
) -> None:
    """凍結仕様変更時は変更履歴の版番号増分が必要であることを確認する。"""
    policy_check = _load_policy_check_module()

    repo_root = tmp_path
    target = repo_root / "docs" / "sec-triage-spec-freeze.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(current_text, encoding="utf-8")

    monkeypatch.setattr(policy_check, "REPO_ROOT", repo_root)
    monkeypatch.setattr(policy_check, "git_show_text", lambda _rev, _path: previous_text)

    issues = policy_check.scan_sec_triage_spec_freeze(target)
    has_version_issue = any("版番号を増分" in issue for issue in issues)

    assert has_version_issue is expected_has_message
