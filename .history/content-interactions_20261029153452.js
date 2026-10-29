(function () {
  'use strict';

  function cycleCarousel(carousel) {
    const slides = Array.from(carousel.querySelectorAll('.carousel-item'));
    if (slides.length < 2 || carousel.dataset.initialized === 'true') return;

    let current = Math.max(0, slides.findIndex(slide => slide.classList.contains('active')));
    let timer = null;
    const interval = Number(carousel.dataset.interval) || 0;
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function show(index) {
      current = (index + slides.length) % slides.length;
      slides.forEach((slide, slideIndex) => {
        const active = slideIndex === current;
        slide.classList.toggle('active', active);
        slide.setAttribute('aria-hidden', String(!active));
      });
    }

    function stop() {
      if (timer !== null) window.clearInterval(timer);
      timer = null;
    }

    function start() {
      stop();
      if (interval > 0 && !reduceMotion && !document.hidden) {
        timer = window.setInterval(() => show(current + 1), interval);
      }
    }

    carousel.querySelectorAll('[data-slide="prev"], .carousel-control-prev').forEach(control => {
      control.addEventListener('click', event => {
        event.preventDefault();
        show(current - 1);
        start();
      });
    });
    carousel.querySelectorAll('[data-slide="next"], .carousel-control-next').forEach(control => {
      control.addEventListener('click', event => {
        event.preventDefault();
        show(current + 1);
        start();
      });
    });
    carousel.addEventListener('mouseenter', stop);
    carousel.addEventListener('mouseleave', start);
    carousel.addEventListener('focusin', stop);
    carousel.addEventListener('focusout', event => {
      if (!carousel.contains(event.relatedTarget)) start();
    });
    document.addEventListener('visibilitychange', start);
    carousel.dataset.initialized = 'true';
    show(current);
    start();
  }

  function weavingDreamsCoverflow(gallery) {
    if (!gallery || gallery.dataset.initialized === 'true') return;
    const stage = gallery.querySelector('.df-coverflow-stage');
    const slides = Array.from(gallery.querySelectorAll('.df-slide'));
    const previous = gallery.querySelector('.df-prev');
    const next = gallery.querySelector('.df-next');
    const label = gallery.querySelector('.df-current-label');
    const number = gallery.querySelector('.df-group-number');
    const title = gallery.querySelector('.df-group-title');
    const members = gallery.querySelector('.df-group-members');
    const groups = [
      ['Rome Heritage Explorer', 'Sirui Xu · Jiancheng Pan · Yinghui Yi · Yuqing Wu · Shuxin Lin · Tianyu Wang · Xi Chen'],
      ['Between Worship and Tourism', 'Mengfei Xue · Ziwen Yao · Yangchen Cui · Zhiyuan He · Jiawei Wang · Yinan Wang'],
      ['Assessment and Regeneration along Atatürk Boulevard', 'Miaoyi Ke · Yixing Tao · Linzhen Ding · Jiayu Bao · Zhaoyi Chen · Zhizheng Liu']
    ];
    if (!stage || !previous || !next || slides.length !== groups.length) return;

    let current = 0;
    let timer = null;
    let paused = false;
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function syncHeight() {
      const ratio = window.innerWidth <= 600 ? 0.9 : 0.74;
      const heights = slides.map(slide => {
        const image = slide.querySelector('img');
        return image && image.naturalWidth ? stage.clientWidth * ratio * image.naturalHeight / image.naturalWidth : 0;
      });
      if (heights.every(Boolean)) stage.style.height = Math.ceil(Math.max(...heights) + 40) + 'px';
    }

    function render(index) {
      current = (index + slides.length) % slides.length;
      slides.forEach((slide, slideIndex) => {
        const offset = (slideIndex - current + slides.length) % slides.length;
        slide.classList.toggle('is-center', offset === 0);
        slide.classList.toggle('is-right', offset === 1);
        slide.classList.toggle('is-left', offset === slides.length - 1);
        slide.setAttribute('aria-current', String(offset === 0));
      });
      const currentNumber = String(current + 1).padStart(2, '0');
      label.textContent = currentNumber + ' / ' + String(slides.length).padStart(2, '0');
      number.textContent = 'GROUP ' + currentNumber;
      title.textContent = groups[current][0];
      members.textContent = groups[current][1];
    }

    function stop() {
      if (timer !== null) window.clearInterval(timer);
      timer = null;
    }

    function start() {
      stop();
      if (!paused && !reduceMotion && !document.hidden) {
        timer = window.setInterval(() => render(current + 1), 2500);
      }
    }

    previous.addEventListener('click', () => { render(current - 1); start(); });
    next.addEventListener('click', () => { render(current + 1); start(); });
    slides.forEach((slide, index) => {
      slide.addEventListener('click', () => { render(index); start(); });
      slide.querySelector('img')?.addEventListener('load', syncHeight);
    });
    gallery.addEventListener('mouseenter', () => { paused = true; stop(); });
    gallery.addEventListener('mouseleave', () => { paused = false; start(); });
    gallery.addEventListener('focusin', () => { paused = true; stop(); });
    gallery.addEventListener('focusout', event => {
      if (!gallery.contains(event.relatedTarget)) { paused = false; start(); }
    });
    document.addEventListener('visibilitychange', start);
    window.addEventListener('resize', syncHeight, { passive: true });

    gallery.dataset.initialized = 'true';
    render(0);
    syncHeight();
    start();
  }

  window.ContentInteractions = {
    initialize(root) {
      root.querySelectorAll('.carousel').forEach(cycleCarousel);
      weavingDreamsCoverflow(root.querySelector('#df-coverflow'));
    }
  };
})();


/* Florence 2024 - Drawing Coverflow */

(function () {
  const titles = [
    "City Evolution · Project Overview",
    "Drawing 01",
    "Drawing 02",
    "Drawing 03",
    "Drawing 04",
    "Drawing 05",
    "Drawing 06"
  ];

  function initFlorenceCoverflow() {
    const root = document.getElementById("florence-coverflow");

    if (!root || root.dataset.initialized === "true") return;
    root.dataset.initialized = "true";

    const slides = [...root.querySelectorAll(".fl-slide")];
    const total = slides.length;
    if (!total) return;

    const counter = root.querySelector(".fl-current-label");
    const title = root.querySelector(".fl-drawing-title");
    let current = 0;

    function show(index) {
      current = (index + total) % total;

      slides.forEach((slide, i) => {
        slide.classList.remove(
          "is-left", "is-center", "is-right"
        );

        slide.setAttribute("aria-hidden", String(i !== current));
        slide.tabIndex = i === current ? 0 : -1;
      });

      slides[current].classList.add("is-center");

      if (total > 1) {
        slides[(current - 1 + total) % total]
          .classList.add("is-left");

        slides[(current + 1) % total]
          .classList.add("is-right");
      }

      if (counter) {
        counter.textContent =
          `${String(current + 1).padStart(2, "0")} / ` +
          `${String(total).padStart(2, "0")}`;
      }

      if (title) {
        title.textContent = titles[current] || `Drawing ${current + 1}`;
      }
    }

    root.querySelector(".fl-prev")?.addEventListener(
      "click", () => show(current - 1)
    );

    root.querySelector(".fl-next")?.addEventListener(
      "click", () => show(current + 1)
    );

    slides.forEach((slide, index) => {
      slide.addEventListener("click", () => {
        if (index !== current) {
          show(index);
          return;
        }

        const src = slide.querySelector("img")?.src;
        if (src) {
          window.open(src, "_blank", "noopener,noreferrer");
        }
      });
    });

    show(0);
  }

  // Initialize once the dynamically rendered page contains the gallery.
  initFlorenceCoverflow();

  const observer = new MutationObserver(() => {
    initFlorenceCoverflow();
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
})();
