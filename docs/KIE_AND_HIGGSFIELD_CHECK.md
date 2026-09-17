# KIE_AND_HIGGSFIELD_CHECK.md

Specific audit for brief §§7–10. **No secrets printed.**

## Is Kie.ai already integrated?

**No.**

Repo search finds no Kie client, no `api.kie.ai` calls, no `KIE_API_KEY` in settings/`.env.example`.

Official docs (verified): https://docs.kie.ai/  
- Async jobs: `POST /api/v1/jobs/createTask`  
- Poll: `GET /api/v1/jobs/recordInfo?taskId=…`  
- Auth: `Authorization: Bearer <API_KEY>`  
- Models: browse live market https://kie.ai/market (do not hard-code lists)  
- Pricing: https://kie.ai/pricing  
- Retention: generated media ~14 days on their side — must copy to our storage  

## Is Higgsfield already integrated?

**No.**

No Higgsfield SDK, no `platform.higgsfield.ai` calls, no `HF_API_KEY_ID` / `HF_API_KEY_SECRET`.

Official docs (verified): https://docs.higgsfield.ai/docs  
- Base: `https://platform.higgsfield.ai`  
- Auth: `Authorization: Key KEY_ID:KEY_SECRET`  
- Async request_id + status polling/webhooks  
- Official SDKs exist (`higgsfield-client`, `higgsfield-js`) — **not installed**  
- Output retention short — download to our storage  

## Which models are configured?

**None** for Kie/Higgsfield.

Current configured “media” path is local/open:

- Visuals: Pillow cards  
- Voice: edge-tts / gTTS / espeak  
- Assembly: FFmpeg  

ElevenLabs appears only as an empty settings field / stub preference string — **NOT CONFIGURED**.

## Which APIs are actually working?

| API | Working? |
| --- | --- |
| Wikipedia / Commons / trends HTTP | Yes |
| gTTS / FFmpeg produce path | Yes |
| YouTube Data/Analytics code | Present |
| YouTube live calls | **No** (missing `token.json`) |
| Kie.ai | **No** |
| Higgsfield | **No** |

## Missing environment variables (for future integration)

- `KIE_API_KEY`  
- `HF_API_KEY_ID`  
- `HF_API_KEY_SECRET`  
- (optional) provider webhook base URL / callback secrets  

Not present today.

## Duplicate media-generation integrations?

**No duplicate AI video/image gateways** — because none exist yet.

There **is** duplicate *local* visual/TTS/assembly code (`kanallar/*` vs new stack). That is separate from Kie/Higgsfield.

## Can provider abstraction already support both?

**Not yet.** There is a narrow TTS waterfall in `voice/provider.py`, but no `MediaProvider` covering image/video/voice/status/cost.

Voice interface is a starting point; it must be generalized before adding Kie/Higgsfield or the app will become provider-locked.

## What needs to change (after approval only)

1. Design `MediaProvider` + job polling/webhooks.  
2. Add `KieProvider` as primary gateway.  
3. Add `HiggsfieldProvider` as secondary/premium/fallback.  
4. Persist provider task IDs, costs, model IDs on scenes/assets.  
5. Copy results to our object storage (both vendors delete outputs).  
6. Scene router chooses asset type + provider + model.  
7. Keep Remotion/FFmpeg as assemblers, not generators.  
