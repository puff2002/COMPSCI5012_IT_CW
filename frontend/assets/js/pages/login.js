import { consumeReturnPath, isAuthenticated, setTokens } from "../auth.js";
import { ROUTES } from "../config.js";
import { login, register } from "../api.js";
import { requireElement, text, toggleDisabled } from "../ui.js";
function validatePassword(password) {
    if (password.length < 8) {
        return "Password must be at least 8 characters.";
    }
    return "";
}
async function onLogin(event) {
    event.preventDefault();
    const username = requireElement("#loginUsername").value.trim();
    const password = requireElement("#loginPassword").value;
    toggleDisabled("#loginBtn", true);
    text("#loginError", "");
    try {
        const tokens = await login(username, password);
        setTokens(tokens);
        window.location.href = consumeReturnPath();
    }
    catch (error) {
        const message = error instanceof Error ? error.message : "Login failed";
        text("#loginError", message);
    }
    finally {
        toggleDisabled("#loginBtn", false);
    }
}
async function onRegister(event) {
    event.preventDefault();
    const username = requireElement("#registerUsername").value.trim();
    const email = requireElement("#registerEmail").value.trim();
    const password = requireElement("#registerPassword").value;
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
        requireElement("#registerForm").reset();
    }
    catch (error) {
        const message = error instanceof Error ? error.message : "Registration failed";
        text("#registerError", message);
    }
    finally {
        toggleDisabled("#registerBtn", false);
    }
}
function bindTabs() {
    const loginTab = requireElement("#tabLogin");
    const registerTab = requireElement("#tabRegister");
    const loginPanel = requireElement("#panelLogin");
    const registerPanel = requireElement("#panelRegister");
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
function init() {
    if (isAuthenticated()) {
        window.location.href = ROUTES.dashboard;
        return;
    }
    bindTabs();
    requireElement("#loginForm").addEventListener("submit", (event) => {
        void onLogin(event);
    });
    requireElement("#registerForm").addEventListener("submit", (event) => {
        void onRegister(event);
    });
}
init();
