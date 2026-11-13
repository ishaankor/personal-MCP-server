# Ishaan Koradia - Personal MCP Server

A production-grade, remote **Model Context Protocol (MCP)** server built with Python and FastMCP. It powers the cognitive backend of [ishaankoradia.com](https://ishaankoradia.com) and serves structured, live telemetry about my engineering career, active research, GitHub codebase evolution, and projects via **StreamableHTTP**.

---

## Architecture Overview

```
                                  +------------------------------------+
                                  |     Frontier LLM / AI Clients      |
                                  |   (IshaanBot, Claude, Cursor, etc) |
                                  +-----------------+------------------+
                                                    |
                                       Model Context Protocol
                                          (StreamableHTTP)
                                                    v
+--------------------------------------------------------------------------------------+
|                           Personal MCP Server (FastMCP)                              |
|                                                                                      |
|  +--------------------+   +-----------------------+   +---------------------------+  |
|  | Knowledge Base     |   | Live Git Telemetry    |   | Live Spotify Telemetry    |  |
|  | (BM25 Search +     |   | (Meta-Fetcher Proxy,  |   | (OAuth 2.0 PKCE,          |  |
|  |  Synonym Expansion)|   |  Contribution Anchor) |   |  iTunes Metadata Enriched)|  |
|  +--------------------+   +-----------------------+   +---------------------------+  |
+------------------------------------------+-------------------------------------------+
                                           |
                                           v
                  +--------------------------------------------------+
                  |                 Remote Data Layer                |
                  |  - GitHub API & Personal Meta Fetcher            |
                  |  - ishaankoradia.com & portfolio.ishaankoradia   |
                  |  - Spotify Web API                               |
                  +--------------------------------------------------+
```

---

## Dynamic Features & Live Telemetry

- **Live Spotify Playback**: Real-time currently-playing track, artist, album artwork, genre detection, and recent listening history via Spotify Web API OAuth with live proxy fallback.
- **NVIDIA & Handshake AI Engineering**: Real-time role details, Nemotron-12B evaluation, golden benchmark datasets, context strategies, and agentic workflows dynamically extracted from live portfolio records.
- **Apple Shortcuts & Origins Narrative**: Dynamic extraction of personal website chapters (Origins story, iCloud install links for Parked Car Pinner, Assignment Teller, Alarm Clock Setter).
- **Dynamic Research & EDA Discovery**: Automatic discovery of Exploratory Data Analysis repositories on GitHub, parsing live READMEs for hypothesis testing, clinical datasets, and video demonstrations.
- **Live Workbench Telemetry**: Real-time GitHub commit stream, line diff statistics (+additions/-deletions), active repositories, and contribution calendar metrics.
- **Deterministic Repository Ground Truth**: Direct enumeration of all 20 public GitHub repositories (including forks), preventing hallucinated or phantom repositories.
- **BM25 Search Engine**: Sub-millisecond keyword ranker with domain-weighted synonym expansion and camelCase tokenization.

---

## Exposed MCP Tools

| Tool | Description |
| :--- | :--- |
| `get_github_repositories` | Complete authoritative list and breakdown of Ishaan's 20 public GitHub repositories (19 original projects + 1 fork). |
| `get_live_workbench_activity` | Real-time engineering telemetry: latest commit, lines of code changed, modified files, active repository. |
| `get_git_telemetry` | Full Git telemetry, LOC changes, commit diff statistics, active repositories, and historical velocity. |
| `query_git_commits_and_repositories` | Deterministic commit queries filtered by date range (ISO YYYY-MM-DD), repository, and chronological/activity ordering. |
| `get_project_details` | Full project metadata, creation timeline, tech stack, architecture, and segmented documentation. |
| `list_projects` | Filterable catalog of software applications, flagship production platforms, and college passion projects. |
| `get_current_job_and_nvidia_experience` | Real-time Handshake AI / NVIDIA Nemotron-12B role details and golden benchmark curation. |
| `get_eda_research` | Dynamic multi-repo Exploratory Data Analysis (EDA) research discovery and clinical findings. |
| `get_apple_shortcuts` | Apple Shortcuts catalog with iCloud install links and origins story. |
| `get_personal_website_info` | Architecture, narrative chronicle, and dynamic features across all 7 website chapters. |
| `get_website_chapter` | Deep-dive into specific chapters (Identity, Spark, Mind, Frontier, Sandbox, Pulse, Connect). |
| `get_current_music` | Human-readable live Spotify status and recent rotation. |
| `get_spotify_telemetry` | Structured real-time Spotify playback telemetry (track, artist, album art, progress, playback state). |
| `get_portfolio_resume_and_work` | Live candidate profile, verified experience, education, certifications, and portfolio Work tab links. |
| `get_basic_info_and_facts` | Biographical facts, location, contact details, education, and curated personal fun facts. |

---

## Getting Started

### 1. Prerequisites
- Python 3.12+
- (Optional) Docker

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/ishaankor/personal-MCP-server.git
cd personal-MCP-server

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy the example environment file:
```bash
cp .env.example .env
```
Fill in your optional Spotify API credentials if you wish to run live Spotify telemetry locally (otherwise fallback mock/production proxies are used).

### 4. Running the Server
```bash
python main.py
```
The server will start on `http://127.0.0.1:5000` (or `PORT` specified in your `.env`).

---

## Docker Deployment

To build and run via Docker:

```bash
# Build the Docker image
docker build -t ishaankor/remotemcpserver:latest .

# Run the container
docker run -p 8000:8000 --env-file .env ishaankor/remotemcpserver:latest
```

---

## Endpoints

- `/` - Root health check and service status
- `/health` - Liveness probe
- `/spotify` - Public REST endpoint for current Spotify playback telemetry
- StreamableHTTP MCP transport for LLM clients

---

## Connect
- **Website**: [ishaankoradia.com](https://ishaankoradia.com)
- **Portfolio**: [portfolio.ishaankoradia.com](https://portfolio.ishaankoradia.com)
- **GitHub**: [github.com/ishaankor](https://github.com/ishaankor)
- **LinkedIn**: [linkedin.com/in/ishaankoradia](https://linkedin.com/in/ishaankoradia)
