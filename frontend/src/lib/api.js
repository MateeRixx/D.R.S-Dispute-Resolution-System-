const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const TOKEN_KEY = "drs_token";
const USER_KEY = "drs_user";

const MAX_RETRIES = 3;
const BASE_DELAY = 500;

export function getAuth() {
  try {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function setAuth(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

async function fetchWithRetry(url, options, retries = MAX_RETRIES) {
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const res = await fetch(url, options);
      if (res.status === 401) {
        clearAuth();
        window.location.href = "/";
        throw new Error("Session expired");
      }
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        const msg = Array.isArray(err.detail) ? err.detail.map((d) => d.msg || d.message).join("; ") : err.detail || `Request failed: ${res.statusText}`;
        throw new Error(msg);
      }
      return res;
    } catch (err) {
      if (attempt === retries || err.message === "Session expired") throw err;
      const delay = BASE_DELAY * Math.pow(2, attempt);
      await new Promise((r) => setTimeout(r, delay));
    }
  }
}

async function api(path, options = {}) {
  const token = getToken();
  const headers = { ...options.headers };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetchWithRetry(`${BASE_URL}${path}`, { ...options, headers });
  return res.json();
}

/* Auth */
export async function login(email, role) {
  const data = await api("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, role }),
  });
  setAuth(data.access_token, {
    id: data.user_id,
    role: data.role,
    name: data.full_name,
    merchant_id: data.merchant_id,
  });
  return data;
}

/* Disputes */
export async function fetchDisputes(params = {}) {
  const query = new URLSearchParams();
  if (params.userId) query.set("user_id", params.userId);
  if (params.merchantId) query.set("merchant_id", params.merchantId);
  if (params.status) query.set("status", params.status);
  const qs = query.toString();
  return api(`/portal/disputes${qs ? `?${qs}` : ""}`);
}

export async function fetchDispute(id) {
  return api(`/portal/disputes/${id}`);
}

export async function createDispute(payload) {
  return api("/disputes/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function uploadEvidence(disputeId, file, uploadedBy = "USER") {
  const form = new FormData();
  form.append("dispute_id", disputeId);
  form.append("file", file);
  form.append("uploaded_by", uploadedBy);
  return api("/evidence/upload", { method: "POST", body: form });
}

/* SSE with auto-reconnect */
export function subscribeDisputeSSE(disputeId, onUpdate, onError) {
  let source = null;
  let closed = false;
  let retries = 0;
  const MAX_SSE_RETRIES = 10;

  function connect() {
    if (closed) return;
    const token = getToken();
    const url = `${BASE_URL}/portal/disputes/${disputeId}/events${token ? `?token=${token}` : ""}`;
    source = new EventSource(url);

    source.addEventListener("dispute_update", (e) => {
      retries = 0;
      try {
        onUpdate(JSON.parse(e.data));
      } catch (err) {
        console.error("SSE parse error:", err);
      }
    });

    source.addEventListener("error", () => {
      source?.close();
      if (closed) return;
      retries++;
      if (retries <= MAX_SSE_RETRIES) {
        const delay = Math.min(1000 * Math.pow(2, retries), 30000);
        setTimeout(connect, delay);
      }
      onError?.(new Error(`SSE disconnected, retry ${retries}/${MAX_SSE_RETRIES}`));
    });
  }

  connect();

  return () => {
    closed = true;
    source?.close();
  };
}
