/**
 * RaktSetu / RaktAnsh Client Suite
 * High-performance UI interactions, theme toggle, toast alerts, geo-helper, live sync.
 */

// Initialize Theme
(function initTheme() {
  const savedTheme = localStorage.getItem('raktsetu_theme');
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
})();

function toggleDarkMode() {
  const isDark = document.documentElement.classList.toggle('dark');
  localStorage.setItem('raktsetu_theme', isDark ? 'dark' : 'light');
  window.dispatchEvent(new CustomEvent('theme-changed', { detail: { isDark } }));
}

// Toast Notifications System
function showToast(message, type = 'info', title = '') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toastId = 'toast-' + Date.now();
  const bgColors = {
    success: 'bg-emerald-500 text-white',
    error: 'bg-rose-500 text-white',
    warning: 'bg-amber-500 text-white',
    info: 'bg-slate-900 text-white dark:bg-slate-800'
  };

  const icons = {
    success: '<i data-lucide="check-circle" class="w-5 h-5 flex-shrink-0"></i>',
    error: '<i data-lucide="alert-octagon" class="w-5 h-5 flex-shrink-0"></i>',
    warning: '<i data-lucide="alert-triangle" class="w-5 h-5 flex-shrink-0"></i>',
    info: '<i data-lucide="info" class="w-5 h-5 flex-shrink-0"></i>'
  };

  const toast = document.createElement('div');
  toast.id = toastId;
  toast.className = `flex items-center gap-3 px-4 py-3 rounded-xl shadow-xl transition-all duration-300 transform translate-y-2 opacity-0 text-sm font-medium ${bgColors[type] || bgColors.info}`;
  toast.innerHTML = `
    ${icons[type] || icons.info}
    <div class="flex-1 pr-2">
      ${title ? `<p class="font-bold text-xs uppercase tracking-wider mb-0.5">${title}</p>` : ''}
      <p class="leading-tight">${message}</p>
    </div>
    <button onclick="dismissToast('${toastId}')" class="opacity-70 hover:opacity-100 transition-opacity">
      <i data-lucide="x" class="w-4 h-4"></i>
    </button>
  `;

  container.appendChild(toast);
  if (window.lucide) window.lucide.createIcons({ scope: toast });

  // Animate in
  requestAnimationFrame(() => {
    toast.classList.remove('translate-y-2', 'opacity-0');
    toast.classList.add('translate-y-0', 'opacity-100');
  });

  // Auto dismiss
  setTimeout(() => {
    dismissToast(toastId);
  }, 4500);
}

function dismissToast(id) {
  const toast = document.getElementById(id);
  if (!toast) return;
  toast.classList.remove('opacity-100', 'translate-y-0');
  toast.classList.add('opacity-0', 'translate-y-2');
  setTimeout(() => toast.remove(), 300);
}

// Geolocation helper
function getUserLocation(callback, errorCallback) {
  if (!navigator.geolocation) {
    if (errorCallback) errorCallback("Geolocation not supported by your browser");
    return;
  }
  navigator.geolocation.getCurrentPosition(
    (position) => {
      callback({
        lat: position.coords.latitude,
        lng: position.coords.longitude
      });
    },
    (err) => {
      console.warn("Geolocation warning:", err.message);
      if (errorCallback) errorCallback(err.message);
    },
    { enableHighAccuracy: true, timeout: 8000 }
  );
}

// Animated Number Counter
function animateCounters() {
  const counters = document.querySelectorAll('[data-counter]');
  counters.forEach(counter => {
    const target = +counter.getAttribute('data-counter');
    const duration = 1200; // ms
    const stepTime = 20;
    const steps = duration / stepTime;
    const increment = target / steps;
    let current = 0;

    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        counter.textContent = target.toLocaleString();
        clearInterval(timer);
      } else {
        counter.textContent = Math.ceil(current).toLocaleString();
      }
    }, stepTime);
  });
}

// Confetti Celebration
function triggerConfetti() {
  if (typeof confetti === 'function') {
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 },
      colors: ['#E11D48', '#14B8A6', '#F59E0B', '#2563EB']
    });
  }
}

// Document Ready Initialization
document.addEventListener('DOMContentLoaded', () => {
  if (window.lucide) {
    window.lucide.createIcons();
  }
  animateCounters();
});
