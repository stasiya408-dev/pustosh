#!/usr/bin/env python3
"""Create an owner-only alpha preview that credits 10,000 test talers once.

The deployable index.html and the normal standalone preview remain unchanged.
Only a separately named test HTML contains the local-save gift.
"""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = root / "game_v173_standalone.html"
target = root / "game_v173_test_10000_talers.html"
html = source.read_text(encoding="utf-8")
if "</body>" not in html:
    raise SystemExit("Missing </body> in standalone preview")

gift = r"""<script id="qa-one-time-10000-talers">
(function(){
  var attempts=0;
  function credit(){
    // Wait until saved profile state has loaded; never alter other players' data.
    if(window._loading || typeof S==="undefined" || !S || typeof S!=="object"){
      if(++attempts<80)setTimeout(credit,250);
      return;
    }
    var marker="qaTalerGift20261021";
    if(S[marker])return;
    S[marker]=1;
    S.tl=Math.max(0,Number(S.tl)||0)+10000;
    if(typeof save==="function")save();
    else try{localStorage.setItem("kozak3",JSON.stringify(S))}catch(e){}
    if(typeof draw==="function")draw();
    if(typeof say==="function")say("🎁 Тест: +10 000 талеров");
  }
  setTimeout(credit,500);
})();
</script>"""
if "qa-one-time-10000-talers" in html:
    raise SystemExit("Test gift already injected")
html = html.replace("</body>", gift + "\n</body>", 1)
target.write_text(html, encoding="utf-8")
print(f"One-time test-credit preview: {target.name} ({target.stat().st_size} bytes)")
