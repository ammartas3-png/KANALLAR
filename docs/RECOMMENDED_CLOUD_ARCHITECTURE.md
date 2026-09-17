# RECOMMENDED_CLOUD_ARCHITECTURE.md

Recommended target architecture **after approval**. Not implemented in this pass.

## North-star topology

```
                    ┌─────────────────────────────┐
                    │  Cloud Worker / API Service │
                    │  (always-on; not Cursor)    │
                    └──────────────┬──────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        ▼                          ▼                          ▼
  Postgres (online)        Object Storage (R2/S3/GCS)     Secrets Manager
  jobs, videos,            scripts, voice, clips,         YT OAuth, Kie,
  analytics, lessons       finals, thumbs                 Higgsfield, LLM
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
            MediaProvider                   YouTubeProvider
            ┌─────────────┐                 Official Data +
            │ Kie (primary)│                 Analytics APIs
            │ Higgsfield   │
            │ (secondary)  │
            └─────────────┘
                    │
                    ▼
            Assembler (cloud)
            Remotion render worker
            and/or FFmpeg worker
                    │
                    ▼
            Preview → Human Approve → Upload private/schedule
                    │
                    ▼
            Analytics snapshots → Learning → Next idea
```

## Layering rules

1. **App never imports Kie/Higgsfield SDKs in agents.** Only `MediaProvider` adapters do.  
2. **Assemblers consume assets + storyboard JSON**, not provider APIs.  
3. **One write path for jobs** with stage/scene state machine.  
4. **Cursor/GitHub = development**; production = cloud worker + DB + storage.  
5. **n8n (optional)** triggers schedules, approval pings, analytics polls — business logic stays in app.

## MediaProvider contract (conceptual)

```
generateImage(prompt, opts) -> JobRef
generateVideo(prompt, opts) -> JobRef
generateVoice(text, voiceProfile) -> JobRef
getJobStatus(jobRef) -> Status
getResult(jobRef) -> AssetURI + cost + meta
estimateCost(request) -> Money
handleError(err) -> Retry | FallbackProvider | Fail
```

Providers: `KieProvider`, `HiggsfieldProvider`, later others.

## Model router (per scene)

Inputs: scene type, budget, deadline, past success, channel style.  
Output: `{asset_type, provider, model_id}` chosen for **quality×cost**, never max spend by default.

## Assembly recommendation

- **V1 assembler:** keep battle-tested **FFmpeg cloud worker** (already works).  
- **V1.5:** add **Remotion cloud render** for captions/motion polish when needed.  
- Do not require both for every video on day one.

## Human approval

Default: `status=awaiting_approval` after QC.  
Upload only after explicit approve action (studio button / n8n webhook / CLI flag with confirmation).

## Multi-channel

Shared engine + per-channel config/secrets/memory. No forked apps.
