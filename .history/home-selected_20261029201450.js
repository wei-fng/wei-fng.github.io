
/* Homepage selected publications and projects */

(() => {
  const entries = window.PAGE_CONTENT || [];

  const escapeHTML = value =>
    String(value ?? '').replace(/[&<>"']/g, c => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    }[c]));

  const toText = value =>
    Array.isArray(value) ? value.join(', ') : String(value || '');

  const detailURL = entry =>
    'content.html?id=' + encodeURIComponent(entry.id);

  function renderSelected(category, elementId, limit = 3) {
    const container = document.getElementById(elementId);
    if (!container || !entries.length) return;

    const selected = entries
      .filter(entry => entry.category === category)
      .sort((a, b) =>
        String(b.date || '').localeCompare(String(a.date || ''))
      )
      .slice(0, limit);

    container.innerHTML = selected.map(entry => {
      const title = escapeHTML(entry.title);
      const subtitle = category === 'projects'
        ? entry.name_cn
        : entry.subtitle;

      const people = category === 'publications'
        ? entry.authors
        : entry.team;

      const source = category === 'publications'
        ? entry.source
        : entry.source || entry.location;

      return `
        <li style="margin-bottom:12px">
          <a class="papertitle"
             href="${detailURL(entry)}">
            ${title}
          </a>
          ${subtitle ? `
            <div class="paper_rest">
              ${escapeHTML(subtitle)}
            </div>
          ` : ''}
          ${toText(people) ? `
            <div class="paper_rest">
              ${escapeHTML(toText(people))}
            </div>
          ` : ''}
          ${source ? `
            <div class="paper-venue">
              ${escapeHTML(source)}
            </div>
          ` : ''}
        </li>
      `;
    }).join('');
  }

  renderSelected('publications', 'selected-papers-list', 3);
  renderSelected('projects', 'projects-list', 3);
})();
