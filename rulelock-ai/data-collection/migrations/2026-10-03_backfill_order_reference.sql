-- Fill canonical Cakely references on existing RuleLock audit records.
UPDATE public.rulelock_audit_log AS audit
SET order_reference = orders.order_number::text
FROM public.orders AS orders
WHERE audit.order_reference IS NULL
  AND orders.id = audit.order_id;
