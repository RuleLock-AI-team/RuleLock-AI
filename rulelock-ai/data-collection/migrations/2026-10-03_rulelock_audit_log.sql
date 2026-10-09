-- Minimal immutable audit records for live and simulated RuleLock reviews.
-- Keep personal customer fields and raw request payloads out of this table.
CREATE TABLE IF NOT EXISTS public.rulelock_audit_log (
    audit_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_id uuid NOT NULL UNIQUE,
    event_type text NOT NULL CHECK (event_type IN ('RULELOCK_REVIEW', 'RULELOCK_SIMULATION')),
    order_id bigint NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    action text NOT NULL,
    decision text NOT NULL,
    reason text NOT NULL DEFAULT '',
    order_reference text,
    account_id text,
    payment_method text,
    total numeric,
    rule_code text,
    anomaly_score double precision
);

CREATE INDEX IF NOT EXISTS rulelock_audit_log_live_created_idx
    ON public.rulelock_audit_log (created_at DESC, audit_id DESC)
    WHERE event_type = 'RULELOCK_REVIEW';
CREATE INDEX IF NOT EXISTS rulelock_audit_log_live_decision_idx
    ON public.rulelock_audit_log (decision, created_at DESC)
    WHERE event_type = 'RULELOCK_REVIEW';
CREATE UNIQUE INDEX IF NOT EXISTS rulelock_audit_log_one_row_per_review
    ON public.rulelock_audit_log (event_type, order_id);

-- Backfill existing RuleLock events so the dashboard has a complete audit
-- history from the point this migration is applied. Keep only minimal fields.
INSERT INTO public.rulelock_audit_log (
    event_id, event_type, order_id, created_at, action, decision, reason,
    order_reference, account_id, payment_method, total, rule_code, anomaly_score
)
SELECT
    e.event_id,
    e.event_type,
    e.order_id,
    e.created_at,
    CASE e.metadata->>'decision'
        WHEN 'accept' THEN 'PASS'
        WHEN 'void_discount' THEN 'VOID'
        WHEN 'reject' THEN 'REJECT'
        WHEN 'hold' THEN 'HOLD'
        ELSE 'HOLD'
    END,
    COALESCE(e.metadata->>'decision', 'hold'),
    LEFT(COALESCE(e.metadata->>'reason', ''), 1000),
    LEFT(e.metadata->>'order_reference', 200),
    LEFT(e.metadata->>'account_id', 200),
    LEFT(e.metadata->>'payment_method', 40),
    CASE WHEN e.metadata->>'total' ~ '^-?([0-9]+(\.[0-9]*)?|\.[0-9]+)([eE][+-]?[0-9]+)?$'
         THEN (e.metadata->>'total')::numeric END,
    e.metadata->'rule_result'->>'rule_code',
    CASE WHEN e.metadata->'anomaly_result'->>'raw_score' ~ '^-?([0-9]+(\.[0-9]*)?|\.[0-9]+)([eE][+-]?[0-9]+)?$'
         THEN (e.metadata->'anomaly_result'->>'raw_score')::double precision END
FROM public.transaction_events AS e
WHERE e.event_type IN ('RULELOCK_REVIEW', 'RULELOCK_SIMULATION')
  AND e.event_id IS NOT NULL
  AND e.order_id IS NOT NULL
ON CONFLICT (event_id) DO NOTHING;

CREATE OR REPLACE FUNCTION public.reject_rulelock_audit_mutation()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'rulelock_audit_log is insert-only';
END;
$$;

DROP TRIGGER IF EXISTS rulelock_audit_log_immutable ON public.rulelock_audit_log;
CREATE TRIGGER rulelock_audit_log_immutable
    BEFORE UPDATE OR DELETE ON public.rulelock_audit_log
    FOR EACH ROW EXECUTE FUNCTION public.reject_rulelock_audit_mutation();

-- Use one PostgREST RPC transaction so every newly accepted transaction event
-- and its audit row commit together or both roll back.
CREATE OR REPLACE FUNCTION public.record_rulelock_review(p_event jsonb, p_audit jsonb)
RETURNS void LANGUAGE plpgsql SECURITY INVOKER SET search_path = public AS $$
BEGIN
    INSERT INTO public.transaction_events (event_id, event_type, user_id, order_id, metadata)
    VALUES (
        (p_event->>'event_id')::uuid,
        p_event->>'event_type',
        NULLIF(p_event->>'user_id', '')::bigint,
        (p_event->>'order_id')::bigint,
        p_event->'metadata'
    );

    INSERT INTO public.rulelock_audit_log (
        event_id, event_type, order_id, created_at, action, decision, reason,
        order_reference, account_id, payment_method, total, rule_code, anomaly_score
    ) VALUES (
        (p_audit->>'event_id')::uuid,
        p_audit->>'event_type',
        (p_audit->>'order_id')::bigint,
        (p_audit->>'created_at')::timestamptz,
        p_audit->>'action',
        p_audit->>'decision',
        COALESCE(p_audit->>'reason', ''),
        p_audit->>'order_reference',
        p_audit->>'account_id',
        p_audit->>'payment_method',
        CASE WHEN p_audit->>'total' ~ '^-?([0-9]+(\.[0-9]*)?|\.[0-9]+)([eE][+-]?[0-9]+)?$'
             THEN (p_audit->>'total')::numeric END,
        p_audit->>'rule_code',
        CASE WHEN p_audit->>'anomaly_score' ~ '^-?([0-9]+(\.[0-9]*)?|\.[0-9]+)([eE][+-]?[0-9]+)?$'
             THEN (p_audit->>'anomaly_score')::double precision END
    );
END;
$$;

REVOKE ALL ON FUNCTION public.record_rulelock_review(jsonb, jsonb) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.record_rulelock_review(jsonb, jsonb) TO service_role;
