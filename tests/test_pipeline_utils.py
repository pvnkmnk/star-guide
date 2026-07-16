"""Tests for pipeline utility functions: parsing, regeneration, export."""
import pytest
import sqlite3
from unittest.mock import patch, MagicMock


class TestExtractReposFromFile:
    """extract_repos_from_file: regex extraction of github.com/owner/repo."""

    def test_extracts_all_github_repos(self, tmp_path):
        from update_stars import extract_repos_from_file
        f = tmp_path / "test.md"
        f.write_text(
            "# Guide\n\n"
            "- [user/repo1](https://github.com/user/repo1) — Tool\n"
            "- [org/app](https://github.com/org/app) — Another\n"
            "- https://github.com/other/tool linked inline\n",
            encoding="utf-8",
        )
        result = extract_repos_from_file(str(f))
        assert result == {"user/repo1", "org/app", "other/tool"}

    def test_no_github_links_returns_empty_set(self, tmp_path):
        from update_stars import extract_repos_from_file
        f = tmp_path / "test.md"
        f.write_text("# Just a header\n\nNo links here.\n", encoding="utf-8")
        result = extract_repos_from_file(str(f))
        assert result == set()


class TestFindSectionEnd:
    """find_section_end: locate section boundaries in STAR-GUIDE."""

    def test_finds_section_in_part_i(self):
        from update_stars import find_section_end
        content = (
            "# Part I: The Catalog\n\n"
            "## 🤖 Agentic Dev Tools\n\n"
            "some content\n\n"
            "## 💻 Dev Tools & Languages\n\n"
            "more content\n"
        )
        start, end = find_section_end(content, "🤖")
        assert start != -1
        assert end != -1
        assert "Agentic Dev Tools" in content[start:end]

    def test_section_not_found_returns_neg1(self):
        from update_stars import find_section_end
        content = "# Part I: The Catalog\n\n## 💻 Dev Tools\n\n"
        start, end = find_section_end(content, "🤖")
        assert start == -1
        assert end == -1

    def test_part_i_missing_returns_neg1(self):
        from update_stars import find_section_end
        content = "## 🤖 Agentic Dev Tools\n\n"
        start, end = find_section_end(content, "🤖")
        assert start == -1

    def test_no_part_ii_boundary_falls_back_to_end(self):
        """Line 255: when no PART_II_HEADERS found, part2_start = len(content)."""
        from update_stars import find_section_end
        content = (
            "# Part I: The Catalog\n\n"
            "## 🤖 Agentic Dev Tools\n\n"
            "some repos here\n"
        )
        start, end = find_section_end(content, "🤖")
        assert start != -1
        assert end == len(content)


class TestParseStarGuideSections:
    """parse_star_guide_sections: parse STAR-GUIDE.md into categorized sections."""

    def test_parses_sections_with_repos(self, tmp_path):
        from update_stars import parse_star_guide_sections
        f = tmp_path / "STAR-GUIDE.md"
        f.write_text(
            "# Part I: The Catalog\n\n"
            "## 🤖 Agentic Dev Tools\n\n"
            "| [user/tool1](https://github.com/user/tool1) | 1,000 | Python | ... |\n"
            "| [user/tool2](https://github.com/user/tool2) | 500 | Go | ... |\n"
            "\n"
            "## 💻 Dev Tools & Languages\n\n"
            "| [dev/app](https://github.com/dev/app) | 300 | Rust | ... |\n"
            "\n",
            encoding="utf-8",
        )
        sections = parse_star_guide_sections(str(f))
        assert len(sections) == 2
        emojis = [s[0] for s in sections]
        assert "🤖" in emojis
        assert "💻" in emojis

    def test_missing_part_i_returns_empty(self, tmp_path):
        from update_stars import parse_star_guide_sections
        f = tmp_path / "STAR-GUIDE.md"
        f.write_text("# No Part I here\n", encoding="utf-8")
        sections = parse_star_guide_sections(str(f))
        assert sections == []

    def test_section_with_no_repos_skipped(self, tmp_path):
        from update_stars import parse_star_guide_sections
        f = tmp_path / "STAR-GUIDE.md"
        f.write_text(
            "# Part I: The Catalog\n\n"
            "## 🤖 Agentic Dev Tools\n\n"
            "just some intro text, no repos\n\n",
            encoding="utf-8",
        )
        sections = parse_star_guide_sections(str(f))
        assert sections == []

    def test_part_ii_boundary_truncates_content(self, tmp_path):
        """Line 486: Part II headers found -> part2_start = min(part2_start, idx)."""
        from update_stars import parse_star_guide_sections
        f = tmp_path / "STAR-GUIDE.md"
        f.write_text(
            "# Part I: The Catalog\n\n"
            "## 🤖 Agentic Dev Tools\n\n"
            "| [user/tool1](https://github.com/user/tool1) | 1,000 | Go | ... |\n\n"
            "# Part II: Top Picks\n\n"
            "## 🤖 Agentic Dev Top 10\n\n"
            "| [user/part2-repo](https://github.com/user/part2-repo) | 100 | Rust | ... |\n",
            encoding="utf-8",
        )
        sections = parse_star_guide_sections(str(f))
        # Only Part I section (🤖 Agentic Dev Tools) is parsed
        # Part II content (🤖 Agentic Dev Top 10) is excluded
        assert len(sections) == 1
        repos_in_section = sections[0][2]
        assert "user/tool1" in repos_in_section
        # Part II repo should NOT appear in any parsed section
        assert "user/part2-repo" not in repos_in_section

    def test_unknown_section_header_skipped(self, tmp_path):
        """Line 509: section header with no matching emoji -> continue (skip)."""
        from update_stars import parse_star_guide_sections
        f = tmp_path / "STAR-GUIDE.md"
        f.write_text(
            "# Part I: The Catalog\n\n"
            "## 🤖 Agentic Dev Tools\n\n"
            "| [user/tool1](https://github.com/user/tool1) | 1,000 | Go | ... |\n\n"
            "## 🦄 Some Unknown Category\n\n"
            "| [user/mystery](https://github.com/user/mystery) | 500 | Rust | ... |\n\n",
            encoding="utf-8",
        )
        sections = parse_star_guide_sections(str(f))
        # Only 🤖 Agentic Dev Tools is recognized (emoji mapped)
        # 🦄 Some Unknown Category has no emoji match -> skipped
        assert len(sections) == 1
        assert sections[0][0] == "🤖"
        assert "user/tool1" in sections[0][2]
        # The unknown section's repo should not appear
        assert "user/mystery" not in sections[0][2]


class TestRegenerateAgentGuide:
    """regenerate_agent_guide: generate AGENT-GUIDE.md from sections + DB."""

    def test_generates_agent_guide(self, tmp_path):
        from update_stars import regenerate_agent_guide
        sections = [
            ("🤖", "Agentic Dev Tools", {"user/tool1", "user/tool2"}),
        ]
        stars_db = {
            "user/tool1": (5000, "Python", "An agentic tool"),
            "user/tool2": (3000, "Go", "Another tool"),
        }
        fp = tmp_path / "AGENT-GUIDE.md"
        regenerate_agent_guide(sections, stars_db, str(fp))
        content = fp.read_text(encoding="utf-8")
        assert "# AGENT-GUIDE" in content
        assert "🤖|5000|user/tool1|Python|An agentic tool" in content
        assert "🤖|3000|user/tool2|Go|Another tool" in content

    def test_repo_not_in_db_gets_fallback_entry(self, tmp_path):
        from update_stars import regenerate_agent_guide
        sections = [
            ("🤖", "Agentic Dev Tools", {"user/missing"}),
        ]
        stars_db = {}
        fp = tmp_path / "AGENT-GUIDE.md"
        regenerate_agent_guide(sections, stars_db, str(fp))
        content = fp.read_text(encoding="utf-8")
        assert "🤖|?|user/missing|-" in content


class TestRegenerateCheatsheet:
    """regenerate_cheatsheet: generate CHEATSHEET.md from sections + DB."""

    def test_generates_cheatsheet(self, tmp_path):
        from update_stars import regenerate_cheatsheet
        sections = [
            ("🤖", "Agentic Dev Tools", {"user/tool1"}),
        ]
        stars_db = {"user/tool1": (5000, "Python", "An agentic tool")}
        fp = tmp_path / "CHEATSHEET.md"
        regenerate_cheatsheet(sections, stars_db, str(fp))
        content = fp.read_text(encoding="utf-8")
        assert "# CHEATSHEET" in content
        assert "user/tool1" in content
        assert "1 tools" in content

    def test_empty_sections_produces_valid_output(self, tmp_path):
        from update_stars import regenerate_cheatsheet
        fp = tmp_path / "CHEATSHEET.md"
        regenerate_cheatsheet([], {}, str(fp))
        content = fp.read_text(encoding="utf-8")
        assert "# CHEATSHEET" in content
        assert "0 tools" in content


class TestExportRawFiles:
    """export_raw_files: export stars to CSV and TXT."""

    def test_exports_csv_and_txt(self, tmp_path):
        from update_stars import export_raw_files
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.execute(
            "CREATE TABLE repos (full_name TEXT, stars INTEGER, language TEXT, description TEXT, html_url TEXT, created_at TEXT, updated_at TEXT, username TEXT)"
        )
        conn.execute(
            "INSERT INTO repos VALUES (?,?,?,?,?,?,?,?)",
            ("user/tool", 5000, "Python", "A great tool", "https://github.com/user/tool", "2025-01-01", "2026-01-01", "pvnkmnk"),
        )
        conn.commit()
        with patch("update_stars.GITHUB_USER", "pvnkmnk"):
            with patch("update_stars.STARS_DIR", tmp_path):
                count = export_raw_files(conn)
        assert count == 1
        csv_path = tmp_path / "star-guide-pvnkmnk.csv"
        txt_path = tmp_path / "star-guide-pvnkmnk.txt"
        assert csv_path.exists()
        assert txt_path.exists()
        csv_content = csv_path.read_text(encoding="utf-8")
        assert "user/tool" in csv_content
        assert "5000" in csv_content

    def test_empty_db_returns_zero(self, tmp_path):
        from update_stars import export_raw_files
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.execute(
            "CREATE TABLE repos (full_name TEXT, stars INTEGER, language TEXT, description TEXT, html_url TEXT, created_at TEXT, updated_at TEXT, username TEXT)"
        )
        with patch("update_stars.GITHUB_USER", "pvnkmnk"):
            with patch("update_stars.STARS_DIR", tmp_path):
                count = export_raw_files(conn)
        assert count == 0

    def test_csv_escapes_quotes_in_description(self, tmp_path):
        from update_stars import export_raw_files
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.execute(
            "CREATE TABLE repos (full_name TEXT, stars INTEGER, language TEXT, description TEXT, html_url TEXT, created_at TEXT, updated_at TEXT, username TEXT)"
        )
        conn.execute(
            "INSERT INTO repos VALUES (?,?,?,?,?,?,?,?)",
            ("user/quoted", 100, "Python", 'Uses "quotes" inside', "https://github.com/user/quoted", "2025-01-01", "2026-01-01", "pvnkmnk"),
        )
        conn.commit()
        with patch("update_stars.GITHUB_USER", "pvnkmnk"):
            with patch("update_stars.STARS_DIR", tmp_path):
                count = export_raw_files(conn)
        csv_content = (tmp_path / "star-guide-pvnkmnk.csv").read_text(encoding="utf-8")
        assert 'Uses ""quotes"" inside' in csv_content
