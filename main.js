/* ============================================
   ToolBoxHub - Shared JavaScript
   ============================================ */

/* --- Redirect pages.dev → custom domain --- */
if (location.hostname === 'toolboxhub-1tr.pages.dev') {
  location.replace('https://toolboxes.top' + location.pathname + location.search);
}

/* --- Global Filter Function (self-contained) --- */
window.filterTools = function(filter) {
  if (!filter) return;
  // Update active button
  document.querySelectorAll('.filter-button').forEach(function(b) { b.classList.remove('active'); });
  document.querySelectorAll('.filter-button[data-filter="' + filter + '"]').forEach(function(b) { b.classList.add('active'); });
  // Get search query
  var searchEl = document.getElementById('toolSearch');
  var q = searchEl ? searchEl.value.toLowerCase().trim() : '';
  // Filter by category AND search
  document.querySelectorAll('#toolsGrid > [data-category]').forEach(function(card) {
    var matchesCat = filter === 'all' || card.dataset.category === filter;
    var title = (card.querySelector('.stretched-link')?.textContent || '').toLowerCase();
    var matchesSearch = !q || title.indexOf(q) !== -1;
    card.style.display = (matchesCat && matchesSearch) ? '' : 'none';
  });
};

/* --- Bookmark Page --- */
window.bookmarkPage = function() {
  var url = window.location.href;
  var title = document.title;
  // Try native bookmark (IE/Edge legacy)
  if (window.external && typeof window.external.AddFavorite === 'function') {
    window.external.AddFavorite(url, title);
    return;
  }
  // Try Chrome/Edge bookmark API (via sidebar)
  if (window.sidebar && typeof window.sidebar.addPanel === 'function') {
    window.sidebar.addPanel(title, url, '');
    return;
  }
  // Fallback: show toast with keyboard shortcut
  var isMac = navigator.platform.indexOf('Mac') !== -1;
  var shortcut = isMac ? '⌘D' : 'Ctrl+D';
  if (typeof window.showToast === 'function') {
    window.showToast('⭐ Press ' + shortcut + ' to bookmark');
  }
};

document.addEventListener('DOMContentLoaded', function() {

  // --- Theme Toggle ---
  var themeToggle = document.getElementById('themeToggle');
  var html = document.documentElement;
  var savedTheme = localStorage.getItem('theme') || 'light';
  html.setAttribute('data-theme', savedTheme);
  if (themeToggle) {
    themeToggle.innerHTML = savedTheme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    themeToggle.addEventListener('click', function() {
      var current = html.getAttribute('data-theme');
      var next = current === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      this.innerHTML = next === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    });
  }

  // --- Mobile Menu ---
  var menuBtn = document.getElementById('mobileMenuBtn');
  var navLinks = document.getElementById('navLinks');
  if (menuBtn && navLinks) {
    menuBtn.addEventListener('click', function() {
      navLinks.classList.toggle('open');
      var icon = this.querySelector('i');
      if (icon) icon.className = navLinks.classList.contains('open') ? 'fas fa-times' : 'fas fa-bars';
    });
    navLinks.querySelectorAll('a').forEach(function(link) {
      link.addEventListener('click', function() { navLinks.classList.remove('open'); });
    });
  }

  // --- Bookmark ---
  var bookmarkBtn = document.getElementById('bookmarkBtn');
  if (bookmarkBtn) {
    bookmarkBtn.addEventListener('click', window.bookmarkPage);
  }

  // --- Category Filter (redundant with onclick on HTML) ---
  document.querySelectorAll('.filter-button').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      var f = this.getAttribute('data-filter');
      if (f) window.filterTools(f);
    });
  });

  // --- Tool Search ---
  var searchInput = document.getElementById('toolSearch');
  if (searchInput) {
    searchInput.addEventListener('input', function() {
      var activeFilter = document.querySelector('.filter-button.active')?.getAttribute('data-filter') || 'all';
      window.filterTools(activeFilter);
    });
  }

  // --- Copy to Clipboard ---
  window.copyToClipboard = function(text, btn) {
    if (!text) return;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function() {
        showToast('Copied to clipboard!');
        if (btn) {
          var orig = btn.innerHTML;
          btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
          setTimeout(function() { btn.innerHTML = orig; }, 2000);
        }
      }).catch(function() {
        fallbackCopy(text, btn);
      });
    } else {
      fallbackCopy(text, btn);
    }
  };

  function fallbackCopy(text, btn) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand('copy');
      showToast('Copied to clipboard!');
      if (btn) {
        var orig = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
        setTimeout(function() { btn.innerHTML = orig; }, 2000);
      }
    } catch (e) {
      showToast('Failed to copy. Please select and copy manually.');
    }
    document.body.removeChild(ta);
  }

  // --- Toast Notification ---
  function showToast(msg) {
    var toast = document.getElementById('toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'toast';
      toast.className = 'toast';
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.classList.add('show');
    clearTimeout(toast._hide);
    toast._hide = setTimeout(function() { toast.classList.remove('show'); }, 2500);
  }
  window.showToast = showToast;

  // --- Secure Random ID ---
  window.generateId = function() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
  };

  // --- Debounce ---
  window.debounce = function(fn, delay) {
    var timer;
    return function() {
      var ctx = this, args = arguments;
      clearTimeout(timer);
      timer = setTimeout(function() { fn.apply(ctx, args); }, delay);
    };
  };

  // --- Contact Form ---
  var contactForm = document.getElementById('contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
      e.preventDefault();
      var name = document.getElementById('name')?.value || '';
      var email = document.getElementById('email')?.value || '';
      var subject = document.getElementById('subject')?.value || 'General';
      var message = document.getElementById('message')?.value || '';
      var mailtoLink = 'mailto:renhongtao2@Gmail.com?subject=' + encodeURIComponent('[Finance ToolBox] ' + subject + ' - ' + name) + '&body=' + encodeURIComponent('From: ' + name + ' (' + email + ')\n\n' + message);
      window.location.href = mailtoLink;
      showToast('Opening your email client...');
    });
  }
});
