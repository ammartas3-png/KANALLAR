from __future__ import annotations


def add_to_playlist(youtube, youtube_video_id: str, playlist_id: str) -> dict:
    """Uses the caller's already channel-verified client."""
    body = {
        "snippet": {
            "playlistId": playlist_id,
            "resourceId": {"kind": "youtube#video", "videoId": youtube_video_id},
        }
    }
    return youtube.playlistItems().insert(part="snippet", body=body).execute()
