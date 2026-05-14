/* ============================================================
   auth.js – JWT token helpers & auth state management
   ============================================================ */

const API_BASE = 'http://localhost:5000/api';

function getToken()  { return localStorage.getItem('token'); }
function getUser()   { const u = localStorage.getItem('user'); return u ? JSON.parse(u) : null; }

function setSession(token, user) {
  localStorage.setItem('token', token);
  localStorage.setItem('user', JSON.stringify(user));
}

function clearSession() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
}

function logout() {
  clearSession();
  window.location.href = 'login.html';
}

function getHeaders(json = true) {
  const h = {};
  if (json) h['Content-Type'] = 'application/json';
  const t = getToken();
  if (t) h['Authorization'] = `Bearer ${t}`;
  return h;
}

async function apiFetch(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: getHeaders(),
    ...options
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw { status: res.status, message: data.error || 'Request failed', data };
  return data;
}

function requireAuth(redirectTo = 'login.html') {
  if (!getToken()) { window.location.href = redirectTo; return false; }
  return true;
}

function requireRole(role, redirectTo = 'index.html') {
  const user = getUser();
  if (!user || user.role !== role) { window.location.href = redirectTo; return false; }
  return true;
}

function requireAnyRole(roles, redirectTo = 'index.html') {
  const user = getUser();
  if (!user || !roles.includes(user.role)) { window.location.href = redirectTo; return false; }
  return true;
}

// Update navbar based on auth state
function updateNavbar() {
  const user = getUser();
  const guestLinks = document.getElementById('guest-links');
  const userLinks  = document.getElementById('user-links');
  const userLabel  = document.getElementById('user-label');

  if (user) {
    if (guestLinks) guestLinks.classList.add('d-none');
    if (userLinks)  userLinks.classList.remove('d-none');
    if (userLabel)  userLabel.textContent = user.full_name;

    // Show role-specific nav items
    document.querySelectorAll('[data-role]').forEach(el => {
      const allowed = el.dataset.role.split(',');
      el.classList.toggle('d-none', !allowed.includes(user.role));
    });
  } else {
    if (guestLinks) guestLinks.classList.remove('d-none');
    if (userLinks)  userLinks.classList.add('d-none');
  }
}

// Login form handler
function setupLoginForm() {
  const form = document.getElementById('login-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email    = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const errEl    = document.getElementById('login-error');

    try {
      const data = await apiFetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
      });
      setSession(data.token, data.user);

      // Redirect based on role
      if (data.user.role === 'admin')    window.location.href = 'admin-dashboard.html';
      else if (data.user.role === 'author') window.location.href = 'author-dashboard.html';
      else window.location.href = 'index.html';
    } catch (err) {
      if (errEl) errEl.textContent = err.message;
    }
  });
}

// Register form handler
function setupRegisterForm() {
  const form = document.getElementById('register-form');
  if (!form) return;

  const roleSelect = document.getElementById('role');
  const extraFields = document.getElementById('extra-fields');

  if (roleSelect && extraFields) {
    roleSelect.addEventListener('change', () => {
      extraFields.innerHTML = buildExtraFields(roleSelect.value);
    });
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const errEl = document.getElementById('register-error');

    const payload = {
      full_name: document.getElementById('full_name').value.trim(),
      email:     document.getElementById('email').value.trim(),
      password:  document.getElementById('password').value,
      role:      document.getElementById('role').value,
    };

    if (payload.role === 'customer') {
      payload.address = document.getElementById('address')?.value || '';
      payload.phone   = document.getElementById('phone')?.value   || '';
    } else if (payload.role === 'author') {
      payload.biography = document.getElementById('biography')?.value || '';
    }

    const confirmPw = document.getElementById('confirm_password').value;
    if (payload.password !== confirmPw) {
      if (errEl) errEl.textContent = 'Passwords do not match.';
      return;
    }

    try {
      const data = await apiFetch('/auth/register', { method: 'POST', body: JSON.stringify(payload) });
      setSession(data.token, data.user);
      if (data.user.role === 'admin')    window.location.href = 'admin-dashboard.html';
      else if (data.user.role === 'author') window.location.href = 'author-dashboard.html';
      else window.location.href = 'index.html';
    } catch (err) {
      if (errEl) errEl.textContent = err.message;
    }
  });
}

function buildExtraFields(role) {
  if (role === 'customer') {
    return `
      <div class="mb-3">
        <label class="form-label">Address</label>
        <input type="text" id="address" class="form-control" placeholder="Your address">
      </div>
      <div class="mb-3">
        <label class="form-label">Phone</label>
        <input type="text" id="phone" class="form-control" placeholder="Phone number">
      </div>`;
  }
  if (role === 'author') {
    return `
      <div class="mb-3">
        <label class="form-label">Biography</label>
        <textarea id="biography" class="form-control" rows="3" placeholder="Tell us about yourself..."></textarea>
      </div>`;
  }
  return '';
}
