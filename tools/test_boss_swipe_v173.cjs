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
  if(errors.length)throw Error("Page errors: "+errors.join(" | "));
  console.log("PASS: 9 larger illustrated boss cards, vertical swipe, last card modal, first boss fight");
  await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
