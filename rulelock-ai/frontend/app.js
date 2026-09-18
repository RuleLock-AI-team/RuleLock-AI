const API_BASE = window.RULELOCK_API_BASE || 'http://localhost:5001';
const SESSION_ID = `demo-${crypto.randomUUID ? crypto.randomUUID() : Date.now()}`;
const FALLBACK_PRODUCTS = { 'sku-1': { name: 'Wireless Mouse', price: 2500 }, 'sku-2': { name: 'USB-C Cable', price: 800 } };
const state = { products: {}, cart: [], coupon: null };
const byId = (id) => document.getElementById(id);
const money = (value) => `LKR ${Math.round(value).toLocaleString('en-LK')}`;

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, { headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }, ...options });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.error || `Request failed (${response.status})`);
  return payload;
}
function subtotal() { return state.cart.reduce((sum, item) => sum + state.products[item.sku].price * item.qty, 0); }
function discount(total) { if (!state.coupon) return 0; return state.coupon.type === 'percent' ? total * state.coupon.value / 100 : state.coupon.value; }
function renderCart() {
  const count = state.cart.reduce((sum, item) => sum + item.qty, 0);
  byId('cart-count').textContent = count;
  byId('checkout-button').disabled = count === 0;
  byId('cart-lines').innerHTML = state.cart.length ? state.cart.map((item) => `<div class="cart-line"><div><strong>${state.products[item.sku].name}</strong><span>${money(state.products[item.sku].price)} · qty ${item.qty}</span></div><button class="remove-button" data-remove="${item.sku}" type="button" aria-label="Remove item">×</button></div>`).join('') : '<div class="empty-cart">Your cart is waiting for something good.</div>';
  const total = subtotal(); const saved = discount(total);
  byId('subtotal').textContent = money(total); byId('discount').textContent = `- ${money(saved)}`; byId('total').textContent = money(Math.max(0, total - saved));
}
function addToCart(sku) { const item = state.cart.find((entry) => entry.sku === sku); if (item) item.qty += 1; else state.cart.push({ sku, qty: 1 }); renderCart(); }
function productMarkup([sku, product], index) { return `<article class="product-card" style="--delay:${index * 80}ms"><div class="product-art product-art-${index % 2 + 1}"><span>${String(index + 1).padStart(2, '0')}</span></div><div class="product-info"><span class="product-type">RuleLock essentials</span><h3>${product.name}</h3><div class="product-bottom"><strong>${money(product.price)}</strong><button class="add-button" data-sku="${sku}" type="button">Add <span>+</span></button></div></div></article>`; }
async function loadProducts() { try { state.products = await request('/browse'); byId('catalog-count').textContent = `${Object.keys(state.products).length} products · live catalog`; } catch { state.products = FALLBACK_PRODUCTS; byId('catalog-count').textContent = '2 products · demo catalog'; } byId('product-grid').innerHTML = Object.entries(state.products).map(productMarkup).join(''); renderCart(); }
async function checkServices() { try { await request('/health'); byId('pipeline-status').textContent = 'Data layer online'; byId('api-origin').textContent = `API: ${new URL(API_BASE).host}`; } catch { byId('pipeline-status').textContent = 'Demo mode · API offline'; byId('api-origin').textContent = 'API: start localhost:5001'; } }
async function applyCoupon() { const code = byId('coupon-code').value.trim().toUpperCase(); const message = byId('coupon-message'); if (!code) { message.textContent = 'Enter a coupon code first.'; return; } try { const result = await request('/apply-coupon', { method: 'POST', body: JSON.stringify({ code, subtotal: subtotal(), session_id: SESSION_ID }) }); const isPercent = result.subtotal > 0 && Math.abs(result.discount - result.subtotal * .1) < .01; state.coupon = { code, type: isPercent ? 'percent' : 'flat', value: isPercent ? 10 : result.discount }; message.textContent = `${code} applied · ${money(result.discount)} saved`; message.className = 'field-message success-message'; renderCart(); } catch (error) { state.coupon = null; message.textContent = error.message; message.className = 'field-message error-message'; renderCart(); } }
async function submitCheckout(event) { event.preventDefault(); const button = byId('checkout-button'); const message = byId('form-message'); const total = subtotal(); const first = state.cart[0]; const body = { order_id: String(Date.now()).slice(-8), account_id: byId('account-id').value.trim(), session_id: SESSION_ID, payment_method: byId('payment-method').value, sku: first.sku, quantity: first.qty, coupons_applied: state.coupon ? [state.coupon.code] : [], discount_value: discount(total), subtotal: total, total: Math.max(0, total - discount(total)), account_verified: true, past_orders: 4, past_refusals: 0 }; button.disabled = true; button.textContent = 'Reviewing order...'; try { const result = await request('/checkout', { method: 'POST', body: JSON.stringify(body) }); renderDecision(result); message.textContent = 'Checkout completed and reviewed by the protection pipeline.'; message.className = 'form-message success-message'; } catch (error) { message.textContent = `${error.message}. Start the data-collection service and try again.`; message.className = 'form-message error-message'; } finally { button.disabled = false; button.textContent = 'Run protected checkout'; } }
function renderDecision(result) { const rule = result.rule_result || {}; const anomaly = result.anomaly_result || {}; const enforcement = result.enforcement_result || {}; byId('decision-section').hidden = false; byId('decision-title').textContent = enforcement.decision === 'none' ? 'Checkout cleared' : 'Checkout needs attention'; byId('decision-pill').textContent = enforcement.decision || 'Reviewed'; byId('rule-result').textContent = rule.passed ? 'Passed' : 'Flagged'; byId('rule-detail').textContent = rule.failures?.[0] || 'All business rules passed'; byId('anomaly-result').textContent = anomaly.is_anomaly ? 'Anomaly' : 'Normal'; byId('anomaly-detail').textContent = `Score ${Number(anomaly.raw_score || 0).toFixed(3)}`; byId('enforcement-result').textContent = enforcement.decision || 'No action'; byId('enforcement-detail').textContent = enforcement.reason || 'No intervention required'; byId('decision-section').scrollIntoView({ behavior: 'smooth', block: 'start' }); }

const storefront = byId('product-grid');
if (storefront) {
  document.addEventListener('click', (event) => { const add = event.target.closest('[data-sku]'); const remove = event.target.closest('[data-remove]'); if (add) addToCart(add.dataset.sku); if (remove) { state.cart = state.cart.filter((item) => item.sku !== remove.dataset.remove); renderCart(); } });
  byId('coupon-button').addEventListener('click', applyCoupon);
  byId('checkout-form').addEventListener('submit', submitCheckout);
  loadProducts();
  checkServices();
}
