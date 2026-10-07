# Ishaan Koradia - Personal MCP Server

A remote Model Context Protocol (MCP) server that provides information about me via StreamableHTTP -- Ishaan Koradia, an aspiring AI/ML Engineer and undergraduate student at UC San Diego. 

## About

This MCP server allows my personal AI chatbot to access structured information about me from my bio, achievements, skills, and contact information. As a backend for [my personal website](https://github.com/ishaankor/my-personal-website), it provides a standardized way to share personal and professional details through the MCP protocol that's both secure and optimal.

## Dynamic Features & Live Telemetry

- **Spotify Live Telemetry**: Real-time currently-playing track, artist, album artwork, and recent listening history via Spotify Web API OAuth and live production fallback (`ishaankoradia.com/api/spotify`).
- **NVIDIA & Handshake AI Collaboration**: Real-time role details, Nemotron-12B evaluation, 300+ context strategies, and agentic workflows dynamically extracted from live `portfolio.ts` and Chapter 04 of `index.html`.
- **Apple Shortcuts & Website Chapters**: Dynamic extraction of all 7 chapters from `ishaankoradia.com` (Origins story, iCloud install links for Parked Car Pinner, Assignment Teller, Alarm Clock Setter, Mind phases, Sandbox thought bubbles, Open Door contacts).
- **Dynamic Research & EDA Discovery**: Automatic discovery of all Exploratory Data Analysis repositories on GitHub matching data science topics, parsing live READMEs for research questions, findings, datasets, and video demonstrations without hardcoded lists.
- **Flagship Projects Catalog**: Dynamically synchronized across `portfolio.ts`, live GitHub repositories, and creative Sandbox notes.
- **Live Workbench Telemetry**: Real-time GitHub commit stream and active repository tracking.
- **BM25 Search Engine**: Sub-millisecond ranker with synonym expansion and domain phrase boosting.

## Exposed MCP Tools

1. `search_ishaan(query)` - Unified semantic BM25 retrieval across all domains.
2. `get_current_music()` - Human-readable live Spotify status.
3. `get_spotify_telemetry()` - Structured real-time Spotify telemetry with album art and playback state.
4. `get_current_job_and_nvidia_experience()` - Real-time Handshake AI / NVIDIA Nemotron-12B role details.
5. `get_apple_shortcuts()` - Live Apple Shortcuts with iCloud installation links and origins narrative.
6. `get_eda_research(study_name)` - Dynamic multi-repo EDA research discovery and live README analysis.
7. `get_personal_website_info()` - Live architectural overview and content for all 7 chapters.
8. `get_website_chapter(chapter_identifier)` - Deep-dive into specific chapters (01-07, identity, spark, mind, frontier, sandbox, pulse, door).
9. `list_projects()` - Structured portfolio systems, featured items, and live GitHub catalog.
10. `get_project_details(project_name)` - Deep-dive into project architecture via segmented READMEs.
11. `get_live_workbench_activity()` - Real-time GitHub commit feed and active workbench telemetry.
12. `get_portfolio_resume_and_work()` - Live candidate profile, verified experience, education, certs, and portfolio Work tab links.

## HTTP Endpoints

- `/health` - Service health check
- `/` - Root status endpoint
- `/spotify` - Public REST endpoint serving real-time Spotify telemetry
- StreamableHTTP MCP protocol transport for AI agents and chat assistants

### Connect
- GitHub: [ishaankor](https://github.com/ishaankor)
- LinkedIn: [ishaankoradia](https://linkedin.com/in/ishaankoradia)
- Email: ishaankor@gmail.com

## Contributing

This is a personal project, but feedback and suggestions are welcome! Feel free to open an issue or reach out directly.
