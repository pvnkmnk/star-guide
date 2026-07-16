"""Integration tests for main() pipeline orchestration."""
import sys
import sqlite3
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


# ── Helper: create a minimal valid STAR-GUIDE for main() to parse ──

MINIMAL_STAR_GUIDE = """# Part I: The Catalog

## 🤖 Agentic Dev Tools

| [existing/tool](https://github.com/existing/tool) | 1,000 | Python | An existing tool | |

## 💻 Dev Tools & Languages

| [another/app](https://github.com/another/app) | 500 | Go | Another app | |

# Part II

## 🤖 Agentic Dev Top 10

Some top-10 content.
"""


@pytest.fixture
def integration_env(tmp_path, monkeypatch):
    """Set up a temp environment for integration testing main()."""
    # Create STAR-GUIDE.md
    sg = tmp_path / "STAR-GUIDE.md"
    sg.write_text(MINIMAL_STAR_GUIDE, encoding="utf-8")

    # Point STARS_DIR to tmp_path
    monkeypatch.setattr("update_stars.STARS_DIR", tmp_path)

    # Prevent CACHE_DB.exists() from failing
    fake_db = tmp_path / "stars.db"
    fake_db.touch()
    monkeypatch.setattr("update_stars.CACHE_DB", fake_db)

    # Mock fetch_stars to no-op
    monkeypatch.setattr("update_stars.fetch_stars", lambda: None)

    # Create an in-memory SQLite DB with test data
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE repos (
            full_name TEXT PRIMARY KEY, stars INTEGER, language TEXT,
            description TEXT, html_url TEXT, created_at TEXT,
            updated_at TEXT, username TEXT
        )
    """)
    conn.execute(
        "INSERT INTO repos VALUES (?,?,?,?,?,?,?,?)",
        ("new/repo", 5000, "Python", "A brand new repo for testing",
         "https://github.com/new/repo", "2026-01-01", "2026-07-01", "pvnkmnk"),
    )
    conn.execute(
        "INSERT INTO repos VALUES (?,?,?,?,?,?,?,?)",
        ("also/new", 100, "Rust", "Also new, lower stars",
         "https://github.com/also/new", "2026-01-01", "2026-07-01", "pvnkmnk"),
    )
    # Also include the two repos already in STAR-GUIDE (should be excluded)
    conn.execute(
        "INSERT INTO repos VALUES (?,?,?,?,?,?,?,?)",
        ("existing/tool", 1000, "Python", "An existing tool",
         "https://github.com/existing/tool", "2025-01-01", "2026-01-01", "pvnkmnk"),
    )
    conn.execute(
        "INSERT INTO repos VALUES (?,?,?,?,?,?,?,?)",
        ("another/app", 500, "Go", "Another app",
         "https://github.com/another/app", "2025-01-01", "2026-01-01", "pvnkmnk"),
    )
    # Auto-curation candidate: has agentic phrases ("mcp server", "ai coding")
    conn.execute(
        "INSERT INTO repos VALUES (?,?,?,?,?,?,?,?)",
        ("agent/mcp-server", 3000, "Python",
         "An MCP server for AI coding agents",
         "https://github.com/agent/mcp-server", "2026-01-01", "2026-07-01", "pvnkmnk"),
    )
    conn.commit()

    # Mock get_db_connection to return our in-memory DB
    def _mock_conn():
        return conn

    monkeypatch.setattr("update_stars.get_db_connection", _mock_conn)

    yield tmp_path, conn
    # main() closes conn; in-memory DB is cleaned up by GC


class TestMainSuggestOnly:
    """main() with --no-fetch --suggest-only."""

    def test_generates_categorization_suggestions(self, integration_env, monkeypatch):
        """--suggest-only writes CATEGORIZATION-SUGGESTIONS.md with new repos only."""
        tmp_path, conn = integration_env

        # Args: --no-fetch --suggest-only
        monkeypatch.setattr(sys, "argv", ["update_stars.py", "--no-fetch", "--suggest-only"])

        from update_stars import main
        main()

        # Verify: CATEGORIZATION-SUGGESTIONS.md was created
        suggestions = tmp_path / "CATEGORIZATION-SUGGESTIONS.md"
        assert suggestions.exists()

        content = suggestions.read_text(encoding="utf-8")
        # Only the 2 NEW repos should appear (not existing/tool or another/app)
        assert "new/repo" in content
        assert "also/new" in content
        assert "existing/tool" not in content  # already in STAR-GUIDE
        assert "another/app" not in content    # already in STAR-GUIDE

        # Verify: no other output files were created (suggest-only skips regeneration)
        assert not (tmp_path / "NOT-CURATED.md").exists()
        assert not (tmp_path / "AGENT-GUIDE.md").exists()
        assert not (tmp_path / "CHEATSHEET.md").exists()

    def test_suggest_only_with_dry_run_no_file_writes(self, integration_env, monkeypatch):
        """--dry-run with --suggest-only prints but doesn't write files."""
        tmp_path, conn = integration_env

        monkeypatch.setattr(
            sys, "argv",
            ["update_stars.py", "--no-fetch", "--suggest-only", "--dry-run"],
        )

        from update_stars import main
        main()

        # No files should be created in dry-run mode
        assert not (tmp_path / "CATEGORIZATION-SUGGESTIONS.md").exists()


class TestMainFullPipeline:
    """main() with --no-fetch (full pipeline: NOT-CURATED, guides, export)."""

    def test_full_pipeline_produces_all_output_files(self, integration_env, monkeypatch):
        """--no-fetch runs the full pipeline and writes all expected output files."""
        tmp_path, conn = integration_env

        monkeypatch.setattr(sys, "argv", ["update_stars.py", "--no-fetch"])

        from update_stars import main
        main()

        # NOT-CURATED.md: should list the 2 new repos
        nc = tmp_path / "NOT-CURATED.md"
        assert nc.exists()
        nc_content = nc.read_text(encoding="utf-8")
        assert "new/repo" in nc_content
        assert "also/new" in nc_content
        # Should be sorted by stars: new/repo (5000) before also/new (100)
        assert nc_content.index("new/repo") < nc_content.index("also/new")

        # CATEGORIZATION-SUGGESTIONS.md
        suggestions = tmp_path / "CATEGORIZATION-SUGGESTIONS.md"
        assert suggestions.exists()

        # AGENT-GUIDE.md: should include repos from STAR-GUIDE sections + DB
        agent = tmp_path / "AGENT-GUIDE.md"
        assert agent.exists()
        agent_content = agent.read_text(encoding="utf-8")
        assert "existing/tool" in agent_content
        assert "another/app" in agent_content
        assert "🤖|" in agent_content

        # CHEATSHEET.md
        cheatsheet = tmp_path / "CHEATSHEET.md"
        assert cheatsheet.exists()
        assert "existing/tool" in cheatsheet.read_text(encoding="utf-8")

        # CSV + TXT exports
        csv = tmp_path / "star-guide-pvnkmnk.csv"
        txt = tmp_path / "star-guide-pvnkmnk.txt"
        assert csv.exists()
        assert txt.exists()

    def test_full_pipeline_dry_run_no_file_writes(self, integration_env, monkeypatch):
        """--dry-run with --no-fetch prints but doesn't write any files."""
        tmp_path, conn = integration_env

        monkeypatch.setattr(
            sys, "argv",
            ["update_stars.py", "--no-fetch", "--dry-run"],
        )

        from update_stars import main
        main()

        # No output files should be created (dry-run stops before writes)
        assert not (tmp_path / "NOT-CURATED.md").exists()
        assert not (tmp_path / "AGENT-GUIDE.md").exists()
        assert not (tmp_path / "CHEATSHEET.md").exists()
        assert not (tmp_path / "CATEGORIZATION-SUGGESTIONS.md").exists()

    def test_no_new_repos_skips_not_curated_write(self, integration_env, monkeypatch):
        """When all DB repos are already in STAR-GUIDE, NOT-CURATED is not written."""
        tmp_path, conn = integration_env

        # Remove ALL new repos from DB — only existing STAR-GUIDE repos remain
        conn.execute("DELETE FROM repos WHERE full_name NOT IN ('existing/tool', 'another/app')")
        conn.commit()

        monkeypatch.setattr(sys, "argv", ["update_stars.py", "--no-fetch"])

        from update_stars import main
        main()

        # NOT-CURATED should NOT be created (no new repos)
        assert not (tmp_path / "NOT-CURATED.md").exists()

        # Guides should still regenerate (existing repos in STAR-GUIDE)
        assert (tmp_path / "AGENT-GUIDE.md").exists()
        assert (tmp_path / "CHEATSHEET.md").exists()

    def test_auto_curate_inserts_repos_into_star_guide(self, integration_env, monkeypatch):
        """--no-fetch --auto-curate 2: all new repos auto-curate at low threshold."""
        tmp_path, conn = integration_env

        monkeypatch.setattr(
            sys, "argv",
            ["update_stars.py", "--no-fetch", "--auto-curate", "2"],
        )

        from update_stars import main
        main()

        # STAR-GUIDE was modified (all 3 new repos inserted into sections)
        sg = tmp_path / "STAR-GUIDE.md"
        sg_content = sg.read_text(encoding="utf-8")
        assert "agent/mcp-server" in sg_content
        assert "new/repo" in sg_content
        assert "also/new" in sg_content

        # NOT-CURATED should NOT exist (all repos auto-curated, none left)
        assert not (tmp_path / "NOT-CURATED.md").exists()

        # Guides should include the auto-curated repos
        agent = tmp_path / "AGENT-GUIDE.md"
        agent_content = agent.read_text(encoding="utf-8")
        assert "agent/mcp-server" in agent_content
        assert "new/repo" in agent_content
