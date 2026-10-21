// Calls to the local server. Errors are shown as a toast in the current language.
async function api(path, body){
  const r = await fetch(path, body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const j = await r.json().catch(()=>({error:T('Network error','Lỗi mạng')}));
  if(r.status===401){ S.data=null; render(); throw new Error('auth'); }
  if(!r.ok) { const msg=(LANG==='vi'&&j.error_vi)||j.error||T('Error','Lỗi'); toast(msg); throw new Error(msg); }
  return j;
}
