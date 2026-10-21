// Tab "Canvas": checks before sending, gradebook import file, marks table.
function labChecks(lab){
  const Lb=K().labs[lab], out=[];
  const st=sorted(), hasVals=s=>(rec(s.sid,lab).values||[]).some(v=>v!==null&&v!==''&&v!==undefined);
  const add=(t,arr)=>{ if(arr.length) out.push(`<li><b>${t}</b>: ${arr.map(s=>esc(s.name)).join(', ')}</li>`); };
  add(T('No team / member (no variant)','Chưa có nhóm / thành viên (không có mã đề)'), st.filter(s=>!variant(s)));
  add(T('Has data but not ticked (measured values get 0)','Có số liệu nhưng chưa tick (số đo đang được 0 điểm)'), st.filter(s=>hasVals(s)&&!rec(s.sid,lab).tick));
  add(T('Ticked but no data (not submitted yet?)','Đã tick nhưng chưa có số liệu (SV chưa nộp bài?)'), st.filter(s=>rec(s.sid,lab).tick&&!hasVals(s)));

  add(T('Score set by hand (check it is intended)','Điểm sửa tay (kiểm tra lại cho chắc)'), st.filter(s=>rec(s.sid,lab).override!=null));
  add(T('No photo of the circuit','Chưa có ảnh mạch'), st.filter(s=>(hasVals(s)||rec(s.sid,lab).tick) && !((((C().photos||{})[lab])||{})[s.sid]||[]).length));
  Lb.manual.forEach(mn=>{
    if(mn[3]==='student') add(T(`“${manLabel(mn)}” not marked`,`Chưa chấm “${manLabel(mn)}”`), st.filter(s=>rec(s.sid,lab).tick && (rec(s.sid,lab).manual||{})[mn[0]]===undefined));
    else { const teams=[...new Set(st.map(s=>s.team).filter(Boolean))].filter(t=>teamRec(t,lab)[mn[0]]===undefined);
      if(teams.length) out.push(`<li><b>${T(`“${manLabel(mn)}” not marked`,`Chưa chấm “${manLabel(mn)}”`)}</b>: ${T('team','nhóm')} ${teams.join(', ')}</li>`); } });
  return out;
}
function buildImport(rows, labs){
  const hd=rows[0], H=hd.map(x=>x.trim().toLowerCase());
  const iName=H.indexOf('student'), iSis=H.indexOf('sis user id'), iSec=H.indexOf('section');
  if(iName<0||iSec<0) return {error:T('Not a Canvas Gradebook export (columns Student / Section are missing).','Không phải file Export của Canvas Gradebook (thiếu cột Student / Section).')};
  const labCol={}; hd.forEach((h,i)=>{ const mm=h.trim().match(/^lab\s*(\d+)\b/i); if(mm && labs().includes(mm[1]) && !(mm[1] in labCol) && !/data/i.test(h) && !/(current|final|unposted)\s+(score|grade|points)/i.test(h)) labCol[mm[1]]=i; });
  const studs=C().students, match=r=>{ const sis=(iSis>=0?r[iSis]:'').trim(); return studs.find(s=>sis&&s.sid.toLowerCase()===sis.toLowerCase()) || studs.find(s=>norm(s.name)===norm(r[iName])); };
  const data=rows.slice(1).filter(r=>(r[iName]||'').trim() && !/points possible/i.test(r[iName]) && !/^test student$/i.test(r[iName].trim()));
  const res={labCol, total:data.length, matched:data.filter(match).length, unmatched:data.filter(r=>!match(r)).map(r=>r[iName]),
             notInFile:studs.filter(s=>!data.some(r=>match(r)===s)).map(s=>s.name)};
  labs=(labs||[]).filter(l=>l in labCol); if(!labs.length) return res;
  const keep=[...Array(iSec+1).keys()], cols=keep.concat(labs.map(l=>labCol[l]));
  const q=v=>{ v=String(v??''); return /[",\n]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v; };
  const out=[cols.map(i=>q(hd[i])).join(',')];
  rows.slice(1).forEach(r=>{ if(!(r[iName]||'').trim()) return; const pp=/points possible/i.test(r[iName]); const st=pp?null:match(r);
    out.push(cols.map((ci,j)=> j<keep.length? q(r[ci]) : (pp? q(r[ci]) : (st? score(st, labs[j-keep.length]) : ''))).join(',')); });
  res.csv='﻿'+out.join('\r\n'); res.labs=labs; return res;
}
function renderSum(m){
  const st=sorted(), lab=S.lab, sy=(C().sync||{})[lab], ch=changedSince(lab), checks=labChecks(lab), gb=S.gbNew||C().gb;
  const done=st.filter(s=>rec(s.sid,lab).tick).length;
  let h = labSeg() + `<div class="stats"><div><b>${st.length}</b>${T('students','SV')}</div><div><b>${done}</b>${T('ticked','đã tick')}</div><div><b>${ch.length}</b>${T('not on Canvas yet','chưa lên Canvas')}</div></div>`;
  h += `<h2>${T(`Step 1 – Check Lab ${lab}`,`Bước 1 – Kiểm tra Lab ${lab}`)}</h2>` + (checks.length? `<div class="card" style="padding:8px 12px"><ul style="margin:0;padding-left:18px">${checks.join('')}</ul></div>` : `<p class="full">${T('Nothing to fix.','Không có gì cần xử lý.')}</p>`);
  h += `<h2>${T('Step 2 – Create the Canvas grades file','Bước 2 – Tạo file điểm cho Canvas')}</h2>`;
  h += `<p class="muted">${sy?T(`Last sent: <b>${esc(sy.time)}</b>. `,`Lần gửi trước: <b>${esc(sy.time)}</b>. `):T('This lab has not been sent yet. ','Chưa gửi lab này lần nào. ')}${ch.length?T(`Changes not sent: ${ch.map(s=>esc(s.name)).join(', ')}.`,`Thay đổi chưa gửi: ${ch.map(s=>esc(s.name)).join(', ')}.`):T('No new changes.','Không có thay đổi mới.')}</p>`;
  h += gb ? `<p class="muted">${T('Canvas gradebook','Sổ điểm Canvas')}: <b>${esc(gb.name||T('saved file','file đã lưu'))}</b>${gb.time?` (${T('saved','lưu')} ${esc(gb.time)})`:''}. ${T('If students were added / removed, export again and choose the new file.','Lớp có thêm / bớt SV thì Export lại và chọn file mới.')}</p>`
          : `<p class="muted">${T(`Canvas → <b>Grades</b> → <b>Export</b> → download the CSV of class <b>${esc(C().name)}</b>, then choose that file (only the first time – the page keeps it).`,`Canvas → <b>Grades</b> → <b>Export</b> → tải CSV của lớp <b>${esc(C().name)}</b>, rồi chọn file đó (chỉ cần làm lần đầu, web sẽ lưu lại).`)}</p>`;
  h += `<div class="btns"><label class="btn" style="cursor:pointer">${gb?T('Choose a new gradebook file','Chọn file sổ điểm mới'):T('Choose the Canvas gradebook file','Chọn file sổ điểm Canvas')}<input type="file" id="gb" accept=".csv,text/csv" hidden></label></div>`;
  let info=null;
  if(gb){ info=buildImport(gb.rows,[]);
    if(info.error) h+=`<p class="zero">${esc(info.error)}</p>`;
    else if(!Object.keys(info.labCol).length) h+=`<p class="zero">${T('The file has no assignment columns named "Lab 1", "Lab 2"…. Create these assignments on Canvas and export again.','File không có cột assignment tên "Lab 1", "Lab 2"…. Tạo các assignment này trên Canvas rồi Export lại.')}</p>`;
    else { const def=new Set([lab, ...labs().filter(l=>changedSince(l).length)]);
      h+=`<p class="muted">${T(`Matched ${info.matched}/${info.total} students.`,`Khớp ${info.matched}/${info.total} SV.`)}${info.unmatched.length?T(` Not matched (left blank): ${info.unmatched.map(esc).join(', ')}.`,` Không khớp (để trống): ${info.unmatched.map(esc).join(', ')}.`):''}${info.notInFile.length?T(` On this page but not in the file: ${info.notInFile.map(esc).join(', ')}.`,` Có trên web nhưng không có trong file: ${info.notInFile.map(esc).join(', ')}.`):''}</p>
      <div class="btns"><span class="lbl">${T('Send labs:','Gửi các lab:')}</span>${Object.keys(info.labCol).sort().map(l=>`<label class="btn" style="padding:6px 10px"><input type="checkbox" data-gl="${l}" ${def.has(l)?'checked':''}> Lab ${l}</label>`).join('')}</div>
      <div class="btns"><button class="on" id="gbdl">${T('Download the Canvas import file','Tải file import Canvas')}</button></div>`; } }
  h += `<h2>${T('Step 3 – On Canvas','Bước 3 – Trên Canvas')}</h2><p class="muted">${T('Canvas → <b>Grades</b> → <b>Import</b> → choose the downloaded file → check the changes → <b>Save</b>. Then post grades / announcements on Canvas as usual.','Canvas → <b>Grades</b> → <b>Import</b> → chọn file vừa tải → kiểm tra các thay đổi → <b>Save</b>. Sau đó công bố điểm / thông báo cho SV trên Canvas như bình thường.')}</p>`;
  h += `<h2>${T('Marks','Bảng điểm')} ${esc(C().name)}</h2><div class="card scroll"><table><tr><th>${T('Name','Họ tên')}</th><th>${T('Team','Nhóm')}</th>${labs().map(l=>`<th>Lab ${l}<br><small>/${K().labs[l].total}</small></th>`).join('')}<th>${T('Total','Tổng')}<br><small>/${labs().reduce((a,l)=>a+K().labs[l].total,0)}</small></th></tr>
   ${st.map(s=>{ const sc=labs().map(l=>score(s,l)); return `<tr><td>${esc(s.name)}<br><small class="muted">${esc(s.sid)}</small></td><td>${s.team||'–'}</td>${sc.map((x,i)=>{ const c=changedSince(labs()[i]).includes(s); return `<td class="num" ${c?'style="background:#fff7e0"':''}>${x}</td>`; }).join('')}<td class="num"><b>${sc.reduce((a,b)=>a+b,0)}</b></td></tr>`; }).join('')}
   </table></div><p class="muted">${T('Yellow cells: marks changed but not sent to Canvas yet.','Ô vàng: điểm đã đổi, chưa đưa lên Canvas.')}</p>
   <div class="btns"><a class="btn" href="/api/export.xlsx?cls=${S.cls}" style="text-decoration:none">${T('Download Excel (this class)','Tải Excel (lớp này)')}</a><a class="btn" href="/api/export.xlsx" style="text-decoration:none">${T('Excel: all my classes','Excel: tất cả lớp của tôi')}</a></div>`;
  m.innerHTML=h; bindSeg(m);
  $('#gb').onchange=async e=>{ const f=e.target.files[0]; if(!f) return; const rows=parseCSV((await f.text()).replace(/^﻿/,''));
    if(rows.length<2){ toast(T('Empty file','File trống')); return; } S.gbNew={rows, name:f.name, time:T('not saved yet','chưa lưu')}; renderSum(m); };
  if($('#gbdl')) $('#gbdl').onclick=async()=>{ const labs=[...document.querySelectorAll('[data-gl]:checked')].map(x=>x.dataset.gl);
    if(!labs.length){ toast(T('Choose at least 1 lab','Chọn ít nhất 1 lab')); return; }
    const r=buildImport(gb.rows, labs); if(!r.csv){ toast(T('Could not create the file','Không tạo được file')); return; }
    const a=document.createElement('a'); a.href=URL.createObjectURL(new Blob([r.csv],{type:'text/csv'}));
    a.download=`Canvas_import_${C().name.replace(/\W+/g,'_')}_Lab${labs.join('-')}.csv`; a.click();
    const scores={}; labs.forEach(l=>{ scores[l]={}; C().students.forEach(s=>scores[l][s.sid]=score(s,l)); });
    S.data=await api('/api/sync',{cls:S.cls, scores, gb:S.gbNew?S.gbNew.rows:null, gbname:S.gbNew?S.gbNew.name:''}); S.gbNew=null;
    toast(T('File created. Go to Canvas → Grades → Import','Đã tạo file. Vào Canvas → Grades → Import')); renderSum(m); };
}
