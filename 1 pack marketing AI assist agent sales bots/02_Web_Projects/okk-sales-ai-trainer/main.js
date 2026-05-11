// ============================================================
// JARVIS — Main JS
// ============================================================

// Theme toggle
(function () {
  const toggle = document.querySelector('[data-theme-toggle]');
  const root = document.documentElement;
  let theme = 'dark'; // default dark
  root.setAttribute('data-theme', theme);

  if (toggle) {
    toggle.addEventListener('click', () => {
      theme = theme === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', theme);
      toggle.setAttribute('aria-label', 'Переключить тему');
      toggle.innerHTML = theme === 'dark'
        ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`
        : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>`;
    });
  }
})();

// Sticky header scroll effect
(function () {
  const header = document.getElementById('header');
  if (!header) return;
  window.addEventListener('scroll', () => {
    if (window.scrollY > 20) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  }, { passive: true });
})();

// Mobile burger menu
(function () {
  const burger = document.getElementById('burger');
  const nav = document.querySelector('.nav');
  if (!burger || !nav) return;

  burger.addEventListener('click', () => {
    const isOpen = nav.style.display === 'flex';
    nav.style.display = isOpen ? '' : 'flex';
    nav.style.flexDirection = 'column';
    nav.style.position = 'absolute';
    nav.style.top = '64px';
    nav.style.left = '0';
    nav.style.right = '0';
    nav.style.background = 'var(--color-surface)';
    nav.style.padding = '1rem 2rem';
    nav.style.borderBottom = '1px solid var(--color-divider)';
    nav.style.zIndex = '99';
    if (isOpen) nav.removeAttribute('style');
  });
})();

// Scroll-triggered fade-up animations
(function () {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.step, .feature-card, .metric-card, .audience-card, .testimonial-card, .blog-card, .pricing-card, .pillar').forEach(el => {
    el.classList.add('fade-up');
    observer.observe(el);
  });
})();

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', (e) => {
    const target = document.querySelector(link.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// FAQ: close others when one opens
document.querySelectorAll('.faq-item').forEach(item => {
  item.addEventListener('toggle', () => {
    if (item.open) {
      document.querySelectorAll('.faq-item[open]').forEach(other => {
        if (other !== item) other.removeAttribute('open');
      });
    }
  });
});
