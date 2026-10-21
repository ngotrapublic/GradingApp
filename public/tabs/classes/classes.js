// Tab "Classes": create a class (course + term + name + variant set), add / remove TAs, rename, delete; the admin also gives classes to lecturers.
const SEASONS=['Spring','Summer','Fall'];
function thisTerm(){ const d=new Date(), m=d.getMonth(); return {season: m<4?'Spring':m<8?'Summer':'Fall', year: d.getFullYear()}; }
async function loadUsers(){ try{ S.users=(await api('/api/users')).users; }catch(e){ S.users=[]; } }

async function renderClasses(m){
  if(!S.users) await loadUsers();
  const me=ME(), ids=Object.keys(S.data.classes), courses=S.data.courses, t0=thisTerm();
  const tas=S.users.filter(u=>u.role==='ta'&&u.active!==0), lecturers=S.users.filter(u=>u.role==='lecturer'||u.role==='admin');
  const seasonSel=(id,cur)=>`<select id="${id}">${SEASONS.map(s=>`<option ${s===cur?'selected':''}>${s}</option>`).join('')}</select>`;
  let h=`<h2>${T('Create a class','Tạo lớp')}</h2><div class="card pad">
    <label class="fl">${T('Course','Môn')}<select id="nc-course">${courses.map(c=>`<option value="${c.code}">${esc(c.code)} – ${esc(c.name)}</option>`).join('')}</select></label>
    <div class="two"><label class="fl">${T('Term','Học kỳ')}${seasonSel('nc-season',t0.season)}</label><label class="fl">${T('Year','Năm')}<input id="nc-year" inputmode="numeric" value="${t0.year}"></label></div>
    <label class="fl">${T('Class name (as on Canvas, e.g. SE009.1)','Tên lớp (như trên Canvas, vd SE009.1)')}<input id="nc-name"></label>
    <label class="fl">${T('Variant set','Bộ đề')}<select id="nc-vset"></select></label>
    ${me.role==='admin'?`<label class="fl">${T('Lecturer in charge','Giảng viên phụ trách')}<select id="nc-owner">${lecturers.map(u=>`<option value="${esc(u.username)}" ${u.id===me.id?'selected':''}>${esc(u.name)} (${esc(u.username)})</option>`).join('')}</select></label>`:''}
    <p class="muted">${T('Classes of the same course and term should use different variant sets, so that neighbouring classes get different numbers.','Các lớp cùng môn, cùng học kỳ nên dùng bộ đề khác nhau để lớp này không chép số của lớp kia.')}</p>
    <div class="btns"><button class="on" id="nc-go">${T('Create class','Tạo lớp')}</button></div></div>`;
  h+=`<h2>${me.role==='admin'?T('All classes','Tất cả các lớp'):T('My classes','Lớp của tôi')} (${ids.length})</h2>`;
  if(!ids.length) h+=`<p class="muted">${T('No class yet.','Chưa có lớp nào.')}</p>`;
  const terms=[...new Set(ids.map(i=>S.data.classes[i].term))].sort(termOrder);
  terms.forEach(t=>{ h+=`<h2 class="muted" style="font-size:14px">${esc(t)}</h2>`;
    ids.filter(i=>S.data.classes[i].term===t).forEach(i=>{ const c=S.data.classes[i], man=canManage(c), sets=(courses.find(x=>x.code===c.course)||{sets:1}).sets;
      h+=`<div class="card pad" data-c="${i}"><div class="row" style="display:flex;gap:8px;align-items:center"><b style="flex:1">${esc(c.name)} <span class="pill">${esc(c.course)}</span>${c.role==='ta'?'<span class="pill">TA</span>':''}</b>
          <button class="btn pri" data-open="${i}">${T('Open','Mở')}</button></div>
        <div class="muted">${esc(c.courseName)} · ${esc(c.term)} · ${T('variant set','bộ đề')} ${c.vset} · ${c.students.length} ${T('students','SV')} · ${T('lecturer','GV')}: ${esc(c.ownerName||c.owner||T('none','chưa có'))}</div>
        <div style="margin-top:6px"><span class="lbl">TA:</span>${c.staff.length?c.staff.map(u=>`<span class="pill">${esc(u.name)} (${esc(u.username)})${man?` <a href="#" data-rmta="${u.id}" title="${T('Remove','Bỏ')}">×</a>`:''}</span>`).join(' '):'<span class="muted">–</span>'}</div>
        ${man?`<details><summary class="muted">${T('Edit this class','Sửa lớp này')}</summary>
          <div class="two"><label class="fl">${T('Add a TA','Thêm TA')}<select data-addta>${['<option value="">–</option>',...tas.filter(u=>!c.staff.some(s=>s.id===u.id)).map(u=>`<option value="${esc(u.username)}">${esc(u.name)} (${esc(u.username)})</option>`)].join('')}</select></label>
          <label class="fl">${T('Variant set','Bộ đề')}<select data-k="vset">${Array.from({length:sets},(_,k)=>`<option ${c.vset===k+1?'selected':''}>${k+1}</option>`).join('')}</select></label></div>
          <div class="two"><label class="fl">${T('Class name','Tên lớp')}<input data-k="name" value="${esc(c.name)}"></label><label class="fl">${T('Term','Học kỳ')}<input data-k="term" value="${esc(c.term)}"></label></div>
          ${me.role==='admin'?`<label class="fl">${T('Lecturer in charge','Giảng viên phụ trách')}<select data-k="owner"><option value="">–</option>${lecturers.map(u=>`<option value="${esc(u.username)}" ${u.username===c.owner?'selected':''}>${esc(u.name)} (${esc(u.username)})</option>`).join('')}</select></label>`:''}
          <p class="muted">${T('Changing the variant set changes every student’s variant – only before the first lab.','Đổi bộ đề làm đổi mã đề của mọi SV – chỉ nên đổi trước Lab 1.')}</p>
          <div class="btns"><button class="on" data-save="${i}">${T('Save','Lưu')}</button><button class="btn warn" data-del="${i}">${T('Delete class','Xóa lớp')}</button></div></details>`:''}
      </div>`; }); });
  m.innerHTML=h;
  // variant set: suggest the first set not used yet by a class of the same course + term
  const fillSets=()=>{ const code=$('#nc-course').value, sets=(courses.find(x=>x.code===code)||{sets:1}).sets, term=`${$('#nc-season').value} ${$('#nc-year').value.trim()}`;
    const used=ids.map(i=>S.data.classes[i]).filter(c=>c.course===code&&c.term===term).map(c=>c.vset), free=Array.from({length:sets},(_,k)=>k+1).find(k=>!used.includes(k))||1;
    $('#nc-vset').innerHTML=Array.from({length:sets},(_,k)=>`<option value="${k+1}" ${k+1===free?'selected':''}>${k+1} (${T('variants','mã đề')} ${k+1}01–${k+1}24)${used.includes(k+1)?' – '+T('used','đã dùng'):''}</option>`).join(''); };
  ['nc-course','nc-season','nc-year'].forEach(id=>$('#'+id).onchange=fillSets); fillSets();
  $('#nc-go').onclick=async()=>{ const body={course:$('#nc-course').value, term:`${$('#nc-season').value} ${$('#nc-year').value.trim()}`, name:$('#nc-name').value.trim(), vset:+$('#nc-vset').value};
    if(me.role==='admin') body.owner=$('#nc-owner').value;
    const r=await api('/api/class_create',body); S.data=r; S.cls=String(r.created); localStorage.setItem('cls',S.cls); S.draft=null;
    toast(T('Class created – now import the student list','Đã tạo lớp – giờ nhập danh sách SV')); S.view='roster'; render(); };
  m.querySelectorAll('[data-open]').forEach(b=>b.onclick=()=>{ S.cls=b.dataset.open; localStorage.setItem('cls',S.cls); S.draft=null; S.open=null; S.view='grade'; render(); });
  m.querySelectorAll('[data-rmta]').forEach(a=>a.onclick=async e=>{ e.preventDefault(); const cls=a.closest('[data-c]').dataset.c;
    S.data=await api('/api/staff_remove',{cls, user_id:+a.dataset.rmta}); toast(T('TA removed','Đã bỏ TA')); renderClasses(m); });
  m.querySelectorAll('[data-addta]').forEach(s=>s.onchange=async()=>{ if(!s.value) return; const cls=s.closest('[data-c]').dataset.c;
    S.data=await api('/api/staff_add',{cls, username:s.value}); toast(T('TA added','Đã thêm TA')); renderClasses(m); });
  m.querySelectorAll('[data-save]').forEach(b=>b.onclick=async()=>{ const box=b.closest('[data-c]'), body={cls:box.dataset.c};
    box.querySelectorAll('[data-k]').forEach(x=>{ if(x.value) body[x.dataset.k]=x.value; });
    S.data=await api('/api/class_update',body); toast(T('Saved','Đã lưu')); render(); });
  m.querySelectorAll('[data-del]').forEach(b=>b.onclick=async()=>{ const c=S.data.classes[b.dataset.del];
    const typed=prompt(T(`Delete ${c.name} (${c.term}) with ALL its students, marks and photos? This cannot be undone.\nType the class name to confirm:`,`Xóa lớp ${c.name} (${c.term}) cùng TOÀN BỘ SV, điểm, ảnh? Không khôi phục được.\nGõ tên lớp để xác nhận:`));
    if(typed===null) return; if(typed.trim()!==c.name) return toast(T('The name does not match – nothing deleted.','Tên không khớp – không xóa.'));
    S.data=await api('/api/class_delete',{cls:b.dataset.del}); toast(T('Class deleted','Đã xóa lớp')); render(); });
}
