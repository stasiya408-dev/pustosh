/* Verify the enlarged boss list scrolls vertically and boss selection still works. */
const {chromium}=require("playwright");
const {resolve}=require("path");
const assert=require("node:assert/strict");

(async()=>{
  const browser=await chromium.launch({channel:"chrome",headless:true,args:["--no-sandbox"]});
  const page=await browser.newPage({viewport:{width:390,height:780},deviceScaleFactor:1});
  const errors=[];
  page.on("pageerror",e=>errors.push(e.message));
  await page.route("https://telegram.org/js/telegram-web-app.js",route=>route.fulfill({
    status:200,contentType:"application/javascript",
    body:"window.Telegram={WebApp:{initData:'',initDataUnsafe:{user:{id:124,first_name:'Тестер'}},ready(){},expand(){},HapticFeedback:{impactOccurred(){},notificationOccurred(){}},CloudStorage:{getItem(k,cb){cb(null,'')},setItem(k,v,cb){cb(null,true)}},isVersionAtLeast(){return true},onEvent(){},openTelegramLink(){}}};"
  }));
  await page.goto("file://"+resolve(__dirname,"../index.html"),{waitUntil:"domcontentloaded"});
  await page.locator("#nav2 [data-a=boss]").click();
  await page.locator("#nbx.on").waitFor({state:"visible"});
  await page.waitForFunction(()=>document.querySelectorAll("#nbLo .nbBossRow").length===9);
  const initial=await page.evaluate(()=>{
    const x=document.getElementById("nbx"),r=document.querySelector(".nbBossRow"),a=document.querySelector(".nbBossArt");
    return {cards:document.querySelectorAll("#nbLo .nbBossRow").length,scrollHeight:x.scrollHeight,clientHeight:x.clientHeight,
      cardWidth:r.getBoundingClientRect().width,cardHeight:r.getBoundingClientRect().height,
      art:getComputedStyle(a).backgroundImage};
  });
  assert.equal(initial.cards,9);
  assert.ok(initial.scrollHeight>initial.clientHeight+350,JSON.stringify(initial));
  assert.ok(initial.cardHeight>=95,JSON.stringify(initial));
  assert.ok(initial.art.includes("list.webp"),initial.art.slice(0,160));
  await page.screenshot({path:"smoke-mobile-big-boss-list-top.png"});

  const last=page.locator("#nbLo .nbBossRow[data-pk='8']");
  await last.scrollIntoViewIfNeeded();
  await page.waitForTimeout(200);
  await page.screenshot({path:"smoke-mobile-big-boss-list-bottom.png"});
  const scrolled=await page.locator("#nbx").evaluate(x=>x.scrollTop);
  assert.ok(scrolled>80,"Boss list did not vertically scroll");
  await last.click();
  await page.locator("#nbmd.on").waitFor({state:"visible"});
  assert.match(await page.locator("#nbmp").innerText(),/ЧАРІВНИЦЯ|Чарівниця|чарівниця/i);
  const stillScrolled=await page.locator("#nbx").evaluate(x=>x.scrollTop);
  assert.ok(stillScrolled>80,"Selecting last boss unexpectedly reset scroll");
  await page.locator("#nbmd [data-a=mclose]").click();
  await page.locator("#nbx").evaluate(x=>x.scrollTop=0);
  await page.locator("#nbLo .nbBossRow[data-pk='0']").click();
  await page.locator("#nbmd.on").waitFor({state:"visible"});
  await page.locator("#nbmp [data-a=confirmboss]").click();
  await page.waitForFunction(()=>getComputedStyle(document.querySelector("#nbF")).display==="block");
  // v174: only Ostap uses the pre-fight choice screen in this alpha prototype.
  await page.evaluate(()=>{
    GAME_CONFIG.DEV_UNLOCK_ALL_BOSSES=true;  // Test account only; production progression remains unchanged.
    PG().bossFightKeys=PG().bossFightKeys||{};
    PG().bossFightKeys.ostap=9;
    window._nb.show("list");
  });
  await page.locator("#nbLo .nbBossRow[data-pk='1']").click();
  await page.locator("#nbmd.on").waitFor({state:"visible"});
  await page.locator("#nbmp [data-a=confirmboss]").click();
  await page.locator("#ostapChoice").waitFor({state:"visible"});
  const before=await page.evaluate(()=>window.ostapTest.get());
  assert.ok(before.keys>=3,"Ostap entrance keys unavailable");
  await page.locator("#ostapChoice [data-os-mode='grp']").click();
  await page.locator("#ostapChoice [data-os-rage='2']").click();
  await page.screenshot({path:"smoke-mobile-ostap-mode-and-rage-selection.png"});
  await page.locator("#ostapChoice [data-os-go]").click();
  await page.waitForFunction(()=>document.getElementById("nbF").style.display==="block" && S.cb===1 && S.mode==="grp");
  const inBattle=await page.evaluate(()=>({
    mode:S.mode,idx:S.cb,battle:S.ostapBattle,
    runs:pgBossRuns("ostap"),keys:PG().bossFightKeys.ostap,
    hp:S.bd.grp.hp,max:S.bd.grp.max,base:BOSSES[1].hp,pe:S.bd.grp.pe,end:S.bd.grp.end
  }));
  assert.equal(inBattle.battle.rage,2,"Third rage level was not saved");
  assert.equal(inBattle.battle.mode,"grp");
  assert.equal(inBattle.max,Math.round(inBattle.base*2.4),"Rage did not increase boss HP");
  assert.equal(inBattle.runs,before.runs+1,"One boss entry must use exactly one daily attempt");
  assert.equal(inBattle.keys,before.keys-3,"Merciless tier costs exactly 3 Ostap keys");
  assert.equal(inBattle.pe,inBattle.end,"Entering fight should mark daily attempt before first shot");
  await page.locator("#nbF [data-a='mode']").evaluate(x=>x.click());
  assert.equal(await page.evaluate(()=>S.mode),"grp","Mode changed after battle began");
  await page.evaluate(()=>window._nb.show("list"));
  assert.equal(await page.locator("#nbF").evaluate(x=>x.style.display),"block","Unclaimed fight was abandoned");
  await page.evaluate(()=>{S.bd.grp.hp=0;window.bossWin(true);window._nb.ui()});
  await page.locator("#nbwn.on").waitFor({state:"visible",timeout:5000});
  await page.locator("#nbwn [data-a=wclose]").click();
  await page.waitForFunction(()=>document.getElementById("nbL").style.display==="block"&&!S.ostapBattle);
  await page.evaluate(()=>{PG().bossFightKeys.ostap=0;save()});
  await page.locator("#nbLo .nbBossRow[data-pk='1']").click();
  await page.locator("#nbmp [data-a=confirmboss]").click();
  assert.equal(await page.locator("#ostapChoice").count(),0,"Selection should not open without keys");
  assert.equal(await page.locator("#nbmd").evaluate(x=>x.classList.contains("on")),true,"Detail modal should stay available without keys");
  console.log("PASS: Ostap pre-fight selector, 3-key rage, daily charge, locked group mode, claim-to-list, no-key gate");
  if(errors.length)throw Error("Page errors: "+errors.join(" | "));
  console.log("PASS: 9 larger illustrated boss cards, vertical swipe, last card modal, first boss fight");
  await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
