// Tiny regression probe for the preview's real clock functions; no browser tab.
const fs=require("node:fs"),vm=require("node:vm"),assert=require("node:assert/strict");
const source=fs.readFileSync(require("node:path").join(__dirname,"preview.template.html"),"utf8");
const frameAt=source.slice(source.indexOf("function frameAt("),source.indexOf("\nfunction draw("));
const tick=source.slice(source.indexOf("function tick(now)"),source.indexOf('\nel("progress")'));
const groups=[{durationMs:40,totalDurationMs:240,frames:Array.from({length:6},(_,i)=>({file:i+".png"}))}];
function probe(last,timestamps,speed=1){
  const state={group:0,frame:0,playing:true,speed,mode:"single",elapsed:0,last};
  let renders=0,scheduled=0;
  const sandbox={groups,state,render(){renders++;const frame=groups[state.group].frames[state.frame];if(!frame)throw new TypeError("Cannot read properties of undefined (reading 'file')");},requestAnimationFrame(){scheduled++;}};
  vm.createContext(sandbox);vm.runInContext(frameAt+"\n"+tick,sandbox);
  timestamps.forEach(t=>sandbox.tick(t));
  return {state,renders,scheduled};
}
const first=probe(100,[99,139,179]); // rAF timestamp may precede performance.now sampled in script.
assert(first.state.frame>=0,"clock must never select a negative frame");
assert(first.state.frame>0,"frame must advance after the first callback");
const normal=probe(null,[100,140,180]);
assert.equal(normal.state.frame,2,"normal speed advances two frames in 80ms after clock initialization");
const slow=probe(null,[100,140,180],.25);
assert.equal(slow.state.frame,0,"quarter speed holds first frame after 80ms");
console.log("PASS: nonnegative first timestamp, normal advance, quarter-speed timing");

