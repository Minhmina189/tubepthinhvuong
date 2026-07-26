// ============================================================
// THỊNH VƯỢNG - Tủ Bếp Inox Cao Cấp
// Script chính - Tất cả tính năng tương tác
// ============================================================

// ── IndexedDB helpers (đồng bộ với admin.html) ──
const _IDB = { name: 'thinhvuong_db', version: 1, store: 'cms' };
function _openDB() {
  return new Promise((res, rej) => {
    const r = indexedDB.open(_IDB.name, _IDB.version);
    r.onupgradeneeded = e => e.target.result.createObjectStore(_IDB.store);
    r.onsuccess = e => res(e.target.result);
    r.onerror = e => rej(e.target.error);
  });
}
function _idbGet(db, k) {
  return new Promise((res, rej) => {
    const r = db.transaction(_IDB.store, 'readonly').objectStore(_IDB.store).get(k);
    r.onsuccess = e => res(e.target.result ?? null);
    r.onerror = e => rej(e.target.error);
  });
}

// ── CMS Loader: áp dụng dữ liệu từ admin.html lên trang ──
(async function applyCMSData() {
  try {
    const db = await _openDB();
    let d = await _idbGet(db, 'data');
    if (!d) {
      const raw = localStorage.getItem('thinhvuong_cms');
      if (!raw) return;
      d = JSON.parse(raw);
    }

    function applyBg(el, src) {
      if (!el || !src) return;
      el.style.backgroundImage = 'url(' + src + ')';
      el.style.backgroundSize = 'cover';
      el.style.backgroundPosition = 'center';
    }

    // Benefits image
    if (d.benefits && d.benefits.image) {
      var bImg = document.getElementById('benefits-custom-img');
      var bHtml = document.getElementById('benefits-html-wrap');
      var bSec = document.getElementById('benefits');
      if (bImg) { bImg.src = d.benefits.image; bImg.style.display = 'block'; }
      if (bHtml) bHtml.style.display = 'none';
      if (bSec) bSec.style.padding = '0';
    }

    // Hero slides
    if (d.hero) {
      const slides = document.querySelectorAll('.hero-slider .slide');
      d.hero.forEach((slide, i) => {
        if (!slides[i]) return;
        applyBg(slides[i].querySelector('.slide-bg'), slide.image);
        const badge = slides[i].querySelector('.hero-badge');
        if (badge && slide.badge) badge.textContent = slide.badge;
        const desc = slides[i].querySelector('.hero-desc');
        if (desc && slide.desc) desc.textContent = slide.desc;
        if (slide.title) {
          const h1 = slides[i].querySelector('h1');
          if (h1) {
            const lines = slide.title.split('\n');
            h1.innerHTML = lines.map((l, li) =>
              li === 1 ? '<span class="gold">' + l + '</span>' : l
            ).join('<br>');
          }
        }
      });
    }

    // About
    if (d.about) {
      const ph = document.querySelector('.about-img-placeholder');
      if (ph && d.about.image) {
        applyBg(ph, d.about.image);
        ph.style.borderRadius = '12px';
        const icon = ph.querySelector('i');
        const span = ph.querySelector('span');
        if (icon) icon.style.display = 'none';
        if (span) span.style.display = 'none';
      }
      const h3 = document.querySelector('.about-content h3');
      if (h3 && d.about.title) h3.textContent = d.about.title;
      const paras = document.querySelectorAll('.about-content > p');
      if (paras[0] && d.about.content1) paras[0].textContent = d.about.content1;
      if (paras[1] && d.about.content2) paras[1].textContent = d.about.content2;
    }

    // Categories
    if (d.categories) {
      const catImgs = document.querySelectorAll('.cat-img');
      const catNames = document.querySelectorAll('.cat-info h3');
      const catDescs = document.querySelectorAll('.cat-info p');
      d.categories.forEach((cat, i) => {
        applyBg(catImgs[i], cat.image);
        if (cat.name && catNames[i]) catNames[i].textContent = cat.name;
        if (cat.desc && catDescs[i]) catDescs[i].textContent = cat.desc;
      });
    }

    // Products
    const productMap = {
      tubep: '#sp-tu-bep',
      thietbi: '#sp-thiet-bi',
      phukien: '#sp-phu-kien',
      banghe: '#sp-ban-ghe',
      giacong: '#sp-gia-cong'
    };
    if (d.products) {
      Object.entries(productMap).forEach(([key, sel]) => {
        const section = document.querySelector(sel);
        if (!section || !d.products[key]) return;
        const cards = section.querySelectorAll('.product-card');
        d.products[key].forEach((prod, i) => {
          if (!cards[i]) return;
          const img = cards[i].querySelector('.product-img');
          applyBg(img, prod.image);
          const h4 = cards[i].querySelector('h4');
          if (h4 && prod.name) h4.textContent = prod.name;
          const p = cards[i].querySelector('p');
          if (p && prod.desc) p.textContent = prod.desc;
          const badge = cards[i].querySelector('.product-badge');
          if (badge && prod.badge !== undefined) {
            if (prod.badge) { badge.textContent = prod.badge; badge.style.display = ''; }
            else badge.style.display = 'none';
          }
        });
      });
    }

    // Projects
    if (d.projects) {
      const projCards = document.querySelectorAll('.project-card');
      d.projects.forEach((proj, i) => {
        if (!projCards[i]) return;
        applyBg(projCards[i].querySelector('.project-img'), proj.image);
        const h4 = projCards[i].querySelector('.project-overlay h4');
        if (h4 && proj.title) h4.textContent = proj.title;
        const p = projCards[i].querySelector('.project-overlay p');
        if (p && proj.subtitle) p.textContent = proj.subtitle;
      });
    }

  } catch (e) {
    console.warn('CMS load error:', e);
  }
})();

document.addEventListener('DOMContentLoaded', () => {
  'use strict';

  // ============================================================
  // 1. MOBILE MENU - Menu di động
  // Toggle hamburger để hiện/ẩn menu mobile và overlay
  // ============================================================
  const hamburger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobileMenu');
  const mobileOverlay = document.getElementById('mobileOverlay');

  if (hamburger && mobileMenu) {
    // Toggle menu khi click hamburger
    hamburger.addEventListener('click', () => {
      hamburger.classList.toggle('active');
      mobileMenu.classList.toggle('active');
      if (mobileOverlay) mobileOverlay.classList.toggle('active');
      document.body.classList.toggle('menu-open');
    });

    // Đóng menu khi click overlay
    if (mobileOverlay) {
      mobileOverlay.addEventListener('click', () => {
        hamburger.classList.remove('active');
        mobileMenu.classList.remove('active');
        mobileOverlay.classList.remove('active');
        document.body.classList.remove('menu-open');
      });
    }

    // Đóng menu khi click vào link trong menu
    const mobileLinks = mobileMenu.querySelectorAll('a');
    mobileLinks.forEach(link => {
      link.addEventListener('click', () => {
        hamburger.classList.remove('active');
        mobileMenu.classList.remove('active');
        if (mobileOverlay) mobileOverlay.classList.remove('active');
        document.body.classList.remove('menu-open');
      });
    });
  }

  // ============================================================
  // 2. HERO SLIDER - Slider ảnh banner chính
  // Tự động chuyển slide mỗi 5 giây, có nút điều hướng
  // ============================================================
  const heroSlider = document.getElementById('heroSlider');
  const sliderDots = document.getElementById('sliderDots');
  const sliderPrev = document.getElementById('sliderPrev');
  const sliderNext = document.getElementById('sliderNext');

  if (heroSlider) {
    const slides = heroSlider.querySelectorAll('.slide');
    const dots = sliderDots ? sliderDots.querySelectorAll('.dot') : [];
    let currentSlide = 0;
    let autoSlideInterval = null;
    const SLIDE_INTERVAL = 5000; // 5 giây

    // Hiển thị slide theo index
    const goToSlide = (index) => {
      // Xử lý vòng lặp
      if (index >= slides.length) index = 0;
      if (index < 0) index = slides.length - 1;

      // Bỏ active tất cả slides và dots
      slides.forEach(slide => slide.classList.remove('active'));
      dots.forEach(dot => dot.classList.remove('active'));

      // Thêm active cho slide và dot hiện tại
      if (slides[index]) slides[index].classList.add('active');
      if (dots[index]) dots[index].classList.add('active');

      currentSlide = index;
    };

    // Chuyển sang slide tiếp theo
    const nextSlide = () => goToSlide(currentSlide + 1);

    // Chuyển sang slide trước
    const prevSlide = () => goToSlide(currentSlide - 1);

    // Bắt đầu auto-slide
    const startAutoSlide = () => {
      stopAutoSlide();
      autoSlideInterval = setInterval(nextSlide, SLIDE_INTERVAL);
    };

    // Dừng auto-slide
    const stopAutoSlide = () => {
      if (autoSlideInterval) {
        clearInterval(autoSlideInterval);
        autoSlideInterval = null;
      }
    };

    // Nút Previous
    if (sliderPrev) {
      sliderPrev.addEventListener('click', () => {
        prevSlide();
        startAutoSlide(); // Reset timer sau khi click
      });
    }

    // Nút Next
    if (sliderNext) {
      sliderNext.addEventListener('click', () => {
        nextSlide();
        startAutoSlide(); // Reset timer sau khi click
      });
    }

    // Click vào dots để chuyển slide
    dots.forEach((dot, index) => {
      dot.addEventListener('click', () => {
        goToSlide(index);
        startAutoSlide();
      });
    });

    // Tạm dừng auto-slide khi hover vào slider
    heroSlider.addEventListener('mouseenter', stopAutoSlide);
    heroSlider.addEventListener('mouseleave', startAutoSlide);

    // Khởi tạo slider
    goToSlide(0);
    startAutoSlide();
  }

  // ============================================================
  // 3. STICKY HEADER - Header cố định khi cuộn
  // Thêm class 'scrolled' khi cuộn xuống > 100px
  // ============================================================
  const header = document.getElementById('header');

  const handleStickyHeader = () => {
    if (!header) return;
    if (window.scrollY > 100) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  };

  // ============================================================
  // 4. SMOOTH SCROLLING - Cuộn mượt đến phần tử đích
  // Tất cả anchor links cuộn mượt với offset cho header
  // ============================================================
  const smoothScrollLinks = document.querySelectorAll('a[href^="#"]');

  smoothScrollLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      const href = link.getAttribute('href');
      // Bỏ qua nếu href chỉ là '#' hoặc rỗng
      if (!href || href === '#') return;

      const target = document.querySelector(href);
      if (!target) return;

      e.preventDefault();

      // Tính offset cho header
      const headerHeight = header ? header.offsetHeight : 0;
      const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight - 20;

      window.scrollTo({
        top: targetPosition,
        behavior: 'smooth'
      });
    });
  });

  // ============================================================
  // 5. ACTIVE NAV HIGHLIGHTING - Highlight menu đang active
  // Cập nhật class .active trên nav links dựa trên vị trí cuộn
  // ============================================================
  const mainNavLinks = document.querySelectorAll('.main-nav a[href^="#"]');
  const sections = [];

  // Thu thập tất cả section tương ứng với nav links
  mainNavLinks.forEach(link => {
    const href = link.getAttribute('href');
    if (href && href !== '#') {
      const section = document.querySelector(href);
      if (section) sections.push({ link, section });
    }
  });

  const handleActiveNav = () => {
    const headerHeight = header ? header.offsetHeight : 0;
    const scrollPos = window.scrollY + headerHeight + 100;

    let currentSection = null;

    sections.forEach(({ link, section }) => {
      const sectionTop = section.offsetTop;
      const sectionBottom = sectionTop + section.offsetHeight;

      if (scrollPos >= sectionTop && scrollPos < sectionBottom) {
        currentSection = link;
      }
    });

    // Cập nhật active class
    mainNavLinks.forEach(link => link.classList.remove('active'));
    if (currentSection) {
      currentSection.classList.add('active');
    }
  };

  // ============================================================
  // 6. COUNTER ANIMATION - Hiệu ứng đếm số
  // Khi .stats-bar xuất hiện trong viewport, đếm số từ 0
  // Sử dụng requestAnimationFrame, chỉ chạy 1 lần
  // ============================================================
  let counterAnimated = false;

  const animateCounters = () => {
    if (counterAnimated) return;

    const statsBar = document.querySelector('.stats-bar');
    if (!statsBar) return;

    const rect = statsBar.getBoundingClientRect();
    const isVisible = rect.top < window.innerHeight && rect.bottom > 0;

    if (!isVisible) return;

    counterAnimated = true;
    const statNumbers = document.querySelectorAll('.stat-number');

    statNumbers.forEach(counter => {
      const target = parseInt(counter.getAttribute('data-target'), 10) || 0;
      const duration = 2000; // 2 giây cho animation
      const startTime = performance.now();
      const startValue = 0;

      const updateCounter = (currentTime) => {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Easing function - easeOutExpo cho hiệu ứng mượt
        const easeProgress = 1 - Math.pow(1 - progress, 3);
        const currentValue = Math.floor(startValue + (target - startValue) * easeProgress);

        counter.textContent = currentValue.toLocaleString('vi-VN');

        if (progress < 1) {
          requestAnimationFrame(updateCounter);
        } else {
          counter.textContent = target.toLocaleString('vi-VN');
        }
      };

      requestAnimationFrame(updateCounter);
    });
  };

  // ============================================================
  // 7. SCROLL REVEAL ANIMATION - Hiệu ứng xuất hiện khi cuộn
  // Thêm class 'revealed' khi phần tử vào viewport
  // Sử dụng IntersectionObserver với threshold 0.15
  // ============================================================
  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          // Ngừng theo dõi sau khi đã reveal
          revealObserver.unobserve(entry.target);
        }
      });
    },
    {
      threshold: 0.15,
      rootMargin: '0px 0px -50px 0px'
    }
  );

  // Quan sát tất cả phần tử có class 'reveal-on-scroll'
  const observeRevealElements = () => {
    const revealElements = document.querySelectorAll('.reveal-on-scroll');
    revealElements.forEach(el => revealObserver.observe(el));
  };

  // ============================================================
  // 8. CATEGORY SIDEBAR TOGGLE - Bật/tắt sidebar danh mục
  // Toggle #categorySidebar khi click #categoryToggle
  // Đóng khi click bên ngoài
  // ============================================================
  const categoryToggle = document.getElementById('categoryToggle');
  const categorySidebar = document.getElementById('categorySidebar');

  if (categoryToggle && categorySidebar) {
    categoryToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      categorySidebar.classList.toggle('active');
      categoryToggle.classList.toggle('active');
    });

    // Đóng sidebar khi click bên ngoài
    document.addEventListener('click', (e) => {
      if (!categorySidebar.contains(e.target) && !categoryToggle.contains(e.target)) {
        categorySidebar.classList.remove('active');
        categoryToggle.classList.remove('active');
      }
    });

    // Ngăn đóng khi click trong sidebar
    categorySidebar.addEventListener('click', (e) => {
      e.stopPropagation();
    });
  }

  // ============================================================
  // 9. PRODUCT CATEGORY DROPDOWN - Dropdown danh mục sản phẩm
  // Hover trên desktop, click trên mobile
  // ============================================================
  const dropdownItems = document.querySelectorAll('.has-dropdown');

  dropdownItems.forEach(item => {
    const dropdown = item.querySelector('.dropdown');
    if (!dropdown) return;

    // Desktop: hover để hiện dropdown
    item.addEventListener('mouseenter', () => {
      if (window.innerWidth > 768) {
        dropdown.classList.add('active');
      }
    });

    item.addEventListener('mouseleave', () => {
      if (window.innerWidth > 768) {
        dropdown.classList.remove('active');
      }
    });

    // Mobile: click để toggle dropdown
    const dropdownTrigger = item.querySelector('a, .dropdown-trigger');
    if (dropdownTrigger) {
      dropdownTrigger.addEventListener('click', (e) => {
        if (window.innerWidth <= 768) {
          e.preventDefault();
          e.stopPropagation();

          // Đóng tất cả dropdown khác
          dropdownItems.forEach(other => {
            if (other !== item) {
              const otherDropdown = other.querySelector('.dropdown');
              if (otherDropdown) otherDropdown.classList.remove('active');
            }
          });

          dropdown.classList.toggle('active');
        }
      });
    }
  });

  // ============================================================
  // 10. BACK TO TOP BUTTON - Nút quay lại đầu trang
  // Hiển thị khi cuộn > 500px, cuộn mượt lên đầu khi click
  // ============================================================
  const backToTop = document.getElementById('backToTop');

  const handleBackToTop = () => {
    if (!backToTop) return;
    if (window.scrollY > 500) {
      backToTop.classList.add('visible');
    } else {
      backToTop.classList.remove('visible');
    }
  };

  if (backToTop) {
    backToTop.addEventListener('click', (e) => {
      e.preventDefault();
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
  }

  // ============================================================
  // 11. CONTACT FORM - Form liên hệ
  // Xác thực cơ bản khi submit, hiện thông báo thành công
  // ============================================================
  const contactForm = document.getElementById('contactForm');

  if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
      e.preventDefault();

      // Thu thập dữ liệu form
      const formData = new FormData(contactForm);
      const data = Object.fromEntries(formData.entries());

      // Xác thực cơ bản
      let isValid = true;
      const errors = [];

      // Kiểm tra tên
      const nameField = contactForm.querySelector('[name="name"], [name="ho-ten"], #name');
      if (nameField && !nameField.value.trim()) {
        isValid = false;
        errors.push('Vui lòng nhập họ và tên');
        nameField.classList.add('error');
      }

      // Kiểm tra số điện thoại
      const phoneField = contactForm.querySelector('[name="phone"], [name="dien-thoai"], #phone');
      if (phoneField) {
        const phoneValue = phoneField.value.trim();
        if (!phoneValue) {
          isValid = false;
          errors.push('Vui lòng nhập số điện thoại');
          phoneField.classList.add('error');
        } else if (!/^(0|\+84)[0-9]{9,10}$/.test(phoneValue.replace(/\s/g, ''))) {
          isValid = false;
          errors.push('Số điện thoại không hợp lệ');
          phoneField.classList.add('error');
        }
      }

      // Kiểm tra email (nếu có)
      const emailField = contactForm.querySelector('[name="email"], #email');
      if (emailField && emailField.value.trim()) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(emailField.value.trim())) {
          isValid = false;
          errors.push('Email không hợp lệ');
          emailField.classList.add('error');
        }
      }

      // Kiểm tra nội dung (nếu có)
      const messageField = contactForm.querySelector('[name="message"], [name="noi-dung"], #message');
      if (messageField && !messageField.value.trim()) {
        isValid = false;
        errors.push('Vui lòng nhập nội dung tin nhắn');
        messageField.classList.add('error');
      }

      // Xóa class error khi focus lại
      contactForm.querySelectorAll('input, textarea, select').forEach(field => {
        field.addEventListener('focus', () => field.classList.remove('error'), { once: true });
      });

      if (!isValid) {
        alert('⚠️ ' + errors.join('\n'));
        return;
      }

      // Thành công
      alert('✅ Cảm ơn bạn đã liên hệ!\n\nChúng tôi sẽ phản hồi trong thời gian sớm nhất.\n\n— Thịnh Vượng Kitchen');
      contactForm.reset();

      // Xóa tất cả class error
      contactForm.querySelectorAll('.error').forEach(el => el.classList.remove('error'));
    });
  }

  // ============================================================
  // 12. FLOATING BUTTONS ANIMATION - Hiệu ứng pulse cho nút nổi
  // Thêm animation pulse nhẹ cho .float-btn
  // ============================================================
  const floatBtns = document.querySelectorAll('.float-btn');

  floatBtns.forEach(btn => {
    // Thêm hiệu ứng pulse bằng CSS animation
    btn.style.animation = 'floatPulse 2s ease-in-out infinite';

    // Dừng pulse khi hover để không bị rối mắt
    btn.addEventListener('mouseenter', () => {
      btn.style.animationPlayState = 'paused';
      btn.style.transform = 'scale(1.1)';
    });

    btn.addEventListener('mouseleave', () => {
      btn.style.animationPlayState = 'running';
      btn.style.transform = 'scale(1)';
    });
  });

  // Inject keyframes cho float pulse animation
  if (floatBtns.length > 0) {
    const pulseStyle = document.createElement('style');
    pulseStyle.textContent = `
      @keyframes floatPulse {
        0%, 100% {
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
          transform: scale(1);
        }
        50% {
          box-shadow: 0 8px 25px rgba(0, 0, 0, 0.35);
          transform: scale(1.05);
        }
      }
    `;
    document.head.appendChild(pulseStyle);
  }

  // ============================================================
  // 13. IMAGE LIGHTBOX FOR PROJECTS - Lightbox ảnh dự án
  // Click .project-card để mở overlay toàn màn hình
  // Đóng khi click bên ngoài hoặc nhấn Escape
  // ============================================================
  const projectCards = document.querySelectorAll('.project-card');

  // Tạo lightbox container
  const createLightbox = () => {
    const lightbox = document.createElement('div');
    lightbox.id = 'projectLightbox';
    lightbox.className = 'lightbox-overlay';
    lightbox.innerHTML = `
      <div class="lightbox-content">
        <button class="lightbox-close" aria-label="Đóng">&times;</button>
        <div class="lightbox-image-container">
          <img class="lightbox-image" src="" alt="" />
        </div>
        <div class="lightbox-details">
          <h3 class="lightbox-title"></h3>
          <p class="lightbox-description"></p>
        </div>
      </div>
    `;

    // Inject lightbox styles
    const lightboxStyle = document.createElement('style');
    lightboxStyle.textContent = `
      .lightbox-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        opacity: 0;
        visibility: hidden;
        transition: opacity 0.3s ease, visibility 0.3s ease;
        cursor: pointer;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
      }

      .lightbox-overlay.active {
        opacity: 1;
        visibility: visible;
      }

      .lightbox-content {
        position: relative;
        max-width: 900px;
        max-height: 90vh;
        width: 90%;
        background: #1a1a1a;
        border-radius: 16px;
        overflow: hidden;
        transform: scale(0.9) translateY(20px);
        transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        cursor: default;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.5);
      }

      .lightbox-overlay.active .lightbox-content {
        transform: scale(1) translateY(0);
      }

      .lightbox-close {
        position: absolute;
        top: 12px;
        right: 16px;
        background: rgba(0, 0, 0, 0.6);
        border: none;
        color: #fff;
        font-size: 28px;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10;
        transition: background 0.2s ease, transform 0.2s ease;
        line-height: 1;
      }

      .lightbox-close:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: rotate(90deg);
      }

      .lightbox-image-container {
        width: 100%;
        max-height: 60vh;
        overflow: hidden;
        background: #111;
      }

      .lightbox-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
      }

      .lightbox-details {
        padding: 24px 28px;
        color: #fff;
      }

      .lightbox-title {
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 8px;
        color: #ffd700;
      }

      .lightbox-description {
        font-size: 0.95rem;
        line-height: 1.6;
        color: #ccc;
        margin: 0;
      }

      @media (max-width: 768px) {
        .lightbox-content {
          width: 95%;
          max-height: 85vh;
          border-radius: 12px;
        }

        .lightbox-details {
          padding: 16px 20px;
        }

        .lightbox-title {
          font-size: 1.15rem;
        }
      }
    `;
    document.head.appendChild(lightboxStyle);
    document.body.appendChild(lightbox);

    return lightbox;
  };

  if (projectCards.length > 0) {
    const lightbox = createLightbox();
    const lightboxImage = lightbox.querySelector('.lightbox-image');
    const lightboxTitle = lightbox.querySelector('.lightbox-title');
    const lightboxDescription = lightbox.querySelector('.lightbox-description');
    const lightboxClose = lightbox.querySelector('.lightbox-close');
    const lightboxContent = lightbox.querySelector('.lightbox-content');

    // Mở lightbox
    const openLightbox = (card) => {
      const img = card.querySelector('img');
      const title = card.querySelector('h3, .project-title, .card-title');
      const desc = card.querySelector('p, .project-desc, .card-desc, .project-description');

      if (img) {
        lightboxImage.src = img.src;
        lightboxImage.alt = img.alt || '';
      }
      lightboxTitle.textContent = title ? title.textContent : '';
      lightboxDescription.textContent = desc ? desc.textContent : '';

      lightbox.classList.add('active');
      document.body.style.overflow = 'hidden';
    };

    // Đóng lightbox
    const closeLightbox = () => {
      lightbox.classList.remove('active');
      document.body.style.overflow = '';
    };

    // Click vào project card để mở
    projectCards.forEach(card => {
      card.style.cursor = 'pointer';
      card.addEventListener('click', (e) => {
        // Không mở lightbox nếu click vào link bên trong
        if (e.target.closest('a')) return;
        openLightbox(card);
      });
    });

    // Đóng khi click nút close
    lightboxClose.addEventListener('click', closeLightbox);

    // Đóng khi click bên ngoài content
    lightbox.addEventListener('click', (e) => {
      if (!lightboxContent.contains(e.target)) {
        closeLightbox();
      }
    });

    // Đóng khi nhấn Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && lightbox.classList.contains('active')) {
        closeLightbox();
      }
    });
  }

  // ============================================================
  // 14. PARALLAX EFFECT - Hiệu ứng parallax cho hero section
  // Tạo hiệu ứng depth nhẹ cho background khi cuộn
  // ============================================================
  const heroSection = document.querySelector('.hero, #hero, .hero-section');

  const handleParallax = () => {
    if (!heroSection) return;

    const scrolled = window.scrollY;
    const heroHeight = heroSection.offsetHeight;

    // Chỉ áp dụng parallax khi hero section còn trong viewport
    if (scrolled <= heroHeight) {
      const parallaxValue = scrolled * 0.4;
      heroSection.style.backgroundPositionY = `${parallaxValue}px`;

      // Giữ nội dung hero luôn hiện rõ khi cuộn
      const heroContent = heroSection.querySelector('.hero-content, .hero-text, .slide-content');
      if (heroContent) {
        heroContent.style.transform = '';
        heroContent.style.opacity = 1;
      }
    }
  };

  // ============================================================
  // 15. DYNAMIC REVEAL CLASSES - Thêm class reveal-on-scroll
  // Tự động thêm class cho các phần tử khi DOM loaded
  // ============================================================
  const revealSelectors = [
    '.category-card',
    '.product-card',
    '.project-card',
    '.feature-card',
    '.contact-item',
    '.about-grid',
    '.stats-bar'
  ];

  revealSelectors.forEach(selector => {
    const elements = document.querySelectorAll(selector);
    elements.forEach((el, index) => {
      el.classList.add('reveal-on-scroll');
      el.style.transitionDelay = `${index * 0.1}s`;
      // Nếu element đã trong viewport khi trang tải → reveal ngay, không chờ scroll
      const rect = el.getBoundingClientRect();
      if (rect.top < window.innerHeight && rect.bottom > 0) {
        el.classList.add('revealed');
      }
    });
  });

  // Tắt hoàn toàn reveal animation - đảm bảo content luôn hiện rõ
  const revealStyle = document.createElement('style');
  revealStyle.textContent = `
    .reveal-on-scroll,
    .reveal-on-scroll.revealed {
      opacity: 1 !important;
      transform: none !important;
      transition: none !important;
      visibility: visible !important;
    }
  `;
  document.head.appendChild(revealStyle);

  // Bắt đầu observe sau khi đã thêm class
  observeRevealElements();

  // Force reveal tất cả elements trong viewport sau 1 frame để chắc chắn
  requestAnimationFrame(() => {
    document.querySelectorAll('.reveal-on-scroll:not(.revealed)').forEach(el => {
      const rect = el.getBoundingClientRect();
      if (rect.top < window.innerHeight && rect.bottom > 0) {
        el.classList.add('revealed');
      }
    });
  });

  // ============================================================
  // 16. FORCE VISIBLE - Ép hiện rõ section-header và about
  // Debug + fix mọi phần tử bị mờ trong section about
  // ============================================================
  const forceAboutVisible = () => {
    const aboutSection = document.querySelector('section.about');
    if (!aboutSection) return;
    const toFix = [aboutSection, ...aboutSection.querySelectorAll('*')];
    toFix.forEach(el => {
      if (!el.classList.contains('dropdown') &&
          !el.classList.contains('lightbox-overlay') &&
          !el.classList.contains('mobile-overlay')) {
        el.style.setProperty('opacity', '1', 'important');
        el.style.setProperty('filter', 'none', 'important');
      }
    });
  };

  // Chạy ngay và sau mỗi scroll lần đầu để đảm bảo
  forceAboutVisible();
  window.addEventListener('scroll', forceAboutVisible, { passive: true, once: true });

  // ============================================================
  // SCROLL EVENT HANDLER - Xử lý tổng hợp sự kiện cuộn
  // Sử dụng requestAnimationFrame để tối ưu hiệu suất
  // ============================================================
  let ticking = false;

  const onScroll = () => {
    if (!ticking) {
      requestAnimationFrame(() => {
        handleStickyHeader();
        handleActiveNav();
        handleBackToTop();
        animateCounters();
        handleParallax();
        ticking = false;
      });
      ticking = true;
    }
  };

  window.addEventListener('scroll', onScroll, { passive: true });

  // Gọi lần đầu để set trạng thái ban đầu
  handleStickyHeader();
  handleActiveNav();
  handleBackToTop();
  animateCounters();

  // ============================================================
  // RESIZE HANDLER - Xử lý khi thay đổi kích thước cửa sổ
  // Đóng mobile menu và dropdown khi chuyển sang desktop
  // ============================================================
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      // Đóng mobile menu khi chuyển sang desktop
      if (window.innerWidth > 768 && mobileMenu) {
        if (hamburger) hamburger.classList.remove('active');
        mobileMenu.classList.remove('active');
        if (mobileOverlay) mobileOverlay.classList.remove('active');
        document.body.classList.remove('menu-open');
      }

      // Đóng tất cả dropdown trên mobile
      if (window.innerWidth <= 768) {
        document.querySelectorAll('.dropdown.active').forEach(dd => {
          dd.classList.remove('active');
        });
      }
    }, 250);
  });

  // ============================================================
  // CONSOLE LOG - Thông báo khởi tạo thành công
  // ============================================================
  console.log('%c🏠 Thịnh Vượng Kitchen - Website loaded successfully!', 
    'color: #ffd700; font-size: 14px; font-weight: bold; background: #1a1a1a; padding: 8px 16px; border-radius: 4px;');
});
