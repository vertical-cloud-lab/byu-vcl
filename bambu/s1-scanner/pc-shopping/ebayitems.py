"""Print title | price | delivery | /itm/ URL for each eBay search result on the current page."""
import sys
from playwright.sync_api import sync_playwright
n = int(sys.argv[1]) if len(sys.argv) > 1 else 60
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = b.contexts[0].pages[0]
    js = """() => {
      const out=[];
      document.querySelectorAll('ul.srp-results > li').forEach(li=>{
        const a=li.querySelector('a[href*="/itm/"]'); if(!a) return;
        const m=a.href.match(/\\/itm\\/(\\d+)/); if(!m) return;
        const t=li.innerText.split('\\n').map(s=>s.trim()).filter(s=>s && !/^(Opens in|derosnopS|Located|Buy It Now|NEW LOW PRICE|JUST LISTED)/.test(s));
        out.push(t.slice(0,7).join(' | ').slice(0,260)+' || https://www.ebay.com/itm/'+m[1]);
      }); return out; }"""
    for line in page.evaluate(js)[:n]:
        print(line)
