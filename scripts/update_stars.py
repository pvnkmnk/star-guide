#!/usr/bin/env python3
"""
Weekly star refresh pipeline:
1. Fetch latest stars via gh-stars
2. Find repos in DB not yet in STAR-GUIDE.md → append to NOT-CURATED.md
3. Generate smart categorization suggestions for new repos
4. Regenerate AGENT-GUIDE.md from STAR-GUIDE.md sections + DB metadata
5. Regenerate CHEATSHEET.md from STAR-GUIDE.md repos + DB metadata
6. Export raw CSV/TXT

Usage:
    python3 scripts/update_stars.py          # from project root
    python3 scripts/update_stars.py --no-fetch  # skip gh-stars fetch
    python3 scripts/update_stars.py --fetch-only  # only fetch, no regeneration
    python3 scripts/update_stars.py --suggest-only  # only categorization, no file changes
    python3 scripts/update_stars.py --auto-curate       # auto-insert high-score repos into STAR-GUIDE
    python3 scripts/update_stars.py --auto-curate 10    # custom threshold (default 8)
"""

import re
import os
import sys
import sqlite3
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# ─── Configuration ────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
STARS_DIR = PROJECT_ROOT / "stars"
CACHE_DB = Path.home() / ".cache" / "gh-stars" / "stars.db"
GITHUB_USER = "pvnkmnk"

# Emoji mapping for STAR-GUIDE sections (header keyword → emoji)
EMOJI_MAP = {
    "Homelab Infrastructure": "📡",
    "Agentic Dev Tools": "🤖",
    "Self-Hosted Media": "🎵",
    "Docker & Container Management": "🐳",
    "AI / LLM Tools": "🧠",
    "Databases & Storage": "🗄️",
    "Security & Authentication": "🔒",
    "Automation & Workflows": "⚡",
    "Dev Tools & Languages": "💻",
    "Terminal, CLI & Shell": "⌨️",
    "Knowledge Management & PKM": "📝",
    "Web & Frontend": "🌐",
    "Chat & Messaging": "💬",
    "Docs & Blog": "📄",
    "Mobile": "📱",
    "Windows": "🪟",
    "Low Signal": "📦",
    "Unique & Niche": "❓",
}

# Part II boundaries (stop parsing Part I at these headers)
PART_II_HEADERS = [
    "# Part II",
    "## 📡 Homelab Top 10",
    "## 🤖 Agentic Dev Top 10",
    "## 🎵 Media Top 10",
    "## 🐳 Docker Top 10",
    "## 🧠 AI/LLM Top 10",
    "## 🏆 If I Could Only Keep 5",
]

# ─── Smart Categorization ─────────────────────────────────────────

# Category keywords: (emoji, category_name, [strong_keywords], [weak_keywords])
# strong = exact word match (weight 3), weak = substring match (weight 1)
CATEGORY_KEYWORDS = [
    ("📡", "Homelab Infrastructure",
     ["self-host", "homelab", "selfhost", "self-hosted", "selfhosted",
      "home-server", "PaaS", "reverse-proxy", "wireguard", "tailscale",
      "proxmox", "ansible", "terraform", "coolify", "unraid",
      "port-forward", "dyndns", "home-assistant", "homeassistant",
      "esphome", "zigbee", "zwave"],
     ["dashboard", "server", "hosting", "infrastructure", "vpn",
      "proxy", "network", "monitoring", "docker-compose", "pi-hole",
      "pihole", "home", "private-cloud", "domains", "cloudflare",
      "vercel", "heroku", "netlify"]),

    ("🤖", "Agentic Dev Tools",
     ["agentic", "coding-agent", "AI-agent", "LLM-agent", "openai-codex",
      "claude-code", "opencode", "gemini-cli", "cursor-ai", "codex-cli",
      "MCP-server", "agent-memory", "agent-skills", "agent-harness",
      "coding-assistant", "superpowers", "aider"],
     ["agent", "MCP", "skills", "coding", "LLM", "AI", "Claude", "Codex",
      "Gemini", "harness", "memory", "context", "subagent", "orchestrat",
      "prompt", "sandbox"]),

    ("🎵", "Self-Hosted Media",
     ["music", "audio", "media-stream", "jellyfin", "plex", "emby",
      "navidrome", "subsonic", "sonarr", "radarr", "lidarr", "beets",
      "soulseek", "picard", "musicbrainz", "immich", "gonic",
      "music-library", "music-player", "music-server"],
     ["streaming", "player", "playback", "lyrics", "tagger", "library",
      "photo", "video", "media", "mpd", "spotify", "tidal", "deezer",
      "youtube-music", "flac", "mp3", "lossless", "iptv"]),

    ("🐳", "Docker & Container Management",
     ["docker", "docker-compose", "container", "kubernetes", "k8s",
      "podman", "dockerfile", "docker-swarm", "containerize"],
     ["compose", "orchestrat", "swarm", "devpod", "codespace",
      "container-registry", "registry"]),

    ("🧠", "AI / LLM Tools",
     ["LLM", "large-language-model", "GPT", "transformer", "inference",
      "fine-tuning", "fine-tune", "RAG",
      "embedding", "ollama", "llama.cpp", "local-ai", "langchain",
      "huggingface", "stable-diffusion", "whisper", "neural-network",
      "deep-learning", "machine-learning", "openai-api",
      "computer-vision"],
     ["model", "AI", "artificial-intelligence", "semantic-search",
      "tokenizer", "NLP", "speech-recognition", "text-to-speech",
      "TTS", "STT", "generative", "prompt-engineering"]),

    ("🗄️", "Databases & Storage",
     ["database", "postgres", "postgresql", "mysql", "mariadb", "sqlite",
      "mongodb", "redis", "vector-db", "vector-database", "timeseries",
      "graph-database", "key-value", "object-storage", "S3",
      "backup", "qdrant", "milvus", "supabase", "pocketbase"],
     ["SQL", "NoSQL", "storage", "query", "cache", "index",
      "data-warehouse", "ETL", "data-lake"]),

    ("🔒", "Security & Authentication",
     ["security", "authentication", "authorization", "OAuth", "OIDC",
      "SSO", "single-sign-on", "firewall", "vulnerability", "pentest",
      "reverse-engineering", "ghidra", "gitleaks", "secret-scan",
      "encrypt", "password-manager", "WAF", "zero-trust"],
     ["auth", "vpn", "scan", "secret", "password", "2FA", "MFA",
      "intrusion", "detection", "malware", "exploit", "harden"]),

    ("⚡", "Automation & Workflows",
     ["workflow", "automation", "CI/CD", "CI", "CD", "pipeline",
      "n8n", "ansible", "terraform", "deployment", "GitHub-Actions",
      "Jenkins", "scheduler", "task-runner"],
     ["automate", "scripting", "scheduling", "github-actions",
      "gitlab-ci", "jenkins", "operat", "devops", "orchestrat"]),

    ("💻", "Dev Tools & Languages",
     ["programming", "framework", "compiler", "interpreter", "package-manager",
      "formatter", "linter", "testing", "API", "REST", "GraphQL",
      "static-site-generator", "web-framework", "tailwind", "playwright",
      "free-programming-books", "build-your-own-x", "bundler", "runtime",
      "javascript-runtime", "task-runner"],
     ["language", "library", "toolkit", "SDK", "template", "boilerplate",
      "curriculum", "tutorial", "algorithm", "course", "cheat-sheet"]),

    ("⌨️", "Terminal, CLI & Shell",
     ["terminal", "CLI", "TUI", "command-line", "shell", "zsh", "bash",
      "neovim", "nvim", "vim", "tmux", "multiplexer", "fuzzy-finder",
      "fzf", "zoxide", "alacritty", "file-manager", "yazi"],
     ["fuzzy", "prompt", "editor", "emulator", "console", "ncurses",
      "readline", "zellij", "wezterm", "cheat"]),

    ("📝", "Knowledge Management & PKM",
     ["knowledge", "PKM", "obsidian", "note-taking", "note-app",
      "second-brain", "wiki", "personal-knowledge", "markdown-notes",
      "notebook", "AFFiNE", "joplin"],
     ["note", "vault", "canvas", "mind-map", "knowledge-base",
      "digital-garden", "journal", "logseq", "roam"]),

    ("🌐", "Web & Frontend",
     ["web", "frontend", "UI", "UX", "design-system", "React", "Vue",
      "Svelte", "CSS", "HTML", "component-library", "web-app",
      "browser-extension", "website", "email-template", "landing-page",
      "shadcn", "mui", "tailwind"],
     ["design", "template", "component", "interface", "responsive",
      "chrome-extension", "email", "landing", "analytics"]),

    ("💬", "Chat & Messaging",
     ["chat", "messaging", "messenger", "Discord", "Telegram", "Slack",
      "Signal", "Matrix", "WhatsApp", "IRC", "communication"],
     ["message", "bot", "webhook", "real-time", "presence"]),

    ("📄", "Docs & Blog",
     ["documentation", "docs", "blog", "static-site", "Hugo", "mkdocs",
      "writing", "publish", "SSG"],
     ["markdown", "content", "article", "guide", "tutorial", "readme"]),

    ("📱", "Mobile",
     ["android", "iOS", "mobile", "app", "iphone", "ipad",
      "flutter", "kotlin", "swift", "termux", "revanced",
      "APK", "phone"],
     ["tablet", "wearable", "smartphone", "mobile-app", "play-store",
      "app-store"]),

    ("🪟", "Windows",
     ["windows", "win32", "PowerShell", "taskbar", "explorer",
      "winget", "WSL", "win11", "win10", "desktop-enhance",
      "explorer-patcher", "seelen-ui", "everything-toolbar"],
     ["desktop", "WinUI", "registry", ".msi", "chocolatey", "scoop",
      "system-tray", "start-menu"]),
]


def tokenize(text):
    """Tokenize text into lowercase words, splitting on non-alphanumeric."""
    if not text:
        return set()
    # Keep hyphens for compound terms, lowercase everything
    text = text.lower()
    # Split on whitespace and common punctuation (but keep hyphens)
    tokens = set()
    for word in re.split(r'[\s,./()\[\]{}:;!?"\'`]+', text):
        if word:
            tokens.add(word)
    return tokens


def score_repo_for_category(full_name, lang, desc, strong_keywords, weak_keywords):
    """
    Score a repo against a category's keywords.
    Returns integer score. Higher = better match.
    """
    # Tokenize description, name, and language
    name_part = full_name.split("/")[-1] if "/" in full_name else full_name
    name_tokens = tokenize(name_part)
    desc_tokens = tokenize(desc)
    lang_tokens = tokenize(lang)
    
    all_tokens = name_tokens | desc_tokens | lang_tokens
    all_text = f"{name_part} {desc or ''} {lang or ''}".lower()
    
    score = 0
    
    # Strong matches (exact word token match): weight 4
    for kw in strong_keywords:
        kw_lower = kw.lower()
        if kw_lower in all_tokens:
            score += 4
            # Bonus if matched in the repo name (more signal)
            if kw_lower in name_tokens:
                score += 2
        # Also check compound keywords as substring in full text
        elif kw_lower in all_text:
            score += 1
    
    # Weak matches (substring match anywhere): weight 1
    for kw in weak_keywords:
        kw_lower = kw.lower()
        if kw_lower in all_tokens:
            score += 1
            if kw_lower in name_tokens:
                score += 1
        elif kw_lower in all_text:
            score += 0.5
    
    return int(score)


def suggest_categories(new_repos):
    """
    Suggest categories for new repos.
    new_repos: list of (stars, full_name, language, description)
    Returns: list of (stars, full_name, lang, desc, [(emoji, cat_name, score)])
    """
    results = []
    for stars, full_name, lang, desc in new_repos:
        cat_scores = []
        for emoji, cat_name, strong_kw, weak_kw in CATEGORY_KEYWORDS:
            score = score_repo_for_category(full_name, lang, desc, strong_kw, weak_kw)
            if score > 0:
                cat_scores.append((emoji, cat_name, score))
        
        # Sort by score descending
        cat_scores.sort(key=lambda x: -x[2])
        results.append((stars, full_name, lang, desc, cat_scores[:3]))
    
    return results


def generate_suggestions_report(new_repos, filepath):
    """
    Generate CATEGORIZATION-SUGGESTIONS.md with smart category suggestions.
    """
    if not new_repos:
        print("  → No new repos, skipping categorization suggestions")
        return
    
    suggestions = suggest_categories(new_repos)
    
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    lines = [
        "# 🏷️ Categorization Suggestions",
        "",
        f"> Auto-generated suggestions for where new repos might fit in STAR-GUIDE.md.",
        f"> Generated: {date_str}",
        f"> {len(suggestions)} repos analyzed",
        "",
        "## How to use",
        "",
        "Review each suggestion below. If it looks correct, copy the repo into",
        "the matching section of STAR-GUIDE.md and remove it from NOT-CURATED.md.",
        "",
        "**Scoring**: Higher score = stronger keyword match. 4+ is strong signal.",
        "",
        "---",
        "",
    ]
    
    # Group by top suggested category
    by_category = defaultdict(list)
    for stars, full_name, lang, desc, cats in suggestions:
        if cats:
            top_cat = cats[0]
            by_category[top_cat].append((stars, full_name, lang, desc, cats))
        else:
            by_category[("❓", "Uncertain", 0)].append((stars, full_name, lang, desc, cats))
    
    # Sort categories by number of suggestions
    for (emoji, cat_name, _), repos in sorted(by_category.items(),
                                                key=lambda x: -len(x[1])):
        lines.append(f"## {emoji} {cat_name}")
        lines.append("")
        lines.append("| Stars | Repo | Lang | Description | Also consider |")
        lines.append("|------:|------|------|-------------|---------------|")
        
        for stars, full_name, lang, desc, cats in sorted(repos, key=lambda x: -x[0]):
            desc_short = (desc or '')[:100].replace('\n', ' ').replace('|', '/')
            
            alt_cats = ""
            if len(cats) > 1:
                alt_parts = []
                for em, cn, sc in cats[1:]:
                    alt_parts.append(f"{em} {cn} ({sc})")
                alt_cats = ", ".join(alt_parts)
            
            lines.append(
                f"| {stars:,} | [{full_name}](https://github.com/{full_name}) | "
                f"{lang or '-'} | {desc_short} | {alt_cats or '—'} |"
            )
        lines.append("")
    
    lines.append("---")
    lines.append(f"*Generated by `scripts/update_stars.py` · {date_str}*")
    
    Path(filepath).write_text('\n'.join(lines) + '\n', encoding="utf-8")
    print(f"  → Generated categorization suggestions ({len(suggestions)} repos)")


# ─── Auto-Curation ───────────────────────────────────────────────

def find_section_end(content, emoji):
    """
    Locate the STAR-GUIDE section for a given emoji header.
    Returns (section_start, section_end) byte offsets, or (-1, -1) if not found.
    Only searches Part I to avoid accidental inserts into Part II Top 10.
    """
    # Find Part I start
    part1_start = content.find("# Part I: The Catalog")
    if part1_start == -1:
        return -1, -1

    # Find Part II start
    part2_start = len(content)
    for header in PART_II_HEADERS:
        idx = content.find("\n" + header, part1_start)
        if idx != -1:
            part2_start = min(part2_start, idx)

    # Find the section header
    header_pattern = f"## {emoji} "
    start = content.find(header_pattern, part1_start, part2_start)
    if start == -1:
        return -1, -1

    # Find the next ## header (section end)
    next_header = content.find("\n## ", start + len(header_pattern))
    if next_header == -1 or next_header > part2_start:
        next_header = part2_start

    return start, next_header


def insert_repo_into_section(content, emoji, stars, full_name, lang, desc):
    """
    Insert a new repo row into the main table of the matching STAR-GUIDE section.
    Inserts after the last | row in the first contiguous table under the section
    header (before any ### subsection or next ## section).

    Returns the modified content, or original content if section not found.
    """
    start, end = find_section_end(content, emoji)
    if start == -1:
        return content

    section_lines = content[start:end].split("\n")

    # Find the first table: locate its header row and last data row
    table_started = False
    last_table_line = -1

    for i, line in enumerate(section_lines):
        stripped = line.strip()
        is_table_row = stripped.startswith("|")

        if is_table_row and not table_started:
            table_started = True

        if table_started:
            if is_table_row:
                last_table_line = i
            else:
                # Table ended (blank line, ###, ##, or non-table text)
                break

    if last_table_line == -1:
        # No table found — shouldn't happen for existing sections
        return content

    # Build the new row
    desc_short = (desc or "")[:120].replace("\n", " ").replace("\r", " ").replace("|", "/")
    stars_fmt = f"{stars:,}"
    new_row = f"| [{full_name}](https://github.com/{full_name}) | {stars_fmt} | {lang or '-'} | {desc_short} | 🆕 |"

    # Insert after the last table row
    insert_line = start + sum(len(l) + 1 for l in section_lines[:last_table_line + 1])
    new_content = content[:insert_line] + "\n" + new_row + content[insert_line:]

    return new_content


def auto_curate_repos(new_repos, star_guide_path, threshold=8, not_curated_path=None):
    """
    Auto-curate repos that score above threshold in a single clear category.

    Rules:
    - Top score must be >= threshold
    - If multiple categories matched, top score must be >= 1.5x second-best
    - If only one category matched, the gap check is trivially satisfied

    Returns: (auto_curated, remaining, modified) where:
      - auto_curated: [(emoji, cat_name, score, stars, full_name, lang, desc), ...]
      - remaining: repos that didn't meet threshold
      - modified: bool, whether STAR-GUIDE was written

    If not_curated_path is provided, auto-curated repos are also removed from
    the NOT-CURATED.md file using reliable bracket-extraction line matching.
    """
    autos = []
    remaining = []

    suggestions = suggest_categories(new_repos)

    for stars, full_name, lang, desc, cats in suggestions:
        if not cats:
            remaining.append((stars, full_name, lang, desc))
            continue

        top_emoji, top_cat, top_score = cats[0]
        second_score = cats[1][2] if len(cats) > 1 else 0

        if top_score >= threshold and top_score >= 1.5 * second_score:
            autos.append((top_emoji, top_cat, top_score, stars, full_name, lang, desc))
        else:
            remaining.append((stars, full_name, lang, desc))

    if not autos:
        return [], remaining, False

    # Read STAR-GUIDE and insert each auto-curated repo
    content = Path(star_guide_path).read_text(encoding="utf-8")
    modified = False

    for emoji, cat_name, score, stars, full_name, lang, desc in autos:
        new_content = insert_repo_into_section(content, emoji, stars, full_name, lang, desc)
        if new_content != content:
            content = new_content
            modified = True
            print(f"  🆕 Auto-curated: {emoji} [{full_name}](https://github.com/{full_name}) — ⭐{stars:,} → {cat_name} (score={score})")
        else:
            print(f"  ⚠️  Could not insert {full_name} into {cat_name} section (section not found?)")

    if modified:
        Path(star_guide_path).write_text(content, encoding="utf-8")
        print(f"  → Wrote {star_guide_path} with {len(autos)} auto-curated repos")

        # Remove auto-curated repos from NOT-CURATED if path provided
        if not_curated_path and Path(not_curated_path).exists():
            auto_names = set(r[4] for r in autos)
            removed = remove_from_not_curated(auto_names, not_curated_path)
            if removed:
                print(f"  → Removed {removed} repos from NOT-CURATED.md")

    return autos, remaining, modified


def remove_from_not_curated(repo_names, filepath):
    """
    Remove repos from NOT-CURATED.md using reliable bracket-extraction matching.

    Scans for lines like: - [owner/repo](https://github.com/...
    and removes lines whose bracketed repo name is in repo_names.

    Returns number of lines removed.
    """
    if not Path(filepath).exists():
        return 0

    content = Path(filepath).read_text(encoding="utf-8")
    lines = content.split("\n")
    new_lines = []
    removed = 0

    for line in lines:
        stripped = line.strip()
        # Match NOT-CURATED lines: - [owner/repo](https://github.com/...)
        if stripped.startswith("- [") and "](https://github.com/" in stripped:
            bracket_start = stripped.index("[") + 1
            bracket_end = stripped.index("]")
            repo_name = stripped[bracket_start:bracket_end]
            if repo_name in repo_names:
                removed += 1
                continue
        new_lines.append(line)

    if removed:
        Path(filepath).write_text("\n".join(new_lines), encoding="utf-8")

    return removed


# ─── Database Helpers ─────────────────────────────────────────────

def get_db_connection():
    """Connect to SQLite stars database."""
    if not CACHE_DB.exists():
        print(f"Error: Database not found at {CACHE_DB}")
        print("Run: gh-stars fetch {GITHUB_USER}")
        sys.exit(1)
    conn = sqlite3.connect(str(CACHE_DB))
    conn.row_factory = sqlite3.Row
    return conn


def get_all_stars(conn):
    """Return all stars as dict[full_name] = {stars, language, description}."""
    rows = conn.execute(
        "SELECT full_name, stars, "
        "COALESCE(language,'-') as language, "
        "COALESCE(description,'') as description "
        "FROM repos WHERE username=? ORDER BY stars DESC",
        (GITHUB_USER,)
    ).fetchall()
    return {r["full_name"]: (r["stars"], r["language"], r["description"]) for r in rows}


# ─── Parsing Helpers ──────────────────────────────────────────────

def extract_repos_from_file(filepath):
    """Extract all github.com/owner/repo patterns from a markdown file."""
    content = Path(filepath).read_text(encoding="utf-8")
    repos = set(re.findall(r'github\.com/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)', content))
    return repos


def parse_star_guide_sections(filepath):
    """
    Parse STAR-GUIDE.md into sections.
    Returns: list of (emoji, section_name, [repo_full_names])
    """
    content = Path(filepath).read_text(encoding="utf-8")
    
    # Find Part I boundaries
    part1_start = content.find("# Part I: The Catalog")
    if part1_start == -1:
        print("Error: Could not find 'Part I: The Catalog' in STAR-GUIDE.md")
        return []
    
    # Find where Part II starts
    part2_start = len(content)
    for header in PART_II_HEADERS:
        idx = content.find(header, part1_start)
        if idx != -1:
            part2_start = min(part2_start, idx)
    
    part1_content = content[part1_start:part2_start]
    
    # Split into sections by ## headers
    sections_raw = re.split(r'\n(?=## )', part1_content)
    
    sections = []
    for section in sections_raw:
        # Identify the section name from its header
        header_match = re.match(r'## (.+)', section)
        if not header_match:
            continue
        section_name = header_match.group(1)
        
        # Find matching emoji
        emoji = None
        for keyword, em in EMOJI_MAP.items():
            if keyword in section_name:
                emoji = em
                break
        
        if emoji is None:
            continue
        
        # Extract all repos from this section
        repos = set(re.findall(r'github\.com/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)', section))
        
        if repos:
            sections.append((emoji, section_name, repos))
    
    return sections


# ─── Regeneration Functions ───────────────────────────────────────

def regenerate_agent_guide(sections, stars_db, filepath):
    """Regenerate AGENT-GUIDE.md from STAR-GUIDE sections + DB metadata."""
    all_entries = []
    
    for emoji, section_name, repos in sections:
        for repo in sorted(repos):
            if repo in stars_db:
                stars, lang, desc = stars_db[repo]
                # Clean description: single line, escape pipes, truncate
                desc = desc.replace('\n', ' ').replace('\r', ' ').replace('|', '/')
                # No truncation needed for agent format - it's compact enough
                all_entries.append(f"{emoji}|{stars}|{repo}|{lang}|{desc}")
            else:
                # Repo in STAR-GUIDE but not in DB (shouldn't happen after fetch)
                all_entries.append(f"{emoji}|?|{repo}|-|")
    
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    header = f"""# AGENT-GUIDE: pvnkmnk's Curated Stars
# Format: EMOJI|STARS|FULL_NAME|LANG|DESCRIPTION
# 18 categories · from {sum(1 for _ in stars_db)} stars · {date_str}

"""
    Path(filepath).write_text(header + '\n'.join(all_entries) + '\n', encoding="utf-8")
    print(f"  → Regenerated AGENT-GUIDE.md ({len(all_entries)} entries)")


def regenerate_cheatsheet(sections, stars_db, filepath):
    """Regenerate CHEATSHEET.md from STAR-GUIDE sections + DB metadata."""
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    total = sum(len(r) for _, _, r in sections)
    
    lines = [
        f"# CHEATSHEET: pvnkmnk's Starred Tools",
        "",
        f"> One line per tool · Compact terminal-friendly · {date_str}",
        f"> Categories: 📡Homelab 🤖Agentic 🎵Media 🐳Docker 🧠AI/LLM 🗄️DB 🔒Security ⚡Auto 💻Dev ⌨️CLI 📝PKM 🌐Web 💬Chat 📄Docs 📱Mobile 🪟Windows 📦LowSignal ❓Unique",
        "",
    ]
    
    # Category order
    cat_order = [
        ("📡", "Homelab Infrastructure"),
        ("🤖", "Agentic Dev Tools"),
        ("🎵", "Self-Hosted Media"),
        ("🐳", "Docker & Container Management"),
        ("🧠", "AI / LLM Tools"),
        ("🗄️", "Databases & Storage"),
        ("🔒", "Security & Authentication"),
        ("⚡", "Automation & Workflows"),
        ("💻", "Dev Tools & Languages"),
        ("⌨️", "Terminal, CLI & Shell"),
        ("📝", "Knowledge Management & PKM"),
        ("🌐", "Web & Frontend"),
        ("💬", "Chat & Messaging"),
        ("📄", "Docs & Blog"),
        ("📱", "Mobile"),
        ("🪟", "Windows"),
        ("📦", "Low Signal"),
        ("❓", "Unique & Niche"),
    ]
    
    for emoji, cat_name in cat_order:
        # Find matching section
        entries = []
        for sec_emoji, sec_name, repos in sections:
            if sec_emoji == emoji:
                for repo in sorted(repos):
                    if repo in stars_db:
                        stars, lang, desc = stars_db[repo]
                        name = repo.split("/")[1]
                        entries.append((stars, name, repo, lang, desc))
                break
        
        if entries:
            lines.append(f"## {emoji} {cat_name}")
            # Sort by stars descending
            for stars, name, repo, lang, desc in sorted(entries, key=lambda x: -x[0]):
                lang_pad = f"{lang:<6}" if lang and lang != '-' else f"{'-':<6}"
                lines.append(f"  {emoji} {stars:>6,} {repo:<52} {lang_pad} {desc[:80]}")
            lines.append("")
    
    lines.append(f"---")
    lines.append(f"{total} tools · 18 categories · from {sum(1 for _ in stars_db)} stars · pvnkmnk · {date_str}")
    
    Path(filepath).write_text('\n'.join(lines) + '\n', encoding="utf-8")
    print(f"  → Regenerated CHEATSHEET.md ({total} entries)")


def append_new_to_not_curated(stars_db, curated_repos, filepath):
    """
    Find repos in DB not in any curated file, append to NOT-CURATED.md.
    Note: main() now uses a direct-write approach that handles auto-curation
    filtering. This function is retained for standalone/imported use.
    """
    curated_all = set(curated_repos)
    
    # Also exclude repos already in NOT-CURATED.md
    if Path(filepath).exists():
        not_curated_repos = extract_repos_from_file(filepath)
        curated_all |= not_curated_repos
    
    new_repos = []
    for full_name, (stars, lang, desc) in stars_db.items():
        if full_name not in curated_all:
            new_repos.append((stars, full_name, lang, desc))
    
    if not new_repos:
        print(f"  → No new repos to append to NOT-CURATED.md")
        return 0
    
    # Sort by stars descending
    new_repos.sort(key=lambda x: -x[0])
    
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    
    # Append to file
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(f"\n## 🆕 New Stars — {date_str}\n\n")
        for stars, full_name, lang, desc in new_repos:
            desc_short = (desc or '')[:120].replace('\n', ' ').replace('|', '/')
            f.write(f"- [{full_name}](https://github.com/{full_name}) — ⭐{stars} ({lang or '-'}) {desc_short}\n")
    
    print(f"  → Appended {len(new_repos)} new repos to NOT-CURATED.md")
    return len(new_repos)


def export_raw_files(conn):
    """Export stars to CSV and TXT."""
    rows = conn.execute(
        "SELECT full_name, stars, "
        "COALESCE(language,'-') as language, "
        "COALESCE(description,'') as description, "
        "html_url, created_at, updated_at "
        "FROM repos WHERE username=? ORDER BY stars DESC",
        (GITHUB_USER,)
    ).fetchall()
    
    if not rows:
        print("  → No rows in database, skipping CSV/TXT export")
        return 0
    
    # CSV
    csv_path = STARS_DIR / f"gh-stars-{GITHUB_USER}.csv"
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write("full_name,stars,language,description,html_url,created_at,updated_at\n")
        for r in rows:
            desc = (r["description"] or '').replace('"', '""')
            f.write(f'"{r["full_name"]}",{r["stars"]},"{r["language"]}","{desc}","{r["html_url"]}","{r["created_at"]}","{r["updated_at"]}"\n')
    print(f"  → Exported {csv_path}")
    
    # TXT
    txt_path = STARS_DIR / f"gh-stars-{GITHUB_USER}.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        f.write(f"GitHub Stars for {GITHUB_USER} — {date_str}\n")
        f.write(f"Total: {len(rows)}\n")
        f.write("=" * 80 + "\n\n")
        for r in rows:
            f.write(f"{r['stars']:>6,} ⭐  {r['full_name']}\n")
            f.write(f"        Lang: {r['language']}  |  {r['html_url']}\n")
            if r["description"]:
                desc = r["description"][:200]
                f.write(f"        {desc}\n")
            f.write(f"        Updated: {r['updated_at']}\n\n")
    print(f"  → Exported {txt_path}")
    
    return len(rows)


# ─── Main Pipeline ────────────────────────────────────────────────

def fetch_stars():
    """Run gh-stars fetch to refresh the database."""
    print("Fetching latest stars via gh-stars...")
    
    # Ensure cache dir exists
    CACHE_DB.parent.mkdir(parents=True, exist_ok=True)
    
    result = subprocess.run(
        ["gh-stars", "fetch", GITHUB_USER],
        capture_output=True,
        text=True,
        timeout=300,  # 5 minutes for large star collections
    )
    
    if result.returncode != 0:
        print(f"Warning: gh-stars fetch returned {result.returncode}")
        print(result.stderr[-500:] if result.stderr else "")
    else:
        print(f"  → Fetch complete")
        # Print last few lines of output for status
        lines = result.stdout.strip().split('\n')
        for line in lines[-3:]:
            print(f"    {line}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Weekly star refresh pipeline")
    parser.add_argument("--no-fetch", action="store_true", help="Skip gh-stars fetch")
    parser.add_argument("--fetch-only", action="store_true", help="Only fetch, no regeneration")
    parser.add_argument("--suggest-only", action="store_true",
                        help="Only generate categorization suggestions from new repos (no file regeneration)")
    parser.add_argument("--auto-curate", nargs="?", const=8, type=int, metavar="THRESHOLD",
                        help="Auto-insert repos scoring >= THRESHOLD (default 8) with clear category match into STAR-GUIDE")
    args = parser.parse_args()
    
    # Step 1: Fetch
    if not args.no_fetch:
        fetch_stars()
    
    if args.fetch_only:
        print("Done (fetch only).")
        return
    
    # Step 2: Connect to DB
    conn = get_db_connection()
    stars_db = get_all_stars(conn)
    print(f"Loaded {len(stars_db)} stars from database")
    
    # Step 3: Parse STAR-GUIDE.md for curated repos
    star_guide_path = STARS_DIR / "STAR-GUIDE.md"
    if not star_guide_path.exists():
        print(f"Error: STAR-GUIDE.md not found at {star_guide_path}")
        sys.exit(1)
    
    curated_repos = extract_repos_from_file(star_guide_path)
    sections = parse_star_guide_sections(star_guide_path)
    print(f"Found {len(curated_repos)} curated repos in {len(sections)} sections")
    
    if not sections:
        print("Error: No sections found in STAR-GUIDE.md. Check file format - aborting.")
        sys.exit(1)
    
    # Build the full "already seen" set
    curated_all = set(curated_repos)
    for guide_file in ["NOT-CURATED.md"]:
        fp = STARS_DIR / guide_file
        if fp.exists():
            curated_all |= extract_repos_from_file(fp)
    
    # Identify truly new repos
    new_repo_list = []
    for full_name, (stars, lang, desc) in stars_db.items():
        if full_name not in curated_all:
            new_repo_list.append((stars, full_name, lang, desc))
    new_repo_list.sort(key=lambda x: -x[0])
    
    if args.suggest_only:
        # Only generate categorization suggestions, no file changes
        suggestions_path = STARS_DIR / "CATEGORIZATION-SUGGESTIONS.md"
        generate_suggestions_report(new_repo_list, suggestions_path)
        conn.close()
        print(f"\n✅ Suggestions generated for {len(new_repo_list)} repos")
        return

    # ── Auto-curation (if enabled) ──────────────────────────
    auto_curated = []
    needs_review = new_repo_list

    if args.auto_curate is not None:
        threshold = args.auto_curate
        print(f"\n🔍 Auto-curation mode — threshold {threshold}")
        print(f"   Scanning {len(new_repo_list)} new repos...")

        auto_curated, needs_review, star_guide_modified = auto_curate_repos(
            new_repo_list, star_guide_path, threshold,
            not_curated_path=STARS_DIR / "NOT-CURATED.md"
        )

        if star_guide_modified:
            # Re-parse STAR-GUIDE so regenerated files include the new repos
            curated_repos = extract_repos_from_file(star_guide_path)
            sections = parse_star_guide_sections(star_guide_path)
            print(f"   Re-parsed: {len(curated_repos)} curated in {len(sections)} sections")

        print(f"   Auto-curated: {len(auto_curated)} · Needs review: {len(needs_review)}")

    # ── Append remaining new repos to NOT-CURATED.md ────────
    not_curated_path = STARS_DIR / "NOT-CURATED.md"
    if needs_review:
        # needs_review already excludes repos already in STAR-GUIDE or NOT-CURATED
        with open(not_curated_path, 'a', encoding='utf-8') as f:
            date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            f.write(f"\n## 🆕 New Stars — {date_str}\n\n")
            for stars, full_name, lang, desc in sorted(needs_review, key=lambda x: -x[0]):
                desc_short = (desc or '')[:120].replace('\n', ' ').replace('|', '/')
                f.write(f"- [{full_name}](https://github.com/{full_name}) — ⭐{stars:,} ({lang or '-'}) {desc_short}\n")
        print(f"  → Appended {len(needs_review)} new repos to NOT-CURATED.md")
        new_count = len(needs_review)
    else:
        new_count = 0
        print(f"  → No new repos to append to NOT-CURATED.md")

    # ── Generate categorization suggestions for remaining ───
    suggestions_path = STARS_DIR / "CATEGORIZATION-SUGGESTIONS.md"
    if len(needs_review) > 0:
        generate_suggestions_report(needs_review, suggestions_path)
    else:
        print("  → No repos needing review, skipping categorization suggestions")
    
    # Step 6: Regenerate AGENT-GUIDE.md
    agent_guide_path = STARS_DIR / "AGENT-GUIDE.md"
    regenerate_agent_guide(sections, stars_db, agent_guide_path)
    
    # Step 7: Regenerate CHEATSHEET.md
    cheatsheet_path = STARS_DIR / "CHEATSHEET.md"
    regenerate_cheatsheet(sections, stars_db, cheatsheet_path)
    
    # Step 8: Export raw files
    total = export_raw_files(conn)
    
    conn.close()
    
    print(f"\n✅ Pipeline complete!")
    print(f"   {len(curated_repos)} curated · {len(auto_curated)} auto-curated · {new_count} new · {total} total stars")


if __name__ == "__main__":
    main()
