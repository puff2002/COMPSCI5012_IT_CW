const API_BASE = process.env.API_BASE ?? "http://127.0.0.1:8000/api";
const USERNAME = process.env.SMOKE_USER ?? "smoke_user";
const EMAIL = process.env.SMOKE_EMAIL ?? "smoke_user@example.com";
const PASSWORD = process.env.SMOKE_PASSWORD ?? "Passw0rd!";

async function call(path, init = {}, token) {
  const isFormData = init.body instanceof FormData;
  const headers = {
    ...(init.body && !isFormData ? { "Content-Type": "application/json" } : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(init.headers ?? {})
  };
  const response = await fetch(`${API_BASE}${path}`, { ...init, headers });
  const text = await response.text();
  let maybeJson = null;
  if (text) {
    try {
      maybeJson = JSON.parse(text);
    } catch {
      maybeJson = text;
    }
  }
  return { status: response.status, data: maybeJson };
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

async function ensureUser() {
  const register = await call("/auth/user/register/", {
    method: "POST",
    body: JSON.stringify({ username: USERNAME, email: EMAIL, password: PASSWORD })
  });
  if (register.status !== 201 && register.status !== 400) {
    throw new Error(`register failed with ${register.status}`);
  }
}

async function run() {
  await ensureUser();

  const login = await call("/auth/user/login/", {
    method: "POST",
    body: JSON.stringify({ username: USERNAME, password: PASSWORD })
  });
  assert(login.status === 200, `login failed: ${login.status}`);
  const access = login.data.access;
  const refresh = login.data.refresh;

  const me = await call("/auth/me/", {}, access);
  assert(me.status === 200, `me failed: ${me.status}`);

  const created = await call("/wardrobe/items/", {
    method: "POST",
    body: (() => {
      const form = new FormData();
      form.append("category", "top");
      form.append("item", "Smoke T-Shirt");
      form.append("style_semantics", JSON.stringify(["casual"]));
      form.append("season_semantics", JSON.stringify(["spring"]));
      form.append("usage_semantics", JSON.stringify(["daily"]));
      form.append("color_semantics", "white");
      form.append("description", "smoke test item");
      return form;
    })()
  }, access);
  assert(created.status === 201, `create item failed: ${created.status} ${JSON.stringify(created.data)}`);

  const list = await call("/wardrobe/items/", {}, access);
  assert(list.status === 200, `list items failed: ${list.status}`);

  const history = await call("/outfits/history/", {}, access);
  assert(history.status === 200, `history list failed: ${history.status}`);

  const refreshRes = await call("/auth/refresh/", {
    method: "POST",
    body: JSON.stringify({ refresh })
  });
  assert(refreshRes.status === 200, `refresh failed: ${refreshRes.status}`);
  const refreshForLogout = refreshRes.data?.refresh ?? refresh;

  const logout = await call("/auth/logout/", {
    method: "POST",
    body: JSON.stringify({ refresh: refreshForLogout })
  }, access);
  assert(logout.status === 204, `logout failed: ${logout.status}`);

  console.log("Smoke test passed.");
}

run().catch((error) => {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`Smoke test failed: ${message}`);
  process.exitCode = 1;
});
