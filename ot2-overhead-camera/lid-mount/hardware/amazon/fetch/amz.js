// node --experimental-websocket amz.js <ASIN...>
// Opens https://www.amazon.com/dp/<ASIN>/?th=1 and writes out/<ASIN>.json (title, bullets,
// description, specs, variations, image URLs), out/<ASIN>.html and out/<ASIN>.png.
const fs = require('fs');
const PORT = 9224;
const sleep = ms => new Promise(r => setTimeout(r, ms));
let ws, id = 0; const pending = new Map();
const send = (method, params = {}) => new Promise(res => { const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
async function ev(expr) {
  const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true });
  if (r.result && r.result.exceptionDetails) return 'EXC:' + JSON.stringify(r.result.exceptionDetails).slice(0, 300);
  return r.result && r.result.result ? r.result.result.value : 'ERR:' + JSON.stringify(r).slice(0, 300);
}
const txt = sel => `(()=>{const e=document.querySelector(${JSON.stringify(sel)}); return e ? e.innerText.replace(/[ \\t]+/g,' ').trim() : null})()`;
async function main() {
  const asins = process.argv.slice(2);
  let targets;
  for (let i = 0; i < 60; i++) { try { targets = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json(); break; } catch (e) { await sleep(500); } }
  ws = new WebSocket(targets.find(t => t.type === 'page').webSocketDebuggerUrl);
  await new Promise(r => ws.onopen = r);
  ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } };
  await send('Page.enable'); await send('Runtime.enable');
  for (const asin of asins) {
    const url = `https://www.amazon.com/dp/${asin}/?th=1`;
    await send('Page.navigate', { url });
    let title = null;
    for (let i = 0; i < 40; i++) {
      await sleep(1000);
      title = await ev(txt('#productTitle'));
      if (title) break;
      // Amazon's soft bot check: a "Continue shopping" button on an otherwise empty page.
      const cont = await ev(`(()=>{const b=[...document.querySelectorAll('button,input[type=submit],a')].find(b=>/continue shopping/i.test(b.innerText||b.value||'')); if(b){b.click(); return true} return false})()`);
      if (cont === true) console.log(asin, 'clicked "Continue shopping"');
    }
    await sleep(2500);
    // Scroll through the page so lazy sections (A+ content) load.
    for (let y = 0; y < 12; y++) { await ev(`window.scrollBy(0, 1500)`); await sleep(400); }
    const data = {
      asin, url, retrieved_utc: new Date().toISOString(), page_title: await ev('document.title'), title,
      byline: await ev(txt('#bylineInfo')),
      price: await ev(txt('#corePrice_feature_div .a-offscreen, #corePriceDisplay_desktop_feature_div .a-offscreen')),
      variations: await ev(`[...document.querySelectorAll('#twister_feature_div, #twister-plus-inline-twister, #inline-twister-expander-content-size_name, #inline-twister-expander-content-color_name, [id^=variation_]')].map(e=>e.innerText.replace(/[ \\t]+/g,' ').trim()).filter(Boolean)`),
      overview: await ev(txt('#productOverview_feature_div')),
      bullets: await ev(`[...document.querySelectorAll('#feature-bullets li, #featurebullets_feature_div li')].map(e=>e.innerText.trim()).filter(Boolean)`),
      description: await ev(txt('#productDescription')),
      details: await ev(`[...document.querySelectorAll('#productDetails_techSpec_section_1 tr, #productDetails_detailBullets_sections1 tr, #detailBullets_feature_div li, #prodDetails tr')].map(e=>e.innerText.replace(/\\s+/g,' ').trim()).filter(Boolean)`),
      aplus_text: await ev(txt('#aplus, #aplus_feature_div')),
      important_info: await ev(txt('#important-information')),
      hires_images: await ev(`[...new Set((document.documentElement.innerHTML.match(/"hiRes":"(https:[^"]+)"/g)||[]).map(s=>s.slice(9,-1)))]`),
      large_images: await ev(`[...new Set((document.documentElement.innerHTML.match(/"large":"(https:[^"]+)"/g)||[]).map(s=>s.slice(9,-1)))]`),
      aplus_images: await ev(`[...document.querySelectorAll('#aplus img, #aplus_feature_div img')].map(i=>i.getAttribute('data-src')||i.src).filter(s=>s&&!/grey-pixel|transparent-pixel/.test(s))`),
    };
    fs.writeFileSync(`out/${asin}.json`, JSON.stringify(data, null, 2));
    fs.writeFileSync(`out/${asin}.html`, await ev('document.documentElement.outerHTML'));
    await ev('window.scrollTo(0,0)'); await sleep(800);
    const shot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
    if (shot.result && shot.result.data) fs.writeFileSync(`out/${asin}.png`, Buffer.from(shot.result.data, 'base64'));
    console.log(asin, 'title:', title, '| bullets', (data.bullets || []).length, '| hiRes', (data.hires_images || []).length,
      '| aplus imgs', (data.aplus_images || []).length);
    await sleep(3000);
  }
  ws.close();
}
main().then(() => process.exit(0)).catch(e => { console.error('ERR', e); process.exit(1); });
