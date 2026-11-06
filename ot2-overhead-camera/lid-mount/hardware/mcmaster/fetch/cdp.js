// node --experimental-websocket cdp.js <mode> <args...>   (modes: list <url> | title <pn...> | step <pn...>)
const fs = require('fs');
const PORT = 9223;
const sleep = ms => new Promise(r => setTimeout(r, ms));
let ws, id = 0; const pending = new Map(); let reqs = [];
const send = (method, params = {}) => new Promise(res => { const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
async function ev(expr) {
  const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true });
  if (r.result && r.result.exceptionDetails) return 'EXC:' + JSON.stringify(r.result.exceptionDetails).slice(0, 300);
  return r.result && r.result.result ? r.result.result.value : 'ERR:' + JSON.stringify(r).slice(0, 300);
}
async function clickAt(expr) {
  const p = await ev(`(()=>{const e=(${expr}); if(!e) return null; e.scrollIntoView({block:'center'}); const r=e.getBoundingClientRect(); return {x:r.x+r.width/2,y:r.y+r.height/2}})()`);
  if (!p || typeof p !== 'object') return 'noelem:' + p;
  for (const type of ['mouseMoved', 'mousePressed', 'mouseReleased'])
    await send('Input.dispatchMouseEvent', { type, x: p.x, y: p.y, button: 'left', clickCount: 1 });
  return true;
}
async function waitTitle(maxMs, pn) {
  const t0 = Date.now(); let t = '';
  while (Date.now() - t0 < maxMs) { t = await ev(`location.pathname.toUpperCase().includes(${JSON.stringify(pn)}) && document.readyState!=='loading' ? document.title : ''`); if (typeof t === 'string' && /\|\s*McMaster/.test(t)) return t; await sleep(300); }
  return t + ' [path=' + (await ev('location.href')) + ']';
}
const ANCHOR = `document.querySelector('a[class*="_downloadAnchor"]')`;
async function main() {
  const [, , mode, ...args] = process.argv;
  let targets;
  for (let i = 0; i < 60; i++) { try { targets = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json(); break; } catch (e) { await sleep(500); } }
  const page = targets.find(t => t.type === 'page');
  ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise(r => ws.onopen = r);
  ws.onmessage = e => {
    const m = JSON.parse(e.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
    else if (m.method === 'Network.requestWillBeSent') { const q = m.params.request; reqs.push(q.method + ' ' + q.url + (q.postData ? ' POST:' + q.postData.slice(0, 300) : '')); }
  };
  await send('Network.enable'); await send('Page.enable'); await send('Runtime.enable');
  await send('Page.setDownloadBehavior', { behavior: 'allow', downloadPath: process.cwd() + '/dl' });
  if (mode === 'list') {
    await send('Page.navigate', { url: args[0] });
    let last = -1;
    for (let i = 0; i < 40; i++) { await sleep(1000); const n = await ev(`(document.body.innerText.match(/\\b9\\d{4}A\\d{3}\\b/g)||[]).length`); if (n > 0 && n === last) break; last = n; }
    console.log('TITLE', await ev('document.title'));
    const rows = await ev(`[...document.querySelectorAll('tr')].map(r=>r.innerText.replace(/\\s+/g,' ').trim()).filter(t=>/${args[1] || '9\\\\d{4}A\\\\d{3}'}/.test(t)).slice(0,200)`);
    console.log(Array.isArray(rows) ? rows.join('\n') : rows);
    return ws.close();
  }
  for (const pn of args) {
    reqs = [];
    await send('Page.navigate', { url: `https://www.mcmaster.com/${pn}/` });
    await sleep(mode === 'title' ? 600 : 2500);
    const title = await waitTitle(mode === 'title' ? 12000 : 25000, pn);
    console.log(`PN ${pn} TITLE ${title}`);
    if (mode === 'title') continue;
    console.log(' spec', JSON.stringify(await ev(`(document.body.innerText.match(/(Thickness|Head Height|Thread Type)[\\s\\S]{0,40}/g)||[]).slice(0,4)`)));
    let ok = false;
    for (let i = 0; i < 40 && ok !== true; i++) { ok = await ev(`!!${ANCHOR}`); if (ok !== true) await sleep(500); }
    console.log(' anchor', ok, await ev(`(${ANCHOR}||{getAttribute:()=>null}).getAttribute('href')`));
    reqs = [];
    console.log(' click dropdown', await clickAt(`[...document.querySelectorAll('button')].find(b=>/^[23]-D /.test(b.textContent.trim()) && b.querySelector('svg'))`));
    await sleep(1500);
    console.log(' menu', JSON.stringify(await ev(`(()=>{const e=[...document.querySelectorAll('*')].filter(e=>/^3-D STEP$/.test(e.textContent.trim())).pop(); if(!e) return null; let p=e; for(let i=0;i<2&&p.parentElement;i++) p=p.parentElement; return p.innerText.slice(0,800)+' || '+e.outerHTML.slice(0,500)})()`)));
    console.log(' click STEP', await clickAt(`[...document.querySelectorAll('*')].filter(e=>/^3-D STEP$/.test(e.textContent.trim())).pop()`));
    await sleep(2500);
    const href = await ev(`(${ANCHOR}||{getAttribute:()=>null}).getAttribute('href')`);
    console.log(' href after STEP', href);
    console.log(' reqs:\n   ' + reqs.filter(u => !/\.(png|gif|jpe?g|svg|css|woff2?)(\?|$)/i.test(u) && !/\/trk\/|analytics|google|doubleclick|bing|facebook/i.test(u)).slice(0, 25).join('\n   '));
    if (typeof href === 'string' && /\.(STEP|stp)$/i.test(href)) {
      const r = await ev(`(async()=>{const r=await fetch(${JSON.stringify(href)},{credentials:'include'}); const b=new Uint8Array(await r.arrayBuffer()); let s=''; for(let i=0;i<b.length;i+=0x8000) s+=String.fromCharCode.apply(null,b.subarray(i,i+0x8000)); return {status:r.status, ct:r.headers.get('content-type'), len:b.length, url:r.url, b64:btoa(s)}})()`);
      if (typeof r !== 'object') { console.log(' fetch failed', r); continue; }
      console.log(' fetch', r.status, r.ct, r.len, r.url);
      if (r.status === 200) { fs.writeFileSync(`${pn}.step`, Buffer.from(r.b64, 'base64')); fs.writeFileSync(`${pn}.meta.json`, JSON.stringify({ pn, title, href, fetched_url: r.url, content_type: r.ct })); }
    }
  }
  ws.close();
}
main().then(() => process.exit(0)).catch(e => { console.error('ERR', e); process.exit(1); });
