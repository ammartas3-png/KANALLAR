from __future__ import annotations

from youtube.api import _client


def add_to_playlist(youtube_video_id: str, playlist_id: str) -> dict:
    youtube = _client()
    body = {
        "snippet": {
            "playlistId": playlist_id,
            "resourceId": {"kind": "youtube#video", "videoId": youtube_video_id},
        }
    }
    return youtube.playlistItems().insert(part="snippet", body=body).execute()
