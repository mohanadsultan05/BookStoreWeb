/* ============================================================
   cart.js – Shopping cart & checkout logic
   ============================================================ */

async function loadCart() {
  const container = document.getElementById('cart-items');
  const totalEl   = document.getElementById('cart-total');
  const summaryEl = document.getElementById('cart-summary');
  if (!container) return;

  showSpinner();
  try {
    const data = await apiFetch('/cart');
    if (!data.items.length) {
      container.innerHTML = `
        <div class="empty-state">
          <i class="bi bi-cart-x"></i>
          <h5>Your cart is empty</h5>
          <a href="books.html" class="btn btn-primary mt-2">Browse Books</a>
        </div>`;
      if (summaryEl) summaryEl.classList.add('d-none');
      return;
    }

    container.innerHTML = data.items.map(item => buildCartRow(item)).join('');
    if (totalEl) totalEl.textContent = formatPrice(data.total);
    if (summaryEl) summaryEl.classList.remove('d-none');
  } catch (err) {
    container.innerHTML = `<p class="text-danger">Failed to load cart: ${err.message}</p>`;
  } finally {
    hideSpinner();
  }
}

function buildCartRow(item) {
  const book = item.book || {};
  const img  = book.image_url || bookPlaceholder(book.title || '');
  const subtotal = formatPrice((book.price || 0) * item.quantity);

  return `
    <div class="card mb-3 border-0 shadow-sm" id="cart-item-${item.id}">
      <div class="card-body">
        <div class="row align-items-center g-3">
          <div class="col-2 col-md-1">
            <img src="${img}" class="cart-item-img" alt="${book.title}"
                 onerror="this.src='${bookPlaceholder(book.title || '')}'">
          </div>
          <div class="col-6 col-md-5">
            <h6 class="mb-0 fw-semibold">${book.title || 'Unknown'}</h6>
            <small class="text-muted">${book.author_name || ''}</small>
          </div>
          <div class="col-4 col-md-2 text-center">
            <span class="text-danger fw-bold">${formatPrice(book.price || 0)}</span>
          </div>
          <div class="col-6 col-md-2">
            <div class="input-group input-group-sm">
              <button class="btn btn-outline-secondary" onclick="changeQty(${item.id}, ${item.quantity - 1})">−</button>
              <input type="number" class="form-control text-center" value="${item.quantity}" min="1"
                     onchange="changeQty(${item.id}, this.value)" style="max-width:50px">
              <button class="btn btn-outline-secondary" onclick="changeQty(${item.id}, ${item.quantity + 1})">+</button>
            </div>
          </div>
          <div class="col-3 col-md-1 text-end fw-bold">${subtotal}</div>
          <div class="col-3 col-md-1 text-end">
            <button class="btn btn-sm btn-outline-danger" onclick="removeItem(${item.id})">
              <i class="bi bi-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>`;
}

async function changeQty(itemId, newQty) {
  if (newQty < 1) { removeItem(itemId); return; }
  try {
    await apiFetch(`/cart/${itemId}`, { method: 'PUT', body: JSON.stringify({ quantity: parseInt(newQty) }) });
    loadCart();
    updateCartBadge();
  } catch (err) {
    showToast(err.message || 'Update failed', 'error');
  }
}

async function removeItem(itemId) {
  try {
    await apiFetch(`/cart/${itemId}`, { method: 'DELETE' });
    document.getElementById(`cart-item-${itemId}`)?.remove();
    loadCart();
    updateCartBadge();
    showToast('Item removed');
  } catch (err) {
    showToast(err.message || 'Remove failed', 'error');
  }
}

async function clearCart() {
  if (!confirm('Clear your entire cart?')) return;
  try {
    await apiFetch('/cart/clear', { method: 'DELETE' });
    loadCart();
    updateCartBadge();
    showToast('Cart cleared');
  } catch (err) {
    showToast(err.message || 'Failed to clear cart', 'error');
  }
}

async function placeOrder() {
  const method = document.getElementById('payment-method')?.value;
  if (!method) { showToast('Select a payment method', 'error'); return; }

  try {
    showSpinner();
    const orderData = await apiFetch('/orders', { method: 'POST' });
    const order = orderData.order;

    // Make payment immediately
    await apiFetch('/payments', {
      method: 'POST',
      body: JSON.stringify({ order_id: order.id, payment_method: method })
    });

    updateCartBadge();
    showOrderSuccess(order);
  } catch (err) {
    showToast(err.message || 'Order failed', 'error');
  } finally {
    hideSpinner();
  }
}

function showOrderSuccess(order) {
  const container = document.getElementById('cart-items');
  const summary   = document.getElementById('cart-summary');
  if (summary) summary.classList.add('d-none');
  if (container) container.innerHTML = `
    <div class="text-center py-5">
      <div class="mb-3" style="font-size:4rem;color:#27ae60">✓</div>
      <h4 class="fw-bold text-success">Order Placed Successfully!</h4>
      <p class="text-muted">Order #${order.id} • ${formatPrice(order.total_amount)}</p>
      <a href="books.html" class="btn btn-primary me-2">Continue Shopping</a>
      <a href="orders.html" class="btn btn-outline-secondary">View Orders</a>
    </div>`;
}

async function loadOrders() {
  const container = document.getElementById('orders-list');
  if (!container) return;

  showSpinner();
  try {
    const data = await apiFetch('/orders');
    if (!data.orders.length) {
      container.innerHTML = `<div class="empty-state"><i class="bi bi-box"></i><p>No orders yet.</p></div>`;
      return;
    }
    container.innerHTML = data.orders.map(buildOrderRow).join('');
  } catch (err) {
    container.innerHTML = `<p class="text-danger">${err.message}</p>`;
  } finally {
    hideSpinner();
  }
}

function buildOrderRow(order) {
  const items = order.items.map(i => `${i.book_title} × ${i.quantity}`).join(', ');
  return `
    <div class="card mb-3 shadow-sm border-0">
      <div class="card-body">
        <div class="row align-items-center">
          <div class="col-md-2"><strong>Order #${order.id}</strong></div>
          <div class="col-md-4 text-muted small">${items}</div>
          <div class="col-md-2 fw-bold text-danger">${formatPrice(order.total_amount)}</div>
          <div class="col-md-2">${statusBadge(order.order_status)}</div>
          <div class="col-md-2 text-muted small">${formatDate(order.created_at)}</div>
        </div>
        ${order.payment ? `<div class="mt-2 small text-muted">Paid via ${order.payment.payment_method} on ${formatDate(order.payment.payment_date)}</div>` : ''}
      </div>
    </div>`;
}
