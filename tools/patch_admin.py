# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding='utf-8')
h = r'C:\Users\dumok\dev\quoka-character\index.html'
s = open(h, encoding='utf-8').read()

css_add = r'''
/* lightbox prompt panel + admin */
.lb .box{max-width:min(94vw,1240px);flex-direction:row;align-items:stretch;gap:16px;cursor:default;position:relative}
.lb .box .pic{flex:1 1 0;min-width:0;display:grid;place-items:center}
.lb img{max-height:80vh;width:auto}
.lb .side{flex:0 0 340px;max-width:340px;display:flex;flex-direction:column;gap:10px;min-height:0}
.lb .side h4{margin:0;font-size:15px;font-weight:800;letter-spacing:-.02em;padding-right:36px}
.lb .side .meta{display:flex;gap:6px;flex-wrap:wrap}
.lb .side .meta span{font-size:11px;font-weight:700;color:var(--ink-soft);background:var(--g2);padding:4px 8px;border-radius:8px}
.lb .side pre{margin:0;flex:1 1 auto;min-height:120px;max-height:52vh;overflow:auto;white-space:pre-wrap;font-family:var(--mono);font-size:12px;line-height:1.6;color:#333D4B;background:var(--g2);border-radius:14px;padding:12px}
.lb .side .row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.lb .side .note{margin:0;font-size:12px;color:var(--ink-faint);font-weight:600;line-height:1.5}
.btn-x{display:inline-flex;align-items:center;gap:6px;border:0;cursor:pointer;background:var(--g2);color:var(--ink);font-size:12px;font-weight:700;padding:7px 12px;border-radius:999px}
.btn-x.danger{background:#FFEEEE;color:#F04452}
.btn-x.dark{background:var(--ink);color:#fff}
.lb .close{position:absolute;top:12px;right:12px;width:34px;height:34px;border-radius:50%;background:var(--g2);border:0;cursor:pointer;font-size:18px;font-weight:800;color:var(--ink);z-index:3}
.gcard{position:relative}
.gcard.hid{opacity:.45}
.gcard .badge{position:absolute;top:18px;left:18px;font-size:10px;font-weight:800;padding:3px 7px;border-radius:999px;background:var(--ink);color:#fff;z-index:2}
.gcard .badge.del{background:#F04452}
.gcard .ptag{font-size:10px;font-weight:700;color:var(--accent);background:var(--accent-bg);padding:2px 7px;border-radius:999px;align-self:flex-start}
.admin-bar{display:none;align-items:center;gap:10px;flex-wrap:wrap;background:var(--card);border:1px solid var(--hairline);border-radius:16px;padding:10px 14px;margin-bottom:16px;font-size:13px;font-weight:700}
body.admin .admin-bar{display:flex}
.admin-bar .st{color:var(--ink-faint);font-weight:600}
.foot .adm{margin-left:10px;border:0;background:transparent;color:var(--ink-faint);font:inherit;cursor:pointer;text-transform:none;letter-spacing:0}
.foot .adm:hover{color:var(--accent)}
@media (max-width:860px){.lb .box{flex-direction:column}.lb .side{flex:none;max-width:none}.lb img{max-height:46vh}.lb .side pre{max-height:26vh}}
'''
assert '\n.foot{font-size:11.5px' in s
s = s.replace('\n.foot{font-size:11.5px', css_add + '\n.foot{font-size:11.5px', 1)

old_lb = '<div class="lb" id="lb"><div class="box"><img id="lbImg" alt=""><div class="cap"><b id="lbT"></b><span id="lbS"></span></div></div></div>'
new_lb = '''<div class="lb" id="lb"><div class="box" id="lbBox">
  <button class="close" id="lbClose" aria-label="닫기">×</button>
  <div class="pic"><img id="lbImg" alt=""></div>
  <div class="side">
    <h4 id="lbT"></h4>
    <div class="meta" id="lbMeta"></div>
    <pre id="lbPrompt"></pre>
    <div class="row"><button class="copy" id="lbCopy">프롬프트 복사</button><button class="btn-x" id="lbOpen">원본 열기</button></div>
    <div class="row" id="lbAdmin" hidden><button class="btn-x" id="lbHide">숨기기</button><button class="btn-x danger" id="lbDel">삭제</button><button class="btn-x dark" id="lbRestore">복원</button></div>
    <p class="note" id="lbS"></p>
  </div>
</div></div>'''
assert old_lb in s
s = s.replace(old_lb, new_lb)

old_chips = '    <div class="chips" id="chips"></div>'
assert old_chips in s
s = s.replace(old_chips, '    <div class="admin-bar" id="adminBar"><span>관리자 모드</span><span class="st" id="adminSt"></span><button class="btn-x" id="adminShowDel">삭제된 항목 보기</button><button class="btn-x" id="adminOut">나가기</button></div>\n' + old_chips)
old_foot = '<p class="foot" id="contact">QUOKA · AI융합교육연구회 · 두목쿼카 · Higgsfield GPT Image 2.5</p>'
assert old_foot in s
s = s.replace(old_foot, '<p class="foot" id="contact">QUOKA · AI융합교육연구회 · 두목쿼카 · Higgsfield GPT Image 2.5 <button class="adm" id="adminBtn">관리</button></p>')

a = s.index('function openLB(')
b = s.index("fetch('assets/samples.json')"); b = s.index('\n', b) + 1
# strip a preceding "let filter='전체';" line if it sits just before openLB
js = r'''/* ---- prompts, admin state, lightbox ---- */
const API='https://quoka-character-api.gottkf12087.workers.dev';
let PROMPTS={}, srv={hidden:[],deleted:[]}, admin=false, showDel=false, cur=null, filter='전체', ALL=[];
try{ const c=localStorage.getItem('qc_state'); if(c) srv=JSON.parse(c); }catch(e){}
const isHidden=f=>srv.hidden.includes(f), isDeleted=f=>srv.deleted.includes(f);
function setState(st){ srv={hidden:st.hidden||[],deleted:st.deleted||[]}; try{localStorage.setItem('qc_state',JSON.stringify(srv));}catch(e){} }
fetch(API+'/api/state').then(r=>r.json()).then(st=>{setState(st);renderGallery();}).catch(()=>{});
fetch('assets/prompts.json').then(r=>r.json()).then(j=>{PROMPTS=j;renderGallery();}).catch(()=>{});
async function adminCall(action,key){
  const pw=sessionStorage.getItem('qc_pw'); if(!pw) return null;
  const r=await fetch(API+'/api/admin',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:pw,action,key})});
  const j=await r.json(); if(j.ok){setState(j);} else toast(j.error||'실패'); return j;
}
async function adminLogin(){
  const pw=prompt('관리자 비밀번호'); if(!pw) return;
  const r=await fetch(API+'/api/admin',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:pw,action:'verify'})}).then(r=>r.json()).catch(()=>({ok:false}));
  if(!r.ok){toast('비밀번호가 달라요');return;}
  sessionStorage.setItem('qc_pw',pw); setState(r); admin=true; document.body.classList.add('admin'); renderGallery(); toast('관리자 모드');
}
function adminLogout(){ sessionStorage.removeItem('qc_pw'); admin=false; showDel=false; document.body.classList.remove('admin'); renderGallery(); }
$('#adminBtn').onclick=()=>admin?adminLogout():adminLogin();
$('#adminOut').onclick=adminLogout;
$('#adminShowDel').onclick=()=>{showDel=!showDel;$('#adminShowDel').textContent=showDel?'삭제된 항목 숨기기':'삭제된 항목 보기';renderGallery();};
if(sessionStorage.getItem('qc_pw')){admin=true;document.body.classList.add('admin');}

function openLB(item){
  if(!item) return;
  cur=item; const p=PROMPTS[item.file];
  $('#lbImg').src=item.file; $('#lbT').textContent=item.name; $('#lbS').textContent=item.group+(p&&p.note?' · '+p.note:'');
  $('#lbMeta').innerHTML=p?[p.model,p.quality,p.ar,p.bg].filter(Boolean).map(m=>`<span>${m}</span>`).join('')+(p.refs&&p.refs.length?`<span>참조 ${p.refs.length}장</span>`:''):'';
  $('#lbPrompt').textContent=p?p.prompt:'이 이미지의 원본 프롬프트 기록이 없어요(극장 초기 공용 포즈·히어로).';
  $('#lbCopy').dataset.copy=p?p.prompt:''; $('#lbCopy').disabled=!p;
  $('#lbAdmin').hidden=!admin;
  if(admin){ const d=isDeleted(item.file), h=isHidden(item.file); $('#lbHide').textContent=h?'숨김 해제':'숨기기'; $('#lbHide').hidden=d; $('#lbDel').hidden=d; $('#lbRestore').hidden=!d; }
  $('#lb').classList.add('on');
}
function closeLB(){$('#lb').classList.remove('on');}
$('#lb').addEventListener('click',e=>{ if(e.target===$('#lb')) closeLB(); });
$('#lbClose').onclick=closeLB;
document.addEventListener('keydown',e=>{ if(e.key==='Escape') closeLB(); });
$('#lbOpen').onclick=()=>{ if(cur) window.open(cur.file,'_blank'); };
$('#lbHide').onclick=async()=>{ if(!cur)return; await adminCall(isHidden(cur.file)?'unhide':'hide',cur.file); renderGallery(); openLB(cur); };
$('#lbDel').onclick=async()=>{ if(!cur)return; if(!confirm('이 이미지를 보관소에서 삭제할까요? (복원 가능)'))return; await adminCall('delete',cur.file); closeLB(); renderGallery(); };
$('#lbRestore').onclick=async()=>{ if(!cur)return; await adminCall('restore',cur.file); renderGallery(); openLB(cur); };

function renderGallery(){
  const theater=[];
  for(const k of DATA.keys){
    if(k.dup)continue;
    const g='극장 의상 · '+k.group;
    theater.push({file:k.file,name:k.name+' · 기본',group:g});
    for(const p of (k.poses||[]))theater.push({file:p.file,name:k.name+' · '+p.name,group:g});
  }
  ALL=[...SHEETS,...DATA.paris,...NEWYEAR,...(DATA.sebae||[]),...(DATA.newyear_v1||[]),...(DATA.sheets_v2||[]),...theater,...(DATA.common||[]),...(DATA.info||[])];
  const vis=ALL.filter(x=>admin?(showDel?isDeleted(x.file):!isDeleted(x.file)):(!isDeleted(x.file)&&!isHidden(x.file)));
  const groups=['전체',...new Set(vis.map(x=>x.group))];
  if(!groups.includes(filter)) filter='전체';
  $('#chips').innerHTML=groups.map(g=>`<button class="chip ${g===filter?'on':''}" data-g="${g}">${g}</button>`).join('');
  const list=filter==='전체'?vis:vis.filter(x=>x.group===filter);
  $('#ggrid').innerHTML=list.map(x=>`<figure class="gcard ${x.scene?'scene':''} ${x.wide?'wide':''} ${admin&&isHidden(x.file)?'hid':''}" data-i="${ALL.indexOf(x)}">${admin&&isDeleted(x.file)?'<span class="badge del">삭제됨</span>':admin&&isHidden(x.file)?'<span class="badge">숨김</span>':''}<div class="im"><img src="${x.file}" alt="${x.name}" loading="lazy"></div><b>${x.name}</b><span>${x.group}</span>${PROMPTS[x.file]?'<span class="ptag">프롬프트</span>':''}</figure>`).join('');
  $('#gcount').textContent=`${list.length}장`;
  $('#adminSt').textContent=`숨김 ${srv.hidden.length} · 삭제 ${srv.deleted.length}`;
}
$('#chips').addEventListener('click',e=>{const c=e.target.closest('.chip');if(!c)return;filter=c.dataset.g;renderGallery();});
$('#ggrid').addEventListener('click',e=>{const c=e.target.closest('.gcard');if(c)openLB(ALL[+c.dataset.i]);});
fetch('assets/samples.json').then(r=>r.json()).then(j=>{DATA=Object.assign({sebae:[]},j);renderGallery();}).catch(()=>renderGallery());
'''
s = s[:a] + js + s[b:]
s = s.replace("let filter='전체';\n/* ---- prompts", "/* ---- prompts")
open(h, 'w', encoding='utf-8').write(s)
print("filter decls", s.count("filter='전체'"), "renderGallery", s.count('function renderGallery'), "openLB", s.count('function openLB'))
