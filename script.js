/* ═══════════════════════════════════════════════
   PHONG MENLY — MẬT MÃ TỰ DO
   Interactive JS
═══════════════════════════════════════════════ */

// ── Nav scroll effect ──
const nav = document.getElementById('nav');
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 40);
}, { passive: true });

// ── Mobile menu ──
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');
hamburger.addEventListener('click', () => {
  mobileMenu.classList.toggle('open');
  const spans = hamburger.querySelectorAll('span');
  const isOpen = mobileMenu.classList.contains('open');
  spans[0].style.transform = isOpen ? 'translateY(7px) rotate(45deg)' : '';
  spans[1].style.opacity = isOpen ? '0' : '1';
  spans[2].style.transform = isOpen ? 'translateY(-7px) rotate(-45deg)' : '';
});
mobileMenu.querySelectorAll('a').forEach(a => {
  a.addEventListener('click', () => {
    mobileMenu.classList.remove('open');
    hamburger.querySelectorAll('span').forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
  });
});

// ── FAQ accordion ──
document.querySelectorAll('.faq-q').forEach(btn => {
  btn.addEventListener('click', () => {
    const answer = btn.nextElementSibling;
    const icon = btn.querySelector('.faq-icon');
    const isOpen = answer.classList.contains('open');

    // Close all
    document.querySelectorAll('.faq-a').forEach(a => a.classList.remove('open'));
    document.querySelectorAll('.faq-icon').forEach(i => { i.textContent = '+'; i.style.transform = ''; });

    if (!isOpen) {
      answer.classList.add('open');
      icon.textContent = '−';
      icon.style.transform = 'rotate(0deg)';
    }
  });
});

// ── Scroll reveal ──
const reveals = document.querySelectorAll(
  '.pain-card, .door-item, .bonus-card, .testi-card, .price-card, .faq-item'
);
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('reveal');
        setTimeout(() => entry.target.classList.add('visible'), i * 80);
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.08, rootMargin: '0px 0px -40px 0px' }
);
reveals.forEach(el => {
  el.classList.add('reveal');
  observer.observe(el);
});

// ── Lead gen form ──
const previewForm = document.getElementById('previewForm');
if (previewForm) {
  previewForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const email = previewForm.querySelector('input[type=email]').value;
    const btn = previewForm.querySelector('button');
    btn.textContent = '✓ Kiểm tra email của bạn!';
    btn.style.background = '#22c55e';
    btn.style.borderColor = '#22c55e';
    btn.style.color = '#fff';
    btn.disabled = true;
    previewForm.querySelector('input').value = '';
    // TODO: connect to email service (Mailchimp, ConvertKit, etc.)
    console.log('Lead email:', email);
  });
}

// ── Smooth scroll for anchor links ──
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', (e) => {
    const target = document.querySelector(anchor.getAttribute('href'));
    if (target) {
      e.preventDefault();
      const offset = 80;
      const top = target.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top, behavior: 'smooth' });
    }
  });
});

// ── Language toggle (stub) ──
document.querySelectorAll('.lang').forEach(l => {
  l.addEventListener('click', () => {
    document.querySelectorAll('.lang').forEach(x => x.classList.remove('active'));
    l.classList.add('active');
    // TODO: implement i18n switching
  });
});

// ── Typing effect on hero title (optional flair) ──
// Disabled by default — uncomment to enable
/*
const words = ['Tự Do', 'Thành Công', 'Giàu Có'];
let wi = 0;
const goldSpans = document.querySelectorAll('.hero-title .gold');
if (goldSpans.length > 0) {
  const lastGold = goldSpans[goldSpans.length - 1];
  setInterval(() => {
    wi = (wi + 1) % words.length;
    lastGold.textContent = words[wi];
  }, 2500);
}
*/
