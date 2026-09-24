"""Channel safety rules for every YouTube write (docs/CHANNELS_STATUS.md, rule 0)."""

from __future__ import annotations

# TAŞDEMİR MA (@tasdemirma3215) — personal channel; nothing is ever uploaded here, tests included.
BLOCKED_CHANNEL_IDS: frozenset[str] = frozenset({"UCa-ulc77JRueoWa11LPQUVg"})


class ChannelGuardError(RuntimeError):
    pass


def assert_upload_allowed(expected_channel_id: str, authorised_channel_id: str) -> None:
    """Raise unless the OAuth token belongs to the configured, non-blocked channel."""
    if not expected_channel_id:
        raise ChannelGuardError("youtube_channel_id boş: bu kanal için upload kapalı")
    if expected_channel_id in BLOCKED_CHANNEL_IDS:
        raise ChannelGuardError(f"config engelli kanala işaret ediyor: {expected_channel_id}")
    if not authorised_channel_id:
        raise ChannelGuardError("OAuth token hiçbir kanala bağlı değil")
    if authorised_channel_id in BLOCKED_CHANNEL_IDS:
        raise ChannelGuardError(f"token engelli kanala ait: {authorised_channel_id}")
    if authorised_channel_id != expected_channel_id:
        raise ChannelGuardError(
            f"kanal uyuşmazlığı: token {authorised_channel_id}, config {expected_channel_id}"
        )
