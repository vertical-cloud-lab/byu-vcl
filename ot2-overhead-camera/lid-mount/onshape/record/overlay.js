// Drawn over the page for the screen recording: a pointer with click ripples, key badges,
// and a caption bar. Playwright sends its mouse and keyboard input through DevTools, so the
// X server's cursor never moves and a raw recording shows no pointer at all. This draws one
// from the page's own events instead. All of it is pointer-events: none and its listeners
// are passive, so Onshape sees exactly the input it would without it.
//
// From the recorder: window.__rec.caption(text), window.__rec.banner(text).
(() => {
  if (window.top !== window || window.__rec) return;

  const css = `
    #__rec, #__rec * { pointer-events: none !important; box-sizing: border-box; }
    #__rec { position: fixed; inset: 0; z-index: 2147483647; font: 500 15px/1.35 system-ui, sans-serif; }
    #__rec .ptr { position: fixed; left: 0; top: 0; width: 26px; height: 26px; display: none;
                  transition: transform 140ms cubic-bezier(.2,.7,.3,1); }
    #__rec .ptr.down { transition-duration: 30ms; }
    #__rec .ptr .ring { position: absolute; left: -11px; top: -11px; width: 26px; height: 26px;
                        border-radius: 50%; border: 3px solid #ff9800; opacity: 0; }
    #__rec .ptr.down .ring { opacity: 1; }
    #__rec .ripple { position: fixed; width: 44px; height: 44px; margin: -22px 0 0 -22px; border-radius: 50%;
                     border: 3px solid #ff9800; animation: __rec_ripple 600ms ease-out forwards; }
    @keyframes __rec_ripple { from { transform: scale(.3); opacity: 1; } to { transform: scale(1.4); opacity: 0; } }
    #__rec .keys { position: fixed; right: 64px; bottom: 150px; display: flex; flex-direction: column;
                   align-items: flex-end; gap: 6px; }
    #__rec .key { background: rgba(20,20,24,.86); color: #fff; padding: 5px 12px; border-radius: 7px;
                  font: 600 20px/1.2 ui-monospace, "DejaVu Sans Mono", monospace; border: 1px solid rgba(255,255,255,.25);
                  transition: opacity 400ms; }
    #__rec .cap { position: fixed; left: 50%; bottom: 58px; transform: translateX(-50%); max-width: 1180px;
                  background: rgba(20,20,24,.84); color: #fff; padding: 9px 20px 11px; border-radius: 10px;
                  text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,.25); display: none; }
    #__rec .cap .b { font-size: 13px; letter-spacing: .02em; color: #ffcc80; margin-bottom: 2px; }
    #__rec .cap .t { font-size: 21px; font-weight: 600; }
  `;

  const make = () => {
    const root = document.createElement('div');
    root.id = '__rec';
    root.innerHTML = `<style>${css}</style>
      <div class="ptr"><div class="ring"></div>
        <svg width="26" height="26" viewBox="0 0 26 26" style="position:absolute;left:0;top:0">
          <path d="M2 2 L2 21 L7.4 16.2 L11.2 24.2 L14.6 22.7 L10.9 14.9 L18 14.9 Z"
                fill="#fff" stroke="#111" stroke-width="1.6" stroke-linejoin="round"/></svg></div>
      <div class="keys"></div>
      <div class="cap"><div class="b"></div><div class="t"></div></div>`;
    return root;
  };

  let root = make();
  const q = (s) => root.querySelector(s);
  const attach = () => { if (!root.isConnected) (document.body || document.documentElement).appendChild(root); };
  // Onshape rebuilds large parts of the DOM as it moves between pages; put the overlay back if it goes.
  setInterval(attach, 500);
  attach();

  let x = -100, y = -100;
  const place = () => {
    const p = q('.ptr');
    p.style.display = 'block';
    p.style.transform = `translate(${x}px, ${y}px)`;
  };
  const opts = { capture: true, passive: true };
  addEventListener('mousemove', (e) => { x = e.clientX; y = e.clientY; place(); }, opts);
  addEventListener('mousedown', (e) => {
    x = e.clientX; y = e.clientY; place();
    q('.ptr').classList.add('down');
    const r = document.createElement('div');
    r.className = 'ripple';
    r.style.left = x + 'px'; r.style.top = y + 'px';
    root.appendChild(r);
    setTimeout(() => r.remove(), 700);
  }, opts);
  addEventListener('mouseup', () => q('.ptr').classList.remove('down'), opts);

  // Key badges for shortcuts. Plain characters typed into a text field are left out;
  // the field itself shows them.
  const NAMES = { Escape: 'Esc', Enter: 'Enter ⏎', Tab: 'Tab', Backspace: 'Backspace', Delete: 'Del', ' ': 'Space' };
  addEventListener('keydown', (e) => {
    if (['Shift', 'Control', 'Alt', 'Meta'].includes(e.key)) return;
    const t = e.target;
    const typing = t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable);
    const mods = [e.ctrlKey && 'Ctrl', e.altKey && 'Alt', e.metaKey && 'Meta', e.shiftKey && 'Shift'].filter(Boolean);
    if (typing && !e.ctrlKey && !e.altKey && !e.metaKey && e.key.length === 1) return;
    let k = NAMES[e.key] || e.key;
    if (mods.length && /^(Key|Digit)/.test(e.code)) k = e.code.replace(/^(Key|Digit)/, '');
    else if (k.length === 1) k = k.toUpperCase();
    const b = document.createElement('div');
    b.className = 'key';
    b.textContent = [...mods, k].join(' + ');
    const box = q('.keys');
    box.appendChild(b);
    while (box.children.length > 4) box.firstChild.remove();
    setTimeout(() => { b.style.opacity = '0'; }, 1500);
    setTimeout(() => b.remove(), 1950);
  }, opts);

  window.__rec = {
    caption(text) {
      const c = q('.cap');
      q('.cap .t').textContent = text || '';
      c.style.display = text ? 'block' : 'none';
    },
    banner(text) { q('.cap .b').textContent = text || ''; },
  };
})();
