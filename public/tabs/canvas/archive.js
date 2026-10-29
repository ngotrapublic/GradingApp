// Archive of one class: an Excel file made in the browser (ExcelJS), one sheet per lab with the marks, the submitted values
// and the photos of every student on the same row, plus a "Tổng" sheet. Made in the browser because a class has too many
// photos for one server response (Vercel limit 4.5 MB); the photos are fetched one by one from /api/photo/<id>.jpg.
const EXCELJS = 'https://cdnjs.cloudflare.com/ajax/libs/exceljs/4.4.0/exceljs.min.js';
const PHOTO_H = 150;                                           // photo height in the sheet (px)

function loadScript(src){
  return new Promise((ok, bad) => { if(window.ExcelJS) return ok();
    const s=document.createElement('script'); s.src=src; s.onload=ok; s.onerror=()=>bad(new Error('load')); document.head.appendChild(s); });
}

async function fetchPhoto(id){
  const r = await fetch(`/api/photo/${id}.jpg`); if(!r.ok) return null;
  const blob = await r.blob(); const buf = await blob.arrayBuffer();
  let w=4, h=3; try { const bm=await createImageBitmap(blob); w=bm.width; h=bm.height; bm.close&&bm.close(); } catch(e) {}
  return {buf, w, h};
}

async function downloadArchive(btn){
  const cls=C(), st=sorted(), all=labs();
  const head=['MSSV','Họ tên','Nhóm','TV','Mã đề'];
  const green={type:'pattern', pattern:'solid', fgColor:{argb:'FF549E39'}};
  const style=row=>{ row.eachCell(c=>{ c.font={bold:true, color:{argb:'FFFFFFFF'}}; c.fill=green; c.alignment={horizontal:'center', vertical:'middle', wrapText:true}; }); };
  const label=btn.textContent; btn.disabled=true;
  try {
    btn.textContent=T('Loading…','Đang tải…'); await loadScript(EXCELJS);
    const wb=new ExcelJS.Workbook(); wb.creator='Lab grading';
    // sheet "Tổng": marks of every lab
    const sum=wb.addWorksheet('Tổng');
    const full=all.reduce((a,l)=>a+K().labs[l].total,0);
    style(sum.addRow([...head, ...all.map(l=>`Lab ${l} (/${K().labs[l].total})`), `Tổng /${full}`, 'Quy về /10']));
    st.forEach(s=>{ const sc=all.map(l=>score(s,l)); const t=sc.reduce((a,b)=>a+b,0);
      sum.addRow([s.sid, s.name, s.team||'', s.member||'', variant(s)||'', ...sc, t, Math.round(t/full*1000)/100]); });
    sum.columns.forEach((c,i)=>c.width=[14,28,7,5,8][i]||11); sum.views=[{state:'frozen', xSplit:2, ySplit:1}];
    // photos to fetch
    const jobs=[]; all.forEach(l=>st.forEach(s=>((((cls.photos||{})[l])||{})[s.sid]||[]).forEach(p=>jobs.push(p.id))));
    const got={}; let done=0;
    const worker=async()=>{ while(jobs.length){ const id=jobs.shift(); got[id]=await fetchPhoto(id).catch(()=>null);
      done++; btn.textContent=T(`Photos ${done}…`,`Ảnh ${done}…`); } };
    await Promise.all([1,2,3,4,5,6].map(worker));
    // one sheet per lab: marks + values + photos on the same row
    all.forEach(l=>{
      const Lb=K().labs[l], ws=wb.addWorksheet(`Lab ${l}`);
      const nph=Math.max(1, ...st.map(s=>((((cls.photos||{})[l])||{})[s.sid]||[]).length));
      const qs=Lb.questions.map(q=>`${q[1]}${q[2]&&q[2]!=='–'?` (${q[2]})`:''}`);
      style(ws.addRow([...head, ...qs, ...Lb.manual.map(m=>manLabel(m)), T('Ticked','Đã tick'), `Điểm (/${Lb.total})`,
                       ...Array.from({length:nph},(_,i)=>`Ảnh ${i+1}`)]));
      const pc=head.length+qs.length+Lb.manual.length+2;   // first photo column (0-based)
      st.forEach((s,k)=>{
        const r=rec(s.sid,l), v=r.values||[];
        const man=Lb.manual.map(m=>m[3]==='student'? (r.manual||{})[m[0]] ?? '' : (s.team? teamRec(s.team,l)[m[0]] ?? '' : ''));
        const row=ws.addRow([s.sid, s.name, s.team||'', s.member||'', variant(s)||'', ...qs.map((_,i)=>v[i]===null||v[i]===undefined||v[i]===''? '' : (isNaN(+v[i])? v[i] : +v[i])),
                             ...man, r.tick? '✓' : '', score(s,l)]);
        row.alignment={vertical:'middle'};
        const ph=((((cls.photos||{})[l])||{})[s.sid]||[]);
        if(ph.length) row.height=PHOTO_H*0.75+6;
        ph.forEach((p,i)=>{ const im=got[p.id]; if(!im) return;
          const id=wb.addImage({buffer:im.buf, extension:'jpeg'});
          ws.addImage(id, {tl:{col:pc+i+0.05, row:k+1+0.05}, ext:{width:Math.round(PHOTO_H*im.w/im.h), height:PHOTO_H}}); });
      });
      ws.columns.forEach((c,i)=>c.width= i<head.length? [14,28,7,5,8][i] : i<pc? 13 : 30);
      ws.views=[{state:'frozen', xSplit:2, ySplit:1}];
    });
    const out=await wb.xlsx.writeBuffer();
    const a=document.createElement('a'); a.href=URL.createObjectURL(new Blob([out],{type:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}));
    a.download=`Luu_tru_${cls.name}_${cls.term}`.replace(/[^\w.-]+/g,'_')+'.xlsx'; a.click();
    toast(T('Excel with photos downloaded','Đã tải Excel kèm ảnh'));
  } catch(e) { toast(T('Could not create the file (check the internet connection)','Không tạo được file (kiểm tra kết nối mạng)')); }
  finally { btn.disabled=false; btn.textContent=label; }
}
