from media.base import MediaJob
from media.local import LocalCardsProvider
from media.router import choose_provider, status_report


def test_local_provider_always_configured():
    provider = LocalCardsProvider()
    assert provider.configured() is True
    job = provider.generate_image("test prompt")
    assert isinstance(job, MediaJob)
    assert job.status == "success"
    assert job.provider == "local"


def test_choose_provider_local_quality(monkeypatch):
    monkeypatch.setenv("MEDIA_QUALITY", "local")
    from config.settings import get_settings

    get_settings.cache_clear()
    provider = choose_provider("image", quality="local")
    assert provider.name == "local"


def test_status_report_keys():
    report = status_report()
    assert set(report) >= {"local", "kie", "higgsfield"}
    assert report["local"]["configured"] is True


def test_kie_not_configured_without_key(monkeypatch):
    monkeypatch.setenv("KIE_API_KEY", "")
    from config.settings import get_settings
    from media.kie import KieProvider

    get_settings.cache_clear()
    provider = KieProvider()
    assert provider.configured() is False
    job = provider.generate_image("x")
    assert job.status == "not_configured"


def test_higgsfield_not_configured_without_keys(monkeypatch):
    monkeypatch.setenv("HF_API_KEY_ID", "")
    monkeypatch.setenv("HF_API_KEY_SECRET", "")
    from config.settings import get_settings
    from media.higgsfield import HiggsfieldProvider

    get_settings.cache_clear()
    provider = HiggsfieldProvider()
    assert provider.configured() is False
