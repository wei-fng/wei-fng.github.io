
/* Homepage Banner and Recent News from Markdown front matter */

(() => {
  const entries = window.PAGE_CONTENT || [];

  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;',
    '"': '&quot;', "'": '&#39;'
  }[c]));

  const hasNav = (entry, key) =>
    Array.isArray(entry.navs) && entry.navs.includes(key);

  const dateSort = (a, b) =>
    String(b.date || '').localeCompare(String(a.date || ''));

  const detailURL = entry =>
    'content.html?id=' + encodeURIComponent(entry.id);

  const safeImage = value => {
    const path = String(value || '').trim().replace(/\\/g, '/');
    return /^(https?:\/\/|\/(?!\/)|(?![a-z]+:)[\w.-])/i.test(path)
      ? path
      : '';
  };

  // FEATURED BANNER
  const bannerEntries = entries
    .filter(entry => hasNav(entry, 'banner') && safeImage(entry.image))
    .sort(dateSort);

  const banner = document.getElementById('homepage-banner');
  const bannerSlides = document.getElementById('home-banner-slides');
  const bannerCount = document.getElementById('home-banner-count');

  if (banner && bannerSlides && bannerEntries.length) {
    banner.hidden = false;
    let current = 0;

    bannerSlides.innerHTML = bannerEntries.map((entry, index) => `
      <a class="home-banner-slide"
         href="${detailURL(entry)}"
         ${index !== 0 ? 'hidden' : ''}>
        <img src="${esc(safeImage(entry.image))}"
             alt="${esc(entry.title)}"
             referrerpolicy="no-referrer">
        <div class="home-banner-caption">
          <strong>${esc(entry.title)}</strong>
          ${entry.name_cn
            ? `<span>${esc(entry.name_cn)}</span>`
            : ''}
        </div>
      </a>
    `).join('');

    const slides = [...bannerSlides.children];

    function renderBanner() {
      slides.forEach((slide, index) => {
        slide.hidden = index !== current;
      });
      bannerCount.textContent =
        `${String(current + 1).padStart(2, '0')} / ${String(slides.length).padStart(2, '0')}`;
    }

    document.getElementById('home-banner-prev').onclick = () => {
      current = (current - 1 + slides.length) % slides.length;
      renderBanner();
    };

    document.getElementById('home-banner-next').onclick = () => {
      current = (current + 1) % slides.length;
      renderBanner();
    };

    if (slides.length === 1) {
      document.querySelector('.home-banner-controls').hidden = true;
    }

    renderBanner();
  }

  // RECENT NEWS
  const newsEntries = entries
    .filter(entry => hasNav(entry, 'news'))
    .sort(dateSort);

  const newsSection = document.getElementById('homepage-news');
  const newsGrid = document.getElementById('home-news-grid');

  if (newsSection && newsGrid && newsEntries.length) {
    newsSection.hidden = false;

    newsGrid.innerHTML = newsEntries.map(entry => {
      const image = safeImage(entry.image);
      const type = {
        publications: 'Publication',
        projects: 'Project',
        activities: 'News'
      }[entry.category] || 'News';

      return `
        <a class="home-news-card" href="${detailURL(entry)}">
          ${image ? `
            <img src="${esc(image)}"
                 alt=""
                 loading="lazy"
                 referrerpolicy="no-referrer">
          ` : ''}
          <div class="home-news-content">
            <div class="home-news-title">${esc(entry.title)}</div>
            <div class="home-news-meta">
              ${type} · ${esc(String(entry.date || '').slice(0, 4))}
            </div>
          </div>
        </a>
      `;
    }).join('');
  }
})();
