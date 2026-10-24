// Tab "Class": import class lists (file / paste), random teams, edit teams.
function renderRoster(m){
  if(!S.draft) S.draft = { name:C().name, students: sorted().map(s=>({...s})) };
  const D=S.draft, used={};
  D.students.forEach(s=>{ if(s.team&&s.member){ const k=s.team+'-'+s.member; used[k]=(used[k]||0)+1; } });
  const opt=(n,cur)=>`<option value="">–</option>`+Array.from({length:n},(_,i)=>`<option ${+cur===i+1?'selected':''}>${i+1}</option>`).join('');
  m.innerHTML = `<h2>${T('Import the class list','Nhập danh sách lớp')}</h2>
    <p class="muted">${T('After import, students are <b>put into teams at random</b> right away (6 teams × 3; extra students make a team of 4). You can edit by hand or press “Shuffle teams again”.','Nhập xong là web <b>chia nhóm ngẫu nhiên ngay</b> (6 nhóm × 3; dư thì có nhóm 4 người). Có thể sửa tay hoặc bấm “Chia lại ngẫu nhiên”.')}</p>
    <p class="muted">${T('Choose <b>one or all 3 files</b> (Canvas → People → export to Excel, or any .xlsx / .csv list). A file goes to the class whose name matches its <b>Section</b> column (e.g. SE009.1 → class “SE009.1”, same course and term), otherwise to the class you are viewing; only rows with <b>Role = Student</b> are taken; “pending” and “(He/Him)” are removed from names. Existing students keep their team and member number.','Chọn <b>một hoặc cả 3 file</b> danh sách (Canvas → People → xuất Excel, hoặc file .xlsx / .csv khác). File nào có cột <b>Section</b> trùng tên một lớp của bạn (vd SE009.1 → lớp “SE009.1”, cùng môn, cùng học kỳ) thì vào lớp đó, không thì vào lớp đang xem; chỉ lấy dòng <b>Role = Student</b>, bỏ chữ “pending”, “(He/Him)” trong tên. SV đã có thì giữ nguyên nhóm và thành viên.')}</p>
    <div class="btns"><label class="btn pri" style="cursor:pointer">${T('Choose class list file(s) (.xlsx / .csv)','Chọn file danh sách (.xlsx / .csv)')}<input type="file" id="rfile" accept=".xlsx,.csv,text/csv" multiple hidden></label></div>
    <p class="muted">${T('Or select the table in Excel (including the header row), copy it, and paste it here:','Hoặc bôi đen bảng trong Excel (kể cả dòng tiêu đề), Copy, rồi dán vào đây:')}</p>
    <textarea id="paste" placeholder="${T('Paste from Excel here (Ctrl/Cmd + V)','Dán từ Excel vào đây (Ctrl/Cmd + V)')}"></textarea>
    <div class="btns"><button class="on" id="add">${T('Import pasted rows','Nhập phần đã dán')}</button></div>
    <div id="impres"></div>
    <h2>${T('Current class','Lớp đang xem')}: ${esc(C().name)}</h2>
    <input type="text" id="cname" value="${esc(D.name)}">
    <h2>${T(`Students (${D.students.length})`,`Danh sách (${D.students.length} SV)`)}</h2><p class="muted">${T('6 teams (6 tables), members 1, 2, 3 in each team. With 19–24 students, a team of 4 gets member 4. Variant: members 1–3 = set×100 + 3×(team−1) + member; member 4 = set×100 + 18 + team (variant set of this class: ${C().vset}).','6 nhóm (6 bàn), mỗi nhóm thành viên 1, 2, 3. Lớp 19–24 SV thì nhóm nào có 4 người chọn thêm thành viên 4. Mã đề: thành viên 1–3 = bộ đề×100 + 3×(nhóm−1) + TV; thành viên 4 = bộ đề×100 + 18 + nhóm (bộ đề của lớp này: ${C().vset}).')}</p>
    <div class="card roster scroll"><table><tr><th>${T('No.','STT')}</th><th>${T('Name','Họ tên')}</th><th>${T('Student ID','MSSV')}</th><th>${T('Team','Nhóm')}</th><th>${T('M','TV')}</th><th>${T('Var.','Mã')}</th><th title="${T('Student page password','Mật khẩu trang SV')}">${T('Password','Mật khẩu')}</th><th></th></tr>
    ${D.students.map((s,i)=>{ const dup = s.team&&s.member&&used[s.team+'-'+s.member]>1;
      return `<tr class="${dup?'bad':''}"><td class="num">${i+1}</td><td>${esc(s.name)}</td><td>${esc(s.sid)}</td><td><select data-i="${i}" data-k="team">${opt(6,s.team)}</select></td>
      <td><select data-i="${i}" data-k="member">${opt(4,s.member)}</select></td><td>${variant(s)||'–'}</td><td>${s.hasPin?`<button class="btn" data-pinreset="${esc(s.sid)}" title="${T('Reset password','Đặt lại mật khẩu')}" style="padding:3px 8px">✓ ↺</button>`:'<span class="muted">–</span>'}</td><td><button class="btn warn" data-del="${i}" style="padding:3px 8px">×</button></td></tr>`; }).join('')}
    </table></div>
    <div class="btns"><button class="on" id="saveR">${T('Save teams / members','Lưu nhóm / thành viên')}</button><button id="cancelR">${T('Discard changes','Hủy thay đổi')}</button><button class="btn warn" id="shuffle">${T('Shuffle teams again','Chia lại ngẫu nhiên')}</button></div>
    ${Object.values(used).some(n=>n>1)?`<p class="zero">${T('Some students share the same team + member (red rows).','Có SV trùng nhóm + thành viên (dòng tô đỏ).')}</p>`:''}`;
  $('#cname').oninput=e=>D.name=e.target.value;
  // import parsed rows into the right class (by Section), saved immediately; unsaved team edits of the open class are kept
  const importRows=async(rows, label)=>{
    const got=rosterFromRows(rows);
    if(!got.list.length) return `<li>${esc(label)}: <span class="zero">${T('no student-ID / name columns found','không tìm thấy cột MSSV / họ tên')}</span></li>`;
    // a file whose Section names another of my classes (same course + term) goes to that class
    const same=Object.values(S.data.classes).filter(c=>c.course===C().course&&c.term===C().term&&canManage(c));
    const hit=got.section && same.find(c=>c.name.replace(/\s/g,'').toUpperCase()===got.section.name);
    const cls = hit ? String(hit.id) : S.cls;
    const body={cls, students:got.list};
    S.data=await api('/api/roster_merge', body);
    if(cls===S.cls){ const keep={}; D.students.forEach(s=>{ if(s.team&&s.member) keep[s.sid]=s; });
      S.draft={ name: D.name, students: sorted().map(s=>({...s, ...(keep[s.sid]?{team:keep[s.sid].team, member:keep[s.sid].member}:{}) })) }; }
    return `<li>${esc(label)} → <b>${esc(S.data.classes[cls].name)}</b>: ${got.list.length} ${T('students','SV')}${got.skipped?T(` (skipped ${got.skipped} non-student rows)`,` (bỏ qua ${got.skipped} dòng không phải Student)`):''}</li>`;
  };
  const showRes=(items)=>{ renderRoster(m); $('#impres').innerHTML=`<div class="card" style="padding:8px 12px"><b>${T('Imported','Đã nhập')}</b><ul style="margin:4px 0;padding-left:18px">${items.join('')}</ul></div>`; };
  $('#rfile').onchange=async e=>{ const files=[...e.target.files]; if(!files.length) return; const res=[];
    for(const f of files){ let rows;
      try{
        if(/\.csv$/i.test(f.name)) rows=parseCSV((await f.text()).replace(/^﻿/,''));
        else { const buf=new Uint8Array(await f.arrayBuffer()); let bin=''; for(let i=0;i<buf.length;i+=32768) bin+=String.fromCharCode(...buf.subarray(i,i+32768));
               rows=(await api('/api/readsheet',{cls:S.cls,b64:btoa(bin)})).rows; }
      }catch(err){ res.push(`<li>${esc(f.name)}: <span class="zero">${T('could not read','không đọc được')}</span></li>`); continue; }
      res.push(await importRows(rows, f.name)); }
    showRes(res); toast(T('Class list imported','Đã nhập danh sách')); };
  $('#add').onclick=async()=>{ const t=$('#paste').value; if(!t.trim()) return;
    const rows=t.split(/\r?\n/).filter(l=>l.trim()).map(l=>l.includes('\t')? l.split('\t') : l.split(/;|,(?=\s*\S)/));
    const r=await importRows(rows,T('Pasted rows','Phần đã dán')); $('#paste').value=''; showRes([r]); toast(T('Class list imported','Đã nhập danh sách')); };
  m.querySelectorAll('[data-pinreset]').forEach(b=>b.onclick=async()=>{ if(!confirm(T('Reset this student\'s password? They create a new one at the next sign-in (the same password is used for all their lab courses).','Đặt lại mật khẩu của SV này? SV sẽ tự tạo mật khẩu mới ở lần đăng nhập sau (một mật khẩu dùng cho mọi môn lab).'))) return;
    S.data=await api('/api/student_pw_reset',{cls:S.cls,sid:b.dataset.pinreset}); if(S.draft) S.draft.students.forEach(s=>{ if(s.sid===b.dataset.pinreset) s.hasPin=false; }); toast(T('Password reset','Đã đặt lại mật khẩu')); renderRoster(m); });
  m.querySelectorAll('select[data-i]').forEach(s=>s.onchange=()=>{ D.students[s.dataset.i][s.dataset.k]= s.value?+s.value:null; renderRoster(m); });
  m.querySelectorAll('[data-del]').forEach(b=>b.onclick=()=>{ if(confirm(T('Remove this student from the list?','Xóa SV này khỏi danh sách?'))){ D.students.splice(+b.dataset.del,1); renderRoster(m);} });
  $('#saveR').onclick=async()=>{ S.data=await api('/api/class',{cls:S.cls,name:D.name,students:D.students}); S.draft=null; toast(T('Saved','Đã lưu')); render(); };
  $('#cancelR').onclick=()=>{ S.draft=null; renderRoster(m); };
  $('#shuffle').onclick=async()=>{ const graded=Object.values(C().labs||{}).some(l=>Object.keys(l).length);
    if(!confirm(graded? T('This class ALREADY HAS MARKS. Shuffling changes the students’ variants and breaks the marks already given. Shuffle anyway?','Lớp này ĐÃ CÓ ĐIỂM. Chia lại sẽ đổi mã đề của SV và làm sai đáp án đã chấm. Vẫn chia lại?') : T('Put all students of this class into new random teams?','Chia lại toàn bộ nhóm của lớp này một cách ngẫu nhiên?'))) return;
    S.data=await api('/api/shuffle',{cls:S.cls}); S.draft=null; toast(T('Teams shuffled','Đã chia lại nhóm')); renderRoster(m); };
}

// roster rows (file or pasted): find header, ID / name / role / section columns
const cleanName = s => String(s||'').replace(/\([^)]*\)/g,' ').replace(/\bpending\b/ig,' ').replace(/\s+/g,' ').trim();
function rosterFromRows(rows){
  const N=x=>norm(x).replace(/[^a-z0-9 ]/g,' ').replace(/\s+/g,' ').trim();
  const sidKeys=['mssv','ma sv','ma sinh vien','roll number','roll','student id','studentid','sis user id','sis id','sis_id','member code','login id','student code','code'];
  const nameKeys=['ho ten','ho va ten','full name','fullname','student name','name','student','sinh vien'];
  let hi=-1, cs=-1, cn=-1, cl=-1, cf=-1, ct=-1, cm=-1, cr=-1, csec=-1;
  for(let i=0;i<Math.min(rows.length,15) && hi<0;i++){ const h=rows[i].map(N);
    const find=keys=>{ for(const k of keys){ const j=h.findIndex(x=>x===k||x.startsWith(k+' ')||x.endsWith(' '+k)); if(j>=0) return j; } return -1; };
    const s_=find(sidKeys), n_=find(nameKeys), last=h.findIndex(x=>x==='ho'||x==='ho dem'||x==='surname'||x==='last name'), first=h.findIndex(x=>x==='ten'||x==='first name'||x==='given name');
    if(s_>=0 && (n_>=0 || (last>=0&&first>=0))){ hi=i; cs=s_; cn=n_; cl=last; cf=first;
      ct=h.findIndex(x=>x==='nhom'||x==='team'||x==='group'); cm=h.findIndex(x=>x==='tv'||x==='thanh vien'||x==='member');
      cr=h.findIndex(x=>x==='role'||x==='vai tro'); csec=h.findIndex(x=>x==='section'||x==='lop'); } }
  const list=[]; let skipped=0, section=null;
  if(hi<0){ // no header: column 1 = ID, column 2 = name
    rows.forEach(r=>{ const c=r.map(x=>String(x).trim()).filter(x=>x); if(c.length>=2 && /\d{3,}/.test(c[0])) list.push({sid:c[0],name:cleanName(c[1]),team:+c[2]||null,member:+c[3]||null}); });
    return {list, skipped, section}; }
  rows.slice(hi+1).forEach(r=>{
    if(cr>=0 && String(r[cr]||'').trim() && !/student|sinh vi/i.test(r[cr])){ skipped++; return; }
    const sid=String(r[cs]||'').trim();
    let name=cn>=0? String(r[cn]||'').trim() : (String(r[cl]||'').trim()+' '+String(r[cf]||'').trim()).trim();
    name=cleanName(name);
    if(!sid || !name || /^(test student|student, test)$/i.test(name)) return;
    if(csec>=0 && !section){ const mm=String(r[csec]||'').match(/\b([A-Z]{2,4}\s*\d{2,4}\s*\.\s*\d+)\b/i); if(mm) section={name:mm[1].replace(/\s/g,'').toUpperCase()}; }
    list.push({sid,name,team:ct>=0?(+r[ct]||null):null,member:cm>=0?(+r[cm]||null):null}); });
  return {list, skipped, section};
}
