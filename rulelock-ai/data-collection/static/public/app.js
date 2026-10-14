const { createElement: h, useEffect, useMemo, useState } = React;
const { createRoot } = ReactDOM;

const viteEnv = import.meta.env || {};
const runtimeConfig = window.RULELOCK_CONFIG || {};
// rule-engine, anomaly-detection, and enforcement-engine now run in-process
// inside data-collection instead of as separate hosted services, so their
// health checks point at the same backend by default.
const CONFIG = {
  dataUrl: runtimeConfig.DATA_COLLECTION_URL || window.RULELOCK_API_BASE || viteEnv.VITE_DATA_COLLECTION_URL || "https://rulelock-data-collection.onrender.com",
};
CONFIG.proxyUrl = CONFIG.dataUrl;

const ROUTES = [
  { id: "dashboard", label: "Dashboard", path: "/dashboard" },
  { id: "attack-simulation", label: "Attack Simulation", path: "/attack-simulation" },
  { id: "audit-log", label: "Audit Log", path: "/audit-log" },
  { id: "pipeline", label: "Pipeline", path: "/pipeline" },
];

const ACTION_TONE = { VOID: "red", HOLD: "orange", PASS: "green", REJECT: "red", SUSPEND: "purple", FAIL: "red", ANOMALY: "orange" };
const money = (value) => `LKR ${Number(value || 0).toLocaleString("en-LK")}`;
const nowOrderId = () => Number(String(Date.now()).slice(-9));
const nowStamp = () => new Date().toLocaleString("en-LK", { hour12: false });

async function jsonFetch(url, options = {}) {
  const response = await fetch(url, { credentials: "include", ...options });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(data.error || `HTTP ${response.status}`);
    error.status = response.status;
    if (response.status === 401) window.dispatchEvent(new Event("rulelock-unauthorized"));
    throw error;
  }
  return data;
}

async function dataGet(path) {
  return jsonFetch(`${CONFIG.proxyUrl}${path}`);
}

async function dataPost(path, payload) {
  return jsonFetch(`${CONFIG.proxyUrl}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

function useRoute() {
  const readRoute = () => {
    const hash = window.location.hash.replace(/^#/, "");
    const path = hash || window.location.pathname;
    const match = ROUTES.find((route) => route.path === path || `/${route.id}` === path);
    return match ? match.id : "dashboard";
  };
  const [route, setRoute] = useState(readRoute);
  useEffect(() => {
    const update = () => setRoute(readRoute());
    window.addEventListener("hashchange", update);
    window.addEventListener("popstate", update);
    return () => {
      window.removeEventListener("hashchange", update);
      window.removeEventListener("popstate", update);
    };
  }, []);
  return route;
}

function useHealth(authenticated) {
  const [health, setHealth] = useState({});
  useEffect(() => {
    if (!authenticated) { setHealth({}); return; }
    fetch(`${CONFIG.proxyUrl}/ready`, { credentials: "include", cache: "no-store" })
      .then(async (response) => {
        const data = await response.json().catch(() => ({}));
        if (response.status === 401) window.dispatchEvent(new Event("rulelock-unauthorized"));
        setHealth(data.checks || { model_loaded: false, supabase_reachable: false });
      })
      .catch(() => setHealth({ model_loaded: false, supabase_reachable: false }));
  }, [authenticated]);
  return health;
}

function Shell({ route, children, health }) {
  const current = ROUTES.find((item) => item.id === route) || ROUTES[0];
  return h("div", { className: "app-shell" },
    h("header", { className: "topbar" },
      h("a", { className: "brand", href: "#/dashboard" },
        h("span", { className: "brand-mark", "aria-hidden": true }, "L"),
        h("span", null,
          h("strong", null, "RuleLock AI"),
          h("small", null, "IE3092 - Business Logic Abuse Detection")
        )
      ),
      h("nav", { className: "nav-tabs", "aria-label": "Primary" },
        ROUTES.map((item, index) => h("a", {
          key: item.id,
          className: `nav-pill ${route === item.id ? "active" : ""}`,
          href: `#${item.path}`,
        }, h("span", null, String(index + 1).padStart(2, "0")), item.label))
      ),
      h("div", { className: "top-status" },
        h("span", { className: `status-pill ${health.model_loaded ? "online" : "offline"}` }, `MODEL ${health.model_loaded ? "READY" : "OFFLINE"}`),
        h("span", { className: `status-pill ${health.supabase_reachable ? "online" : "offline"}` }, `SUPABASE ${health.supabase_reachable ? "READY" : "OFFLINE"}`),
        h("span", { className: "version" }, "v1.0.0")
      )
    ),
    h("div", { className: "breadcrumb" }, "rulelock / ", current.id),
    h("main", { className: "page" }, children)
  );
}

function Badge({ children, tone = "green" }) {
  return h("span", { className: `badge tone-${tone}` }, children);
}

function Panel({ title, kicker, children, className = "" }) {
  return h("section", { className: `panel ${className}` },
    kicker && h("div", { className: "section-kicker" }, kicker),
    title && h("h2", null, title),
    children
  );
}

function Dashboard({ health }) {
  const empty = {
    threats_blocked: "n/a",
    threats_blocked_delta: "n/a",
    rule_violations: { total: "n/a", coupon: "n/a", cod: "n/a" },
    anomaly_detections: "n/a",
    discounts_voided: "n/a",
    cod_orders_held: "n/a",
    components: { enforcement_engine: { manual_overrides: "n/a" } },
    abuse_breakdown: { coupon_discount_abuse: "n/a", price_quantity_manipulation: "n/a", cod_fake_order_abuse: "n/a" },
    enforcement_feed: [],
  };
  const [summary, setSummary] = useState(empty);
  useEffect(() => {
    dataGet("/dashboard/summary").then(setSummary).catch(() => setSummary(empty));
  }, []);

  const kpis = [
    ["THREATS BLOCKED (24H)", summary.threats_blocked, `${summary.threats_blocked_delta > 0 ? "+" : ""}${summary.threats_blocked_delta ?? "n/a"} vs previous 24h`, "pink"],
    ["RULE VIOLATIONS", summary.rule_violations?.total ?? "n/a", `${summary.rule_violations?.coupon ?? "n/a"} coupon / ${summary.rule_violations?.cod ?? "n/a"} COD`, "orange"],
    ["ANOMALY DETECTIONS", summary.anomaly_detections, "Isolation Forest", "purple"],
    ["DISCOUNTS VOIDED", summary.discounts_voided, "auto-enforced", "cyan"],
    ["COD ORDERS HELD", summary.cod_orders_held, "awaiting prepayment", "cyan"],
    ["ACCOUNTS SUSPENDED", summary.accounts_suspended, "anomaly model rejects", "purple"],
    ["MANUAL OVERRIDES", summary.components?.enforcement_engine?.manual_overrides ?? "n/a", "RULELOCK_OVERRIDE events (24h)", "orange"],
  ];
  const breakdown = [
    ["Coupon / Discount Abuse", summary.abuse_breakdown.coupon_discount_abuse, "red"],
    ["Price & Quantity Manipulation", summary.abuse_breakdown.price_quantity_manipulation, "orange"],
    ["COD Fake-Order & Return Abuse", summary.abuse_breakdown.cod_fake_order_abuse, "cyan"],
  ];
  const maxBreakdown = Math.max(...breakdown.map((row) => Number(row[1]) || 0), 1);

  return h("div", null,
    h("div", { className: "kpi-grid" }, kpis.map(([label, value, subtext, tone]) =>
      h("article", { className: "kpi-card", key: label },
        h("span", { className: "mono-label" }, label),
        h("strong", { className: `text-${tone}` }, value ?? "n/a"),
        h("small", null, subtext)
      )
    )),
    h("div", { className: "dashboard-grid" },
      h(Panel, { title: "ENFORCEMENT FEED - LIVE", kicker: h("span", { className: "live-dot" }, "ONLINE") },
        h("div", { className: "feed-list" },
          summary.enforcement_feed.length ? summary.enforcement_feed.map((item, index) =>
            h("div", { className: "feed-row", key: `${item.timestamp}-${index}` },
              h("time", null, formatTimestamp(item.timestamp)),
              h(Badge, { tone: ACTION_TONE[item.action] || "green" }, item.action || "PASS"),
              h("span", null,
                h("strong", null, item.order_reference || `Order ${item.order_id}`),
                item.order_id != null && h("small", { className: "secondary-order-id" }, `#${item.order_id}`),
                ` · ${item.account_username || item.account_id || ""}${item.description ? ` — ${item.description}` : ""}${item.total != null ? ` (${money(item.total)})` : ""}`)
            )
          ) : h("div", { className: "empty-state" }, "No RuleLock reviews in the last 24 hours.")
        )
      ),
      h("div", { className: "stack" },
        h(Panel, { title: "ABUSE BREAKDOWN (24H)" },
          h("div", { className: "breakdown-list" }, breakdown.map(([label, count, tone]) =>
            h("div", { className: "breakdown-row", key: label },
              h("div", null, h("span", null, label), h("strong", null, count ?? "n/a")),
              h("i", { className: `bar tone-${tone}`, style: { width: `${Math.max(((Number(count) || 0) / maxBreakdown) * 100, count ? 8 : 0)}%` } })
            )
          ))
        ),
        h(Panel, { title: "SYSTEM STATUS" },
          [
            ["Model Loaded", health.model_loaded],
            ["Supabase Reachable", health.supabase_reachable],
          ].map(([name, ok]) => h("div", { className: "status-row", key: name },
            h("span", null, name),
            h(Badge, { tone: ok ? "green" : "red" }, ok ? "ONLINE" : "OFFLINE")
          ))
        )
      )
    )
  );
}



const SCENARIOS = {
  normal: { tab: "NORMAL ORDER", tone: "cyan", title: "Normal order (accept)", subtitle: "Verified account, ordinary quantity and no coupon abuse", body: "A standard checkout should pass every rule and continue to payment.", rows: () => [["Items", "1 cake"], ["Payment", "Prepaid"], ["Expected", "Accept"]], payload: (orderId) => ({ order_id: orderId, user_id: 501, customer_name: "Demo Customer", payment_method: "CARD", subtotal: 2400, total: 2400, items: [{ sku: "sku-1", quantity: 1 }], coupons_applied: [], simulated_account: { cod_orders: 0, cod_bad: 0, completed_orders: 2, account_age_days: 180 } }) },
  coupons: { tab: "COUPON STACKING", tone: "pink", title: "Coupon stacking (2 coupons)", subtitle: "Two coupons exceed the configured maximum of one", body: "C2 should void the discount and allow the order to continue with an updated total.", rows: () => [["Coupons", "CAKE10 + CAKE20", true], ["Maximum", "1 coupon"], ["Expected", "Void discount"]], payload: (orderId) => ({ order_id: orderId, user_id: 502, payment_method: "CARD", subtotal: 2400, discount_value: 300, total: 2100, items: [{ sku: "sku-1", quantity: 1 }], coupons_applied: ["CAKE10", "CAKE20"], simulated_account: { cod_orders: 0, cod_bad: 0, completed_orders: 1, account_age_days: 90 } }) },
  quantity: { tab: "QUANTITY", tone: "orange", title: "Quantity manipulation (35)", subtitle: "One line exceeds the limit of 20", body: "C2 should reject the order and report the quantity ceiling check.", rows: () => [["SKU", "sku-3"], ["Quantity", "35 (limit 20)", true], ["Expected", "Reject"]], payload: (orderId) => ({ order_id: orderId, user_id: 503, payment_method: "CARD", subtotal: 35000, total: 35000, items: [{ sku: "sku-3", quantity: 35 }], coupons_applied: [], simulated_account: { cod_orders: 0, cod_bad: 0, completed_orders: 1, account_age_days: 30 } }) },
  cod_hold: { tab: "COD HOLD", tone: "cyan", title: "COD abuse hold (2 of 4)", subtitle: "Two bad outcomes among four previous COD orders", body: "A 50% bad-outcome rate at two or more orders triggers a hold.", rows: () => [["Payment", "Cash on delivery"], ["Bad / total", "2 / 4", true], ["Expected", "Hold"]], payload: (orderId) => ({ order_id: orderId, user_id: 504, payment_method: "COD", subtotal: 2400, total: 2400, items: [{ sku: "sku-1", quantity: 1 }], coupons_applied: [], simulated_account: { cod_orders: 4, cod_bad: 2, completed_orders: 0, account_age_days: 10 } }) },
  cod_reject: { tab: "COD REJECT", tone: "pink", title: "COD abuse reject (3 of 4)", subtitle: "Three bad outcomes among four previous COD orders", body: "Three bad outcomes at a 75% rate trigger the severe COD abuse rejection.", rows: () => [["Payment", "Cash on delivery"], ["Bad / total", "3 / 4", true], ["Expected", "Reject"]], payload: (orderId) => ({ order_id: orderId, user_id: 505, payment_method: "COD", subtotal: 2400, total: 2400, items: [{ sku: "sku-1", quantity: 1 }], coupons_applied: [], simulated_account: { cod_orders: 4, cod_bad: 3, completed_orders: 0, account_age_days: 10 } }) },
};
function AttackSimulation() {
  const [active, setActive] = useState("normal");
  const [sessionSeed, setSessionSeed] = useState(() => `lab-${Date.now()}`);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const scenario = SCENARIOS[active];
  const previewRows = scenario.rows(sessionSeed);

  async function run() {
    const orderId = nowOrderId();
    setLoading(true);
    setResult(null);
    try {
      const response = await dataPost("/review-order", { ...scenario.payload(orderId, sessionSeed), simulation: true });
      setResult({ ok: true, response, timestamp: nowStamp() });
    } catch (error) {
      setResult({ ok: false, error: error.message, timestamp: nowStamp() });
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setResult(null);
    setSessionSeed(`lab-${Date.now()}`);
  }

  const pipeline = buildPipeline(result);
  return h("div", null,
    h("div", { className: "page-head" },
      h("div", null,
        h("div", { className: "section-kicker" }, "TESTING LAB"),
        h("h1", null, "Attack Simulation Lab"),
        h("p", null, "Select an abuse scenario and run it through the full RuleLock AI detection pipeline. All four components execute in sequence.")
      )
    ),
    h("div", { className: "scenario-tabs" }, Object.entries(SCENARIOS).map(([key, item]) =>
      h("button", {
        key,
        className: `scenario-tab tone-${item.tone} ${active === key ? "active" : ""}`,
        onClick: () => { setActive(key); reset(); },
      }, item.tab)
    )),
    h("div", { className: "lab-grid" },
      h(Panel, { className: "scenario-card" },
        h("span", { className: `scenario-type text-${scenario.tone}` }, scenario.tab),
        h("h2", null, scenario.title),
        h("h3", null, scenario.subtitle),
        h("p", null, scenario.body),
        h("div", { className: "request-preview" },
        h("code", null, "POST /review-order HTTP/1.1 (simulation:true)"),
          previewRows.map(([label, value, danger]) => h("div", { className: danger ? "danger" : "", key: label },
            h("span", null, label),
            h("strong", null, value)
          ))
        ),
        result ? h("button", { className: "btn-outline", onClick: reset }, "RESET") :
          h("button", { className: `btn-run tone-${scenario.tone}`, disabled: loading, onClick: run }, loading ? "RUNNING..." : "RUN SIMULATION")
      ),
      h(PipelineResult, { pipeline, result, tone: scenario.tone })
    )
  );
}

function buildPipeline(result) {
  const base = [
    ["C1", "Transaction Monitor", "WAITING", "Simulation request has not been sent."],
    ["C2", "Rule Validation Engine", "WAITING", "Waiting for rule-engine response."],
    ["C3", "Anomaly Detection (IF)", "WAITING", "Waiting for Isolation Forest score."],
    ["C4", "Enforcement Engine", "WAITING", "Waiting for enforcement decision."],
  ];
  if (!result) return base;
  if (!result.ok) return base.map(([code, name]) => [code, name, "FAIL", "service unreachable"]);
  const r = result.response;
  const p = r.pipeline || {};
  const c1 = p.c1_data_collection || {};
  const c2 = p.c2_rule_engine || {};
  const c3 = p.c3_anomaly || {};
  const c4 = p.c4_enforcement || {};
  const account = c1.account || {};
  const checks = c2.checks || [];
  return [
    ["C1", "Transaction Monitor", c1.status?.toUpperCase() || "PASS", `${account.username || "Account"} Â· ${account.account_age_days ?? 0} days Â· ${account.completed_orders ?? 0} completed Â· ${c1.events_in_session ?? 0} session events`],
    ["C2", "Rule Validation Engine", c2.status?.toUpperCase() || (r.rule_result?.passed ? "PASS" : "FAIL"), checks.map((check) => `${check.passed ? "âœ“" : "âœ•"} ${check.label}: ${check.detail}`).join(" Â· ") || (r.rule_result?.failures || []).join("; ") || "All checks passed."],
    ["C3", "Anomaly Detection (IF)", c3.status?.toUpperCase() || "NORMAL", `score=${Number(c3.score ?? r.anomaly_result?.raw_score ?? 0).toFixed(3)} Â· hold ${c3.hold_threshold ?? "n/a"} Â· reject ${c3.reject_threshold ?? "n/a"}`],
    ["C4", "Enforcement Engine", c4.decision?.toUpperCase() || r.decision?.toUpperCase() || "PASS", `${c4.action || r.enforcement_result?.action || "none"} Â· ${c4.reason || r.reason || "No action required."}`],
  ];
}

function PipelineResult({ pipeline, result, tone }) {
  const decision = result?.ok ? result.response.decision : result ? "reject" : null;
  const bannerTone = !result ? "muted" : result.ok ? (decision === "accept" ? "green" : decision === "hold" ? tone : "red") : "red";
  const verdict = !result ? "Awaiting simulation" : result.ok ? `${result.response.payment_action || decision} / ${result.response.cakely_order_status || ""}` : "FAIL / SERVICE UNREACHABLE";
  const reason = !result ? "Run a scenario to see the real pipeline response." : result.ok ? result.response.reason : result.error;
  return h(Panel, { title: "DETECTION PIPELINE", className: "pipeline-panel" },
    h("div", { className: "pipeline-list" }, pipeline.map(([code, name, state, text]) =>
      h("div", { className: "pipeline-step", key: code },
        h("span", { className: "component-code" }, code),
        h("div", null, h("strong", null, name), h("small", null, text)),
        h(Badge, { tone: ACTION_TONE[state] || "muted" }, state)
      )
    )),
    h("div", { className: `verdict tone-${bannerTone}` },
      result?.ok && h("small", { className: "simulation-order-reference" },
        h("strong", null, result.response.order_reference || `Order ${result.response.order_id}`),
        result.response.order_id != null && h("span", { className: "secondary-order-id" }, `#${result.response.order_id}`)),
      h("strong", null, verdict),
      h("p", null, reason),
      h("small", null, result ? `Action logged to audit trail / ${result.timestamp}` : "n/a")
    )
  );
}

const ACTION_EXPLAIN = {
  PASS: "Passed RuleLock checks â€” payment may proceed",
  REJECT: "Order rejected",
  HOLD: "Held for review â€” payment NOT captured",
  VOID: "Discount voided",
  SUSPEND: "Account rate-limited",
  FAIL: "Could not complete the review",
  ANOMALY: "Flagged as anomalous",
};

function formatTimestamp(value) {
  if (!value) return "n/a";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("en-LK", { year: "numeric", month: "short", day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: true });
}

function AuditLog() {
  const [filter, setFilter] = useState("ALL");
  const [search, setSearch] = useState("");
  const [rows, setRows] = useState([]);
  const [cursor, setCursor] = useState(null);
  const [hasMore, setHasMore] = useState(false);
  const [selected, setSelected] = useState(null);
  const [detail, setDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  useEffect(() => {
    let active = true;
    const timer = setTimeout(() => {
      const query = new URLSearchParams({ limit: "50", action: filter, search });
      dataGet(`/audit-log?${query}`).then((data) => {
        if (!active) return;
        setRows(data.records || []); setCursor(data.next_cursor || null); setHasMore(Boolean(data.next_cursor));
      }).catch(() => { if (active) { setRows([]); setCursor(null); setHasMore(false); } });
    }, 180);
    return () => { active = false; clearTimeout(timer); };
  }, [filter, search]);
  function loadMore() {
    if (!cursor) return;
    const query = new URLSearchParams({ limit: "50", action: filter, search, cursor: String(cursor) });
    dataGet(`/audit-log?${query}`).then((data) => {
      setRows((current) => [...current, ...(data.records || [])]); setCursor(data.next_cursor || null); setHasMore(Boolean(data.next_cursor));
    }).catch(() => setHasMore(false));
  }
  async function openDetail(row) {
    setSelected(row);
    setDetail(null);
    setDetailLoading(true);
    try { setDetail(await dataGet(`/audit-log/${encodeURIComponent(row.order_reference || row.order_id)}`)); }
    catch (error) { setDetail({ error: error.message }); }
    finally { setDetailLoading(false); }
  }
  return h("div", null,
    h("div", { className: "page-head" },
      h("div", null, h("h1", null, "Enforcement Audit Log"), h("p", null, "Every order RuleLock has reviewed, what happened to it, and why."))
    ),
    h("div", { className: "audit-tools" },
      h("div", { className: "filter-row" }, ["ALL", "VOID", "HOLD", "REJECT", "PASS"].map((item) =>
        h("button", { key: item, className: filter === item ? "active" : "", onClick: () => setFilter(item) }, item)
      )),
      h("input", { value: search, placeholder: "Search CK order reference or numeric order ID...", onChange: (event) => setSearch(event.target.value) }),
      h("span", { className: "record-count" }, `${rows.length} records`)
    ),
    h("div", { className: "table-wrap" },
      h("table", { className: "audit-table" },
        h("thead", null, h("tr", null, ["DATE & TIME", "ORDER #", "ACCOUNT", "AMOUNT", "WHAT HAPPENED", "RULE", "SCORE"].map((label) => h("th", { key: label }, label)))),
        h("tbody", null, rows.length ? rows.map((row) => h("tr", { key: row.action_id, onClick: () => openDetail(row), onKeyDown: (event) => { if (event.key === "Enter") openDetail(row); }, tabIndex: 0, style: { cursor: "pointer" } },
          h("td", null, formatTimestamp(row.timestamp)),
          h("td", null,
            h("strong", null, row.order_reference || `Order ${row.order_id}`),
            row.order_id != null && h("small", { className: "secondary-order-id" }, `#${row.order_id}`)),
          h("td", null, row.account_username || row.account_id || "n/a"),
          h("td", null, row.total != null ? money(row.total) : "n/a"),
          h("td", null,
            h("div", { style: { display: "flex", alignItems: "center", gap: "8px" } },
              h(Badge, { tone: ACTION_TONE[row.action] || "green" }, row.action),
              h("span", null, `${ACTION_EXPLAIN[row.action] || "Reviewed"} â€” ${row.reason || "no reason recorded"}`)
            )
          ),
          h("td", null, row.rule_violated || "n/a"),
          h("td", null, row.score != null ? Number(row.score).toFixed(3) : "n/a")
        )) : h("tr", null, h("td", { colSpan: 7 }, "No audit records found.")))
      )
    ),
    selected && h(Panel, { title: "ORDER REVIEW DETAILS", kicker: h(React.Fragment, null,
      selected.order_reference || `Order ${selected.order_id}`,
      selected.order_id != null && h("small", { className: "secondary-order-id" }, `#${selected.order_id}`)), className: "audit-detail" },
      detailLoading ? h("p", null, "Loading stored reviewâ€¦") : detail?.error ? h("p", { role: "alert" }, detail.error) : detail ? h(React.Fragment, null,
        h("div", { className: "detail-summary" },
          h("strong", null, detail.customer_name || detail.account_username || selected.account_username || "Customer"),
          h(Badge, { tone: ACTION_TONE[selected.action] || "orange" }, String(detail.decision || selected.decision || "review").toUpperCase()),
          h("p", null, detail.reason || selected.reason || "No cause recorded.")),
        h(PipelineDetail, { pipeline: detail.pipeline, fallbackAccount: detail.account })
      ) : null
    ),
    hasMore && h("button", { className: "btn-outline", onClick: loadMore, style: { marginTop: "14px" } }, "LOAD MORE")
  );
}

function PipelineDetail({ pipeline, fallbackAccount }) {
  const p = pipeline || {};
  const c1 = p.c1_data_collection || {};
  const account = c1.account || fallbackAccount || {};
  const c2 = p.c2_rule_engine || {};
  const c3 = p.c3_anomaly || {};
  const c4 = p.c4_enforcement || {};
  const featureList = Object.entries(c1.session_features || {});
  return h("div", { className: "detail-components" },
    h("section", null, h("h3", null, "C1 Â· Data collection"),
      h("p", null, `${account.username || "Unknown customer"} Â· account age ${account.account_age_days ?? "n/a"} days Â· ${account.completed_orders ?? "n/a"} completed orders Â· ${account.cod_orders ?? 0} COD orders (${account.cod_bad_orders ?? 0} bad)`),
      h("p", null, `${c1.events_in_session ?? 0} events in session`),
      h("ul", null, featureList.map(([name, value]) => h("li", { key: name }, `${name.replaceAll("_", " ")}: ${value}`)))),
    h("section", null, h("h3", null, `C2 Â· Rules (${c2.status || "n/a"})`),
      h("ul", null, (c2.checks || []).map((check, index) => h("li", { key: `${check.code}-${index}` }, `${check.passed ? "PASSED" : "FAILED"} Â· ${check.label}: ${check.detail}`))),
      (c2.violations || []).map((violation, index) => h("p", { key: `${violation.code}-${index}` }, `${violation.code}: ${violation.reason}`))),
    h("section", null, h("h3", null, `C3 Â· Anomaly (${c3.status || "n/a"})`),
      h("p", null, `Score ${c3.score ?? "n/a"} Â· hold ${c3.hold_threshold ?? "n/a"} Â· reject ${c3.reject_threshold ?? "n/a"}`)),
    h("section", null, h("h3", null, `C4 Â· Enforcement (${c4.decision || "n/a"})`),
      h("p", null, `${c4.action || "none"} Â· ${c4.reason || "No reason recorded."}`),
      c4.account_action && h("p", null, `Account action: ${JSON.stringify(c4.account_action)}`))
  );
}

function Pipeline({ health }) {
  const [summary, setSummary] = useState(null);
  const [info, setInfo] = useState(null);
  useEffect(() => {
    dataGet("/dashboard/summary").then(setSummary).catch(() => setSummary(null));
    dataGet("/pipeline/info").then(setInfo).catch(() => setInfo(null));
  }, []);
  const components = [
    ["C1", "Transaction Monitoring & Data Collection", "Charuka", "data", "Captures checkout, coupon, session, and order review events before payment capture.", ["Events Captured (24H)", summary?.components?.transaction_monitor?.events_captured_24h ?? "n/a"], ["Avg Latency", summary?.components?.transaction_monitor?.avg_latency ?? "n/a"], ["Sessions Active", summary?.components?.transaction_monitor?.sessions_active ?? "n/a"], ["DB Write Errors", summary?.components?.transaction_monitor?.db_write_errors ?? "n/a"], ["Flask", "Supabase", "REST"], "POST /review-order"],
    ["C2", "Business Rule Validation Engine", "Sadini", "rule", "Applies deterministic business logic limits for coupons, quantities, minimums, and COD risk.", ["Requests Validated (24H)", summary?.components?.rule_engine?.requests_validated_24h ?? "n/a"], ["Rule Violations", summary?.components?.rule_engine?.rule_violations ?? "n/a"], ["Avg Validation Time", summary?.components?.rule_engine?.avg_validation_time ?? "n/a"], ["False Positives", summary?.components?.rule_engine?.false_positives ?? "n/a"], ["Flask", "Python", "Rules"], "rules.validate_transaction() (in-process)"],
    ["C3", "AI-Based Anomaly Detection", "Nihara", "anomaly", "Scores session features with an Isolation Forest to catch abuse spread across accounts and requests.", ["Model", info?.model || "n/a"], ["Anomaly Threshold", info?.thresholds?.hold ?? "n/a"], ["Reject Threshold", info?.thresholds?.reject ?? "n/a"], ["Trained", info?.trained_at || "n/a"], ["scikit-learn", "NumPy", "joblib"], "anomaly_scoring.score_session() (in-process)"],
    ["C4", "Automated Enforcement Engine", "Mishen, Lead", "enforcement", "Turns rule and anomaly results into automatic actions and records the audit trail.", ["Actions Taken (24H)", summary?.components?.enforcement_engine?.actions_taken_24h ?? "n/a"], ["Avg Decision Time", summary?.components?.enforcement_engine?.avg_decision_time ?? "n/a"], ["Audit Log Entries", summary?.components?.enforcement_engine?.audit_log_entries ?? "n/a"], ["Manual Overrides", summary?.components?.enforcement_engine?.manual_overrides ?? "n/a"], ["Flask", "Supabase", "Actions"], "decision.decide() (in-process)"],
  ];
  return h("div", null,
    h("div", { className: "page-head" }, h("div", null, h("h1", null, "Pipeline Components"), h("p", null, "Four end-to-end components, each owned by one team member, composing the full RuleLock AI detection pipeline."))),
    h("div", { className: "flow" }, components.map(([code, name, owner], index) =>
      h("div", { className: "flow-node", key: code },
        h("span", { className: "component-code" }, code),
        h("strong", null, name),
        h("small", null, owner),
        index < components.length - 1 && h("i", null)
      )
    )),
    h("div", { className: "component-grid" }, components.map((component) => h(ComponentCard, { key: component[0], component, health, info })))
  );
}

function ComponentCard({ component, health, info }) {
  const [code, name, owner, healthKey, description, stat1, stat2, stat3, stat4, tags, endpoint] = component;
  return h("article", { className: "component-card" },
    h("div", { className: "component-head" }, h("span", { className: "component-code" }, code)),
    h("h2", null, name),
    h("p", { className: "owner" }, owner),
    h("p", null, description),
    h("div", { className: "mini-stats" }, [stat1, stat2, stat3, stat4].map(([label, value]) =>
      h("div", { key: label }, h("span", null, label), h("strong", null, value))
    )),
    code === "C2" && h("dl", { className: "kv-list" },
      Object.entries(info?.rule_thresholds || {}).map(([k, v]) => h(React.Fragment, { key: k }, h("dt", null, k.replaceAll("_", " ")), h("dd", null, v)))
    ),
    code === "C3" && h("ul", { className: "feature-list" }, (info?.features || []).map((item) => h("li", { key: item }, item))),
    h("div", { className: "tag-row" }, tags.map((tag) => h("span", { key: tag }, tag))),
    h("code", { className: "endpoint" }, endpoint)
  );
}

function DashboardLogin({ onAuthenticated }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await dataPost("/login", { username, password });
      onAuthenticated();
    } catch (loginError) {
      setError(loginError.message);
    } finally {
      setLoading(false);
    }
  }

  return h("main", { className: "page", style: { maxWidth: "480px", paddingTop: "12vh" } },
    h("section", { className: "panel" },
      h("div", { className: "section-kicker" }, "RULELOCK AI"),
      h("h1", { style: { margin: "12px 0 20px" } }, "Dashboard login"),
      h("form", { className: "login-form", onSubmit: submit },
        h("label", { htmlFor: "dashboard-user" }, "Username"),
        h("input", { className: "login-input", id: "dashboard-user", autoComplete: "username", required: true, value: username, onChange: (event) => setUsername(event.target.value) }),
        h("label", { htmlFor: "dashboard-password", style: { display: "block", marginTop: "14px" } }, "Password"),
        h("input", { className: "login-input", id: "dashboard-password", type: "password", autoComplete: "current-password", required: true, value: password, onChange: (event) => setPassword(event.target.value) }),
        error ? h("p", { role: "alert", style: { color: "#fca5a5", marginTop: "14px" } }, error) : null,
        h("button", { className: "btn-run tone-cyan", type: "submit", disabled: loading, style: { marginTop: "20px" } }, loading ? "Signing inâ€¦" : "Sign in")
      )
    )
  );
}

function App() {
  const route = useRoute();
  const [authenticated, setAuthenticated] = useState(null);
  const health = useHealth(authenticated === true);
  useEffect(() => {
    const expireSession = () => setAuthenticated(false);
    window.addEventListener("rulelock-unauthorized", expireSession);
    return () => window.removeEventListener("rulelock-unauthorized", expireSession);
  }, []);
  useEffect(() => {
    dataGet("/dashboard/summary")
      .then(() => setAuthenticated(true))
      .catch((error) => setAuthenticated(error.status !== 401));
  }, []);
  const page = useMemo(() => {
    if (route === "attack-simulation") return h(AttackSimulation);
    if (route === "audit-log") return h(AuditLog);
    if (route === "pipeline") return h(Pipeline, { health });
    return h(Dashboard, { health });
  }, [route, health]);
  if (authenticated === null) return h("main", { className: "page" }, "Checking dashboard sessionâ€¦");
  if (!authenticated) return h(DashboardLogin, { onAuthenticated: () => setAuthenticated(true) });
  return h(Shell, { route, health }, page);
}

createRoot(document.getElementById("root")).render(h(App));
