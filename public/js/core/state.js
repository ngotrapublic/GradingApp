// App state, variant numbers and the scoring rule (same rule as backend/scoring.py).
const S = {data:null, keys:null, cls:localStorage.getItem('cls')||'1', lab:localStorage.getItem('lab')||'1', view:'grade', open:null, q:'', preview:null, draft:null};
function C(){ return S.data.classes[S.cls]; }
function L(){ return S.keys.labs[S.lab]; }
function variant(st){ if(!(st.team&&st.member)) return null; const t=+st.team, m=+st.member; return (+S.cls)*100 + (m<=3? 3*(t-1)+m : 18+t); }
function rec(sid, lab=S.lab){ return ((C().labs[lab]||{})[sid])||{}; }
function teamRec(team, lab=S.lab){ return ((C().team||{})[lab]||{})[team]||{}; }
function mark(x, key, m){ if(x===undefined||x===null||x===''||isNaN(+x)) return null; const e=Math.abs(+x/key-1);
  return e<=S.keys.rule.full? m : e<=S.keys.rule.half? m/2 : 0; }
function score(st, lab=S.lab){
  const Lb=S.keys.labs[lab], v=variant(st), r=rec(st.sid, lab); let t=0;
  if(r.override!==undefined && r.override!==null) return +r.override;   // lecturer's manual score wins
  if(v && Lb.variants[v] && r.tick){ Lb.questions.forEach((q,i)=>{ const s=mark((r.values||[])[i], Lb.variants[v].keys[i], q[3]); if(s) t+=s; }); }
  Lb.manual.forEach(m=>{ t += +(m[3]==='student'? (r.manual||{})[m[0]] : (st.team? teamRec(st.team, lab)[m[0]] : 0)) || 0; });
  return t;
}
const sorted = () => [...C().students].sort((a,b)=>(a.team||99)-(b.team||99)||(a.member||9)-(b.member||9)||a.name.localeCompare(b.name,'vi'));
const manLabel = mn => ({graph:T('Graph + conclusion','Đồ thị + kết luận'), demo:T('Team demo','Demo nhóm')})[mn[0]] || mn[1];


function changedSince(lab){
  const sy=((C().sync||{})[lab]||{}).scores||{};
  return sorted().filter(st=>{ const now=score(st,lab), was=sy[st.sid];
    return was===undefined ? now>0 : Math.abs(now-was)>1e-9; });
}
