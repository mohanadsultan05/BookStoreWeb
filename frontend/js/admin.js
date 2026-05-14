/* ============================================================
   admin.js – Admin dashboard logic
   ============================================================ */

let activeSection = 'dashboard';

function showSection(section) {
  document.querySelectorAll('.admin-section').forEach(s => s.classList.add('d-none'));
  const el = document.getElementById(`section-${section}`);
  if (el) el.classList.remove('d-none');
  activeSection = section;

  document.querySelectorAll('.sidebar .nav-link').forEach(l => l.classList.remove('active'));
  const link = document.querySelector(`.sidebar [data-section="${section}"]`);
  if (link) link.classList.add('active');

  const loaders = {
    dashboard: loadDashboard,
    books:     loadAdminBooks,
    orders:    loadAdminOrders,
    users:     loadAdminUsers,
    genres:    loadAdminGenres,
    payments:  loadAdminPayments,
    reports:   loadReports,
  };
  if (loaders[section]) loaders[section]();
}

async function loadDashboard() {
  try {
    const data = await apiFetch('/admin/dashboard');
    const s = data.stats;

    document.getElementById('stat-users').textContent    = s.total_users;
    document.getElementById('stat-books').textContent    = s.total_books;
    document.getElementById('stat-orders').textContent   = s.total_orders;
    document.getElementById('stat-revenue').textContent  = formatPrice(s.total_revenue);
    document.getElementById('stat-pending').textContent  = s.pending_orders;
    document.getElementById('stat-completed').textContent= s.completed_orders;

    // Recent orders table
    const tbody = document.getElementById('recent-orders-body');
    if (tbody) {
      tbody.innerHTML = data.recent_orders.map(o => `
        <tr>
          <td>#${o.id}</td>
          <td>${o.customer_name || '-'}</td>
          <td>${formatPrice(o.total_amount)}</td>
          <td>${statusBadge(o.order_status)}</td>
          <td>${formatDate(o.created_at)}</td>
        </tr>`).join('');
    }

    // Low stock
    const lowStockEl = document.getElementById('low-stock-body');
    if (lowStockEl) {
      lowStockEl.innerHTML = data.low_stock_books.length
        ? data.low_stock_books.map(b => `
            <tr>
              <td>${b.title}</td>
              <td>${b.author_name || '-'}</td>
              <td><span class="text-danger fw-bold">${b.stock_quantity}</span></td>
              <td>
                <button class="btn btn-sm btn-outline-primary" onclick="promptUpdateStock(${b.id}, ${b.stock_quantity})">
                  Update
                </button>
              </td>
            </tr>`).join('')
        : '<tr><td colspan="4" class="text-center text-muted">No low-stock books</td></tr>';
    }
  } catch (err) {
    showToast('Failed to load dashboard: ' + err.message, 'error');
  }
}

async function loadAdminBooks() {
  const tbody = document.getElementById('admin-books-body');
  if (!tbody) return;
  try {
    const data = await apiFetch('/admin/books');
    tbody.innerHTML = data.books.map(b => `
      <tr>
        <td>${b.id}</td>
        <td>
          <img src="${b.image_url || bookPlaceholder(b.title)}" width="36" height="46"
               style="object-fit:cover;border-radius:4px" class="me-2"
               onerror="this.src='${bookPlaceholder(b.title)}'">
          ${b.title}
        </td>
        <td>${b.author_name || '-'}</td>
        <td>${b.genre_name || '-'}</td>
        <td>${formatPrice(b.price)}</td>
        <td>${b.stock_quantity}</td>
        <td>${b.rating || 0}</td>
        <td>
          <button class="btn btn-sm btn-outline-primary me-1"
                  onclick="promptUpdateStock(${b.id}, ${b.stock_quantity})">Stock</button>
          <button class="btn btn-sm btn-outline-danger"
                  onclick="deleteBook(${b.id})">Delete</button>
        </td>
      </tr>`).join('');
  } catch (err) {
    showToast('Failed to load books: ' + err.message, 'error');
  }
}

async function loadAdminOrders() {
  const tbody = document.getElementById('admin-orders-body');
  if (!tbody) return;
  try {
    const data = await apiFetch('/admin/orders');
    tbody.innerHTML = data.orders.map(o => `
      <tr>
        <td>#${o.id}</td>
        <td>${o.customer_name || '-'}</td>
        <td>${o.items.length} item(s)</td>
        <td>${formatPrice(o.total_amount)}</td>
        <td>${statusBadge(o.order_status)}</td>
        <td>${formatDate(o.created_at)}</td>
        <td>
          <select class="form-select form-select-sm" onchange="updateOrderStatus(${o.id}, this.value)"
                  ${o.order_status === 'Completed' ? 'disabled' : ''}>
            <option value="">Change...</option>
            <option value="Pending"    ${o.order_status==='Pending'    ?'selected':''}>Pending</option>
            <option value="Processing" ${o.order_status==='Processing' ?'selected':''}>Processing</option>
            <option value="Completed"  ${o.order_status==='Completed'  ?'selected':''}>Completed</option>
          </select>
        </td>
      </tr>`).join('');
  } catch (err) {
    showToast('Failed to load orders: ' + err.message, 'error');
  }
}

async function loadAdminUsers() {
  const tbody = document.getElementById('admin-users-body');
  if (!tbody) return;
  try {
    const data = await apiFetch('/admin/users');
    tbody.innerHTML = data.users.map(u => `
      <tr>
        <td>${u.id}</td>
        <td>${u.full_name}</td>
        <td>${u.email}</td>
        <td><span class="badge bg-${u.role==='admin'?'danger':u.role==='author'?'warning':'primary'}">${u.role}</span></td>
        <td>${formatDate(u.created_at)}</td>
        <td>
          <button class="btn btn-sm btn-outline-danger" onclick="deleteUser(${u.id})">Delete</button>
        </td>
      </tr>`).join('');
  } catch (err) {
    showToast('Failed to load users: ' + err.message, 'error');
  }
}

async function loadAdminGenres() {
  const list = document.getElementById('genres-list');
  if (!list) return;
  try {
    const data = await apiFetch('/genres');
    list.innerHTML = data.genres.map(g => `
      <li class="list-group-item d-flex justify-content-between align-items-center">
        <span id="genre-name-${g.id}">${g.genre_name}</span>
        <div>
          <button class="btn btn-sm btn-outline-primary me-1"
                  onclick="editGenre(${g.id}, '${g.genre_name.replace(/'/g,"\\'")}')">Edit</button>
          <button class="btn btn-sm btn-outline-danger"
                  onclick="deleteGenre(${g.id})">Delete</button>
        </div>
      </li>`).join('');
  } catch (err) {
    showToast('Failed to load genres', 'error');
  }
}

async function loadAdminPayments() {
  const tbody = document.getElementById('admin-payments-body');
  if (!tbody) return;
  try {
    const data = await apiFetch('/admin/payments');
    tbody.innerHTML = data.payments.map(p => `
      <tr>
        <td>#${p.id}</td>
        <td>Order #${p.order_id}</td>
        <td>${p.payment_method}</td>
        <td>${statusBadge(p.payment_status)}</td>
        <td>${formatPrice(p.amount)}</td>
        <td>${formatDate(p.payment_date)}</td>
      </tr>`).join('');
  } catch (err) {
    showToast('Failed to load payments', 'error');
  }
}

async function loadReports() {
  try {
    const data = await apiFetch('/admin/reports');

    // Genre sales table
    const genreBody = document.getElementById('genre-sales-body');
    if (genreBody) {
      genreBody.innerHTML = data.genre_sales.map(r => `
        <tr>
          <td>${r.genre}</td>
          <td>${r.units}</td>
          <td>${formatPrice(r.revenue)}</td>
        </tr>`).join('') || '<tr><td colspan="3" class="text-center text-muted">No data</td></tr>';
    }

    // Top books table
    const booksBody = document.getElementById('top-books-body');
    if (booksBody) {
      booksBody.innerHTML = data.top_books.map((r, i) => `
        <tr>
          <td>${i + 1}</td>
          <td>${r.title}</td>
          <td>${r.units_sold}</td>
        </tr>`).join('') || '<tr><td colspan="3" class="text-center text-muted">No data</td></tr>';
    }
  } catch (err) {
    showToast('Failed to load reports', 'error');
  }
}

// ── Actions ─────────────────────────────────────────────────

async function updateOrderStatus(orderId, status) {
  if (!status) return;
  try {
    await apiFetch(`/orders/${orderId}/status`, { method: 'PUT', body: JSON.stringify({ order_status: status }) });
    showToast('Order status updated');
    loadAdminOrders();
  } catch (err) {
    showToast(err.message || 'Update failed', 'error');
  }
}

function promptUpdateStock(bookId, current) {
  const val = prompt(`Enter new stock quantity for book #${bookId}:`, current);
  if (val === null || isNaN(val)) return;
  apiFetch(`/admin/books/${bookId}/stock`, {
    method: 'PUT',
    body: JSON.stringify({ stock_quantity: parseInt(val) })
  }).then(() => { showToast('Stock updated'); loadAdminBooks(); })
    .catch(err => showToast(err.message, 'error'));
}

async function deleteBook(bookId) {
  if (!confirm(`Delete book #${bookId}? This cannot be undone.`)) return;
  try {
    await apiFetch(`/books/${bookId}`, { method: 'DELETE' });
    showToast('Book deleted');
    loadAdminBooks();
  } catch (err) {
    showToast(err.message || 'Delete failed', 'error');
  }
}

async function deleteUser(userId) {
  if (!confirm(`Delete user #${userId}?`)) return;
  try {
    await apiFetch(`/admin/users/${userId}`, { method: 'DELETE' });
    showToast('User deleted');
    loadAdminUsers();
  } catch (err) {
    showToast(err.message || 'Delete failed', 'error');
  }
}

async function addGenre() {
  const name = document.getElementById('new-genre-name')?.value.trim();
  if (!name) { showToast('Genre name is required', 'error'); return; }
  try {
    await apiFetch('/genres', { method: 'POST', body: JSON.stringify({ genre_name: name }) });
    document.getElementById('new-genre-name').value = '';
    showToast('Genre added');
    loadAdminGenres();
  } catch (err) {
    showToast(err.message || 'Failed to add genre', 'error');
  }
}

async function editGenre(id, currentName) {
  const name = prompt('New genre name:', currentName);
  if (!name || name === currentName) return;
  try {
    await apiFetch(`/genres/${id}`, { method: 'PUT', body: JSON.stringify({ genre_name: name }) });
    showToast('Genre updated');
    loadAdminGenres();
  } catch (err) {
    showToast(err.message || 'Update failed', 'error');
  }
}

async function deleteGenre(id) {
  if (!confirm('Delete this genre?')) return;
  try {
    await apiFetch(`/genres/${id}`, { method: 'DELETE' });
    showToast('Genre deleted');
    loadAdminGenres();
  } catch (err) {
    showToast(err.message || 'Delete failed', 'error');
  }
}

// Add book form (admin)
async function adminAddBook(e) {
  e.preventDefault();
  const form = e.target;
  const payload = {
    title:          form.title.value.trim(),
    description:    form.description.value.trim(),
    isbn:           form.isbn.value.trim(),
    price:          parseFloat(form.price.value),
    stock_quantity: parseInt(form.stock_quantity.value),
    genre_id:       form.genre_id.value || null,
    author_id:      form.author_id.value ? parseInt(form.author_id.value) : null,
    image_url:      form.image_url.value.trim()
  };
  try {
    await apiFetch('/books', { method: 'POST', body: JSON.stringify(payload) });
    showToast('Book added successfully');
    form.reset();
    loadAdminBooks();
    showSection('books');
  } catch (err) {
    showToast(err.message || 'Failed to add book', 'error');
  }
}

async function populateAddBookForm() {
  try {
    const [genresData, authorsData] = await Promise.all([
      apiFetch('/genres'),
      apiFetch('/authors')
    ]);
    const genreSel = document.getElementById('book-genre-select');
    const authorSel = document.getElementById('book-author-select');
    if (genreSel) {
      genreSel.innerHTML = '<option value="">Select Genre</option>' +
        genresData.genres.map(g => `<option value="${g.id}">${g.genre_name}</option>`).join('');
    }
    if (authorSel) {
      authorSel.innerHTML = '<option value="">Select Author</option>' +
        authorsData.authors.map(a => `<option value="${a.id}">${a.author_name}</option>`).join('');
    }
  } catch (_) {}
}
