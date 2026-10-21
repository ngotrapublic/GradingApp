// Small helpers: DOM, escaping, toast, number format, subscripts, CSV parsing, name normalising.
const $ = s => document.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function toast(t){const e=$('#toast');e.textContent=t;e.classList.add('show');clearTimeout(e._t);e._t=setTimeout(()=>e.classList.remove('show'),1600)}
const fmt = x => { if(x===null||x===undefined||x===''||isNaN(+x)) return '–'; x=+x; const a=Math.abs(x);
  return a>=1000? x.toFixed(0) : a>=100? x.toFixed(1) : a>=10? x.toFixed(2) : x.toFixed(3); };
const sub = s => esc(s).replace(/\b([A-Za-z]{1,2})_([A-Za-z0-9,]+)/g,'$1<sub>$2</sub>');
function parseCSV(t){ const rows=[]; let row=[], f='', q=false;
  for(let i=0;i<t.length;i++){ const c=t[i];
    if(q){ if(c==='"'){ if(t[i+1]==='"'){f+='"';i++;} else q=false; } else f+=c; }
    else if(c==='"') q=true; else if(c===','){ row.push(f); f=''; } else if(c==='\n'||c==='\r'){ if(c==='\r'&&t[i+1]==='\n') i++; row.push(f); rows.push(row); row=[]; f=''; } else f+=c; }
  if(f!==''||row.length){ row.push(f); rows.push(row); } return rows.filter(r=>r.some(x=>x.trim()!==''));
}
const norm = s => String(s||'').normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/đ/g,'d').replace(/Đ/g,'D').toLowerCase().replace(/\s+/g,' ').trim();
