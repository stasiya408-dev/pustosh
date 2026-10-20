/* Mobile alpha smoke test: v173, 390x780, actual rendered controls. */
const { chromium } = require("playwright");
const { resolve } = require("path");
const assert = require("node:assert/strict");

(async () => {
  const browser = await chromium.launch({channel:"chrome",headless:true,args:["--no-sandbox"]});
  const page = await browser.newPage({viewport:{width:390,height:780},deviceScaleFactor:1});
  const errors=[];
  page.on("pageerror",e=>errors.push(e.message));
  await page.route("https://telegram.org/js/telegram-web-app.js", route=>route.fulfill({
    status:200,
    contentType:"application/javascript",
    body:"window.Telegram={WebApp:{initData:'',initDataUnsafe:{user:{id:124,first_name:'Тестер'}},ready(){},expand(){},HapticFeedback:{impactOccurred(){},notificationOccurred(){}},CloudStorage:{getItem(k,cb){cb(null,'')},setItem(k,v,cb){cb(null,true)}},isVersionAtLeast(){return true},onEvent(){},openTelegramLink(){}}};"
  }));
  const started=Date.now();
  await page.goto("file://"+resolve(__dirname,"../index.html"),{waitUntil:"domcontentloaded"});
  await page.locator("#nav2 [data-a=boss]").waitFor({state:"visible",timeout:20000});
  console.log("DOM interactive:",Date.now()-started,"ms");
  await page.locator("#nav2 [data-a=boss]").click();
  await page.locator("#nbx.on").waitFor({state:"visible"});
  await page.waitForFunction(()=>{const x=document.getElementById("nbbg");return x&&x.complete&&x.naturalWidth>0});
  assert.equal(await page.locator("#nbL").evaluate(x=>getComputedStyle(x).display),"block");
  await page.locator("#nbx [data-pk='0']").click();
  await page.locator("#nbmd.on").waitFor({state:"visible"});
  assert.match(await page.locator("#nbmp").innerText(),/Спроби з цим босом/);
  await page.screenshot({path:"smoke-mobile-boss-preview.png"});
  await page.locator("#nbmp [data-a=confirmboss]").click();
  await page.locator("#nbF").waitFor({state:"visible"});
  assert.equal(await page.locator("#nbbg").evaluate(x=>x.naturalWidth>0),true);
  await page.screenshot({path:"smoke-mobile-boss-fight.png"});
  await page.evaluate(()=>{
    const b1=BOSSES[0].id,b2=BOSSES[1].id;
    for(let i=0;i<6;i++)if(!pgBossMarkRun(b1))throw Error("could not count boss start "+i);
    if(pgBossRuns(b1)!==6||pgBossMarkRun(b1)!==false)throw Error("boss limit invalid");
    if(pgBossRuns(b2)!==0)throw Error("second boss incorrectly limited");
    PG().bossDaily.date="2000-01-01";
    if(pgBossRuns(b1)!==0)throw Error("Kyiv reset invalid");
  });
  await page.evaluate(()=>{
    let p=PG();p.ringShards.g1=500;S.sv=50000;window.jwOpen();
  });
  await page.locator("#jwx [data-a=tab][data-t=shop]").click();
  assert.match(await page.locator("#jwc").innerText(),/100/);
  await page.evaluate(()=>window.__oldRandom=Math.random);
  await page.evaluate(()=>Math.random=()=>.99);
  await page.locator("#jwx [data-a=craft][data-g='1']").click();
  await page.locator("#jwx [data-a=yes]").click();
  let state=await page.evaluate(()=>({fail:PG().jewel.failsByGroup.g1,shards:PG().ringShards.g1}));
  assert.deepEqual(state,{fail:1,shards:400});
  assert.match(await page.locator("#jwc").innerText(),/120/);
  await page.evaluate(()=>Math.random=()=>0);
  await page.locator("#jwx [data-a=craft][data-g='1']").click();
  await page.locator("#jwx [data-a=yes]").click();
  state=await page.evaluate(()=>({fail:PG().jewel.failsByGroup.g1,shards:PG().ringShards.g1,rings:PG().rings.length}));
  assert.deepEqual(state,{fail:0,shards:280,rings:1});
  await page.evaluate(()=>Math.random=window.__oldRandom);
  if(errors.length)throw Error("Page errors: "+errors.join(" | "));
  console.log("PASS: mobile boss images and preview, per-boss limit, fail/success forge");
  await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});

