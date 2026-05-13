/* EduLens — Asosiy JavaScript */

// ─── DOM Ready ───────────────────────────────────
document.addEventListener('DOMContentLoaded', function() {
  initNavLinks();
  initModals();
  initAutoHideMessages();
  initMobileMenu();
  initConfirmForms();
});

// ─── Nav links active state ───────────────────────
function initNavLinks() {
  // Active state templateda hardcoded — JS bilan conflict bo'lmasin
  // Faqat joriy URL bilan EXACT mos kelganda qo'shamiz
  // (templateda allaqachon to'g'ri active bor, shuning uchun bu funksiya hozir bo'sh)
}

// ─── Modal open/close ─────────────────────────────
function initModals() {
  // Close on overlay click
  document.querySelectorAll('[id$="-modal"]').forEach(modal => {
    modal.addEventListener('click', function(e) {
      if (e.target === this) this.classList.add('hidden');
    });
  });
  // Close on Escape
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('[id$="-modal"]:not(.hidden)').forEach(m => m.classList.add('hidden'));
    }
  });
}

// ─── Auto-hide Django messages ───────────────────
function initAutoHideMessages() {
  setTimeout(() => {
    document.querySelectorAll('.django-message').forEach(el => {
      el.style.transition = 'opacity 0.5s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 500);
    });
  }, 4500);
}

// ─── Mobile sidebar toggle ────────────────────────
function initMobileMenu() {
  const sidebar = document.querySelector('aside');
  const toggle  = document.getElementById('menu-toggle');
  if (!toggle || !sidebar) return;
  toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
  // Close on outside click
  document.addEventListener('click', function(e) {
    if (!sidebar.contains(e.target) && !toggle.contains(e.target)) {
      sidebar.classList.remove('open');
    }
  });
}

// ─── Confirm forms (delete etc.) ─────────────────
function initConfirmForms() {
  document.querySelectorAll('form[data-confirm]').forEach(form => {
    form.addEventListener('submit', function(e) {
      if (!confirm(this.dataset.confirm)) e.preventDefault();
    });
  });
}

// ─── Toast notification system ───────────────────
function showToast(message, type = 'info', duration = 4000) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'fixed top-20 right-4 z-[100] space-y-2 max-w-sm';
    document.body.appendChild(container);
  }

  const icons = { success: 'check_circle', error: 'error', warning: 'warning', info: 'info' };
  const colors = {
    success: 'bg-green-50 border-green-500 text-green-800',
    error:   'bg-red-50 border-red-500 text-red-800',
    warning: 'bg-yellow-50 border-yellow-500 text-yellow-800',
    info:    'bg-blue-50 border-blue-500 text-blue-800',
  };

  const toast = document.createElement('div');
  toast.className = `flex items-start gap-3 p-4 rounded-xl border-l-4 shadow-lg text-sm font-medium animate-fade-in ${colors[type] || colors.info}`;
  toast.innerHTML = `
    <span class="material-symbols-outlined text-[18px] flex-shrink-0">${icons[type] || 'info'}</span>
    <p class="flex-1">${message}</p>
    <button onclick="this.closest('.toast-item, div').remove()" class="opacity-60 hover:opacity-100">
      <span class="material-symbols-outlined text-[16px]">close</span>
    </button>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = 'opacity 0.4s, transform 0.4s';
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(20px)';
    setTimeout(() => toast.remove(), 400);
  }, duration);
}

// ─── AJAX notification mark read ─────────────────
function markNotificationRead(pk) {
  fetch(`/dashboard/notifications/${pk}/read/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': getCsrfToken() }
  });
}

function getCsrfToken() {
  const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
  return cookie ? cookie.split('=')[1] : '';
}

// ─── Table sort ───────────────────────────────────
function sortTable(table, col, asc) {
  const rows = Array.from(table.querySelectorAll('tbody tr'));
  rows.sort((a, b) => {
    const av = a.cells[col]?.textContent.trim() || '';
    const bv = b.cells[col]?.textContent.trim() || '';
    const an = parseFloat(av), bn = parseFloat(bv);
    if (!isNaN(an) && !isNaN(bn)) return asc ? an - bn : bn - an;
    return asc ? av.localeCompare(bv) : bv.localeCompare(av);
  });
  const tbody = table.querySelector('tbody');
  rows.forEach(r => tbody.appendChild(r));
}

// ─── Grade book: auto-calculate score color ──────
function updateScoreColor(input) {
  const val = parseFloat(input.value);
  input.classList.remove('text-green-600', 'text-yellow-600', 'text-red-600');
  if (!isNaN(val)) {
    if (val >= 80) input.classList.add('text-green-600');
    else if (val >= 60) input.classList.add('text-yellow-600');
    else input.classList.add('text-red-600');
  }
}
document.querySelectorAll('input[name^="score_"]').forEach(inp => {
  inp.addEventListener('input', () => updateScoreColor(inp));
  updateScoreColor(inp);
});

// ─── Word count for textarea ─────────────────────
function initWordCount(textareaId, counterId) {
  const ta = document.getElementById(textareaId);
  const wc = document.getElementById(counterId);
  if (!ta || !wc) return;
  function update() {
    const words = ta.value.trim().split(/\s+/).filter(Boolean).length;
    wc.textContent = `${words} so'z`;
    wc.className = words < 50 ? 'text-xs text-red-400' : words < 100 ? 'text-xs text-yellow-500' : 'text-xs text-green-600';
  }
  ta.addEventListener('input', update);
  update();
}

// ─── File drag and drop ───────────────────────────
function initFileDrop(dropZoneId, inputId) {
  const zone = document.getElementById(dropZoneId);
  const input = document.getElementById(inputId);
  if (!zone || !input) return;

  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('border-[#0058be]', 'bg-blue-50'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('border-[#0058be]', 'bg-blue-50'));
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('border-[#0058be]', 'bg-blue-50');
    const files = e.dataTransfer.files;
    if (files.length) {
      input.files = files;
      const nameEl = document.getElementById(dropZoneId + '-name');
      if (nameEl) nameEl.textContent = files[0].name;
    }
  });
}

// ─── Type selector for create_assignment ─────────
window.toggleTypeFields = function(type) {
  const testFields = document.getElementById('test-fields');
  const fileFields = document.getElementById('file-fields');
  if (testFields) testFields.classList.toggle('hidden', type !== 'test');
  if (fileFields) fileFields.classList.toggle('hidden', type !== 'file');
  document.querySelectorAll('.type-card').forEach(c => {
    c.classList.remove('border-[#00236f]', 'bg-blue-50');
  });
  const selected = document.querySelector(`input[name="assignment_type"][value="${type}"]`);
  if (selected) {
    selected.closest('.type-option')?.querySelector('.type-card')?.classList.add('border-[#00236f]', 'bg-blue-50');
  }
};

// ─── Chart helper (simple bar) ───────────────────
function renderBarChart(canvasId, labels, data, color = '#0058be') {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const max = Math.max(...data, 1);
  const w = canvas.width, h = canvas.height;
  const barW = w / data.length * 0.6;
  const gap = w / data.length;

  ctx.clearRect(0, 0, w, h);
  data.forEach((val, i) => {
    const x = gap * i + gap * 0.2;
    const barH = (val / max) * (h - 30);
    ctx.fillStyle = color;
    ctx.fillRect(x, h - barH - 20, barW, barH);
    ctx.fillStyle = '#6b7280';
    ctx.font = '10px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(labels[i] || '', x + barW/2, h - 5);
    if (val > 0) ctx.fillText(val, x + barW/2, h - barH - 25);
  });
}

// ─── Speech-to-Text (Ko'zi ojiz talabalar uchun) ─
class EduLensTTS {
  constructor() {
    this.synth      = window.speechSynthesis;
    this.recognition = null;
    this.isListening = false;
    this._initRecognition();
  }

  _initRecognition() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) return;
    this.recognition       = new SR();
    this.recognition.lang  = 'uz-UZ';
    this.recognition.continuous     = false;
    this.recognition.interimResults = false;
  }

  speak(text, onEnd) {
    this.synth.cancel();
    const utt = new SpeechSynthesisUtterance(text);
    utt.lang  = 'uz-UZ';
    utt.rate  = 0.88;
    utt.pitch = 1;
    if (onEnd) utt.onend = onEnd;
    this.synth.speak(utt);
  }

  stopSpeaking() { this.synth.cancel(); }

  listen(onResult, onError) {
    if (!this.recognition) {
      if (onError) onError('Brauzeringiz ovoz tanishni qo\'llab-quvvatlamaydi.');
      return;
    }
    this.recognition.onresult = e => {
      const text = e.results[0][0].transcript;
      if (onResult) onResult(text);
    };
    this.recognition.onerror = e => { if (onError) onError(e.error); };
    this.recognition.onend   = () => { this.isListening = false; };
    this.recognition.start();
    this.isListening = true;
  }

  stopListening() {
    if (this.recognition && this.isListening) {
      this.recognition.stop();
      this.isListening = false;
    }
  }
}

window.eduLensTTS = new EduLensTTS();

// ─── Accessible Test Helper ───────────────────────
window.AccessibleTest = {
  currentIdx: 0,
  questions:  [],

  init(questionsJson) {
    this.questions = questionsJson;
    this.speakQuestion(0);
  },

  speakQuestion(idx) {
    const q = this.questions[idx];
    if (!q) return;
    this.currentIdx = idx;
    let text = `${idx + 1}-savol. ${q.text}. `;
    if (q.accessible !== false) {
      q.options.forEach(o => { text += `${o.k}: ${o.t}. `; });
    }
    text += 'Javobingizni aytib bering yoki klaviaturadan A, B, C bosing.';
    window.eduLensTTS.speak(text);
  },

  listenAnswer(questionId, onAnswer) {
    window.eduLensTTS.speak('Javobingizni ayting:');
    setTimeout(() => {
      window.eduLensTTS.listen(text => {
        const upper = text.trim().toUpperCase();
        const letter = upper.includes('A') ? 'A'
                     : upper.includes('B') ? 'B'
                     : upper.includes('C') ? 'C'
                     : upper.includes('D') ? 'D' : null;
        if (letter && onAnswer) onAnswer(letter);
        else window.eduLensTTS.speak('Tushunmadim. Iltimos qaytadan ayting.');
      }, err => {
        window.eduLensTTS.speak(`Xato: ${err}. Klaviatura orqali javob bering.`);
      });
    }, 800);
  },

  next() {
    if (this.currentIdx < this.questions.length - 1) {
      this.speakQuestion(this.currentIdx + 1);
    } else {
      window.eduLensTTS.speak('Test yakunlandi. Yuborish tugmasini bosing.');
    }
  },

  prev() {
    if (this.currentIdx > 0) this.speakQuestion(this.currentIdx - 1);
  },
};
