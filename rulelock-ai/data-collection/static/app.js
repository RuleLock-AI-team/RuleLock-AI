// Demo storefront frontend — deliberately minimal.
// TODO (Charuka): wire cart state through /cart before hitting /apply-coupon
// with a real subtotal instead of the hardcoded demo value below.

async function loadProducts() {
  const res = await fetch("/browse");
  const products = await res.json();
  const container = document.getElementById("products");
  container.innerHTML = Object.entries(products)
    .map(([sku, p]) => `<div class="product">${p.name} — Rs. ${p.price} (${sku})</div>`)
    .join("");
}

async function applyCoupon() {
  const code = document.getElementById("coupon").value;
  const res = await fetch("/apply-coupon", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, subtotal: 2500 }),
  });
  const data = await res.json();
  document.getElementById("result").textContent = JSON.stringify(data, null, 2);
}

loadProducts();
