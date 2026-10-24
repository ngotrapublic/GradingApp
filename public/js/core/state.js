// App state, variant numbers and the scoring rule (same rule as backend/scoring.py).
// S.data = what /api/data returns: me (signed-in account), courses, classes {id: class}. S.keys = {course code: answer keys}.
const S = {data:null, keys:null, cls:localStorage.getItem('cls')||'', lab:localStorage.getItem('lab')||'1', view:'grade', open:null, q:'', preview:null, draft:null};
function C(){ return S.data.classes[S.cls]; }
function K(cls=C()){ return S.keys[cls.course]; }                 // answer keys of the course of a class
function L(){ return K().labs[S.lab]; }
function labs(){ return Object.keys(K().labs); }
const ME = () => S.data.me;
const canManage = (cls=C()) => cls && ['admin','owner'].includes(cls.role);   // lecturer of the class or admin; a TA only grades
function variant(st, cls=C()){ if(!(st.team&&st.member&&cls.vset)) return null; const t=+st.team, m=+st.member; return cls.vset*100 + (m<=3? 3*(t-1)+m : 18+t); }
function rec(sid, lab=S.lab){ return ((C().labs[lab]||{})[sid])||{}; }
function teamRec(team, lab=S.lab){ return ((C().team||{})[lab]||{})[team]||{}; }
const qrule = q => (q && q[4] && q[4].full)? q[4] : K().rule;      // a question may have its own tolerance (5th item)
function mark(x, key, m, rule=K().rule){ if(x===undefined||x===null||x===''||isNaN(+x)) return null; const e=Math.abs(+x/key-1);
  return e<=rule.full? m : e<=rule.half? m/2 : 0; }
// the number a question is marked on: the value, or fc = 1/(2πRC) in kHz for {calc:'rc_fc', from:j} (Lab 2 Task 1 design: R in Ω, C in nF)
function qval(q, values, i){ const x=(values||[])[i]; if(x===undefined||x===null||x===''||isNaN(+x)) return null;
  const r=(q&&q[4])||{}; if(r.calc!=='rc_fc') return +x;
  const R=(values||[])[r.from]; if(R===undefined||R===null||R===''||isNaN(+R)||!+R||!+x) return null;
  return 1/(2*Math.PI*(+R)*(+x)*1e-9)/1e3; }
function score(st, lab=S.lab){
  const Lb=K().labs[lab], v=variant(st), r=rec(st.sid, lab); let t=0;
  if(r.override!==undefined && r.override!==null) return +r.override;   // lecturer's manual score wins
  if(v && Lb.variants[v] && r.tick){ Lb.questions.forEach((q,i)=>{ if(!q[3]) return; const s=mark(qval(q, r.values, i), Lb.variants[v].keys[i], q[3], qrule(q)); if(s) t+=s; }); }
  Lb.manual.forEach(m=>{ t += +(m[3]==='student'? (r.manual||{})[m[0]] : (st.team? teamRec(st.team, lab)[m[0]] : 0)) || 0; });
  return t;
}
const sorted = () => [...C().students].sort((a,b)=>(a.team||99)-(b.team||99)||(a.member||9)-(b.member||9)||a.name.localeCompare(b.name,'vi'));
const manLabel = mn => ({graph:T('Graph + conclusion','Đồ thị + kết luận'), demo:T('Team demo','Demo nhóm')})[mn[0]] || mn[1];
const classLabel = c => `${c.name} – ${c.course} – ${c.term}`;


function changedSince(lab){
  const sy=((C().sync||{})[lab]||{}).scores||{};
  return sorted().filter(st=>{ const now=score(st,lab), was=sy[st.sid];
    return was===undefined ? now>0 : Math.abs(now-was)>1e-9; });
}
