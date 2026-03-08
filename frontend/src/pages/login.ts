import { consumeReturnPath, isAuthenticated, setTokens } from "../auth.js";
import { ROUTES } from "../config.js";
import { login, register } from "../api.js";
import { requireElement, text, toggleDisabled } from "../ui.js";

function validatePassword(password: string): string {
  if (password.length < 8) {
    return "Password must be at least 8 characters.";
  }
  return "";
}

async function onLogin(event: SubmitEvent): Promise<void> {
  event.preventDefault();
  const username = requireElement<HTMLInputElement>("#loginUsername").value.trim();
  const password = requireElement<HTMLInputElement>("#loginPassword").value;

  toggleDisabled("#loginBtn", true);
  text("#loginError", "");

  try {
    const tokens = await login(username, password);
    setTokens(tokens);
    window.location.href = consumeReturnPath();
  } catch (error) {
    const message = error instanceof Error ? error.message : "Login failed";
    text("#loginError", message);
  } finally {
    toggleDisabled("#loginBtn", false);
  }
}

async function onRegister(event: SubmitEvent): Promise<void> {
  event.preventDefault();

  const username = requireElement<HTMLInputElement>("#registerUsername").value.trim();
  const email = requireElement<HTMLInputElement>("#registerEmail").value.trim();
  const password = requireElement<HTMLInputElement>("#registerPassword").value;

  const passwordError = validatePassword(password);
  if (passwordError) {
    text("#registerError", passwordError);
    return;
  }

  toggleDisabled("#registerBtn", true);
  text("#registerError", "");
  text("#registerSuccess", "");

  try {
    await register(username, email, password);
    text("#registerSuccess", "Registration successful. You can now log in.");
    requireElement<HTMLFormElement>("#registerForm").reset();
  } catch (error) {
    const message = error instanceof Error ? error.message : "Registration failed";
    text("#registerError", message);
  } finally {
    toggleDisabled("#registerBtn", false);
  }
}

function bindTabs(): void {
  const loginTab = requireElement<HTMLButtonElement>("#tabLogin");
  const registerTab = requireElement<HTMLButtonElement>("#tabRegister");
  const loginPanel = requireElement<HTMLElement>("#panelLogin");
  const registerPanel = requireElement<HTMLElement>("#panelRegister");

  loginTab.addEventListener("click", () => {
    loginPanel.hidden = false;
    registerPanel.hidden = true;
    loginTab.classList.add("active");
    registerTab.classList.remove("active");
  });

  registerTab.addEventListener("click", () => {
    loginPanel.hidden = true;
    registerPanel.hidden = false;
    registerTab.classList.add("active");
    loginTab.classList.remove("active");
  });
}

function init(): void {
  if (isAuthenticated()) {
    window.location.href = ROUTES.dashboard;
    return;
  }
  bindTabs();
  requireElement<HTMLFormElement>("#loginForm").addEventListener("submit", (event) => {
    void onLogin(event as SubmitEvent);
  });
  requireElement<HTMLFormElement>("#registerForm").addEventListener("submit", (event) => {
    void onRegister(event as SubmitEvent);
  });
}

init();
