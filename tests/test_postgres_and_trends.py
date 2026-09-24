import os

import pytest
from sqlalchemy import inspect, text

from database.session import init_db
from research.trends import wikipedia_most_read


def test_postgres_schema_if_available():
    url = "postgresql+psycopg://kanallar:kanallar@127.0.0.1:5432/kanallar"
    try:
        engine = init_db(url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        pytest.skip(f"PostgreSQL yok: {exc}")
    tables = set(inspect(engine).get_table_names())
    assert {"channels", "ideas", "scripts", "videos", "uploads", "analytics", "experiments", "memory"} <= tables


def test_wikipedia_trends_optional():
    if os.environ.get("SKIP_NET"):
        pytest.skip("ağ kapalı")
    rows = wikipedia_most_read("tr", limit=3)
    if not rows:
        pytest.skip("Wikipedia most-read boş/erişilemedi")
    assert rows[0]["title"]
    assert rows[0]["source"] == "wikipedia_mostread"
