/* Content comes only from the owner's local Markdown files. */
const pageEntries = window.PAGE_CONTENT || [];
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const listValue = value => Array.isArray(value) ? value.join(', ') : String(value || '');
const safeURL = value => { const s=String(value||'').trim(); return /^(https?:\/\/|mailto:)/i.test(s) || (!/^[a-z]+:/i.test(s) && !s.startsWith('//')) ? s : ''; };
const detailURL = entry => 'content.html?id='+encodeURIComponent(entry.id);
function entryMeta(entry) {
  if (entry.category === 'publications') {
    return [
      listValue(entry.authors),
      [
        entry.source,
        entry.date?.slice(0, 4),
        entry.pub_type || entry.type
      ].filter(Boolean).join(' · ')
    ].filter(Boolean);
  }

  return [
    entry.source || entry.event || entry.location,
    entry.date,
    entry.pub_type || entry.type
  ].filter(Boolean);
}
const category = document.querySelector('[data-category]')?.dataset.category;
if (category) {
 const entries=pageEntries.filter(e=>e.category===category);
 const search=document.getElementById('content-search'), select=document.getElementById('content-type');
 [...new Set(entries.map(e=>e.pub_type||e.type).filter(Boolean))].sort().forEach(type=>{const option=document.createElement('option');option.value=type;option.textContent=type;select.append(option);});
 function renderList(){
  const query=search.value.toLowerCase().trim();
  const filtered=entries.filter(e=>(!select.value || (e.pub_type||e.type)===select.value) && [e.title,e.subtitle,listValue(e.authors),e.source,listValue(e.tags),listValue(e.keywords)].join(' ').toLowerCase().includes(query));
  let year='';
  document.getElementById('content-list').innerHTML=filtered.map(e=>{
   const next=e.date ? e.date.slice(0,4) : 'Undated';const heading=next!==year ? `<h2 class="content-year">${esc(next)}</h2>`:'';year=next;
   const url=detailURL(e);
   return heading+`<article class="content-row ${e.image?'':'no-image'}">${e.image?`<a href="${url}" tabindex="-1" aria-hidden="true"><img loading="lazy" src="${esc(safeURL(e.image))}" alt=""></a>`:''}<div><h3><a href="${url}">${esc(e.title)}</a></h3>${e.subtitle?`<p>${esc(e.subtitle)}</p>`:''}${entryMeta(e).map(m=>`<p class="content-meta">${esc(m)}</p>`).join('')}<div class="content-tags">${(Array.isArray(e.tags)?e.tags:[]).map(t=>`<span>${esc(t)}</span>`).join('')}</div></div></article>`;
  }).join('') || `<p class="content-empty">${entries.length?'No matching entries.':'No entries yet. / 暂无记录'}</p>`;
 }
 search.addEventListener('input',renderList);select.addEventListener('change',renderList);renderList();
}
const detail=document.getElementById('content-detail');
if(detail){
 const entry=pageEntries.find(e=>e.id===new URLSearchParams(location.search).get('id'));
 if(!entry) detail.innerHTML='<h1>Page not found</h1><p><a href="publications.html">Publications</a> / <a href="projects.html">Projects</a> / <a href="activities.html">Activities</a></p>';
 else {
  document.title=entry.title+' - Wei Feng';
  detail.innerHTML=`<a class="content-back" href="${entry.category}.html">← ${esc(entry.category.toUpperCase())}</a><h1>${esc(entry.title)}</h1>${entry.subtitle?`<p>${esc(entry.subtitle)}</p>`:''}<div class="detail-meta">${entryMeta(entry).map(m=>`<p>${esc(m)}</p>`).join('')}</div>${entry.external_url?`<p><a href="${esc(safeURL(entry.external_url))}" rel="noopener" target="_blank">External link ↗</a></p>`:''}<div class="markdown-body">${marked.parse(entry.body)}</div>`;
  // Markdown is owner-authored; remove executable elements and unsafe URL schemes.
  detail.querySelectorAll('a[href^="/people/"]').forEach(a => a.href = 'https://archialgo.com' + a.getAttribute('href'));
  detail.querySelectorAll('.carousel-control-prev,.carousel-control-next').forEach(el=>el.remove());
  detail.querySelectorAll('script,iframe,object,embed,style,form').forEach(el=>el.remove());
  detail.querySelectorAll('*').forEach(el=>[...el.attributes].forEach(a=>{if(a.name.startsWith('on')||((a.name==='href'||a.name==='src')&&!safeURL(a.value)))el.removeAttribute(a.name);}));
 }
}
document.addEventListener('DOMContentLoaded', () => {
 if (typeof initializeDarkMode === 'function') initializeDarkMode();
 if (typeof initializeBackToTop === 'function') initializeBackToTop();
});
