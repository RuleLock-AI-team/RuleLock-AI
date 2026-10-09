import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts import purge_old_events as purge


class Response:
    headers = {"Content-Range": "0-0/17"}

    @staticmethod
    def raise_for_status():
        pass


def test_purge_defaults_to_count_only(monkeypatch):
    calls = []

    class Http:
        @staticmethod
        def get(url, **kwargs):
            calls.append(("get", url, kwargs))
            return Response()

        @staticmethod
        def delete(url, **kwargs):
            calls.append(("delete", url, kwargs))
            return Response()

    monkeypatch.setenv("SUPABASE_URL", "https://supabase.example")
    monkeypatch.setenv("SUPABASE_SECRET_KEY", "test-secret")
    monkeypatch.setenv("RETENTION_DAYS", "30")
    result = purge.purge_old_events(http=Http)
    assert result["matched"] == 17
    assert result["deleted"] == 0
    assert [call[0] for call in calls] == ["get"]


def test_purge_execute_uses_configured_cutoff(monkeypatch):
    calls = []

    class Http:
        @staticmethod
        def get(url, **kwargs):
            raise AssertionError("execute should not run a dry-run read")

        @staticmethod
        def delete(url, **kwargs):
            calls.append((url, kwargs))
            return Response()

    monkeypatch.setenv("SUPABASE_URL", "https://supabase.example")
    monkeypatch.setenv("SUPABASE_SECRET_KEY", "test-secret")
    monkeypatch.setenv("RETENTION_DAYS", "30")
    result = purge.purge_old_events(execute=True, http=Http)
    assert result["deleted"] == 17
    assert calls[0][1]["params"]["created_at"].startswith("lt.")


def test_retention_days_must_be_positive_integer():
    for value in (None, "zero", "0", "-1"):
        try:
            purge.retention_cutoff(value)
        except ValueError:
            continue
        raise AssertionError(f"invalid retention value accepted: {value}")
