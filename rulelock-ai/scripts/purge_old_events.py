"""Purge transaction events past the configured retention window.

By default this reports the number of matching rows. Pass --execute to delete.
The caller must provide SUPABASE_URL, SUPABASE_SECRET_KEY, and RETENTION_DAYS.
"""
import argparse
from datetime import datetime, timedelta, timezone
import os
import sys

import requests


def retention_cutoff(days_value, now=None):
    try:
        days = int(days_value)
    except (TypeError, ValueError) as exc:
        raise ValueError("RETENTION_DAYS must be a positive integer") from exc
    if days < 1:
        raise ValueError("RETENTION_DAYS must be a positive integer")
    return (now or datetime.now(timezone.utc)) - timedelta(days=days)


def purge_old_events(execute=False, http=requests):
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_SECRET_KEY", "")
    days = os.environ.get("RETENTION_DAYS", "365")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SECRET_KEY must be set")
    cutoff = retention_cutoff(days).isoformat()
    endpoint = f"{url}/rest/v1/transaction_events"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Prefer": "count=exact,return=minimal",
    }
    params = {"created_at": f"lt.{cutoff}"}
    if not execute:
        response = http.get(endpoint, headers=headers, params={**params, "select": "event_id", "limit": "1"}, timeout=15)
        response.raise_for_status()
        content_range = response.headers.get("Content-Range", "*/0")
        total = content_range.rsplit("/", 1)[-1]
        if total == "*":
            raise RuntimeError("Supabase did not return an exact purge count")
        return {"cutoff": cutoff, "matched": int(total), "deleted": 0}

    response = http.delete(endpoint, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    content_range = response.headers.get("Content-Range", "*/unknown")
    total = content_range.rsplit("/", 1)[-1]
    return {"cutoff": cutoff, "matched": int(total) if total.isdigit() else None,
            "deleted": int(total) if total.isdigit() else None}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="delete matching events; default is a dry run")
    args = parser.parse_args(argv)
    try:
        result = purge_old_events(execute=args.execute)
    except (RuntimeError, ValueError, requests.RequestException) as exc:
        print(f"Purge failed: {exc}", file=sys.stderr)
        return 1
    mode = "deleted" if args.execute else "would delete"
    count = result["deleted"] if args.execute else result["matched"]
    print(f"cutoff={result['cutoff']} rows_{mode}={count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
