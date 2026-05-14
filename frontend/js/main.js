/* ============================================================
   main.js – Shared utilities: toasts, stars, cart badge
   ============================================================ */

function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `toast-msg toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3200);
}

function renderStars(rating) {
  const full  = Math.floor(rating);
  const half  = rating - full >= 0.5;
  const empty = 5 - full - (half ? 1 : 0);
  return '★'.repeat(full) + (half ? '½' : '') + '☆'.repeat(empty);
}

function formatPrice(price) {
  return '$' + Number(price).toFixed(2);
}

function formatDate(iso) {
  if (!iso) return '-';
  return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function statusBadge(status) {
  const map = {
    'Pending':    'badge-pending',
    'Processing': 'badge-processing',
    'Completed':  'badge-completed',
    'Paid':       'badge-completed',
    'Failed':     'badge-failed',
  };
  return `<span class="badge ${map[status] || 'bg-secondary'}">${status}</span>`;
}

function bookPlaceholder(title) {
  const colors = ['4a90d9', 'e74c3c', '27ae60', 'f39c12', '8e44ad'];
  const color = colors[Math.abs(title.charCodeAt(0)) % colors.length];
  return `https://via.placeholder.com/200x300/${color}/ffffff?text=${encodeURIComponent(title.substring(0,10))}`;
}

async function updateCartBadge() {
  const badge = document.getElementById('cart-count');
  if (!badge || !getToken()) return;
  try {
    const data = await apiFetch('/cart');
    badge.textContent = data.count || 0;
    badge.style.display = data.count > 0 ? 'inline' : 'none';
  } catch (_) {}
}

function showSpinner() {
  let s = document.getElementById('spinner-overlay');
  if (!s) {
    s = document.createElement('div');
    s.id = 'spinner-overlay';
    s.className = 'spinner-overlay';
    s.innerHTML = '<div class="spinner-border text-primary" style="width:3rem;height:3rem"></div>';
    document.body.appendChild(s);
  }
}

function hideSpinner() {
  const s = document.getElementById('spinner-overlay');
  if (s) s.remove();
}

// Build a book card HTML snippet
function buildBookCard(book) {
  const img   = book.image_url || bookPlaceholder(book.title);
  const stars = renderStars(book.rating || 0);
  const inStock = book.stock_quantity > 0;

  return `
    <div class="col">
      <div class="card book-card h-100">
        <a href="book-detail.html?id=${book.id}">
          <img src="${img}" alt="${book.title}" onerror="this.src='${bookPlaceholder(book.title)}'">
        </a>
        <div class="card-body d-flex flex-column">
          <a href="book-detail.html?id=${book.id}" class="text-decoration-none text-dark">
            <h6 class="card-title">${book.title}</h6>
          </a>
          <p class="author-name mb-1">${book.author_name || 'Unknown Author'}</p>
          <div class="stars mb-2">${stars} <small class="text-muted">(${book.rating || 0})</small></div>
          <div class="d-flex justify-content-between align-items-center mt-auto">
            <span class="price">${formatPrice(book.price)}</span>
            ${inStock
              ? `<button class="btn-add-cart" onclick="addToCart(${book.id}, event)"><i class="bi bi-cart-plus"></i> Add</button>`
              : `<span class="badge bg-secondary">Out of Stock</span>`}
          </div>
        </div>
      </div>
    </div>`;
}

async function addToCart(bookId, event) {
  if (event) event.stopPropagation();
  if (!getToken()) { window.location.href = 'login.html'; return; }
  const user = getUser();
  if (user && user.role !== 'customer') { showToast('Only customers can add to cart', 'error'); return; }

  try {
    await apiFetch('/cart/add', { method: 'POST', body: JSON.stringify({ book_id: bookId, quantity: 1 }) });
    showToast('Added to cart!');
    updateCartBadge();
  } catch (err) {
    showToast(err.message || 'Failed to add to cart', 'error');
  }
}
