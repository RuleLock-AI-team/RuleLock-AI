const { createElement: h, useEffect, useState } = React;
const { createRoot } = ReactDOM;
const API_BASE = window.RULELOCK_API_BASE || 'https://rulelock-data-collection.onrender.com';
const CAKELY_URL = 'https://charukagimhan2020-hub.github.io/cakely-final/';
const FALLBACK_PRODUCTS = { 'sku-1': { name: 'Wireless Mouse', price: 2500 }, 'sku-2': { name: 'USB-C Cable', price: 800 } };
const money = (value) => `LKR ${Math.round(value).toLocaleString('en-LK')}`;

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, { headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }, ...options });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || `API ${response.status}`);
  return data;
}

function Metric({ label, value, detail, tone = '' }) { return h('div', { className: 'metric-card' }, h('span', { className: 'metric-label' }, label), h('strong', { className: tone }, value), h('small', null, detail)); }
function Product({ sku, product, onAdd }) { return h('div', { className: 'col-md-6' }, h('div', { className: 'product-card h-100' }, h('div', { className: `product-art ${sku === 'sku-1' ? 'art-green' : 'art-orange'}` }, h('span', null, sku.toUpperCase())), h('div', { className: 'p-3' }, h('small', { className: 'text-secondary' }, 'CATALOG ITEM'), h('h3', { className: 'h5 mt-2' }, product.name), h('div', { className: 'd-flex justify-content-between align-items-center mt-4' }, h('strong', { className: 'price' }, money(product.price)), h('button', { className: 'btn btn-sm btn-outline-info', onClick: () => onAdd(sku) }, 'Add to review'))))); }

function App() {
  const [products, setProducts] = useState(FALLBACK_PRODUCTS);
  const [cart, setCart] = useState([]);
  const [online, setOnline] = useState(false);
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const total = cart.reduce((sum, item) => sum + products[item.sku].price * item.qty, 0);
  useEffect(() => { api('/browse').then(setProducts).catch(() => {}).finally(() => api('/health').then(() => setOnline(true)).catch(() => setOnline(false))); }, []);
  const add = (sku) => setCart((items) => { const found = items.find((item) => item.sku === sku); return found ? items.map((item) => item.sku === sku ? { ...item, qty: item.qty + 1 } : item) : [...items, { sku, qty: 1 }]; });
  const remove = (sku) => setCart((items) => items.filter((item) => item.sku !== sku));
  async function runReview() {
    if (!cart.length) return;
    setLoading(true); setMessage('');
    const first = cart[0];
    try {
      const data = await api('/checkout', { method: 'POST', body: JSON.stringify({ order_id: Number(String(Date.now()).slice(-8)), account_id: 'dashboard-demo', session_id: `dashboard-${Date.now()}`, payment_method: 'PREPAID', sku: first.sku, quantity: first.qty, coupons_applied: [], discount_value: 0, subtotal: total, total, account_verified: true, past_orders: 4, past_refusals: 0 }) });
      setReview(data);
    } catch (error) { setMessage(`${error.message}. Check the Render service token and CORS origin.`); } finally { setLoading(false); }
  }
  const brand = h('a', { className: 'navbar-brand fw-bold', href: '#' }, h('span', { className: 'brand-mark' }, 'R'), ' RuleLock ', h('span', { className: 'brand-accent' }, 'AI'));
  const navActions = h('div', { className: 'd-flex align-items-center gap-3' }, h('span', { className: online ? 'status online' : 'status' }, online ? '● API live' : '○ API offline'), h('a', { className: 'btn btn-sm btn-info', href: CAKELY_URL, target: '_blank', rel: 'noreferrer' }, 'Open Cakely ↗'));
  const nav = h('nav', { className: 'navbar navbar-expand-lg border-bottom border-secondary-subtle' }, h('div', { className: 'container-fluid px-4' }, brand, navActions));
  const hero = h('div', { className: 'row g-4 align-items-end mb-5' }, h('div', { className: 'col-lg-8' }, h('p', { className: 'eyebrow' }, 'LIVE COMMERCE DEFENSE / RENDER'), h('h1', { className: 'display-3 fw-bold' }, 'Rules that move at ', h('span', { className: 'text-info' }, 'checkout speed.')), h('p', { className: 'lead text-secondary col-xl-8' }, 'Monitor the Cakely storefront pipeline, review an order, and see the exact protection decision before payment capture.')), h('div', { className: 'col-lg-4' }, h('div', { className: 'live-panel' }, h('span', { className: 'eyebrow' }, 'UPSTREAM STOREFRONT'), h('strong', null, 'Cakely'), h('small', null, 'charukagimhan2020-hub.github.io/cakely-final'))));
  const metrics = h('div', { className: 'row g-3 mb-5' }, h('div', { className: 'col-sm-4' }, h(Metric, { label: 'API status', value: online ? 'ONLINE' : 'OFFLINE', detail: API_BASE, tone: online ? 'text-success' : 'text-danger' })), h('div', { className: 'col-sm-4' }, h(Metric, { label: 'Catalog', value: Object.keys(products).length, detail: 'active items available' })), h('div', { className: 'col-sm-4' }, h(Metric, { label: 'Review mode', value: 'PRE-CAPTURE', detail: 'payment gate active', tone: 'text-warning' })));
  const catalog = h('section', { className: 'col-xl-8' }, h('div', { className: 'section-head' }, h('div', null, h('p', { className: 'eyebrow' }, 'LIVE CATALOG'), h('h2', null, 'Review a Cakely order')), h('span', { className: 'text-secondary small' }, `${Object.keys(products).length} products`)), h('div', { className: 'row g-3' }, Object.entries(products).map(([sku, product]) => h(Product, { key: sku, sku, product, onAdd: add }))));
  const order = h('aside', { className: 'col-xl-4' }, h('div', { className: 'review-panel' }, h('p', { className: 'eyebrow' }, 'ORDER GATE'), h('h2', { className: 'h3' }, 'Protected review'), h('p', { className: 'text-secondary small' }, 'This demo calls RuleLock before a Cakely payment should be captured.'), h('div', { className: 'order-list my-4' }, cart.length ? cart.map((item) => h('div', { className: 'order-line', key: item.sku }, h('span', null, `${products[item.sku].name} × ${item.qty}`), h('button', { className: 'btn btn-link text-danger p-0', onClick: () => remove(item.sku) }, 'remove'))) : h('span', { className: 'text-secondary' }, 'No order selected')), h('div', { className: 'total-line' }, h('span', null, 'Server review total'), h('strong', null, money(total))), h('button', { className: 'btn btn-info w-100 mt-4', disabled: !cart.length || loading || !online, onClick: runReview }, loading ? 'Reviewing...' : 'Run RuleLock review'), message && h('div', { className: 'alert alert-danger mt-3 small' }, message), review && h('div', { className: `decision mt-4 ${review.decision}` }, h('div', { className: 'd-flex justify-content-between' }, h('strong', null, review.decision.toUpperCase()), h('span', null, review.reason)), h('small', null, `Rule: ${review.rule_result?.passed ? 'passed' : 'flagged'} · Model: ${review.anomaly_result?.is_anomaly ? 'anomaly' : 'normal'}`))));
  return h('div', null, nav, h('main', { className: 'container-fluid px-4 py-5' }, hero, metrics, h('div', { className: 'row g-4' }, catalog, order), h('footer', { className: 'border-top border-secondary-subtle mt-5 pt-4 text-secondary small' }, 'RuleLock AI · Cakely integration monitor · Payment capture belongs to Cakely server-side checkout after accept.')));
}

createRoot(document.getElementById('root')).render(h(App));
