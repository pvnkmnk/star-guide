# 🧰 Personal Toolbox

> Top 10 picks from each category of my GitHub stars — what I'd actually use and why.
> [pvnkmnk](https://github.com/pvnkmnk) · 2026-06-18

---

## 📡 Homelab Infrastructure — Top 10

### 1. [khuedoan/homelab](https://github.com/khuedoan/homelab) ⭐9,344
**Why I starred this:** The holy grail of homelab automation. One command takes you from bare metal to a fully running stack — DNS, VPN, monitoring, media, the works. It's a learning goldmine even if you don't run it verbatim, because every Ansible playbook and Terraform module is documented and reusable. If I were starting from scratch tomorrow, this is where I'd begin.

### 2. [coollabsio/coolify](https://github.com/coollabsio/coolify) ⭐57,133
**Why I starred this:** Vercel/Heroku/Netlify, but self-hosted. One-click deploys for anything with a Dockerfile — Next.js, Node, Python, databases, you name it. It's the PaaS that makes self-hosting feel like a managed service. Paired with a $20 VPS, this replaces $200/mo in cloud bills.

### 3. [gethomepage/homepage](https://github.com/gethomepage/homepage) ⭐30,704
**Why I starred this:** The dashboard every homelab needs. It auto-discovers your Docker containers via labels, shows live status, integrates with dozens of service APIs (Plex, Sonarr, Pi-hole, etc.), and looks gorgeous doing it. It's the first thing I open every morning to check my lab's pulse.

### 4. [juanfont/headscale](https://github.com/juanfont/headscale) ⭐40,154
**Why I starred this:** Tailscale without the Tailscale servers. Full WireGuard mesh networking that I control end-to-end. Every device in my homelab joins the same private tailnet — my laptop, my servers, my phone. No open ports, no Cloudflare tunnels needed for internal access. It's the networking backbone that makes everything else work securely.

### 5. [glanceapp/glance](https://github.com/glanceapp/glance) ⭐35,221
**Why I starred this:** A single page that aggregates all my feeds — RSS, Reddit, YouTube, Hacker News, weather, stocks, Docker status. It's my information radiator. Minimal, fast, and self-hosted. I use it as my browser's new tab page.

### 6. [ChristianLempa/boilerplates](https://github.com/ChristianLempa/boilerplates) ⭐7,819
**Why I starred this:** A library of production-ready Docker Compose templates for common self-hosted apps — all configured with security best practices, proper networking, and sane defaults. Every time I want to spin up a new service, I check here first to avoid reinventing the wheel.

### 7. [azukaar/Cosmos-Server](https://github.com/azukaar/Cosmos-Server) ⭐5,973
**Why I starred this:** A full home server OS in a single binary. Built-in reverse proxy with auto-SSL, authentication, anti-DDOS, and a marketplace to install apps. It's the "I want it all and I want it secure" option. Great for setting up a server for non-technical family members.

### 8. [IAmStoxe/wirehole](https://github.com/IAmStoxe/wirehole) ⭐4,959
**Why I starred this:** WireGuard + Pi-hole + Unbound in one docker-compose. One `docker compose up` and I have a VPN that blocks ads and malware across every device. I run this on a $5 VPS and it's been rock-solid for years.

### 9. [octelium/octelium](https://github.com/octelium/octelium) ⭐3,892
**Why I starred this:** The Swiss Army knife of secure access — VPN, ZTNA, API gateway, MCP gateway, ngrok alternative, all in one Go binary. It's the most ambitious self-hosted networking project I've seen. If it delivers on half its promises, it replaces 5 separate tools.

### 10. [linkwarden/linkwarden](https://github.com/linkwarden/linkwarden) ⭐18,653
**Why I starred this:** Self-hosted bookmark manager that actually preserves pages — full-text snapshots, screenshots, PDFs. My "read later" list doesn't rot anymore. It's also collaborative, so my whole household can share and organize links. Think Pocket, but I own the data.

---

## 🤖 Agentic Dev Tools — Top 10

### 1. [anomalyco/opencode](https://github.com/anomalyco/opencode) ⭐175,985
**Why I starred this:** The open-source coding agent that I actually use daily. It runs in my terminal, understands my entire codebase, and produces real, working code. It's not a toy — it's a force multiplier. The plugin ecosystem and community are incredible. This is the agent I'd recommend to anyone starting out.

### 2. [anthropics/claude-code](https://github.com/anthropics/claude-code) ⭐133,185
**Why I starred this:** The original coding agent that proved the paradigm. Claude Code showed the world that an agent can understand a million-line codebase and make surgical edits. I star it because it defined the category, and I still reach for it for hard architectural problems.

### 3. [mem0ai/mem0](https://github.com/mem0ai/mem0) ⭐58,853
**Why I starred this:** Universal memory for agents. The missing piece in every agent workflow — persistent, searchable memory that survives sessions. Instead of repeating context every conversation, my agents remember preferences, past decisions, and project state. It's the difference between a smart assistant and a colleague.

### 4. [bytedance/deer-flow](https://github.com/bytedance/deer-flow) ⭐71,473
**Why I starred this:** The long-horizon agent harness. While most coding agents handle a single task, deer-flow manages multi-hour research → code → deploy pipelines with sandboxes, subagents, and memory. It's the closest thing to an autonomous software engineer I've seen. The message gateway pattern is worth studying alone.

### 5. [ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) ⭐43,923
**Why I starred this:** Gives my coding agents eyes in the browser. DevTools-level access to any webpage — inspect DOM, monitor network, check console errors, take screenshots, run performance audits. Essential for agents that build or debug web apps. This + OpenCode = a full-stack agent that actually sees what it's doing.

### 6. [colbymchenry/codegraph](https://github.com/colbymchenry/codegraph) ⭐51,516
**Why I starred this:** Pre-indexed code knowledge graph that reduces agent token usage by 10x. Instead of reading every file, the agent queries a graph that already knows the code structure. It syncs on file changes automatically and works with every major agent. This is the kind of infrastructure all agents will need.

### 7. [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) ⭐83,103
**Why I starred this:** Session-to-session memory that actually works. It captures everything the agent does, compresses it with AI, and injects relevant context into future sessions. Unlike raw context dumps, it figures out what's relevant. Works across Claude Code, OpenCode, Codex, Gemini, and more.

### 8. [ComposioHQ/composio](https://github.com/ComposioHQ/composio) ⭐28,829
**Why I starred this:** 1,000+ pre-built tool integrations for agents — Gmail, Slack, GitHub, Jira, databases, APIs — with managed auth. Instead of building custom integrations for every tool my agent needs, I connect through Composio. It handles OAuth, rate limiting, and sandboxed execution.

### 9. [aaif-goose/goose](https://github.com/aaif-goose/goose) ⭐49,755
**Why I starred this:** The agent that goes beyond coding. Goose installs packages, runs tests, edits files, and executes commands — it's a full development lifecycle agent written in Rust. I star it for its philosophy: an agent shouldn't just suggest code, it should be able to fully execute.

### 10. [obra/superpowers](https://github.com/obra/superpowers) ⭐232,087
**Why I starred this:** The skills framework that showed agents can be more than prompt engineering. Superpowers treats agent capabilities as composable, reusable building blocks with clear interfaces. It's the Unix philosophy applied to AI: small, focused tools that compose into powerful workflows. My most-starred repo for good reason.

---

## 🎵 Self-Hosted Media — Top 10

### 1. [immich-app/immich](https://github.com/immich-app/immich) ⭐103,674
**Why I starred this:** Google Photos, but I own every byte. Auto-backup from my phone, face recognition, geolocation, shared albums, search — all self-hosted. The development velocity is staggering (releases every few weeks), and the mobile app is genuinely polished. This is the killer app that justifies owning a server.

### 2. [navidrome/navidrome](https://github.com/navidrome/navidrome) ⭐21,790
**Why I starred this:** My personal Spotify. It streams my FLAC collection to any device, is Subsonic-compatible (works with dozens of clients), and the web UI is clean and fast. I've been running it for years and it's never crashed, never corrupted my library, and never complained. The true definition of boring technology done right.

### 3. [beetbox/beets](https://github.com/beetbox/beets) ⭐15,285
**Why I starred this:** The ultimate music librarian. It auto-tags and organizes my entire music collection using MusicBrainz, Discogs, and Beatport. The plugin system is incredible — fetch lyrics, calculate BPM, find duplicate tracks, generate playlists based on acoustic similarity. Without beets, my 50k-track library would be chaos.

### 4. [jeffvli/feishin](https://github.com/jeffvli/feishin) ⭐8,814
**Why I starred this:** The modern, beautiful desktop client that Jellyfin and Navidrome deserve. It looks like a premium streaming app — album art, artist bios, playlist management, gapless playback — but it connects to my self-hosted servers. If you want your self-hosted music to *feel* premium, this is the client.

### 5. [LumePart/Explo](https://github.com/LumePart/Explo) ⭐1,636
**Why I starred this:** Spotify's "Discover Weekly" algorithm, but for my self-hosted music. It analyzes listening history and finds tracks I haven't heard but will probably love. The magic of music discovery without sending data to anyone else. This is the feature that made me stop missing Spotify.

### 6. [metabrainz/picard](https://github.com/metabrainz/picard) ⭐4,954
**Why I starred this:** The gold standard for music tagging. When beets can't figure out a track, Picard can — it uses acoustic fingerprinting (AcoustID) to identify songs even with completely missing metadata. It's saved me countless hours of manual tagging.

### 7. [LizardByte/Sunshine](https://github.com/LizardByte/Sunshine) ⭐38,401
**Why I starred this:** Self-hosted game streaming that actually works at low latency. Pair it with Moonlight on any client device and I can play my gaming PC from my laptop, tablet, or TV. It's the backbone of my home gaming setup — no cloud service needed.

### 8. [geekau/mediastack](https://github.com/geekau/mediastack) ⭐1,782
**Why I starred this:** Pre-configured Docker Compose for the entire *arr stack with security built in — VPN-bound traffic, MFA on remote access, proper network segmentation. It's the template I used to stand up my media server in an afternoon instead of a weekend.

### 9. [KRTirtho/spotube](https://github.com/KRTirtho/spotube) ⭐47,028
**Why I starred this:** A cross-platform music app that uses YouTube Music as its backend — open source, no account needed, works on desktop and mobile. It's the music player I recommend to friends who want to ditch subscriptions but don't want to self-host a full server.

### 10. [clangen/musikcube](https://github.com/clangen/musikcube) ⭐4,784
**Why I starred this:** A terminal-based music player that doubles as a streaming server. It's blazing fast (C++), has a gorgeous ncurses interface, and indexes even my largest libraries in seconds. When I'm SSH'd into my server and want to cue up music, this is what I use. Terminal aesthetics + real functionality.

---

## 🐳 Docker & Container Management — Top 10

### 1. [jesseduffield/lazydocker](https://github.com/jesseduffield/lazydocker) ⭐51,380
**Why I starred this:** The single best Docker TUI ever made. Full control over containers, images, volumes, networks — view logs, restart services, exec into containers, all with vim-keybindings and a beautiful terminal UI. It's the first tool I install on any server. Lazygit + lazydocker = my entire terminal workflow.

### 2. [amir20/dozzle](https://github.com/amir20/dozzle) ⭐13,314
**Why I starred this:** Real-time log viewer for Docker containers with fuzzy search, auto-scroll, and multi-host support. Instead of `docker logs -f` one container at a time, I see all my logs in one browser tab with filtering. It's so lightweight I forget it's running, and so useful I'd never go back.

### 3. [gethomepage/homepage](https://github.com/gethomepage/homepage) ⭐30,704
**Why I starred this:** (Yes, also in Homelab — it's that good.) Docker-native service dashboard. Add a few labels to your compose files and homepage auto-discovers every service, shows status indicators, and creates a beautiful launch page. It's the control center for my Docker fleet.

### 4. [ChrispyBacon-dev/DockFlare](https://github.com/ChrispyBacon-dev/DockFlare) ⭐2,191
**Why I starred this:** Automates Cloudflare Tunnel creation from Docker labels. Add `dockflare.tunnel: myapp` to a container label and it auto-creates a secure tunnel with Let's Encrypt. No more manual Cloudflare configuration. For anyone exposing services through Cloudflare, this is a massive time-saver.

### 5. [marvinvr/docktail](https://github.com/marvinvr/docktail) ⭐767
**Why I starred this:** Expose Docker containers as Tailscale services via labels. Combine Docker + Tailscale without touching Tailscale's config — just add a label and the container joins the tailnet. It's the cleanest integration between my two favorite networking tools.

### 6. [docker/docker-agent](https://github.com/docker/docker-agent) ⭐3,089
**Why I starred this:** Docker's own AI agent builder. It's the official Docker take on agent-native tooling — letting you build, run, and manage AI agents as Docker containers. I star it as a bet on where the industry is heading: agents as containerized workloads managed like any other service.

### 7. [loft-sh/devpod](https://github.com/loft-sh/devpod) ⭐14,972
**Why I starred this:** Codespaces, but open-source and provider-agnostic. Spin up dev environments on any cloud, Kubernetes cluster, or local Docker. It works with any IDE (VS Code, JetBrains, cursor, etc.). I use it for ephemeral dev environments — no more "works on my machine."

### 8. [getarcaneapp/arcane](https://github.com/getarcaneapp/arcane) ⭐5,787
**Why I starred this:** A modern, polished Docker management UI that doesn't feel like it was built in 2015. It's designed for "everyone" — not just ops people. I use it when I want a visual overview of my containers without opening Portainer's sometimes-overwhelming interface.

### 9. [clemcer/LoggiFly](https://github.com/clemcer/LoggiFly) ⭐1,741
**Why I starred this:** Alerting for Docker logs. It watches container logs for patterns (errors, warnings, custom regex) and sends notifications (Discord, Slack, Telegram). Instead of discovering a crashed service days later, I get a ping the moment something goes wrong. Simple, focused, effective.

### 10. [DockSTARTer/DockSTARTer](https://github.com/GhostWriters/DockSTARTer) ⭐2,560
**Why I starred this:** The "I want Docker apps running but don't want to think about it" tool. Interactive TUI that lets you pick from 100+ apps, then generates optimized docker-compose configs with proper networking, permissions, and update strategies. It's how I onboard friends to self-hosting.

---

## 🧠 AI / LLM Tools — Top 10

### 1. [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp) ⭐117,150
**Why I starred this:** The engine that made local LLMs practical. Before llama.cpp, running a language model locally required a GPU and patience. Now I run Llama 3, Mistral, and Qwen on my laptop CPU. It's the foundation that everything else — Ollama, LocalAI, LM Studio — is built on. A genuine revolution in a C++ codebase.

### 2. [mudler/LocalAI](https://github.com/mudler/LocalAI) ⭐46,960
**Why I starred this:** The everything-in-one local AI engine. Drop-in OpenAI API replacement that runs LLMs, image generation, audio transcription, text-to-speech, embeddings — all locally, no GPU required. I use it as my personal AI backend for privacy-sensitive projects. It's the self-hoster's answer to the OpenAI API.

### 3. [qdrant/qdrant](https://github.com/qdrant/qdrant) ⭐32,438
**Why I starred this:** The vector database I trust for production workloads. Written in Rust, blisteringly fast, and the API is a joy to use. It powers semantic search, RAG pipelines, and recommendation systems in my projects. The filtering + vector search combination is unmatched.

### 4. [HKUDS/LightRAG](https://github.com/HKUDS/LightRAG) ⭐36,752
**Why I starred this:** RAG made simple and actually fast. LightRAG doesn't try to be everything — it does retrieval-augmented generation with a focus on speed and simplicity. Graphs + vectors working together. For projects where I need "search my documents" without a PhD in information retrieval, this is it.

### 5. [tashfeenahmed/freellmapi](https://github.com/tashfeenahmed/freellmapi) ⭐10,763
**Why I starred this:** A single OpenAI-compatible endpoint that stacks the free tiers of 16 different LLM providers. Smart routing, automatic failover, ~1.7 billion tokens/month for free. It's my fallback for when I don't want to pay for API calls during development and experimentation.

### 6. [yamadashy/repomix](https://github.com/yamadashy/repomix) ⭐26,381
**Why I starred this:** Packs an entire repository into a single AI-friendly file — respecting .gitignore, with token counting and intelligent formatting. When I need to feed a codebase to ChatGPT or Claude, this is how I do it. Essential for the "understand my project" prompt.

### 7. [dragonflydb/dragonfly](https://github.com/dragonflydb/dragonfly) ⭐30,730
**Why I starred this:** A Redis replacement that's 25x faster on a single node and uses dramatically less memory. Drop-in compatible with the Redis protocol, so all my existing code works. I use it as the fast cache layer in my agent memory stack — sub-millisecond latency with no operational overhead.

### 8. [hiyouga/LlamaFactory](https://github.com/hiyouga/LlamaFactory) ⭐72,279
**Why I starred this:** Fine-tuning made accessible. One tool that supports 100+ models with a unified interface — LoRA, QLoRA, full fine-tuning, RLHF. Before LlamaFactory, fine-tuning a model meant stitching together 5 different libraries. Now it's a single config file and one command.

### 9. [upstash/context7](https://github.com/upstash/context7) ⭐57,625
**Why I starred this:** Always-updated code documentation injected into LLM context. When my coding agent needs to use a library, Context7 provides the actual API reference rather than stale training data. It's the difference between "I think this function exists" and "I know this is the current API."

### 10. [browser-use/browser-harness](https://github.com/browser-use/browser-harness) ⭐15,058
**Why I starred this:** Self-healing browser automation for LLMs. It handles the messy reality of web automation — selectors change, pages load slowly, popups appear — so my agents don't get stuck. If an agent needs to interact with any website reliably, this is the harness that makes it possible.

---

## 🏆 The "If I Could Only Keep 5" List

If I had to rebuild from scratch with only 5 tools from these stars:

| # | Repo | Category | Why |
|---|------|----------|-----|
| 1 | [anomalyco/opencode](https://github.com/anomalyco/opencode) | Agentic Dev | The agent I actually live in |
| 2 | [coollabsio/coolify](https://github.com/coollabsio/coolify) | Homelab | Deploys everything else |
| 3 | [immich-app/immich](https://github.com/immich-app/immich) | Media | The app my family cares about |
| 4 | [jesseduffield/lazydocker](https://github.com/jesseduffield/lazydocker) | Docker | Ops without the pain |
| 5 | [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp) | AI/LLM | The engine that runs everything else locally |

---

*From [pvnkmnk's stars](https://github.com/pvnkmnk) · Curated with [gh-stars](https://github.com/prabirshrestha/gh-stars)*
