#!/usr/bin/env python3
"""Fail when repository text contains private paths, run artifacts, or likely secrets."""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path


SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".wheel-check",
    ".install-check",
    "build",
    "dist",
}
TEXT_SUFFIXES = {
    "", ".cff", ".css", ".html", ".ini", ".json", ".md", ".py", ".toml",
    ".txt", ".yaml", ".yml",
}


@dataclass(frozen=True)
class Check:
    code: str
    expression: re.Pattern[str]
    message: str


checks = [
    Check("local-file-uri", re.compile("file" + r":/{3}", re.I), "local file URI"),
    Check("private-drive-g", re.compile(r"\b[gG]:[\\/]"), "G drive absolute path"),
    Check("private-user-path", re.compile(r"\b[cC]:[\\/]Users[\\/]"), "Windows user path"),
    Check("agent-artifact", re.compile("agent" + r"-run", re.I), "agent run artifact"),
    Check(
        "output" + "-artifact",
        re.compile("output" + r"-(?!dir\b)[\w.-]+(?:[\\/]|[\"'])", re.I),
        "generated output directory",
    ),
    Check(
        "temporary-mmbiz-url",
        re.compile(r"https?://mmbiz[.]qpic[.]cn/[^\s)>'\"]+", re.I),
        "embedded mmbiz experiment URL",
    ),
    Check("private-key", re.compile("BEGIN " + r"(?:RSA |EC |OPENSSH )?PRIVATE KEY"), "private key"),
    Check("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key"),
    Check("github-token", re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"), "GitHub token"),
    Check(
        "assigned-secret",
        re.compile(
            r"(?i)\b(?:api[_-]?key|client[_-]?secret|access[_-]?token|password)\b"
            r"\s*[:=]\s*['\"][^'\"\s]{8,}['\"]"
        ),
        "assigned secret-like value",
    ),
]


def scan(root: Path) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for current, directories, files in os.walk(root):
        current_path = Path(current)
        directories[:] = sorted(
            directory
            for directory in directories
            if directory not in SKIP_DIRS
            and not (current_path / directory / "pyvenv.cfg").is_file()
        )
        for filename in sorted(files):
            path = current_path / filename
            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for number, line in enumerate(text.splitlines(), 1):
                for check in checks:
                    if check.expression.search(line):
                        findings.append(
                            {
                                "file": path.relative_to(root).as_posix(),
                                "line": number,
                                "code": check.code,
                                "message": check.message,
                            }
                        )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    findings = scan(root)
    report = {"root": root.name, "files_clean": not findings, "findings": findings}
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif findings:
        for item in findings:
            print(f"{item['file']}:{item['line']} {item['code']}: {item['message']}")
    else:
        print("repository hygiene: pass")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
