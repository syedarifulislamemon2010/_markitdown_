# -*- coding: utf-8 -*-
"""
Workspace Security and Path Traversal Attack Prevention Tests.
Verifies that the workspace backend enforces strict containment within workspace root,
blocking directory traversal attempts (../../, absolute system paths, etc.).
"""

import os
import tempfile
import requests
import pytest


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create some nested files and folders
        sub = os.path.join(tmpdir, "notes")
        os.makedirs(sub, exist_ok=True)
        file1 = os.path.join(tmpdir, "welcome.md")
        with open(file1, "w", encoding="utf-8") as f:
            f.write("# Welcome to Workspace\n\nContent here.")

        file2 = os.path.join(sub, "todo.txt")
        with open(file2, "w", encoding="utf-8") as f:
            f.write("- Task 1\n- Task 2")

        yield tmpdir


def test_workspace_tree_retrieval(server_url, temp_workspace):
    """Verify recursive directory tree generation."""
    resp = requests.get(f"{server_url}/api/workspace/tree?path={temp_workspace}", timeout=5.0)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["name"] == os.path.basename(temp_workspace)
    assert len(data["tree"]) >= 2
    names = [item["name"] for item in data["tree"]]
    assert "welcome.md" in names
    assert "notes" in names


def test_workspace_file_read_and_save(server_url, temp_workspace):
    """Verify safe read and in-place save back (Ctrl+S) inside workspace."""
    # 1. Read
    resp = requests.get(
        f"{server_url}/api/workspace/file?path=welcome.md&root={temp_workspace}",
        timeout=5.0
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "# Welcome to Workspace" in data["content"]

    # 2. Save back modified content
    new_content = "# Welcome to Workspace\n\nUpdated via Ctrl+S!"
    save_resp = requests.post(
        f"{server_url}/api/workspace/save",
        json={"root": temp_workspace, "path": "welcome.md", "content": new_content},
        timeout=5.0
    )
    assert save_resp.status_code == 200
    assert save_resp.json()["success"] is True

    # 3. Verify on disk
    with open(os.path.join(temp_workspace, "welcome.md"), "r", encoding="utf-8") as f:
        assert f.read() == new_content


def test_path_traversal_read_blocked(server_url, temp_workspace):
    """Verify directory traversal attack on /api/workspace/file returns 403 Forbidden."""
    traversal_paths = [
        "../../../../Windows/System32/drivers/etc/hosts",
        "../" * 10 + "etc/passwd",
        "C:\\Windows\\System32\\calc.exe",
        "/etc/shadow",
    ]
    for bad_path in traversal_paths:
        resp = requests.get(
            f"{server_url}/api/workspace/file?path={bad_path}&root={temp_workspace}",
            timeout=5.0
        )
        assert resp.status_code == 403, f"Expected 403 for path traversal attempt: {bad_path}"
        data = resp.json()
        assert data["success"] is False
        assert "Path traversal detected" in data["error"]


def test_path_traversal_save_blocked(server_url, temp_workspace):
    """Verify directory traversal attack on /api/workspace/save returns 403 Forbidden."""
    resp = requests.post(
        f"{server_url}/api/workspace/save",
        json={"root": temp_workspace, "path": "../../evil.txt", "content": "malicious payload"},
        timeout=5.0
    )
    assert resp.status_code == 403
    assert resp.json()["success"] is False
    assert "Path traversal detected" in resp.json()["error"]


def test_path_traversal_file_op_blocked(server_url, temp_workspace):
    """Verify directory traversal attack on /api/workspace/file-op returns 403 Forbidden."""
    resp = requests.post(
        f"{server_url}/api/workspace/file-op",
        json={"action": "delete", "root": temp_workspace, "path": "../../../system_file"},
        timeout=5.0
    )
    assert resp.status_code == 403
    assert resp.json()["success"] is False
    assert "Path traversal detected" in resp.json()["error"]


def test_workspace_file_operations(server_url, temp_workspace):
    """Verify safe create, rename, and delete inside workspace root."""
    # 1. Create file
    create_resp = requests.post(
        f"{server_url}/api/workspace/file-op",
        json={"action": "create_file", "root": temp_workspace, "path": "new_doc.md"},
        timeout=5.0
    )
    assert create_resp.status_code == 200
    assert create_resp.json()["success"] is True
    assert os.path.exists(os.path.join(temp_workspace, "new_doc.md"))

    # 2. Rename file
    rename_resp = requests.post(
        f"{server_url}/api/workspace/file-op",
        json={"action": "rename", "root": temp_workspace, "path": "new_doc.md", "new_name": "renamed_doc.md"},
        timeout=5.0
    )
    assert rename_resp.status_code == 200
    assert rename_resp.json()["success"] is True
    assert not os.path.exists(os.path.join(temp_workspace, "new_doc.md"))
    assert os.path.exists(os.path.join(temp_workspace, "renamed_doc.md"))

    # 3. Delete file
    del_resp = requests.post(
        f"{server_url}/api/workspace/file-op",
        json={"action": "delete", "root": temp_workspace, "path": "renamed_doc.md"},
        timeout=5.0
    )
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True
    assert not os.path.exists(os.path.join(temp_workspace, "renamed_doc.md"))


def test_workspace_git_status(server_url):
    """Verify git status endpoint returns valid repository branch info."""
    resp = requests.get(f"{server_url}/api/workspace/git-status", timeout=5.0)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "is_git" in data
    assert "branch" in data
    assert "dirty" in data
