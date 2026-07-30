from pathlib import Path

import pytest

from agent.errors import SecurityError
from agent.tools.filesystem import SafeFilesystem


def test_read_write_and_listing(tmp_path: Path) -> None:
    fs = SafeFilesystem(tmp_path)
    fs.write_file("nested/a.txt", "hello", create_only=True)
    assert fs.read_file("nested/a.txt") == "hello"
    assert fs.list_directory("nested") == ["a.txt"]


def test_path_traversal_is_rejected(tmp_path: Path) -> None:
    fs = SafeFilesystem(tmp_path)
    with pytest.raises(SecurityError):
        fs.resolve("../outside", must_exist=False)


def test_absolute_outside_path_is_rejected(tmp_path: Path) -> None:
    fs = SafeFilesystem(tmp_path)
    with pytest.raises(SecurityError):
        fs.resolve(tmp_path.parent / "outside", must_exist=False)


def test_binary_and_size_limits(tmp_path: Path) -> None:
    (tmp_path / "binary").write_bytes(b"a\x00b")
    (tmp_path / "large").write_text("12345", encoding="utf-8")
    fs = SafeFilesystem(tmp_path, max_file_size=4)
    with pytest.raises(SecurityError):
        fs.read_file("binary")
    with pytest.raises(SecurityError):
        fs.read_file("large")


def test_symlink_escape_is_rejected(tmp_path: Path) -> None:
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir()
    (outside / "secret").write_text("no", encoding="utf-8")
    link = tmp_path / "link"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("Symlinks unavailable on this platform")
    with pytest.raises(SecurityError):
        SafeFilesystem(tmp_path).read_file("link/secret")
