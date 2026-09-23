const { createElement: h, useEffect, useMemo, useState } = React;
const { createRoot } = ReactDOM;

const viteEnv = import.meta.env || {};
const runtimeConfig = window.RULELOCK_CONFIG || {};
const CONFIG = {
  dataUrl: runtimeConfig.DATA_COLLECTION_URL || window.RULELOCK_API_BASE || viteEnv.VITE_DATA_COLLECTION_URL || "https://rulelock-data-collection.onrender.com",
  proxyUrl: runtimeConfig.RULELOCK_PROXY_URL || "/.netlify/functions/rulelock",
  ruleUrl: runtimeConfig.RULE_ENGINE_URL || viteEnv.VITE_RULE_ENGINE_URL || "https://rulelock-engine.onrender.com",
  anomalyUrl: runtimeConfig.ANOMALY_URL || viteEnv.VITE_ANOMALY_URL || "https://rulelock-anomaly.onrender.com",
  enforcementUrl: runtimeConfig.ENFORCEMENT_URL || viteEnv.VITE_ENFORCEMENT_URL || "https://rulelock-enforcement.onrender.com",
  token: runtimeConfig.RULELOCK_API_TOKEN || window.RULELOCK_API_TOKEN || viteEnv.VITE_RULELOCK_API_TOKEN || "",
};

const ROUTES = [
  { id: "cakely", label: "Cakely Store", path: "/cakely" },
  { id: "dashboard", label: "Dashboard", path: "/dashboard" },
  { id: "attack-simulation", label: "Attack Simulation", path: "/attack-simulation" },
  { id: "audit-log", label: "Audit Log", path: "/audit-log" },
  { id: "pipeline", label: "Pipeline", path: "/pipeline" },
];

const ACTION_TONE = { VOID: "red", HOLD: "orange", PASS: "green", SUSPEND: "purple", FAIL: "red", ANOMALY: "orange" };
const money = (value) => `LKR ${Number(value || 0).toLocaleString("en-LK")}`;
const nowOrderId = () => Number(String(Date.now()).slice(-9));
const nowStamp = () => new Date().toLocaleString("en-LK", { hour12: false });

function authHeaders(extra = {}) {
  return {
    "Content-Type": "application/json",
    ...(CONFIG.token ? { Authorization: `Bearer ${CONFIG.token}` } : {}),
    ...extra,
  };
}

async function jsonFetch(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
  return data;
}

async function dataGet(path) {
  return jsonFetch(`${CONFIG.proxyUrl}?path=${encodeURIComponent(path)}`);
}

async function dataPost(path, payload) {
  return jsonFetch(`${CONFIG.proxyUrl}?path=${encodeURIComponent(path)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

function newSessionId() {
  return `cakely-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function accountIdFor(name, phone) {
  const key = `${name || "guest"}-${phone || "0"}`;
  let hash = 0;
  for (let i = 0; i < key.length; i += 1) hash = (hash * 31 + key.charCodeAt(i)) >>> 0;
  return `cakely-account-${hash}`;
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

function useHealth() {
  const [health, setHealth] = useState({});
  useEffect(() => {
    const services = {
      data: CONFIG.dataUrl,
      rule: CONFIG.ruleUrl,
      anomaly: CONFIG.anomalyUrl,
      enforcement: CONFIG.enforcementUrl,
    };
    Object.entries(services).forEach(async ([key, url]) => {
      try {
        const response = await fetch(`${url}/health`, { cache: "no-store" });
        setHealth((current) => ({ ...current, [key]: response.ok }));
      } catch {
        setHealth((current) => ({ ...current, [key]: false }));
      }
    });
  }, []);
  return health;
}

function Shell({ route, children, health }) {
  const current = ROUTES.find((item) => item.id === route) || ROUTES[0];
  const allOnline = ["data", "rule", "anomaly", "enforcement"].every((key) => health[key] === true);
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
        h("span", { className: `status-pill ${allOnline ? "online" : "offline"}` }, allOnline ? "ALL SYSTEMS ONLINE" : "SERVICE CHECKING"),
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
    threats_blocked: 0,
    threats_blocked_delta: 0,
    rule_violations: { total: 0, coupon: 0, cod: 0 },
    anomaly_detections: 0,
    discounts_voided: 0,
    cod_orders_held: 0,
    accounts_suspended: 0,
    abuse_breakdown: { coupon_discount_abuse: 0, price_quantity_manipulation: 0, cod_fake_order_abuse: 0 },
    enforcement_feed: [],
  };
  const [summary, setSummary] = useState(empty);
  useEffect(() => {
    dataGet("/dashboard/summary").then(setSummary).catch(() => setSummary(empty));
  }, []);

  const kpis = [
    ["THREATS BLOCKED (24H)", summary.threats_blocked, `+${summary.threats_blocked_delta || 0} vs yesterday`, "pink"],
    ["RULE VIOLATIONS", summary.rule_violations.total, `${summary.rule_violations.coupon} coupon / ${summary.rule_violations.cod} COD`, "orange"],
    ["ANOMALY DETECTIONS", summary.anomaly_detections, "Isolation Forest", "purple"],
    ["DISCOUNTS VOIDED", summary.discounts_voided, "auto-enforced", "cyan"],
    ["COD ORDERS HELD", summary.cod_orders_held, "awaiting prepayment", "cyan"],
    ["ACCOUNTS SUSPENDED", summary.accounts_suspended, "rate-limited (session)", "orange"],
  ];
  const breakdown = [
    ["Coupon / Discount Abuse", summary.abuse_breakdown.coupon_discount_abuse, "red"],
    ["Price & Quantity Manipulation", summary.abuse_breakdown.price_quantity_manipulation, "orange"],
    ["COD Fake-Order & Return Abuse", summary.abuse_breakdown.cod_fake_order_abuse, "cyan"],
  ];
  const maxBreakdown = Math.max(...breakdown.map((row) => row[1]), 1);

  return h("div", null,
    h("div", { className: "kpi-grid" }, kpis.map(([label, value, subtext, tone]) =>
      h("article", { className: "kpi-card", key: label },
        h("span", { className: "mono-label" }, label),
        h("strong", { className: `text-${tone}` }, value ?? 0),
        h("small", null, subtext)
      )
    )),
    h("div", { className: "dashboard-grid" },
      h(Panel, { title: "ENFORCEMENT FEED - LIVE", kicker: h("span", { className: "live-dot" }, "ONLINE") },
        h("div", { className: "feed-list" },
          summary.enforcement_feed.length ? summary.enforcement_feed.map((item, index) =>
            h("div", { className: "feed-row", key: `${item.timestamp}-${index}` },
              h("time", null, item.timestamp || "-"),
              h(Badge, { tone: ACTION_TONE[item.action] || "green" }, item.action || "PASS"),
              h("span", null, item.description || "RuleLock review completed")
            )
          ) : h("div", { className: "empty-state" }, "No RuleLock reviews in the last 24 hours.")
        )
      ),
      h("div", { className: "stack" },
        h(Panel, { title: "ABUSE BREAKDOWN (24H)" },
          h("div", { className: "breakdown-list" }, breakdown.map(([label, count, tone]) =>
            h("div", { className: "breakdown-row", key: label },
              h("div", null, h("span", null, label), h("strong", null, count)),
              h("i", { className: `bar tone-${tone}`, style: { width: `${Math.max((count / maxBreakdown) * 100, count ? 8 : 0)}%` } })
            )
          ))
        ),
        h(Panel, { title: "SYSTEM STATUS" },
          [
            ["Transaction Monitor", health.data],
            ["Rule Validation Engine", health.rule],
            ["Anomaly Detection (IF)", health.anomaly],
            ["Enforcement Engine", health.enforcement],
          ].map(([name, ok]) => h("div", { className: "status-row", key: name },
            h("span", null, name),
            h(Badge, { tone: ok ? "green" : "red" }, ok ? "ONLINE" : "OFFLINE")
          ))
        )
      )
    )
  );
}

function CakelyStore() {
  const [products, setProducts] = useState(null);
  const [cart, setCart] = useState([]);
  const [couponCode, setCouponCode] = useState("");
  const [coupon, setCoupon] = useState(null);
  const [couponError, setCouponError] = useState("");
  const [couponLoading, setCouponLoading] = useState(false);
  const [form, setForm] = useState({ name: "", phone: "", address: "", accountVerified: true, paymentMethod: "PREPAID" });
  const [session] = useState(newSessionId);
  const [checkoutState, setCheckoutState] = useState({ loading: false, result: null, error: "" });

  useEffect(() => {
    dataGet("/browse").then((data) => setProducts(data)).catch(() => setProducts({}));
  }, []);

  function addToCart(sku, item) {
    setCart((current) => {
      const existing = current.find((row) => row.sku === sku);
      if (existing) return current.map((row) => (row.sku === sku ? { ...row, qty: row.qty + 1 } : row));
      return [...current, { sku, name: item.name, price: item.price, qty: 1 }];
    });
  }

  function changeQty(sku, delta) {
    setCart((current) => current
      .map((row) => (row.sku === sku ? { ...row, qty: row.qty + delta } : row))
      .filter((row) => row.qty > 0));
  }

  function removeFromCart(sku) {
    setCart((current) => current.filter((row) => row.sku !== sku));
  }

  const subtotal = cart.reduce((sum, row) => sum + row.price * row.qty, 0);
  const discount = coupon ? coupon.discount : 0;
  const total = Math.max(subtotal - discount, 0);
  const totalQty = cart.reduce((sum, row) => sum + row.qty, 0);

  async function applyCoupon() {
    if (!couponCode.trim()) return;
    setCouponLoading(true);
    setCouponError("");
    try {
      const response = await dataPost("/apply-coupon", { coupon_code: couponCode.trim().toUpperCase(), subtotal, session_id: session });
      setCoupon({ code: couponCode.trim().toUpperCase(), discount: response.discount || 0 });
    } catch (error) {
      setCoupon(null);
      setCouponError(error.message);
    } finally {
      setCouponLoading(false);
    }
  }

  function removeCoupon() {
    setCoupon(null);
    setCouponCode("");
    setCouponError("");
  }

  async function placeOrder() {
    if (!cart.length || !form.name.trim() || !form.phone.trim() || !form.address.trim()) {
      setCheckoutState({ loading: false, result: null, error: "Fill in your name, phone, and delivery address, and add at least one cake to the cart." });
      return;
    }
    setCheckoutState({ loading: true, result: null, error: "" });
    const orderId = nowOrderId();
    const primary = cart[0];
    const payload = {
      order_id: orderId,
      account_id: accountIdFor(form.name, form.phone),
      user_id: Number(String(orderId).slice(-6)),
      session_id: session,
      payment_method: form.paymentMethod,
      sku: primary.sku,
      quantity: totalQty,
      coupons_applied: coupon ? [coupon.code] : [],
      discount_value: discount,
      subtotal,
      total,
      account_verified: form.accountVerified,
      past_orders: 0,
      past_refusals: 0,
      customer_name: form.name,
      customer_phone: form.phone,
      customer_address: form.address,
      items: cart,
    };
    try {
      const response = await dataPost("/checkout", payload);
      setCheckoutState({ loading: false, result: { order_id: orderId, ...response }, error: "" });
      if (response.decision === "accept") {
        setCart([]);
        setCoupon(null);
        setCouponCode("");
      }
    } catch (error) {
      setCheckoutState({ loading: false, result: null, error: error.message });
    }
  }

  const entries = Object.entries(products || {});
  return h("div", null,
    h("div", { className: "page-head" },
      h("div", null,
        h("div", { className: "section-kicker" }, "CAKELY"),
        h("h1", null, "Order a Cake"),
        h("p", null, "Every checkout here is a real order. It is reviewed by the live RuleLock AI pipeline before payment is captured.")
      )
    ),
    h("div", { className: "store-grid" },
      h(Panel, { title: "Cake Menu" },
        products === null ? h("div", { className: "empty-state" }, "Loading menu...") :
        !entries.length ? h("div", { className: "empty-state" }, "No products available right now.") :
        h("div", { className: "product-grid" }, entries.map(([sku, item]) =>
          h("article", { className: "product-card", key: sku },
            h("h4", null, item.name),
            h("span", { className: "price" }, money(item.price)),
            h("div", { className: "qty-row" },
              h("button", { className: "add-btn", onClick: () => addToCart(sku, item) }, "Add to cart")
            )
          )
        ))
      ),
      h("div", { className: "stack" },
        h(Panel, { title: "Your Cart" },
          h("div", { className: "cart-panel" },
            !cart.length ? h("div", { className: "empty-cart" }, "Your cart is empty. Add a cake to get started.") :
            cart.map((row) => h("div", { className: "cart-row", key: row.sku },
              h("span", null, `${row.name} x ${row.qty}`),
              h("span", null, money(row.price * row.qty)),
              h("div", { className: "qty-row" },
                h("button", { onClick: () => changeQty(row.sku, -1) }, "-"),
                h("button", { onClick: () => changeQty(row.sku, 1) }, "+"),
                h("button", { onClick: () => removeFromCart(row.sku) }, "Remove")
              )
            )),
            h("div", { className: "coupon-row" },
              h("input", {
                placeholder: "Coupon code (e.g. WELCOME10)",
                value: couponCode,
                disabled: !!coupon,
                onChange: (event) => setCouponCode(event.target.value),
              }),
              coupon
                ? h("button", { className: "btn-outline", onClick: removeCoupon }, "Remove")
                : h("button", { className: "btn-outline", disabled: couponLoading || !subtotal, onClick: applyCoupon }, couponLoading ? "Checking..." : "Apply")
            ),
            couponError && h("div", { className: "danger" }, couponError),
            h("div", { className: "cart-totals" },
              h("div", null, h("span", null, "Subtotal"), h("strong", null, money(subtotal))),
              coupon && h("div", null, h("span", null, `Discount (${coupon.code})`), h("strong", null, `- ${money(discount)}`)),
              h("div", { className: "grand" }, h("span", null, "Total"), h("strong", null, money(total)))
            )
          )
        ),
        h(Panel, { title: "Delivery & Payment" },
          h("div", { className: "checkout-form" },
            h("label", { className: "half" }, "Full name",
              h("input", { value: form.name, onChange: (event) => setForm({ ...form, name: event.target.value }) })
            ),
            h("label", { className: "half" }, "Phone number",
              h("input", { value: form.phone, onChange: (event) => setForm({ ...form, phone: event.target.value }) })
            ),
            h("label", null, "Delivery address",
              h("textarea", { rows: 2, value: form.address, onChange: (event) => setForm({ ...form, address: event.target.value }) })
            ),
            h("label", null, "Payment method",
              h("div", { className: "payment-toggle" },
                h("button", { type: "button", className: form.paymentMethod === "PREPAID" ? "active" : "", onClick: () => setForm({ ...form, paymentMethod: "PREPAID" }) }, "Card (Prepaid)"),
                h("button", { type: "button", className: form.paymentMethod === "COD" ? "active" : "", onClick: () => setForm({ ...form, paymentMethod: "COD" }) }, "Cash on Delivery")
              )
            ),
            h("button", { className: "checkout-btn", disabled: checkoutState.loading, onClick: placeOrder }, checkoutState.loading ? "Placing order..." : `Place order - ${money(total)}`)
          ),
          checkoutState.error && h("div", { className: "danger", style: { marginTop: "10px" } }, checkoutState.error),
          checkoutState.result && h(OrderResultBanner, { result: checkoutState.result })
        )
      )
    )
  );
}

function OrderResultBanner({ result }) {
  const decision = result.decision || "hold";
  const copy = {
    accept: ["Order confirmed!", "Payment captured. Your cake is being prepared."],
    hold: ["Order under review", "Payment was not captured yet. Our team will contact you shortly."],
    reject: ["Order blocked", "This order could not be placed."],
  }[decision] || ["Order received", result.reason || ""];
  return h("div", { className: `decision-banner ${decision}` },
    h("h3", null, copy[0]),
    h("p", null, copy[1]),
    h("p", null, h("strong", null, "Order ID: "), result.order_id),
    h("p", null, h("strong", null, "RuleLock reason: "), result.reason || "-")
  );
}

const SCENARIOS = {
  coupon: {
    tab: "COUPON ABUSE",
    tone: "pink",
    title: "Coupon Stacking Attack",
    subtitle: "Applying multiple coupon codes in a single checkout session",
    body: "Attacker applies 4 coupon codes across rapid successive requests in the same session. Each code is individually valid; the abuse only becomes visible at the session level.",
    rows: (session) => [
      ["Product", "Sony WH-1000XM5 Headphones"],
      ["Catalog Price", money(68800)],
      ["Coupons Applied", "x4 (SAVE10, FLASH20, NEWUSER, LOYALTY15)", true],
      ["Final Price Claimed", "LKR 23,800 (-65%)", true],
      ["Session ID", session],
      ["Coupon Attempts", "4 in 38 sec", true],
    ],
    payload: (orderId, session) => ({
      order_id: orderId,
      account_id: "coupon-lab-account",
      user_id: 501,
      session_id: session,
      payment_method: "PREPAID",
      sku: "sku-sony-headphones",
      quantity: 1,
      coupons_applied: ["SAVE10", "FLASH20", "NEWUSER", "LOYALTY15"],
      discount_value: 45000,
      subtotal: 68800,
      total: 23800,
      account_verified: true,
      past_orders: 2,
      past_refusals: 0,
      session_features: {
        coupon_attempts_per_session: 4,
        avg_seconds_between_requests: 9.5,
        distinct_accounts_same_device: 1,
        distinct_addresses_same_phone: 1,
      },
    }),
  },
  price: {
    tab: "PRICE MANIPULATION",
    tone: "orange",
    title: "Price Tampering Attack",
    subtitle: "Client-side price manipulation on checkout POST request",
    body: "Attacker intercepts the checkout API request and modifies the unit_price field from LKR 4,800 to LKR 1,200, then submits. The order appears legitimate; it passed product validation.",
    rows: (session) => [
      ["Product", "Nike Air Max 270 (Size 42)"],
      ["Catalog Price", money(4800)],
      ["Submitted Price", "LKR 1,200 (-75%)", true],
      ["Quantity", "12 units", true],
      ["Total Claimed", "LKR 14,400 (catalog: LKR 57,600)", true],
      ["Session ID", session],
    ],
    payload: (orderId, session) => ({
      order_id: orderId,
      account_id: "price-lab-account",
      user_id: 502,
      session_id: session,
      payment_method: "PREPAID",
      sku: "sku-nike-270",
      quantity: 12,
      coupons_applied: [],
      discount_value: 0,
      subtotal: 14400,
      total: 14400,
      account_verified: true,
      past_orders: 3,
      past_refusals: 0,
      session_features: {
        coupon_attempts_per_session: 0,
        avg_seconds_between_requests: 4,
        distinct_accounts_same_device: 1,
        distinct_addresses_same_phone: 1,
      },
    }),
  },
  cod: {
    tab: "COD ABUSE",
    tone: "cyan",
    title: "COD Fake-Order Abuse",
    subtitle: "High-value cash-on-delivery order from a high-risk account",
    body: "An unverified account with a 78% prior refusal rate places a high-value COD order. No prepayment risk for the attacker; wasted delivery and stock for the seller.",
    rows: () => [
      ["Product", "Samsung 65\" QLED TV"],
      ["Order Value", money(187000), true],
      ["Payment Method", "Cash on Delivery", true],
      ["Account Status", "Unverified (email only)", true],
      ["Prior Refusal Rate", "78% (7 of 9 orders)", true],
      ["Phone / Address", "Linked to 3 other flagged accounts", true],
    ],
    payload: (orderId, session) => ({
      order_id: orderId,
      account_id: "cod-lab-account",
      user_id: 503,
      session_id: session,
      payment_method: "COD",
      sku: "sku-samsung-qled",
      quantity: 1,
      coupons_applied: [],
      discount_value: 0,
      subtotal: 187000,
      total: 187000,
      account_verified: false,
      past_orders: 9,
      past_refusals: 7,
      session_features: {
        coupon_attempts_per_session: 0,
        avg_seconds_between_requests: 2.5,
        distinct_accounts_same_device: 3,
        distinct_addresses_same_phone: 3,
      },
    }),
  },
};

function AttackSimulation() {
  const [active, setActive] = useState("coupon");
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
      const response = await dataPost("/review-order", scenario.payload(orderId, sessionSeed));
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
          h("code", null, "POST /api/checkout HTTP/1.1"),
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
    ["C1", "Transaction Monitor", "-", "Captured checkout event and session metadata."],
    ["C2", "Rule Validation Engine", "-", "Waiting for rule-engine response."],
    ["C3", "Anomaly Detection (IF)", "-", "Waiting for Isolation Forest score."],
    ["C4", "Enforcement Engine", "-", "Waiting for enforcement decision."],
  ];
  if (!result) return base;
  if (!result.ok) return base.map(([code, name]) => [code, name, "FAIL", "service unreachable"]);
  const r = result.response;
  return [
    ["C1", "Transaction Monitor", "PASS", "Order payload captured and logged."],
    ["C2", "Rule Validation Engine", r.rule_result?.passed ? "PASS" : "FAIL", (r.rule_result?.failures || []).join("; ") || r.rule_result?.rule_code || "No rule violations."],
    ["C3", "Anomaly Detection (IF)", r.anomaly_result?.is_anomaly ? "ANOMALY" : "PASS", `raw_score=${Number(r.anomaly_result?.raw_score || 0).toFixed(3)}`],
    ["C4", "Enforcement Engine", r.enforcement_result?.decision === "none" ? "PASS" : "FAIL", r.enforcement_result?.reason || r.reason || "No action required."],
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
      h("strong", null, verdict),
      h("p", null, reason),
      h("small", null, result ? `Action logged to audit trail / ${result.timestamp}` : "-")
    )
  );
}

function AuditLog() {
  const [filter, setFilter] = useState("ALL");
  const [search, setSearch] = useState("");
  const [rows, setRows] = useState([]);
  useEffect(() => {
    dataGet("/audit-log?limit=200").then((data) => setRows(data.records || [])).catch(() => setRows([]));
  }, []);
  const filtered = rows.filter((row) => {
    if (filter !== "ALL" && row.action !== filter) return false;
    if (search && !JSON.stringify(row).toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });
  return h("div", null,
    h("div", { className: "page-head" },
      h("div", null, h("h1", null, "Enforcement Audit Log"), h("p", null, "Append-only record of every automated action taken by the enforcement engine."))
    ),
    h("div", { className: "audit-tools" },
      h("div", { className: "filter-row" }, ["ALL", "VOID", "HOLD", "SUSPEND", "PASS"].map((item) =>
        h("button", { key: item, className: filter === item ? "active" : "", onClick: () => setFilter(item) }, item)
      )),
      h("input", { value: search, placeholder: "Search session, order, rule...", onChange: (event) => setSearch(event.target.value) }),
      h("span", { className: "record-count" }, `${filtered.length} records`)
    ),
    h("div", { className: "table-wrap" },
      h("table", { className: "audit-table" },
        h("thead", null, h("tr", null, ["ACTION ID", "TIMESTAMP", "ACTION", "REASON", "RULE VIOLATED", "SCORE", "ORDER"].map((label) => h("th", { key: label }, label)))),
        h("tbody", null, filtered.length ? filtered.map((row) => h("tr", { key: row.action_id },
          h("td", null, row.action_id),
          h("td", null, row.timestamp || "-"),
          h("td", null, h(Badge, { tone: ACTION_TONE[row.action] || "green" }, row.action)),
          h("td", null, row.reason || "-"),
          h("td", null, row.rule_violated || "-"),
          h("td", { className: Number(row.score) < -0.06 ? "risk-high" : "risk-low" }, row.score ?? "-"),
          h("td", null, row.order_id || "-")
        )) : h("tr", null, h("td", { colSpan: 7 }, "No audit records found.")))
      )
    )
  );
}

function Pipeline({ health }) {
  const [summary, setSummary] = useState(null);
  useEffect(() => {
    dataGet("/dashboard/summary").then(setSummary).catch(() => setSummary(null));
  }, []);
  const components = [
    ["C1", "Transaction Monitoring & Data Collection", "Charuka", "data", "Captures checkout, coupon, session, and order review events before payment capture.", ["Events Captured (24H)", summary?.components?.transaction_monitor?.events_captured_24h ?? "-"], ["Avg Latency", summary?.components?.transaction_monitor?.avg_latency ?? "-"], ["Sessions Active", summary?.components?.transaction_monitor?.sessions_active ?? "-"], ["DB Write Errors", summary?.components?.transaction_monitor?.db_write_errors ?? "-"], ["Flask", "Supabase", "REST"], "POST /review-order"],
    ["C2", "Business Rule Validation Engine", "Sadini", "rule", "Applies deterministic business logic limits for coupons, quantities, minimums, and COD risk.", ["Requests Validated (24H)", summary?.components?.rule_engine?.requests_validated_24h ?? "-"], ["Rule Violations", summary?.components?.rule_engine?.rule_violations ?? "-"], ["Avg Validation Time", summary?.components?.rule_engine?.avg_validation_time ?? "-"], ["False Positives", summary?.components?.rule_engine?.false_positives ?? "-"], ["Flask", "Python", "Rules"], "POST /validate"],
    ["C3", "AI-Based Anomaly Detection", "Nihara", "anomaly", "Scores session features with an Isolation Forest to catch abuse spread across accounts and requests.", ["Model", "Isolation Forest"], ["Anomaly Threshold", summary?.components?.anomaly_detection?.anomaly_threshold ?? "-0.06"], ["Precision (test set)", summary?.components?.anomaly_detection?.precision ?? "-"], ["False Positive Rate", summary?.components?.anomaly_detection?.false_positive_rate ?? "-"], ["scikit-learn", "NumPy", "joblib"], "POST /score"],
    ["C4", "Automated Enforcement Engine", "Mishen, Lead", "enforcement", "Turns rule and anomaly results into automatic actions and records the audit trail.", ["Actions Taken (24H)", summary?.components?.enforcement_engine?.actions_taken_24h ?? "-"], ["Avg Decision Time", summary?.components?.enforcement_engine?.avg_decision_time ?? "-"], ["Audit Log Entries", summary?.components?.enforcement_engine?.audit_log_entries ?? "-"], ["Manual Overrides", summary?.components?.enforcement_engine?.manual_overrides ?? "-"], ["Flask", "SQLite", "Actions"], "POST /enforce"],
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
    h("div", { className: "component-grid" }, components.map((component) => h(ComponentCard, { key: component[0], component, health })))
  );
}

function ComponentCard({ component, health }) {
  const [code, name, owner, healthKey, description, stat1, stat2, stat3, stat4, tags, endpoint] = component;
  const ok = health[healthKey];
  return h("article", { className: "component-card" },
    h("div", { className: "component-head" }, h("span", { className: "component-code" }, code), h(Badge, { tone: ok ? "green" : "red" }, ok ? "ONLINE" : "OFFLINE")),
    h("h2", null, name),
    h("p", { className: "owner" }, owner),
    h("p", null, description),
    h("div", { className: "mini-stats" }, [stat1, stat2, stat3, stat4].map(([label, value]) =>
      h("div", { key: label }, h("span", null, label), h("strong", null, value))
    )),
    code === "C2" && h("dl", { className: "kv-list" },
      [["Max coupons/session", "1"], ["Max discount depth", "LKR 5,000"], ["Quantity ceiling/SKU", "10 units"], ["Min purchase (coupon)", "LKR 500"], ["COD cap (unverified)", "LKR 15,000"], ["COD refusal-rate limit", "50% -> HOLD"]].map(([k, v]) => h(React.Fragment, { key: k }, h("dt", null, k), h("dd", null, v)))
    ),
    code === "C3" && h("ul", { className: "feature-list" }, ["request_timing_variance", "coupon_attempts_per_session", "cross_account_device_overlap", "cross_account_address_overlap", "session_velocity_score"].map((item) => h("li", { key: item }, item))),
    h("div", { className: "tag-row" }, tags.map((tag) => h("span", { key: tag }, tag))),
    h("code", { className: "endpoint" }, endpoint)
  );
}

function App() {
  const route = useRoute();
  const health = useHealth();
  const page = useMemo(() => {
    if (route === "cakely") return h(CakelyStore);
    if (route === "attack-simulation") return h(AttackSimulation);
    if (route === "audit-log") return h(AuditLog);
    if (route === "pipeline") return h(Pipeline, { health });
    return h(Dashboard, { health });
  }, [route, health]);
  return h(Shell, { route, health }, page);
}

createRoot(document.getElementById("root")).render(h(App));
