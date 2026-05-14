/* ============================================================
   books.js – Book catalog page logic
   ============================================================ */

let currentPage = 1;
let totalPages  = 1;
let activeFilters = { search: '', genre_id: '', min_price: '', max_price: '' };

async function loadGenres() {
  try {
    const data = await apiFetch('/genres');
    const sel  = document.getElementById('genre-filter');
    if (!sel) return;
    data.genres.forEach(g => {
      const opt = document.createElement('option');
      opt.value = g.id;
      opt.textContent = g.genre_name;
      sel.appendChild(opt);
    });
  } catch (_) {}
}

async function loadBooks(page = 1) {
  const grid = document.getElementById('books-grid');
  const pag  = document.getElementById('pagination');
  if (!grid) return;

  showSpinner();
  const params = new URLSearchParams({ page, per_page: 12 });
  if (activeFilters.search)    params.set('search',    activeFilters.search);
  if (activeFilters.genre_id)  params.set('genre_id',  activeFilters.genre_id);
  if (activeFilters.min_price) params.set('min_price', activeFilters.min_price);
  if (activeFilters.max_price) params.set('max_price', activeFilters.max_price);

  try {
    const data = await apiFetch(`/books?${params}`);
    totalPages  = data.pages || 1;
    currentPage = data.current_page || 1;

    if (!data.books.length) {
      grid.innerHTML = `<div class="col-12"><div class="empty-state"><i class="bi bi-book"></i><p>No books found.</p></div></div>`;
    } else {
      grid.innerHTML = data.books.map(buildBookCard).join('');
    }

    renderPagination(pag, currentPage, totalPages);
    document.getElementById('result-count').textContent = `${data.total} book${data.total !== 1 ? 's' : ''} found`;
  } catch (err) {
    grid.innerHTML = `<div class="col-12 text-center text-danger">Failed to load books: ${err.message}</div>`;
  } finally {
    hideSpinner();
  }
}

function renderPagination(container, current, total) {
  if (!container || total <= 1) { if (container) container.innerHTML = ''; return; }
  let html = '<nav><ul class="pagination justify-content-center flex-wrap">';

  html += `<li class="page-item ${current <= 1 ? 'disabled' : ''}">
    <a class="page-link" href="#" onclick="changePage(${current - 1})">‹</a></li>`;

  for (let i = 1; i <= total; i++) {
    if (total > 7 && i > 3 && i < total - 2 && Math.abs(i - current) > 2) {
      if (i === 4) html += '<li class="page-item disabled"><span class="page-link">…</span></li>';
      continue;
    }
    html += `<li class="page-item ${i === current ? 'active' : ''}">
      <a class="page-link" href="#" onclick="changePage(${i})">${i}</a></li>`;
  }

  html += `<li class="page-item ${current >= total ? 'disabled' : ''}">
    <a class="page-link" href="#" onclick="changePage(${current + 1})">›</a></li>`;
  html += '</ul></nav>';
  container.innerHTML = html;
}

function changePage(page) {
  event.preventDefault();
  if (page < 1 || page > totalPages) return;
  currentPage = page;
  loadBooks(page);
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function setupFilters() {
  const searchInput = document.getElementById('search-input');
  const searchBtn   = document.getElementById('search-btn');
  const genreFilter = document.getElementById('genre-filter');
  const minPrice    = document.getElementById('min-price');
  const maxPrice    = document.getElementById('max-price');
  const clearBtn    = document.getElementById('clear-filters');

  function applyFilters() {
    activeFilters.search    = searchInput?.value.trim() || '';
    activeFilters.genre_id  = genreFilter?.value || '';
    activeFilters.min_price = minPrice?.value || '';
    activeFilters.max_price = maxPrice?.value || '';
    currentPage = 1;
    loadBooks(1);
  }

  if (searchBtn) searchBtn.addEventListener('click', applyFilters);
  if (searchInput) searchInput.addEventListener('keypress', e => e.key === 'Enter' && applyFilters());
  if (genreFilter) genreFilter.addEventListener('change', applyFilters);

  if (clearBtn) clearBtn.addEventListener('click', () => {
    if (searchInput) searchInput.value = '';
    if (genreFilter) genreFilter.value = '';
    if (minPrice) minPrice.value = '';
    if (maxPrice) maxPrice.value = '';
    activeFilters = { search: '', genre_id: '', min_price: '', max_price: '' };
    loadBooks(1);
  });
}

// Init books page
async function initBooksPage() {
  await loadGenres();
  setupFilters();

  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('search')) {
    const si = document.getElementById('search-input');
    if (si) si.value = urlParams.get('search');
    activeFilters.search = urlParams.get('search');
  }
  if (urlParams.get('genre_id')) {
    const gf = document.getElementById('genre-filter');
    if (gf) gf.value = urlParams.get('genre_id');
    activeFilters.genre_id = urlParams.get('genre_id');
  }

  await loadBooks(1);
}

// Book detail page
async function initBookDetail() {
  const id = new URLSearchParams(window.location.search).get('id');
  if (!id) { window.location.href = 'books.html'; return; }

  showSpinner();
  try {
    const data = await apiFetch(`/books/${id}`);
    const book = data.book;
    renderBookDetail(book);
  } catch (err) {
    document.getElementById('book-detail').innerHTML = `<p class="text-danger">Book not found.</p>`;
  } finally {
    hideSpinner();
  }
}

function renderBookDetail(book) {
  const container = document.getElementById('book-detail');
  if (!container) return;
  const img   = book.image_url || bookPlaceholder(book.title);
  const stars = renderStars(book.rating || 0);
  const inStock = book.stock_quantity > 0;

  container.innerHTML = `
    <div class="row g-4">
      <div class="col-md-4 text-center">
        <img src="${img}" alt="${book.title}" class="img-fluid rounded shadow" style="max-height:380px"
             onerror="this.src='${bookPlaceholder(book.title)}'">
      </div>
      <div class="col-md-8">
        <h2 class="fw-bold">${book.title}</h2>
        <p class="text-muted mb-1"><i class="bi bi-person"></i> ${book.author_name || 'Unknown Author'}</p>
        <p class="text-muted mb-2"><i class="bi bi-tag"></i> ${book.genre_name || 'Uncategorized'}</p>
        <div class="stars mb-3" style="font-size:1.2rem">${stars} <span class="text-muted fs-6">${book.rating || 0}/5</span></div>
        <h3 class="text-danger fw-bold mb-3">${formatPrice(book.price)}</h3>
        <p class="mb-3">${book.description || 'No description available.'}</p>
        <p class="mb-1"><strong>ISBN:</strong> ${book.isbn || '-'}</p>
        <p class="mb-3"><strong>Stock:</strong>
          ${inStock ? `<span class="text-success">${book.stock_quantity} available</span>` : '<span class="text-danger">Out of stock</span>'}
        </p>
        ${inStock
          ? `<button class="btn btn-danger btn-lg me-2" onclick="addToCart(${book.id}, event)">
               <i class="bi bi-cart-plus"></i> Add to Cart
             </button>`
          : `<button class="btn btn-secondary btn-lg" disabled>Out of Stock</button>`}
        <a href="books.html" class="btn btn-outline-secondary btn-lg">← Back to Catalog</a>
      </div>
    </div>`;
}
