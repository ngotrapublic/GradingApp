// Room map of the lab: 6 benches in a U, 2 per side, numbered clockwise; bench 1 is on the lecturer's left.
// The lecturer's desk and the board are at the open end of the U (bottom of the drawing).
// benchMap({mine, active, clickable, notes}) -> SVG string. mine = the student's bench (filled),
// active = bench chosen as a filter (lecturer page), notes = {bench: 'small text under the number'}.
const BENCHES = {
  1: [4, 50, 13, 19], 2: [4, 28, 13, 19],          // left side: 1 near the lecturer, 2 far
  3: [24, 6, 22, 13], 4: [54, 6, 22, 13],          // back of the U
  5: [83, 28, 13, 19], 6: [83, 50, 13, 19],        // right side: 5 far, 6 near the lecturer
};
function benchMap({mine=null, active=null, clickable=false, notes={}}={}){
  const orange='#C2410C', navy='#141E2B';
  let s=`<svg viewBox="0 0 100 92" class="benchmap" role="img" aria-label="${T('Lab room map','Sơ đồ phòng lab')}" xmlns="http://www.w3.org/2000/svg">`;
  s+=`<rect x="1" y="1" width="98" height="90" rx="2" fill="#fff" stroke="#999" stroke-width="0.6"/>`;
  for(const [n,[x,y,w,h]] of Object.entries(BENCHES)){
    const on=String(n)===String(mine), act=String(n)===String(active);
    const fill=on?orange:(act?navy:'#fff'), txt=(on||act)?'#fff':navy;
    s+=`<g ${clickable?`data-bench="${n}" style="cursor:pointer"`:''}><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="2" fill="${fill}" stroke="${on?orange:(act?navy:orange)}" stroke-width="1.1"/>`;
    s+=`<text x="${x+w/2}" y="${y+h/2+(notes[n]?-0.5:2.5)}" text-anchor="middle" font-size="8" font-weight="700" fill="${txt}">${n}</text>`;
    if(notes[n]) s+=`<text x="${x+w/2}" y="${y+h/2+5.5}" text-anchor="middle" font-size="3.6" fill="${txt}">${esc(notes[n])}</text>`;
    s+=`</g>`;
  }
  s+=`<rect x="36" y="74" width="28" height="8" rx="1.5" fill="#eee" stroke="${navy}" stroke-width="0.5"/>`;
  s+=`<text x="50" y="79.4" text-anchor="middle" font-size="3.6" fill="${navy}">${T('Lecturer','Giảng viên')}</text>`;
  s+=`<rect x="32" y="86" width="36" height="1.6" fill="${navy}"/><text x="50" y="84.6" text-anchor="middle" font-size="3" fill="#666">${T('Board','Bảng')}</text>`;
  // dashed arc inside the U: the order of the numbers (clockwise, seen from above)
  s+=`<defs><marker id="ah" markerWidth="5" markerHeight="5" refX="2.5" refY="2.5" orient="auto"><path d="M0,0 L5,2.5 L0,5 z" fill="#aaa"/></marker></defs>`;
  s+=`<path d="M 23 62 Q 23 26 50 26 Q 77 26 77 60" fill="none" stroke="#aaa" stroke-width="0.6" stroke-dasharray="1.5 1.2" marker-end="url(#ah)"/>`;
  s+=`<text x="50" y="47" text-anchor="middle" font-size="3.4" fill="#999">${T('numbers go clockwise','đánh số theo chiều kim đồng hồ')}</text>`;
  return s+`</svg>`;
}
