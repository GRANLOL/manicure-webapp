const toastStack = document.getElementById('toast-stack');

function createToast({ title, message, variant = 'neutral' }) {
    const toast = document.createElement('div');
    toast.className = `toast toast--${variant}`;

    const titleEl = document.createElement('div');
    titleEl.className = 'toast-title';
    titleEl.textContent = title;

    const messageEl = document.createElement('div');
    messageEl.textContent = message;

    toast.append(titleEl, messageEl);
    return toast;
}

export function showToast({ title, message, variant = 'neutral', duration = 2200 }) {
    if (!toastStack) {
        return;
    }

    const toast = createToast({ title, message, variant });
    toastStack.appendChild(toast);

    requestAnimationFrame(() => {
        toast.classList.add('show');
    });

    window.setTimeout(() => {
        toast.classList.remove('show');
        window.setTimeout(() => {
            toast.remove();
        }, 280);
    }, duration);
}
