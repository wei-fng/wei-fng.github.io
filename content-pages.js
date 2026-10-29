/* Content comes only from the owner's local Markdown files. */
const pageEntries = window.PAGE_CONTENT || [];
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const listValue = value => Array.isArray(value) ? value.join(', ') : String(value || '');
const safeURL = value => {
  const url = String(value || '').trim().replace(/\\/g, '/');
  if (!url || /[\u0000-\u001f\u007f]/.test(url)) return '';
  return /^(https?:\/\/|mailto:)/i.test(url) || (!/^[a-z][a-z0-9+.-]*:/i.test(url) && !url.startsWith('//')) ? url : '';
};
const detailURL = entry => 'content.html?id=' + encodeURIComponent(entry.id);
const entryType = entry => entry.pub_type || entry.type || entry.event || '';
const localImageFallback = entry => {
  const folders = { publications:'publication', projects:'project', activities:'activity' };
  const filename = safeURL(entry.image).split('/').pop();
  return folders[entry.category] && filename ? `photos/${folders[entry.category]}/${filename}` : '';
};
const formatDate = value => {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value || '')) return value || '';
  return new Intl.DateTimeFormat('en-GB', { day:'numeric', month:'long', year:'numeric', timeZone:'UTC' }).format(new Date(value + 'T00:00:00Z'));
};

function entryMeta(entry, detailView = false) {
  const lines = [];
  if (entry.category === 'publications') {
    if (listValue(entry.authors)) lines.push(listValue(entry.authors));
    if (entry.source) lines.push(entry.source);
  } else {
    if (listValue(entry.team || entry.authors)) lines.push(listValue(entry.team || entry.authors));
    if (entry.source || entry.location) lines.push(entry.source || entry.location);
  }
  if (detailView && (entry.date || entryType(entry))) lines.push([formatDate(entry.date), entryType(entry)].filter(Boolean).join(' | '));
  return lines;
}

function renderTags(tags, className = 'content-tags') {
  const values = Array.isArray(tags) ? tags : [];
  return values.length ? `<div class="${className}" aria-label="Tags">${values.map(tag => `<span>${esc(tag)}</span>`).join('')}</div>` : '';
}

// CommonMark ends type-6 HTML blocks at blank lines. Collapse only blank lines
// occurring directly between tags so owner-authored galleries remain real DOM.
const normalizeCustomHTML = markdown => String(markdown || '')
  .replace(/<(video|source|img|a)\b[^>]*>/gi, tag => tag.replace(/\s*\n\s*/g, ' '))
  .replace(/>\s*\n(?:[ \t]*\n)+[ \t]*</g, '>\n<');

const category = document.querySelector('[data-category]')?.dataset.category;
if (category) {
  const entries = pageEntries.filter(entry => entry.category === category);
  const search = document.getElementById('content-search');
  const select = document.getElementById('content-type');
  [...new Set(entries.map(entryType).filter(Boolean))].sort().forEach(type => {
    const option = document.createElement('option');
    option.value = type;
    option.textContent = type;
    select.append(option);
  });
  
  function renderList() {
    const query = search.value.toLowerCase().trim();

    const filtered = entries.filter(entry =>
      (!select.value || entryType(entry) === select.value) &&
      [
        entry.title,
        entry.subtitle,
        entry.name_cn,
        listValue(entry.authors),
        listValue(entry.team),
        entry.source,
        entry.location,
        listValue(entry.tags),
        listValue(entry.keywords)
      ].join(' ').toLowerCase().includes(query)
    );

    let year = '';

    document.getElementById('content-list').innerHTML =
      filtered.map(entry => {
        const nextYear = entry.date
          ? entry.date.slice(0, 4)
          : 'Undated';

        const heading = nextYear !== year
          ? `<h2 class="content-year">${esc(nextYear)}</h2>`
          : '';

        year = nextYear;

        const url = detailURL(entry);
        const image = safeURL(entry.image);
        const fallback = localImageFallback(entry);

        // Projects: Chinese name; Publications: original subtitle
        const subtitle = entry.category === 'projects'
          ? entry.name_cn
          : entry.subtitle;

        return heading + `
          <article class="content-row ${image ? '' : 'no-image'}">

            ${image ? `
              <a class="content-row-image"
                href="${url}"
                tabindex="-1"
                aria-hidden="true">
                <img
                  loading="lazy"
                  decoding="async"
                  referrerpolicy="no-referrer"
                  src="${esc(image)}"
                  data-fallback="${esc(fallback)}"
                  alt="">
              </a>
            ` : ''}

            <div class="content-row-body">

              <h3>
                <a href="${url}">${esc(entry.title)}</a>
              </h3>

              ${subtitle ? `
                <p class="content-subtitle">${esc(subtitle)}</p>
              ` : ''}

              ${entryMeta(entry).map(line => `
                <p class="content-meta">${esc(line)}</p>
              `).join('')}

              <div class="content-row-footer">
                ${entryType(entry) ? `
                  <p class="content-kind">
                    ${esc(entryType(entry))}
                  </p>
                ` : ''}
              </div>

            </div>
          </article>
        `;
      }).join('') ||
      `<p class="content-empty">
        ${entries.length
          ? 'No matching entries.'
          : 'No entries yet. / 暂无记录'}
      </p>`;

    document.querySelectorAll(
      '#content-list img[data-fallback]'
    ).forEach(image => {
      image.addEventListener('error', () => {
        const fallback = image.dataset.fallback;

        if (fallback && image.getAttribute('src') !== fallback) {
          image.src = fallback;
        }
      });
    });
  }

  search.addEventListener('input', renderList);
  select.addEventListener('change', renderList);
  renderList();
}

function sanitizeMarkdown(root) {
  root.querySelectorAll('a[href^="/people/"]').forEach(link => link.href = 'https://archialgo.com' + link.getAttribute('href'));
  root.querySelectorAll('script,object,embed,base,meta,link,form').forEach(element => element.remove());
  root.querySelectorAll('style').forEach(style => style.remove());
  root.querySelectorAll('iframe').forEach(frame => {
    const src = safeURL(frame.getAttribute('src'));
    if (!/^https:\/\//i.test(src)) return frame.remove();
    frame.setAttribute('src', src);
    frame.setAttribute('loading', 'lazy');
    frame.setAttribute('referrerpolicy', 'no-referrer');
    frame.setAttribute('sandbox', 'allow-scripts allow-same-origin allow-presentation');
  });
  root.querySelectorAll('img').forEach(image => {
    image.setAttribute('referrerpolicy', 'no-referrer');
    image.setAttribute('loading', 'lazy');
    image.setAttribute('decoding', 'async');
  });
  root.querySelectorAll('*').forEach(element => {
    [...element.attributes].forEach(attribute => {
      const name = attribute.name.toLowerCase();
      if (name.startsWith('on')) element.removeAttribute(attribute.name);
      if ((name === 'href' || name === 'src' || name === 'poster') && !safeURL(attribute.value)) element.removeAttribute(attribute.name);
      if (name === 'style' && /url\s*\(|expression\s*\(|javascript\s*:|behavior\s*:|-moz-binding/i.test(attribute.value)) element.removeAttribute('style');
    });
    if (element.tagName === 'A' && element.getAttribute('target') === '_blank') element.setAttribute('rel', 'noopener noreferrer');
  });
}

const detail = document.getElementById('content-detail');
if (detail) {
  const entry = pageEntries.find(item => item.id === new URLSearchParams(location.search).get('id'));
  if (!entry) {
    detail.innerHTML = '<h1>Page not found</h1><p><a href="publications.html">Publications</a> / <a href="projects.html">Projects</a> / <a href="activities.html">Activities</a></p>';
  } else {
    document.title = entry.title + ' - Wei Feng';
    detail.innerHTML = `<a class="content-back" href="${entry.category}.html">← ${esc(entry.category.toUpperCase())}</a><h1>${esc(entry.title)}</h1>${entry.subtitle ? `<h2 class="detail-subtitle">${esc(entry.subtitle)}</h2>` : ''}<div class="detail-meta">${entryMeta(entry, true).map(line => `<p>${esc(line)}</p>`).join('')}</div>${entry.external_url && safeURL(entry.external_url) ? `<p><a href="${esc(safeURL(entry.external_url))}" rel="noopener noreferrer" target="_blank">External link ↗</a></p>` : ''}<div class="markdown-body">${marked.parse(normalizeCustomHTML(entry.body))}</div>`;
    sanitizeMarkdown(detail);
    if (window.ContentInteractions) window.ContentInteractions.initialize(detail);

  }
}

document.addEventListener('DOMContentLoaded', () => {
  if (typeof initializeDarkMode === 'function') initializeDarkMode();
  if (typeof initializeBackToTop === 'function') initializeBackToTop();
});


// Disable right-click and dragging on project detail images
document.addEventListener('contextmenu', event => {
  if (event.target.closest('.content-detail .markdown-body img')) {
    event.preventDefault();
  }
});

document.addEventListener('dragstart', event => {
  if (event.target.closest('.content-detail .markdown-body img')) {
    event.preventDefault();
  }
});