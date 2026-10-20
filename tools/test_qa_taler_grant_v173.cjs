/* The isolated owner test HTML adds 10k talers exactly once per local save. */
const {chromium}=require("playwright");
const {resolve}=require("path");
const assert=require("node:assert/strict");

(async()=>{
  const browser=await chromium.launch({channel:"chrome",headless:true,args:["--no-sandbox"]});
  const page=await browser.newPage({viewport:{width:390,height:780}});
  page.on("pageerror",err=>{throw err});
  await page.route("https://telegram.org/js/telegram-web-app.js",route=>route.fulfill({
    status:200,contentType:"application/javascript",
    body:"window.Telegram={WebApp:{initData:'',initDataUnsafe:{user:{id:124,first_name:'Тестер'}},ready(){},expand(){},HapticFeedback:{impactOccurred(){},notificationOccurred(){}},CloudStorage:{getItem(k,cb){cb(null,'')},setItem(k,v,cb){cb(null,true)}},isVersionAtLeast(){return true},onEvent(){},openTelegramLink(){}}};"
  }));
  const url="file://"+resolve(__dirname,"../game_v173_test_10000_talers.html");
  await page.goto(url,{waitUntil:"domcontentloaded"});
  await page.waitForFunction(()=>typeof S!=="undefined" && S.qaTalerGift20261021===1,null,{timeout:12000});
  const first=await page.evaluate(()=>({balance:S.tl,stored:JSON.parse(localStorage.getItem("kozak3")).qaTalerGift20261021}));
  assert.ok(first.balance>=10000,"The one-time taler gift was not credited");
  assert.equal(first.stored,1,"The gift was not saved");
  await page.reload({waitUntil:"domcontentloaded"});
  await page.waitForFunction(()=>typeof S!=="undefined" && S.qaTalerGift20261021===1,null,{timeout:12000});
  await page.waitForTimeout(1000);
  const second=await page.evaluate(()=>S.tl);
  assert.ok(second<first.balance+5000,"The 10k gift was credited a second time");
  console.log("PASS: private alpha HTML credits +10000 once and persists it on reload");
  await browser.close();
})().catch(err=>{console.error(err);process.exit(1)});
