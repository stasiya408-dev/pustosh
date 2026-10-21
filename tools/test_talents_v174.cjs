const fs=require("node:fs"),vm=require("node:vm"),assert=require("node:assert/strict");
const player={bossStats:{totalPersonalDamage:0}};
let saves=0;
const window={};
const ctx={window, PG:()=>player, S:{mode:"solo"},save:()=>{saves++},document:{readyState:"loading",addEventListener(){}},console,Math};
vm.runInNewContext(fs.readFileSync("tools/talents_v174.js","utf8"),ctx);
const T=window.TALENTS;
const tests=[
[0,0,0,1000],
[999,0,0,1],
[1000,1,1,1200],
[2199,1,1,1],
[2200,2,2,1400],
[3600,3,3,1600],
[5200,4,4,1800],
[7000,5,5,2000],
[19000,10,10,3000],
[414000,60,60,13000]
];
for(const [d,level,points,nextCost] of tests){
player.bossStats.totalPersonalDamage=d;
assert.equal(T.level(),level,"level at damage "+d);
assert.equal(T.free(),points,"free points at "+d);
assert.equal(T.needForPoint(level+1),nextCost,"next cost at "+d);
}
for(let k=1;k<=200;k++){
assert.equal(T.needForPoint(k),1000+(k-1)*200);
assert.equal(T.totalFor(k)-T.totalFor(k-1),T.needForPoint(k));
assert.equal(T.levelFromDamage(T.totalFor(k)),k);
}
player.bossStats.totalPersonalDamage=7000;
for(let k=0;k<4;k++)assert.equal(T.upgrade("powder"),true);
assert.equal(T.upgrade("eagle"),true);
assert.equal(T.rank("powder"),4);
assert.equal(T.rank("eagle"),1);
assert.equal(T.rank("finish"),0);
assert.equal(T.free(),0);
assert.equal(T.upgrade("finish"),false,"cannot spend extra points");
assert.equal(saves,5);
player.bossStats.totalPersonalDamage=9000; // +2000 damage -> 6th point
assert.equal(T.level(),6);
assert.equal(T.free(),1);
assert.equal(T.upgrade("finish"),true,"carryover enables next unlock");
assert.equal(T.free(),0);
const before=T.level();
player.bossStats.totalPersonalDamage=9010;
assert.equal(T.level(),before,"fractional damage does not grant a bonus point");
const resetStats={...player.bossStats}; delete resetStats.totalPersonalDamage;
player.bossStats=resetStats;
assert.equal(T.damage(),0,"new player stats must not crash");
console.log("v174 cumulative talent XP checks passed");
