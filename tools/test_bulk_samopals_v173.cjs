/* Test multiple samopal purchases and immediate total on mobile-sized UI. */
const {chromium}=require("playwright");
const {resolve}=require("path");
const assert=require("node:assert/strict");
(async()=>{
 const browser=await chromium.launch({channel:"chrome",headless:true,args:["--no-sandbox"]});
 const page=await browser.newPage({viewport:{width:390,height:780}});
 const errors=[];page.on("pageerror",e=>errors.push(e.message));
 await page.route("https://telegram.org/js/telegram-web-app.js",route=>route.fulfill({
  status:200,contentType:"application/javascript",
  body:"window.Telegram={WebApp:{initData:'',initDataUnsafe:{user:{id:124,first_name:'Тестер'}},ready(){},expand(){},HapticFeedback:{impactOccurred(){},notificationOccurred(){}},CloudStorage:{getItem(k,cb){cb(null,'')},setItem(k,v,cb){cb(null,true)}},isVersionAtLeast(){return true},onEvent(){},openTelegramLink(){}}};"
 }));
 await page.goto("file://"+resolve(__dirname,"../index.html"),{waitUntil:"domcontentloaded"});
 await page.waitForFunction(()=>typeof marketOpen==="function" && typeof S!=="undefined");
 await page.evaluate(()=>{S.tl=10000;S.fz=0;S.mb=0;marketOpen()});
 await page.locator("#mkqty").fill("5");
 assert.match(await page.locator("#mkTotal").innerText(),/5 × 8 = 40/);
 await page.locator("#mkbuy").click();
 let result=await page.evaluate(()=>({tl:S.tl,fz:S.fz,mb:S.mb}));
 assert.deepEqual(result,{tl:9960,fz:5,mb:5},"Five guns must be purchased in one transaction");
 await page.evaluate(()=>{S.tl=80});
 await page.locator("#mkt [data-mkq=max]").click();
 assert.equal(await page.locator("#mkqty").inputValue(),"10");
 assert.match(await page.locator("#mkTotal").innerText(),/10 × 8 = 80/);
 await page.locator("#mkbuy").click();
 result=await page.evaluate(()=>({tl:S.tl,fz:S.fz,mb:S.mb}));
 assert.deepEqual(result,{tl:0,fz:15,mb:15},"MAX purchases only affordable quantity");
 await page.evaluate(()=>{S.tl=3});
 await page.locator("#mkqty").fill("2");
 await page.locator("#mkbuy").click();
 result=await page.evaluate(()=>({tl:S.tl,fz:S.fz,mb:S.mb}));
 assert.deepEqual(result,{tl:3,fz:15,mb:15},"Insufficient money must not purchase guns");
 await page.screenshot({path:"smoke-mobile-bulk-samopal-market.png"});
 if(errors.length)throw Error(errors.join(" | "));
 console.log("PASS: mobile market quantity input, live totals, MAX button, atomic bulk purchase and insufficient funds");
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
