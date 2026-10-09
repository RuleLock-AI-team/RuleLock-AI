from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta, timezone
import logging
import hmac
import re
import uuid
from requests import RequestException

from config import RULELOCK_ALLOW_NO_AUTH, RULELOCK_API_TOKEN
from db import (
    get_device_events,
    get_phone_events,
    get_review_event,
    get_audit_log,
    insert_audit_log,
    count_audit_events,
    count_transaction_events,
    get_rulelock_setting,
    get_session_events,
    insert_review_record,
    set_rulelock_setting,
    get_account_profile,
    get_cod_history,
    get_usernames,
    get_order_reference,
    get_order_references,
    get_order_id_by_reference,
)
from services.forwarder import call_anomaly_engine, call_enforcement_engine, call_rule_engine

bp = Blueprint("events", __name__)
logger = logging.getLogger(__name__)

def session_features(session_id, device_id=None, phone_hash=None):
    rows = get_session_events(session_id) or []
    from features import average_seconds_between_requests
    avg_seconds_between_requests = average_seconds_between_requests(rows)

    metadata_rows = [row.get("metadata") or {} for row in rows]
    device_id = device_id or next((meta.get("device_id") for meta in metadata_rows if meta.get("device_id")), None)
    phone_hash = phone_hash or next((meta.get("phone_hash") for meta in metadata_rows if meta.get("phone_hash")), None)
    device_rows = get_device_events(device_id) if device_id else []
    phone_rows = get_phone_events(phone_hash) if phone_hash else []
    accounts = {str((row.get("metadata") or {}).get("account_id") or row.get("user_id"))
                for row in device_rows
                if (row.get("metadata") or {}).get("account_id") is not None or row.get("user_id") is not None}
    addresses = {(row.get("metadata") or {}).get("address_hash") for row in phone_rows
                 if (row.get("metadata") or {}).get("address_hash")}
    span_rows = []
    for row in rows:
        stamp = row.get("created_at")
        try:
            parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            span_rows.append(parsed)
        except (AttributeError, TypeError, ValueError):
            pass
    span_seconds = (max(span_rows) - min(span_rows)).total_seconds() if len(span_rows) >= 2 else 0

    return {
        "session_id": session_id,
        "event_count": len(rows),
        "coupon_attempts": sum(row["event_type"] == "APPLY_COUPON" for row in rows),
        "checkout_count": sum(row["event_type"] == "CHECKOUT" for row in rows),
        "session_span_seconds": span_seconds,
        "coupon_attempts_per_session": sum(row["event_type"] == "APPLY_COUPON" for row in rows),
        "avg_seconds_between_requests": avg_seconds_between_requests,
        "distinct_accounts_same_device": max(len(accounts), 1),
        "distinct_addresses_same_phone": max(len(addresses), 1),
    }


def _bigint(value):
    try:
        if isinstance(value, bool):
            return None
        if isinstance(value, float) and not value.is_integer():
            return None
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _authorized_request():
    if not RULELOCK_API_TOKEN:
        return RULELOCK_ALLOW_NO_AUTH
    supplied = request.headers.get("Authorization", "")
    scheme, _, token = supplied.partition(" ")
    return scheme.lower() == "bearer" and hmac.compare_digest(token, RULELOCK_API_TOKEN)


def _as_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _decision_from_results(rule_result, anomaly_result, enforcement_result):
    if not rule_result.get("available", True):
        return "hold", rule_result.get("reason", "rule-engine unavailable")
    if not anomaly_result.get("available", True):
        return "hold", anomaly_result.get("reason", "anomaly-detection unavailable")
    if not enforcement_result.get("available", True):
        return "hold", enforcement_result.get("reason", "enforcement-engine unavailable")
    if enforcement_result.get("decision") == "accept":
        return "accept", "order passed RuleLock checks"
    if enforcement_result.get("decision") == "void_discount":
        return "void_discount", enforcement_result.get("reason", "discount removed")
    if enforcement_result.get("decision") == "hold":
        return "hold", enforcement_result.get("reason", "order requires review")
    if enforcement_result.get("decision") == "reject":
        return "reject", enforcement_result.get("reason", "order rejected by RuleLock")
    return "hold", enforcement_result.get("reason", "review could not be completed")


def _cakely_status(decision):
    return {
        "accept": "capture_payment",
        "void_discount": "void_discount",
        "hold": "hold_payment",
        "reject": "block_payment",
    }.get(decision, ("hold_payment", "review"))


def _review_response(order_id, decision, reason, rule_result=None, anomaly_result=None, enforcement_result=None, order_reference=None):
    enforcement_result = enforcement_result or {"decision": "hold"}
    return {
        "order_id": order_id,
        "order_reference": order_reference or str(order_id),
        "decision": decision,
        "reason": reason,
        "customer_message": {
            "accept": "Your order is ready to continue.",
            "void_discount": "Your order can continue with an updated total.",
            "hold": "Your order needs a quick review before it can continue.",
            "reject": "We could not complete this order. Please contact support.",
        }.get(decision, "Your order needs a quick review before it can continue."),
        "payment_action": _cakely_status(decision),
        "account_action": enforcement_result.get("account_action"),
        "rule_result": rule_result or {"available": True, "passed": True, "failures": []},
        "anomaly_result": anomaly_result or {"available": True, "raw_score": 0.0, "is_anomaly": False},
        "enforcement_result": enforcement_result,
        "rulelock_enabled": True,
    }


def _stored_review_response(stored, fallback_order_id, fallback_order_reference=None):
    prior_decision = stored.get("decision", "hold")
    if prior_decision not in {"accept", "hold", "reject", "void_discount"}:
        prior_enforcement = stored.get("enforcement_result") or {}
        prior_decision = {
            "none": "accept", "void_discount": "void_discount",
            "hold_cod_order": "hold", "rate_limit_account": "reject",
        }.get(prior_enforcement.get("decision"), "hold")
    response = _review_response(
        stored.get("order_id", fallback_order_id), prior_decision,
        stored.get("reason", "Stored RuleLock decision"), stored.get("rule_result"),
        stored.get("anomaly_result"), stored.get("enforcement_result"),
        stored.get("order_reference") or fallback_order_reference or str(stored.get("order_id", fallback_order_id)),
    )
    if stored.get("customer_message"):
        response["customer_message"] = stored["customer_message"]
    if "account_action" in stored:
        response["account_action"] = stored["account_action"]
    if stored.get("pipeline"):
        response["pipeline"] = stored["pipeline"]
    return response


def _pipeline_snapshot(features, profile, rule_result, anomaly_result, enforcement_result):
    from decision import ANOMALY_HOLD_THRESHOLD, ANOMALY_REJECT_THRESHOLD
    from features import FEATURE_DEFAULTS
    score = float(anomaly_result.get("raw_score", 0.0) or 0.0)
    anomaly_status = "high_risk" if score < ANOMALY_REJECT_THRESHOLD else (
        "suspicious" if score < ANOMALY_HOLD_THRESHOLD else "normal")
    feature_names = ("coupon_attempts_per_session", "avg_seconds_between_requests",
                     "distinct_accounts_same_device", "distinct_addresses_same_phone")
    return {
        "c1_data_collection": {
            "status": "complete", "events_in_session": int(features.get("event_count", 0) or 0),
            "session_features": {name: features.get(name, FEATURE_DEFAULTS.get(name, 0)) for name in feature_names},
            "account": profile,
        },
        "c2_rule_engine": {"status": "pass" if rule_result.get("passed", True) else "fail",
                           "checks": rule_result.get("checks", []), "violations": rule_result.get("violations", [])},
        "c3_anomaly": {"status": anomaly_status, "score": score,
                       "hold_threshold": ANOMALY_HOLD_THRESHOLD, "reject_threshold": ANOMALY_REJECT_THRESHOLD},
        "c4_enforcement": {"decision": enforcement_result.get("decision", "hold"),
                           "action": enforcement_result.get("action") or {
                               "accept": "none", "void_discount": "void_discount",
                               "hold": "hold_cod_order", "reject": "reject_order",
                           }.get(enforcement_result.get("decision"), "none"),
                           "reason": enforcement_result.get("reason", ""),
                           "account_action": enforcement_result.get("account_action")},
    }


def _event_metadata(row):
    return row.get("metadata") or {}


def _order_context(body):
    """Extra order details worth keeping on the audit trail alongside the
    decision itself, so the dashboard/audit log can show who/what/how much
    instead of just pass/hold/reject.

    order_id must stay numeric (shared transaction_events.order_id column),
    but Cakely's own admin panel shows a human-readable code like
    "CK-20260923093651" — accept it under order_reference (or a couple of
    likely aliases) so the audit log can display the SAME code Cakely shows,
    instead of only RuleLock's internal numeric id.
    """
    return {
        "account_id": body.get("account_id") or body.get("user_id"),
        "customer_name": body.get("customer_name"),
        "order_reference": body.get("order_reference") or body.get("order_ref") or body.get("external_order_id"),
        "sku": body.get("sku"),
        "quantity": body.get("quantity"),
        "subtotal": body.get("subtotal"),
        "total": body.get("total"),
        "payment_method": body.get("payment_method", "PREPAID"),
        "session_id": body.get("session_id"),
        "device_id": body.get("device_id"),
        "phone_hash": body.get("phone_hash"),
        "address_hash": body.get("address_hash"),
        "coupons_applied": body.get("coupons_applied", []),
    }


def _rule_result(metadata):
    return metadata.get("rule_result") or {}


def _anomaly_result(metadata):
    return metadata.get("anomaly_result") or {}


def _enforcement_result(metadata):
    return metadata.get("enforcement_result") or {}


def _feed_action(metadata):
    enforcement_decision = _enforcement_result(metadata).get("decision")
    if enforcement_decision == "rate_limit_account":
        return "SUSPEND"
    decision = metadata.get("decision")
    return {
        "reject": "REJECT",
        "void_discount": "VOID",
        "hold": "HOLD",
        "accept": "PASS",
    }.get(decision, "PASS")


def _empty_summary():
    return {
        "threats_blocked": 0,
        "threats_blocked_delta": 0,
        "rule_violations": {"total": 0, "coupon": 0, "cod": 0},
        "anomaly_detections": 0,
        "discounts_voided": 0,
        "cod_orders_held": 0,
        "accounts_suspended": 0,
        "abuse_breakdown": {
            "coupon_discount_abuse": 0,
            "price_quantity_manipulation": 0,
            "cod_fake_order_abuse": 0,
        },
        "enforcement_feed": [],
        "components": {
            "transaction_monitor": {"events_captured_24h": 0, "avg_latency": "n/a", "sessions_active": 0, "db_write_errors": 0},
            "rule_engine": {"requests_validated_24h": 0, "rule_violations": 0, "avg_validation_time": "n/a", "false_positives": "n/a"},
            "anomaly_detection": {"model": "Isolation Forest", "anomaly_threshold": "n/a", "precision": "n/a", "false_positive_rate": "n/a"},
            "enforcement_engine": {"actions_taken_24h": 0, "avg_decision_time": "n/a", "audit_log_entries": 0, "manual_overrides": 0},
        },
    }


def _run_review_pipeline(order_id, account_id, payment_method, order_payload, features):
    # rule validation and anomaly scoring run in-process now (no separate
    # services to call over the network), so there's no latency to hide by
    # parallelizing them — plain sequential calls are simplest and fast.
    rule_result = call_rule_engine(order_payload)
    anomaly_result = call_anomaly_engine(features)
    if not rule_result.get("available", True) or not anomaly_result.get("available", True):
        return rule_result, anomaly_result, {
            "available": False,
            "decision": "hold",
            "reason": "upstream detection service unavailable; enforcement skipped",
        }
    enforcement_result = call_enforcement_engine(
        order_id=order_id,
        account_id=account_id,
        rule_result=rule_result,
        anomaly_result=anomaly_result,
        payment_method=payment_method,
    )
    return rule_result, anomaly_result, enforcement_result


@bp.get("/dashboard/summary")
def dashboard_summary():
    if not _authorized_request():
        return jsonify(error="invalid RuleLock authorization"), 401
    try:
        now = datetime.now(timezone.utc)
        current_start = now - timedelta(hours=24)
        previous_start = now - timedelta(hours=48)
        audit_rows = get_audit_log(limit=2000, start=current_start, end=now) or []
        summary = _empty_summary()
        audit_total = count_audit_events(current_start, now)
        summary["threats_blocked"] = count_audit_events(current_start, now, blocked_only=True)
        summary["threats_blocked_delta"] = summary["threats_blocked"] - count_audit_events(previous_start, current_start, blocked_only=True)
        summary["components"]["enforcement_engine"]["manual_overrides"] = count_transaction_events("RULELOCK_OVERRIDE", current_start, now)
        try:
            names = get_usernames([row.get("account_id") for row in audit_rows])
        except Exception:
            logger.exception("Could not resolve summary account usernames")
            names = {}
        try:
            references = get_order_references([row.get("order_id") for row in audit_rows if not row.get("order_reference")])
        except Exception:
            logger.exception("Could not resolve summary order references")
            references = {}
        rows = [{"event_id": row.get("event_id"), "created_at": row.get("created_at"), "order_id": row.get("order_id"),
                 "metadata": {"decision": row.get("decision"), "reason": row.get("reason"),
                              "order_reference": row.get("order_reference") or references.get(str(row.get("order_id"))) or str(row.get("order_id")),
                              "account_id": row.get("account_id"), "account_username": names.get(str(row.get("account_id"))), "total": row.get("total"), "rule_result": {"rule_code": row.get("rule_code")},
                              "anomaly_result": {"raw_score": row.get("anomaly_score")}, "enforcement_result": {"decision": row.get("decision")}}}
                for row in audit_rows]
    except (RequestException, RuntimeError):
        rows = []
        summary = _empty_summary()
        summary.update({
            "threats_blocked": "n/a", "threats_blocked_delta": "n/a", "rule_violations": "n/a",
            "anomaly_detections": "n/a", "discounts_voided": "n/a", "cod_orders_held": "n/a",
            "abuse_breakdown": "n/a",
        })
        summary["components"]["enforcement_engine"]["manual_overrides"] = "n/a"
        for component in summary["components"].values():
            for key in ("events_captured_24h", "sessions_active", "requests_validated_24h", "rule_violations", "actions_taken_24h", "audit_log_entries"):
                if key in component:
                    component[key] = "n/a"

    if not rows:
        return jsonify(summary), 200

    coupon_codes = {"coupon_usage", "discount_range", "coupon_velocity"}
    price_quantity_codes = {"quantity_ceiling", "price_mismatch", "minimum_purchase"}

    coupon_violations = 0
    cod_violations = 0
    price_quantity_violations = 0
    feed = []

    for row in rows:
        metadata = _event_metadata(row)
        rule = _rule_result(metadata)
        anomaly = _anomaly_result(metadata)
        enforcement = _enforcement_result(metadata)
        rule_code = rule.get("rule_code")

        if rule_code in coupon_codes:
            coupon_violations += 1
        if rule_code and rule_code.startswith("cod_"):
            cod_violations += 1
        if rule_code in price_quantity_codes:
            price_quantity_violations += 1
        from anomaly_scoring import ANOMALY_THRESHOLD
        if anomaly.get("raw_score") is not None and anomaly.get("raw_score") < ANOMALY_THRESHOLD:
            summary["anomaly_detections"] += 1
        if enforcement.get("decision") == "void_discount":
            summary["discounts_voided"] += 1
        if metadata.get("decision") == "hold" and rule_code and rule_code.startswith("cod_"):
            summary["cod_orders_held"] += 1
        if metadata.get("decision") == "reject" and not rule_code:
            summary["accounts_suspended"] += 1

        if len(feed) < 20:
            feed.append({
                "timestamp": row.get("created_at"),
                "action": _feed_action(metadata),
                "description": metadata.get("reason", "RuleLock review completed"),
                "order_id": row.get("order_id"),
                "order_reference": metadata.get("order_reference"),
                "rule_code": rule_code,
                "account_id": metadata.get("account_id"),
                "account_username": metadata.get("account_username"),
                "total": metadata.get("total"),
            })

    rule_total = coupon_violations + cod_violations + price_quantity_violations
    summary["rule_violations"] = {
        "total": rule_total,
        "coupon": coupon_violations,
        "cod": cod_violations,
    }
    summary["abuse_breakdown"] = {
        "coupon_discount_abuse": coupon_violations,
        "price_quantity_manipulation": price_quantity_violations,
        "cod_fake_order_abuse": cod_violations,
    }
    summary["enforcement_feed"] = feed
    summary["components"]["transaction_monitor"].update({"events_captured_24h": audit_total, "sessions_active": "n/a", "db_write_errors": "n/a"})
    summary["components"]["rule_engine"]["requests_validated_24h"] = audit_total
    summary["components"]["rule_engine"]["rule_violations"] = rule_total
    summary["components"]["enforcement_engine"]["actions_taken_24h"] = summary["threats_blocked"]
    summary["components"]["enforcement_engine"]["audit_log_entries"] = audit_total
    return jsonify(summary), 200


@bp.get("/audit-log")
def audit_log():
    if not _authorized_request():
        return jsonify(error="invalid RuleLock authorization"), 401
    action_filter = request.args.get("action")
    search = request.args.get("search", "").strip()
    cursor = request.args.get("cursor")
    try:
        limit = max(1, min(int(request.args.get("limit", 50)), 200))
    except (TypeError, ValueError):
        limit = 50
    if cursor is not None and not cursor.isdigit():
        return jsonify(error="cursor must be a numeric audit ID"), 400

    try:
        rows = get_audit_log(action=action_filter, search=search, cursor=cursor, limit=limit) or []
    except (RequestException, RuntimeError):
        rows = []
    has_more = len(rows) > limit
    page = rows[:limit]
    try:
        missing_ids = [row.get("order_id") for row in page if not row.get("order_reference")]
        references = get_order_references(missing_ids)
    except Exception:
        logger.exception("Could not backfill missing audit order references for response")
        references = {}
    entries = [{
        "action_id": f"ACT-{row.get('event_id')}", "timestamp": row.get("created_at"), "action": row.get("action"),
        "decision": row.get("decision"), "reason": row.get("reason", ""), "rule_violated": row.get("rule_code"),
        "score": row.get("anomaly_score"), "order_id": row.get("order_id"),
        "order_reference": row.get("order_reference") or references.get(str(row.get("order_id"))) or str(row.get("order_id")),
        "account_id": row.get("account_id"), "payment_method": row.get("payment_method"), "total": row.get("total"),
    } for row in page]
    try:
        names = get_usernames([entry.get("account_id") for entry in entries])
        for entry in entries:
            entry["account_username"] = names.get(str(entry.get("account_id")))
    except Exception:
        logger.exception("Could not resolve audit account usernames")
        for entry in entries:
            entry["account_username"] = None
    return jsonify({"records": entries, "count": len(entries), "next_cursor": page[-1].get("audit_id") if has_more and page else None}), 200


@bp.get("/audit-log/<order_key>")
def audit_log_detail(order_key):
    if not _authorized_request():
        return jsonify(error="invalid RuleLock authorization"), 401
    try:
        order_id = _bigint(order_key)
        if order_id is None:
            if not re.fullmatch(r"[A-Za-z0-9_-]{1,200}", order_key):
                return jsonify(error="review not found"), 404
            order_id = _bigint(get_order_id_by_reference(order_key))
        if order_id is None:
            return jsonify(error="review not found"), 404
        event = get_review_event(order_id)
        if not event:
            return jsonify(error="review not found"), 404
        metadata = _event_metadata(event)
        profile = get_account_profile(event.get("user_id")) if event.get("user_id") is not None else {}
        reference = metadata.get("order_reference")
        if not reference:
            try:
                reference = get_order_reference(order_id)
            except Exception:
                logger.exception("Could not resolve review order reference for order %s", order_id)
            reference = reference or str(order_id)
        return jsonify({"order_id": order_id, "order_reference": reference,
                        "customer_name": metadata.get("customer_name") or profile.get("username"),
                        "account_username": profile.get("username"), "decision": metadata.get("decision"),
                        "reason": metadata.get("reason"), "pipeline": metadata.get("pipeline"),
                        "account": (metadata.get("pipeline") or {}).get("c1_data_collection", {}).get("account", profile),
                        "stored_review": metadata}), 200
    except (RequestException, RuntimeError, TypeError, ValueError):
        logger.exception("Could not load review detail for order %s", order_key)
        return jsonify(error="review detail unavailable"), 503


@bp.get("/settings/rulelock")
def get_rulelock_toggle():
    if not _authorized_request():
        return jsonify(error="invalid RuleLock authorization"), 401
    setting = get_rulelock_setting()
    enabled = True if setting is None else _as_bool(setting.get("rulelock_enabled"))
    return jsonify(rulelock_enabled=enabled, source="default" if setting is None else "platform_settings"), 200


@bp.post("/settings/rulelock")
def update_rulelock_toggle():
    if not _authorized_request():
        return jsonify(error="invalid RuleLock authorization"), 401
    body = request.get_json(silent=True) or {}
    if "rulelock_enabled" not in body:
        return jsonify(error="rulelock_enabled is required"), 400
    try:
        setting = set_rulelock_setting(_as_bool(body["rulelock_enabled"]))
    except (RequestException, RuntimeError) as exc:
        return jsonify(error=f"could not update RuleLock setting ({exc})"), 503
    return jsonify(rulelock_enabled=_as_bool(setting.get("rulelock_enabled")), source="platform_settings"), 200


@bp.post("/review-order")
def review_order():
    """Review an order for an external commerce app before payment capture."""
    if not _authorized_request():
        return jsonify(error="invalid RuleLock authorization"), 401

    body = request.get_json(silent=True) or {}
    session_id = body.get("session_id") or request.headers.get("X-Session-ID")
    order_id = body.get("order_id")
    if not order_id:
        return jsonify(error="order_id is required"), 400

    numeric_order_id = _bigint(order_id)
    if numeric_order_id is None:
        return jsonify(error="order_id must be numeric for the shared transaction_events table"), 400

    # The setting is owned by Cakely. If Cakely called this endpoint, review it.
    review_event_type = "RULELOCK_SIMULATION" if body.get("simulation") is True else "RULELOCK_REVIEW"
    supplied_reference = body.get("order_reference") or body.get("order_ref") or body.get("external_order_id")
    if review_event_type == "RULELOCK_SIMULATION":
        order_reference = f"SIM-{numeric_order_id}"
    elif supplied_reference:
        order_reference = str(supplied_reference)
    else:
        try:
            order_reference = get_order_reference(numeric_order_id) or str(numeric_order_id)
        except Exception:
            logger.exception("Could not look up Cakely order reference for order %s", numeric_order_id)
            order_reference = str(numeric_order_id)
    try:
        previous = get_review_event(numeric_order_id, event_type=review_event_type)
        if previous:
            try:
                stored_metadata = {**_event_metadata(previous), "order_reference": _event_metadata(previous).get("order_reference") or order_reference}
                insert_audit_log(previous.get("event_id"), review_event_type, numeric_order_id, stored_metadata)
            except Exception:
                logger.exception("Could not reconcile audit row for order %s", numeric_order_id)
                return jsonify(_review_response(numeric_order_id, "hold", "Review storage is temporarily unavailable", order_reference=order_reference)), 200
            return jsonify(_stored_review_response(_event_metadata(previous), numeric_order_id, order_reference)), 200
    except Exception:
        logger.exception("Could not check idempotent review record for order %s", numeric_order_id)
        response = _review_response(numeric_order_id, "hold", "Review storage is temporarily unavailable", order_reference=order_reference)
        response["reason"] = "Review storage is temporarily unavailable"
        return jsonify(response), 200

    account_id = str(body.get("user_id", body.get("account_id", "")))
    user_id = _bigint(body.get("user_id"))
    try:
        features = session_features(session_id, body.get("device_id"), body.get("phone_hash")) if session_id else {}
        payment_method = str(body.get("payment_method", "CARD")).upper()
        order_payload = dict(body)
        if body.get("simulation") is True:
            simulated = body.get("simulated_account") or {}
            history_total = int(simulated.get("cod_orders", 0) or 0)
            history_bad = int(simulated.get("cod_bad", 0) or 0)
            completed = int(simulated.get("completed_orders", 0) or 0)
            profile = {"user_id": user_id, "username": body.get("customer_name") or "Simulation account",
                       "account_age_days": int(simulated.get("account_age_days", 0) or 0),
                       "completed_orders": completed, "cod_orders": history_total, "cod_bad_orders": history_bad}
            account_history_error = False
        else:
            try:
                profile = get_account_profile(user_id) if user_id is not None else {
                    "user_id": None, "username": None, "account_age_days": 0, "completed_orders": 0}
                history = get_cod_history(user_id, numeric_order_id) if payment_method == "COD" and user_id is not None else {"total": 0, "bad": 0}
                history_total, history_bad = history["total"], history["bad"]
                account_history_error = payment_method == "COD" and user_id is None
            except Exception:
                if payment_method != "COD":
                    raise
                logger.exception("COD account history unavailable for user %s", user_id)
                profile = {"user_id": user_id, "username": None, "account_age_days": 0,
                           "completed_orders": 0, "cod_orders": 0, "cod_bad_orders": 0}
                history_total, history_bad = 0, 0
                account_history_error = True
            profile.update({"cod_orders": history_total, "cod_bad_orders": history_bad})
        order_payload["account_verified"] = profile.get("completed_orders", 0) >= 1
        order_payload["past_orders"] = history_total
        order_payload["past_refusals"] = history_bad
        rule_result, anomaly_result, enforcement_result = _run_review_pipeline(
            order_id=numeric_order_id,
            account_id=account_id,
            payment_method=payment_method,
            order_payload=order_payload,
            features=features,
        )
        if account_history_error:
            decision, reason = "hold", "account history unavailable"
            enforcement_result = {"decision": "hold", "action": "hold_cod_order", "reason": reason, "account_action": None}
        else:
            decision, reason = _decision_from_results(rule_result, anomaly_result, enforcement_result)
        response = _review_response(numeric_order_id, decision, reason, rule_result, anomaly_result, enforcement_result)
        response["pipeline"] = _pipeline_snapshot(features, profile, rule_result, anomaly_result, enforcement_result)
    except Exception:
        logger.exception("Review pipeline failed for order %s", numeric_order_id)
        response = _review_response(numeric_order_id, "hold", "Review could not be completed")
        response["pipeline"] = _pipeline_snapshot({}, {}, {"passed": False, "checks": [], "violations": []},
                                                 {"raw_score": 0.0}, {"decision": "hold", "action": "none", "reason": response["reason"]})

    response["order_reference"] = order_reference
    event_metadata = {**response, **_order_context(body), "order_reference": order_reference, "session_id": session_id}
    event_id = str(uuid.uuid4())
    try:
        insert_review_record(review_event_type, session_id or "", _bigint(body.get("user_id")), numeric_order_id, event_metadata, event_id)
    except Exception:
        logger.exception("Could not persist review for order %s", numeric_order_id)
        try:
            previous = get_review_event(numeric_order_id, event_type=review_event_type)
            if previous:
                previous_metadata = _event_metadata(previous)
                insert_audit_log(previous.get("event_id"), review_event_type, numeric_order_id,
                                 {**previous_metadata, "order_reference": previous_metadata.get("order_reference") or order_reference})
                return jsonify(_stored_review_response(_event_metadata(previous), numeric_order_id, order_reference)), 200
        except Exception:
            logger.exception("Could not retrieve concurrent review for order %s", numeric_order_id)
        response = _review_response(numeric_order_id, "hold", "Review could not be completed", order_reference=order_reference)
    return jsonify(response), 200


@bp.get("/pipeline/info")
def pipeline_info():
    from anomaly_scoring import model_metadata
    from features import FEATURE_NAMES
    import rules
    info = model_metadata()
    info.setdefault("features", FEATURE_NAMES)
    info["rule_thresholds"] = {
        "max_coupons": rules.MAX_COUPONS,
        "max_coupons_per_session": rules.MAX_COUPONS,
        "max_discount_ratio": rules.MAX_DISCOUNT_RATIO,
        "max_quantity_per_line": rules.MAX_QUANTITY_PER_LINE,
        "min_purchase_amount": rules.MIN_PURCHASE_AMOUNT,
        "cod_unverified_order_cap": rules.COD_UNVERIFIED_ORDER_CAP,
        "cod_bad_hold": rules.COD_BAD_HOLD,
        "cod_bad_reject": rules.COD_BAD_REJECT,
    }
    return jsonify(info), 200
