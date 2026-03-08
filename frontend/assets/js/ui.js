export function text(id, value) {
    const el = document.querySelector(id);
    if (el) {
        el.textContent = value;
    }
}
export function html(id, value) {
    const el = document.querySelector(id);
    if (el) {
        el.innerHTML = value;
    }
}
export function toggleDisabled(id, disabled) {
    const button = document.querySelector(id);
    if (button) {
        button.disabled = disabled;
    }
}
export async function parseError(response) {
    try {
        const data = (await response.json());
        if (data.detail) {
            return data.detail;
        }
    }
    catch {
        return `Request failed (${response.status})`;
    }
    return `Request failed (${response.status})`;
}
export function formatDate(value) {
    const dt = new Date(value);
    return Number.isNaN(dt.getTime()) ? value : dt.toLocaleString();
}
export function requireElement(selector) {
    const element = document.querySelector(selector);
    if (!element) {
        throw new Error(`Missing element: ${selector}`);
    }
    return element;
}
export function badge(textValue, kind = "ok") {
    return `<span class="status-badge status-${kind}">${textValue}</span>`;
}
