"use strict";
// The Evidence Room: offline, dependency-free, no network requests.
const $ = id => document.getElementById(id);
let records = [], sourceName = "";
const safeString = value => typeof value === "string" ? value : value == null ? "" : String(value);
function normalizeRole(role) {
  const r = safeString(role).toLowerCase().trim();
  return ["user","assistant","system","tool"].includes(r) ? r : "unknown";
}
function jsonMessages(parsed) {
  // Accept common exported shapes without claiming universal compatibility.
  const items = Array.isArray(parsed) ? parsed :
    Array.isArray(parsed?.messages) ? parsed.messages :
    Array.isArray(parsed?.conversation?.messages) ? parsed.conversation.messages : null;
  if (!items) throw new Error("JSON needs an array of messages, or a messages/conversation.messages array.");
  return items.map((m, i) => {
    if (typeof m === "string") return {role:"unknown",text:m,index:i};
    if (!m || typeof m !== "object") return {role:"unknown",text:safeString(m),index:i};
    let value = m.content ?? m.text ?? m.message ?? "";
    if (Array.isArray(value)) value = value.map(p => typeof p === "string" ? p : safeString(p?.text ?? p?.content ?? "")).join("\n");
    if (typeof value === "object") value = value?.text ?? JSON.stringify(value);
    return {role:normalizeRole(m.role ?? m.sender ?? m.author?.role),text:safeString(value),time:safeString(m.timestamp ?? m.created_at ?? ""),index:i};
  });
}
function textMessages(raw) {
  // Only parse explicit line-start speaker markers; everything else stays unattributed.
  const lines = raw.replace(/\r\n?/g,"\n").split("\n");
  const out = []; let current = null;
  for (const line of lines) {
    const match = /^(USER|ASSISTANT|SYSTEM|TOOL):\s?(.*)$/i.exec(line);
    if (match) { if(current) out.push(current); current={role:normalizeRole(match[1]),text:match[2],index:out.length}; }
    else if(current) current.text += "\n"+line;
    else { if (!out.length) out.push({role:"unknown",text:line,index:0}); else out[out.length-1].text += "\n"+line; }
  }
  if(current) out.push(current);
  return out.filter(m=>m.text.trim());
}
function setStatus(s) {$("status").textContent=s;}
function render() {
  const term=$("search").value.toLocaleLowerCase();
  const filtered=records.filter(r=>r.text.toLocaleLowerCase().includes(term));
  const target=$("messages");target.replaceChildren();
  $("heading").textContent=sourceName ? "Evidence: "+sourceName : "Messages";
  $("count").textContent=filtered.length+" of "+records.length+" entries shown";
  if (!filtered.length) {const p=document.createElement("p");p.textContent="No matching entries.";target.append(p);return;}
  const frag=document.createDocumentFragment();
  for (const item of filtered) {
    const section=document.createElement("article");section.className="message "+item.role;
    const head=document.createElement("div");head.className="tag";head.textContent=(item.role==="unknown"?"UNATTRIBUTED":item.role.toUpperCase())+" · #"+(item.index+1)+(item.time?" · "+item.time:"");
    const body=document.createElement("pre");body.textContent=item.text;
    section.append(head,body);frag.append(section);
  }target.append(frag);
}
function load(raw,name) {
  const isJson=name.toLowerCase().endsWith(".json") || /^[\s]*[\[{]/.test(raw);
  let data;
  if(isJson){try {data=jsonMessages(JSON.parse(raw));} catch(e) { if(name.toLowerCase().endsWith(".json")) throw e;data=textMessages(raw);}}
  else data=textMessages(raw);
  records=data;sourceName=name;$("search").value="";
  for(const id of ["search","export","clear"]) $(id).disabled=!records.length;
  setStatus("Loaded "+records.length+" entries from "+name+". Speaker roles may be unknown; no missing history has been reconstructed.");
  render();
}
$("file").addEventListener("change",async e=>{
  const f=e.target.files?.[0];if(!f)return;
  try{if(f.size>10*1024*1024)throw new Error("File exceeds 10 MB safety limit.");
    load(await f.text(),f.name);
  }catch(err){setStatus("Could not open file: "+err.message);}
});
$("loadPaste").addEventListener("click",()=>{try{load($("paste").value,"pasted-transcript.txt");}catch(err){setStatus(err.message);}});
$("search").addEventListener("input",render);
$("clear").addEventListener("click",()=>{records=[];sourceName="";$("file").value="";$("paste").value="";$("search").value="";for(const id of ["search","export","clear"]) $(id).disabled=true;setStatus("Session cleared.");render();});
function escapeHtml(s){return safeString(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
$("export").addEventListener("click",()=>{
  if(!records.length)return;
  const entries=records.map(m=>'<article><h2>'+escapeHtml(m.role==="unknown"?"UNATTRIBUTED":m.role.toUpperCase())+' #'+(m.index+1)+(m.time?' · '+escapeHtml(m.time):'')+'</h2><pre>'+escapeHtml(m.text)+'</pre></article>').join("\n");
  const documentText='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Offline Evidence Archive</title><style>body{font:16px/1.5 system-ui,sans-serif;max-width:850px;margin:auto;padding:20px}article{border:1px solid #aaa;padding:16px;margin:12px 0;break-inside:avoid}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}h2{font-size:1rem}</style></head><body><h1>Offline Evidence Archive</h1><p>Source: '+escapeHtml(sourceName)+'. Partial or unknown attribution may remain. No missing messages were reconstructed.</p>'+entries+'</body></html>';
  const url=URL.createObjectURL(new Blob([documentText],{type:"text/html;charset=utf-8"}));
  const a=document.createElement("a");a.href=url;a.download="evidence-room-archive.html";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
});
