-- Enforce one RuleLock review record per numeric Cakely order.
-- Review code handles a duplicate insert by returning the existing result.
CREATE UNIQUE INDEX IF NOT EXISTS transaction_events_one_rulelock_review_per_order
    ON public.transaction_events (order_id)
    WHERE event_type = 'RULELOCK_REVIEW' AND order_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS transaction_events_one_rulelock_simulation_per_order
    ON public.transaction_events (order_id)
    WHERE event_type = 'RULELOCK_SIMULATION' AND order_id IS NOT NULL;
