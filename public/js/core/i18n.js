// Language: English (default) / Vietnamese. T(english, vietnamese) returns the text for the current language.
let LANG = 'en'; try { LANG = localStorage.getItem('lang') || 'en'; } catch(e) {}
const T = (en, vi) => LANG === 'vi' ? vi : en;
function setLang(l){ LANG=l; try{ localStorage.setItem('lang', l); }catch(e){} document.documentElement.lang=l; document.title=T('Lab grading','Chấm Lab'); render(); }
// Two-position toggle  [ EN | VI ]  – the active language is highlighted.
const langToggle = () => `<div class="lang-toggle" role="radiogroup" aria-label="Language / Ngôn ngữ">${['en','vi'].map(l=>
  `<button type="button" role="radio" aria-checked="${LANG===l}" data-lang="${l}" class="${LANG===l?'on':''}">${l.toUpperCase()}</button>`).join('')}</div>`;
function bindLangToggle(root){ root.querySelectorAll('.lang-toggle [data-lang]').forEach(b=>b.onclick=()=>{ if(b.dataset.lang!==LANG) setLang(b.dataset.lang); }); }
