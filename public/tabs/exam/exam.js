// Tab "Exam": the final exam. Students write their results on the exam paper; the examiner marks here with the rubric
// (keys "exam"): group items once per exam group, contribution / personal skills / penalty per student.
// Exam groups are drawn at random on the exam day (absent students left out), up to 3 per group, within the class.
const exRec = sid => rec(sid, 'exam');
const exMan = sid => exRec(sid).manual || {};
const exTeam = g => teamRec(g, 'exam');

function exGroups(){
  const by = {};
  sorted().forEach(s => { const g = exMan(s.sid).group; if(g && !exMan(s.sid).absent) (by[g] = by[g] || []).push(s); });
  return by;
}
// random groups of 3 (the last ones of 2 when the number does not divide), with crypto randomness
function exDraw(present, size){
  const a = [...present], r = new Uint32Array(a.length); crypto.getRandomValues(r);
  for(let i = a.length - 1; i > 0; i--){ const j = r[i] % (i + 1); [a[i], a[j]] = [a[j], a[i]]; }
  const n = Math.ceil(a.length / size), out = {};
  a.forEach((s, i) => { out[s.sid] = i % n + 1; });
  return out;
}
const exBtns = (vals, cur, attrs) => vals.map(v => `<button class="${cur !== undefined && +cur === v ? 'on' : ''}" ${attrs} data-val="${v}">${v}</button>`).join('');
const range = n => [...Array(n + 1).keys()];

function renderExam(m){
  const E = K().exam;
  if(!E){ m.innerHTML = `<p class="muted">${T('This course has no exam rubric.','Môn này chưa có rubric thi.')}</p>`; return; }
  const st = sorted(), groups = exGroups(), gids = Object.keys(groups).map(Number).sort((a,b)=>a-b);
  const absent = st.filter(s => exMan(s.sid).absent), noGroup = st.filter(s => !exMan(s.sid).absent && !exMan(s.sid).group);
  const graded = st.filter(s => examParts(s).graded || examParts(s).absent).length;
  const gsum = g => E.group.filter(x=>x[3]).reduce((a,x)=>a+(+exTeam(g)[x[0]]||0),0);
  let h = `<div class="stats"><div><b>${st.length}</b>${T('students','SV')}</div><div><b>${absent.length}</b>${T('absent','vắng')}</div><div><b>${gids.length}</b>${T('groups','nhóm thi')}</div><div><b>${graded}</b>${T('graded','đã chấm xong')}</div></div>
    <p class="muted">${T('Students write their results on the exam paper. Mark here with the rubric: the group part once for the whole group, then each student.','SV vẫn ghi kết quả vào giấy thi. Chấm ở đây theo rubric: phần nhóm chấm một lần cho cả nhóm, rồi từng SV.')}</p>`;
  // before the exam: absent students, draw the groups
  if(canManage()){
    h += `<details class="card" ${gids.length ? '' : 'open'} style="padding:10px 12px"><summary><b>${T('1. Absent students and exam groups','1. SV vắng và bốc nhóm thi')}</b></summary>
      <p class="muted">${T('Tap the students who are absent (they get 0 and no group). Then draw the groups: random, '+E.groupSize+' per group (some groups of '+(E.groupSize-1)+' if needed).','Bấm vào SV vắng (SV vắng được 0, không vào nhóm). Rồi bốc nhóm: ngẫu nhiên, mỗi nhóm '+E.groupSize+' SV (vài nhóm '+(E.groupSize-1)+' nếu lẻ).')}</p>
      <div class="btns">${st.map(s => `<button class="${exMan(s.sid).absent ? 'warn on' : ''}" data-absent="${esc(s.sid)}">${esc(s.name)}${exMan(s.sid).absent ? ' – '+T('absent','vắng') : ''}</button>`).join('')}</div>
      <div class="btns"><button class="on" id="exdraw">${gids.length ? T('Draw the groups again (deletes the group marks)','Bốc lại nhóm (xóa điểm nhóm đã chấm)') : T('Draw the exam groups','Bốc nhóm thi')}</button></div>
      ${noGroup.length && gids.length ? `<p class="zero">${T('Present but without a group','Có mặt nhưng chưa có nhóm')}: ${noGroup.map(s=>esc(s.name)).join(', ')} – ${T('choose a group for them below.','chọn nhóm cho các bạn này ở dưới.')}</p>
        <div class="btns">${noGroup.map(s=>`<label class="lbl">${esc(s.name)} <select data-move="${esc(s.sid)}"><option value="">–</option>${gids.map(g=>`<option value="${g}">${T('Group','Nhóm')} ${g}</option>`).join('')}<option value="${(gids.at(-1)||0)+1}">${T('New group','Nhóm mới')}</option></select></label>`).join('')}</div>` : ''}
    </details>`;
  }
  if(!gids.length){ h += `<p class="muted">${T('No exam groups yet.','Chưa có nhóm thi.')}</p>`; m.innerHTML = h; bindExam(m); return; }
  h += `<h2>${T('2. Mark each group','2. Chấm từng nhóm')}</h2>`;
  gids.forEach(g => {
    const mem = groups[g], open = S.exOpen === g, done = E.group.filter(x=>x[3] && exTeam(g)[x[0]] !== undefined).length, n = E.group.filter(x=>x[3]).length;
    h += `<div class="card"><div class="team" data-exg="${g}" style="cursor:pointer"><span class="sp">${T('Group','Nhóm')} ${g}</span>
      <span class="lbl">${mem.map(s=>esc(s.name)).join(', ')}</span><span class="sc">${gsum(g)}/35</span>
      <span class="chip ${done===n?'tick':'open'}">${done}/${n}</span></div>`;
    if(open){
      h += `<div class="panel">`;
      E.group.forEach(x => {
        if(!x[3]){ h += `<div class="lbl" style="margin-top:8px"><b>${esc(T(x[1],x[2]))}</b></div>`; return; }
        h += `<div class="btns"><span class="lbl" style="flex:1 1 220px">${esc(T(x[1],x[2]))} <small class="muted">/${x[3]}</small></span>${exBtns(range(x[3]), exTeam(g)[x[0]], `data-exitem="${x[0]}" data-g="${g}"`)}</div>`;
      });
      h += `<p><b>${T('Group work','Phần nhóm')}: ${gsum(g)} / 35</b></p>`;
      mem.forEach(s => {
        const man = exMan(s.sid), p = examParts(s);
        h += `<div class="card" style="padding:8px 10px;margin:8px 0"><div><b>${esc(s.name)}</b> <small class="muted">${esc(s.sid)}</small>
          <span class="sc" style="float:right">${p.fail ? `<span class="zero">${T('FAIL','RỚT')} 0</span>` : p.total} / ${E.total}</span></div>`;
        E.individual.forEach(x => {
          h += `<div class="btns"><span class="lbl" style="flex:1 1 220px">${esc(T(x[1],x[2]))}</span>${exBtns(range(x[3]), man[x[0]], `data-exind="${x[0]}" data-sid="${esc(s.sid)}"`)}</div>`;
        });
        const P = E.penalty;
        h += `<div class="btns"><span class="lbl" style="flex:1 1 220px">${esc(T(P[1],P[2]))}</span>${exBtns([0,1,2,3,5,10], man.penalty, `data-exind="penalty" data-sid="${esc(s.sid)}"`)}</div>
          <div class="btns"><input data-exnote="${esc(s.sid)}" value="${esc(man.note||'')}" placeholder="${T('Note (e.g. late, what you asked)','Ghi chú (vd đi trễ, câu đã hỏi)')}" style="flex:1">
          ${canManage() ? `<select data-move="${esc(s.sid)}">${gids.map(x=>`<option value="${x}" ${x===g?'selected':''}>${T('Group','Nhóm')} ${x}</option>`).join('')}<option value="${(gids.at(-1)||0)+1}">${T('New group','Nhóm mới')}</option></select>` : ''}</div></div>`;
      });
      h += `</div>`;
    }
    h += `</div>`;
  });
  // all marks
  h += `<h2>${T('3. Exam marks','3. Bảng điểm thi')} ${esc(C().name)}</h2><div class="card scroll"><table><tr><th>${T('Name','Họ tên')}</th><th>${T('Group','Nhóm')}</th><th>${T('Group','Nhóm')}<br><small>/35</small></th><th>${T('Indiv.','Cá nhân')}<br><small>/15</small></th><th>${T('Minus','Trừ')}</th><th>${T('Total','Tổng')}<br><small>/${E.total}</small></th></tr>
    ${[...st].sort((a,b) => (examParts(a).group||99) - (examParts(b).group||99) || a.name.localeCompare(b.name,'vi')).map(s => { const p = examParts(s); return `<tr><td>${esc(s.name)}<br><small class="muted">${esc(s.sid)}</small></td><td>${p.absent ? T('absent','vắng') : (p.group || '–')}</td><td class="num">${p.grp}</td><td class="num">${p.ind}</td><td class="num">${p.pen ? '−'+p.pen : ''}</td><td class="num ${p.fail ? 'zero' : ''}"><b>${p.total}</b>${p.fail && !p.absent ? ' '+T('FAIL','RỚT') : ''}${!p.graded && !p.absent ? ` <small class="muted">${T('(not finished)','(chưa xong)')}</small>` : ''}</td></tr>`; }).join('')}
    </table></div><p class="muted">${T('Send the exam marks to Canvas in the Canvas tab (column "Final exam").','Gửi điểm thi lên Canvas ở tab Gửi Canvas (cột "Final exam").')}</p>`;
  m.innerHTML = h; bindExam(m);
}

function bindExam(m){
  const save = async (sid, patch) => { S.data = await api('/api/record', {cls:S.cls, lab:'exam', sid, manual:{...exMan(sid), ...patch}}); };
  m.querySelectorAll('[data-absent]').forEach(b => b.onclick = async () => { const sid = b.dataset.absent, on = !exMan(sid).absent;
    await save(sid, {absent: on}); toast(on ? T('Marked absent','Đã đánh dấu vắng') : T('Present','Có mặt')); renderExam(m); });
  if($('#exdraw')) $('#exdraw').onclick = async () => {
    const had = Object.keys(exGroups()).length;
    if(had && !confirm(T('Draw again? All group marks of the exam are deleted.','Bốc lại? Mọi điểm nhóm của bài thi sẽ bị xóa.'))) return;
    const present = sorted().filter(s => !exMan(s.sid).absent), groups = exDraw(present, K().exam.groupSize);
    sorted().filter(s => exMan(s.sid).absent).forEach(s => groups[s.sid] = null);
    S.data = await api('/api/exam_groups', {cls:S.cls, groups, clear: !!had}); S.exOpen = null;
    toast(T('Exam groups drawn','Đã bốc nhóm thi')); renderExam(m); };
  m.querySelectorAll('[data-exg]').forEach(e => e.onclick = () => { const g = +e.dataset.exg; S.exOpen = S.exOpen === g ? null : g; renderExam(m); });
  m.querySelectorAll('[data-exitem]').forEach(b => b.onclick = async () => { const g = b.dataset.g, f = b.dataset.exitem, cur = exTeam(g)[f], off = cur !== undefined && +cur === +b.dataset.val;
    S.data = await api('/api/team', {cls:S.cls, lab:'exam', team:g, field:f, value: off ? null : +b.dataset.val}); renderExam(m); });
  m.querySelectorAll('[data-exind]').forEach(b => b.onclick = async () => { const sid = b.dataset.sid, f = b.dataset.exind, man = exMan(sid), off = man[f] !== undefined && +man[f] === +b.dataset.val;
    const patch = {...man}; if(off) delete patch[f]; else patch[f] = +b.dataset.val;
    S.data = await api('/api/record', {cls:S.cls, lab:'exam', sid, manual:patch});
    if(f === 'contrib' && !off && +b.dataset.val === 0) toast(T('Contribution 0: this student fails the exam','Đóng góp 0: SV này rớt bài thi'));
    renderExam(m); });
  m.querySelectorAll('[data-exnote]').forEach(i => i.onchange = async () => { await save(i.dataset.exnote, {note: i.value.trim().slice(0, 200)}); toast(T('Note saved','Đã lưu ghi chú')); });
  m.querySelectorAll('[data-move]').forEach(sel => sel.onchange = async () => { if(!sel.value) return;
    S.data = await api('/api/exam_groups', {cls:S.cls, groups:{[sel.dataset.move]: +sel.value}}); S.exOpen = +sel.value;
    toast(T('Moved','Đã chuyển nhóm')); renderExam(m); });
}
