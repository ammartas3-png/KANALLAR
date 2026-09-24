# GITHUB_REPOSITORIES_AUDIT.md

Do **not** install automatically. Classification: **REQUIRED** / **USEFUL LATER** / **REDUNDANT** / **NOT RELEVANT**.

| Repository / tool | Problem it claims to solve | Already solved here? | Class | Decision |
| --- | --- | --- | --- | --- |
| Official Google YouTube APIs (via google-api-python-client) | Upload + analytics | Partially (code yes, token no) | REQUIRED | Keep |
| FFmpeg (system) | Assemble/encode Shorts | Yes | REQUIRED | Keep |
| Remotion (`remotion-dev/remotion`) | Programmatic 9:16 compose | Partially (template only) | USEFUL LATER | Keep as optional cloud renderer candidate; do not dual-run until chosen |
| remotion-dev/template-tiktok + Whisper.cpp | ASR captions | No | NOT RELEVANT for V1 | Local/heavy; brief forbids local Whisper |
| yt-dlp/yt-dlp | Competitor metadata | Partially | USEFUL LATER | Metadata only |
| calesthio/OpenMontage | Full agentic studio | Partially (flow inspiration) | REDUNDANT | Do not vendor; too many paid/tooling deps |
| browser-use/browser-use | Browser automation | Stub only | NOT RELEVANT for V1 | Official YouTube API preferred |
| DeusData/codebase-memory-mcp | Repo context efficiency | Local script exists | USEFUL LATER | Optional; disabled MCP |
| OpenViking | Long-term memory | DB memory tables exist | USEFUL LATER | Not needed for V1 |
| agency-agents / agent-memory / gstack / Switchyard | Agent frameworks | Custom agents exist | REDUNDANT | Avoid framework sprawl |
| G0DM0D3 | Unclear/niche tooling | No | NOT RELEVANT | Skip |
| FreeLLMApi / AirLLM / Nemotron / Ollama | Cheap/local LLM | LLM stub unused | NOT RELEVANT for V1 | Local AI out of scope |
| higgsfield-ai/higgsfield-client | Official HF SDK | Not integrated | USEFUL LATER | Only after MediaProvider exists |
| Kie.ai (SaaS, not a GitHub dep) | Unified media gateway | Not integrated | USEFUL LATER / likely primary gateway | Evaluate after approval |
| n8n | Orchestration | APScheduler stub | USEFUL LATER | Schedules/webhooks/approvals only |

## Principle check

Adding OpenMontage or agent frameworks would **duplicate** existing pipeline modules and violate minimum-tools.

Adding Kie/Higgsfield SDKs is justified **only after** a `MediaProvider` interface exists — otherwise the app becomes provider-locked.
