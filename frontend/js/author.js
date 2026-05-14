/* ============================================================
   author.js – Author dashboard logic
   ============================================================ */

function showAuthorSection(section) {
  document.querySelectorAll('.author-section').forEach(s => s.classList.add('d-none'));
  const el = document.getElementById(`section-${section}`);
  if (el) el.classList.remove('d-none');

  document.querySelectorAll('.sidebar .nav-link').forEach(l => l.classList.remove('active'));
  const link = document.querySelector(`.sidebar [data-section="${section}"]`);
  if (link) link.classList.add('active');

  const loaders = {
    overview: loadAuthorOverview,
    books:    loadAuthorBooks,
    stats:    loadAuthorStats,
    profile:  loadAuthorProfile,
    addbook:  initAddBookForm,
  };
  if (loaders[section]) loaders[section]();
}

async function loadAuthorOverview() {
  try {
    const data = await apiFetch('/authors/me/stats');
    document.getElementById('auth-total-books').textContent    = data.total_books;
    document.getElementById('auth-units-sold').textContent     = data.total_units_sold;
    document.getElementById('auth-total-revenue').textContent  = formatPrice(data.total_revenue);

    const tbody = document.getElementById('author-top-books-body');
    if (tbody) {
      tbody.innerHTML = data.book_stats.slice(0, 5).map(bs => `
        <tr>
          <td>${bs.book.title}</td>
          <td>${bs.book.genre_name || '-'}</td>
          <td>${formatPrice(bs.book.price)}</td>
          <td>${bs.units_sold}</td>
          <td>${formatPrice(bs.revenue)}</td>
        </tr>`).join('') || '<tr><td colspan="5" class="text-muted text-center">No books yet</td></tr>';
    }
  } catch (err) {
    showToast('Failed to load overview: ' + err.message, 'error');
  }
}

async function loadAuthorBooks() {
  const user = getUser();
  if (!user) return;

  try {
    // Find author record via profile endpoint
    const profileData = await apiFetch('/auth/profile');
    const authorProfile = profileData.user.profile;
    if (!authorProfile) { showToast('Author profile not found', 'error'); return; }

    const data = await apiFetch(`/authors/${authorProfile.id}/books`);
    const tbody = document.getElementById('author-books-body');
    if (!tbody) return;

    if (!data.books.length) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No books yet. Add your first book!</td></tr>';
      return;
    }

    tbody.innerHTML = data.books.map(b => `
      <tr>
        <td>${b.id}</td>
        <td>
          <img src="${b.image_url || bookPlaceholder(b.title)}" width="32" height="42"
               style="object-fit:cover;border-radius:3px" class="me-1"
               onerror="this.src='${bookPlaceholder(b.title)}'">
          ${b.title}
        </td>
        <td>${b.genre_name || '-'}</td>
        <td>${formatPrice(b.price)}</td>
        <td>${b.stock_quantity}</td>
        <td><span class="stars">${renderStars(b.rating || 0)}</span> ${b.rating || 0}</td>
        <td>
          <button class="btn btn-sm btn-outline-primary me-1"
                  onclick="showEditBook(${b.id})">Edit</button>
          <button class="btn btn-sm btn-outline-danger"
                  onclick="authorDeleteBook(${b.id})">Delete</button>
        </td>
      </tr>`).join('');
  } catch (err) {
    showToast('Failed to load books: ' + err.message, 'error');
  }
}

async function loadAuthorStats() {
  try {
    const data = await apiFetch('/authors/me/stats');
    const tbody = document.getElementById('author-stats-body');
    if (!tbody) return;

    tbody.innerHTML = data.book_stats.map(bs => `
      <tr>
        <td>${bs.book.title}</td>
        <td>${formatPrice(bs.book.price)}</td>
        <td>${bs.units_sold}</td>
        <td>${formatPrice(bs.revenue)}</td>
        <td><span class="stars">${renderStars(bs.book.rating || 0)}</span> ${bs.book.rating || 0}</td>
      </tr>`).join('') || '<tr><td colspan="5" class="text-center text-muted">No sales data</td></tr>';

    const totalRevEl = document.getElementById('stats-total-revenue');
    if (totalRevEl) totalRevEl.textContent = formatPrice(data.total_revenue);
  } catch (err) {
    showToast('Failed to load stats: ' + err.message, 'error');
  }
}

async function loadAuthorProfile() {
  try {
    const data = await apiFetch('/auth/profile');
    const u = data.user;
    const nameEl = document.getElementById('profile-full-name');
    const emailEl = document.getElementById('profile-email');
    const bioEl = document.getElementById('profile-bio');

    if (nameEl) nameEl.value = u.full_name;
    if (emailEl) emailEl.value = u.email;
    if (bioEl && u.profile) bioEl.value = u.profile.biography || '';
  } catch (err) {
    showToast('Failed to load profile', 'error');
  }
}

async function saveAuthorProfile(e) {
  e.preventDefault();
  const payload = {
    full_name: document.getElementById('profile-full-name')?.value.trim(),
    biography: document.getElementById('profile-bio')?.value.trim()
  };
  try {
    await apiFetch('/auth/profile', { method: 'PUT', body: JSON.stringify(payload) });
    showToast('Profile saved');
    // Update stored user name
    const user = getUser();
    if (user && payload.full_name) { user.full_name = payload.full_name; localStorage.setItem('user', JSON.stringify(user)); }
  } catch (err) {
    showToast(err.message || 'Save failed', 'error');
  }
}

async function initAddBookForm() {
  try {
    const data = await apiFetch('/genres');
    const sel = document.getElementById('author-book-genre');
    if (sel) {
      sel.innerHTML = '<option value="">Select Genre (optional)</option>' +
        data.genres.map(g => `<option value="${g.id}">${g.genre_name}</option>`).join('');
    }
  } catch (_) {}

  const form = document.getElementById('add-book-form');
  if (form) {
    form.onsubmit = async (e) => {
      e.preventDefault();
      const payload = {
        title:          form.title.value.trim(),
        description:    form.description.value.trim(),
        isbn:           form.isbn.value.trim() || null,
        price:          parseFloat(form.price.value),
        stock_quantity: parseInt(form.stock_quantity.value) || 0,
        genre_id:       form.genre_id.value ? parseInt(form.genre_id.value) : null,
        image_url:      form.image_url.value.trim() || null
      };
      try {
        await apiFetch('/books', { method: 'POST', body: JSON.stringify(payload) });
        showToast('Book added successfully!');
        form.reset();
        showAuthorSection('books');
      } catch (err) {
        showToast(err.message || 'Failed to add book', 'error');
      }
    };
  }
}

async function showEditBook(bookId) {
  try {
    const data = await apiFetch(`/books/${bookId}`);
    const b = data.book;

    document.getElementById('edit-book-id').value          = b.id;
    document.getElementById('edit-book-title').value       = b.title;
    document.getElementById('edit-book-description').value = b.description || '';
    document.getElementById('edit-book-isbn').value        = b.isbn || '';
    document.getElementById('edit-book-price').value       = b.price;
    document.getElementById('edit-book-stock').value       = b.stock_quantity;
    document.getElementById('edit-book-image').value       = b.image_url || '';

    const genreSel = document.getElementById('edit-book-genre');
    if (genreSel) {
      const genres = await apiFetch('/genres');
      genreSel.innerHTML = '<option value="">No Genre</option>' +
        genres.genres.map(g => `<option value="${g.id}" ${g.id === b.genre_id ? 'selected' : ''}>${g.genre_name}</option>`).join('');
    }

    const modal = new bootstrap.Modal(document.getElementById('editBookModal'));
    modal.show();
  } catch (err) {
    showToast('Failed to load book: ' + err.message, 'error');
  }
}

async function saveEditBook(e) {
  e.preventDefault();
  const id = document.getElementById('edit-book-id').value;
  const payload = {
    title:          document.getElementById('edit-book-title').value.trim(),
    description:    document.getElementById('edit-book-description').value.trim(),
    isbn:           document.getElementById('edit-book-isbn').value.trim() || null,
    price:          parseFloat(document.getElementById('edit-book-price').value),
    stock_quantity: parseInt(document.getElementById('edit-book-stock').value),
    image_url:      document.getElementById('edit-book-image').value.trim() || null,
    genre_id:       document.getElementById('edit-book-genre')?.value || null
  };
  try {
    await apiFetch(`/books/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
    showToast('Book updated');
    bootstrap.Modal.getInstance(document.getElementById('editBookModal'))?.hide();
    loadAuthorBooks();
  } catch (err) {
    showToast(err.message || 'Update failed', 'error');
  }
}

async function authorDeleteBook(bookId) {
  if (!confirm(`Delete book #${bookId}? This cannot be undone.`)) return;
  try {
    await apiFetch(`/books/${bookId}`, { method: 'DELETE' });
    showToast('Book deleted');
    loadAuthorBooks();
  } catch (err) {
    showToast(err.message || 'Delete failed', 'error');
  }
}
