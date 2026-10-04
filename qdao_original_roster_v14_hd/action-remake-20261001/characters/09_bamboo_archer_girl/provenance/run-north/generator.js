async function run(d,f) {
 const root="D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/09_bamboo_archer_girl";
 const py="C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe";
 const q=s=>"'"+String(s).replace(/'/g,"''")+"'";
 const p=await tools.exec_command({cmd:"& "+q(py)+" -X utf8 "+q(root+"/provenance/run-north/prepare_frame.py")+" "+d+" "+f,max_output_tokens:4000});
 if(p.exit_code!==0)throw Error(p.output);
 const prep=JSON.parse(p.output.trim()),path=prep.request.replace(/\.request\.json$/,".receipt.json");
 try{
 const r=await tools.image_gen__imagegen(prep.args);generatedImage(r);
 const native=(r.output_hint||"").match(/ as (.+?\.png) by default/);
 const receipt={returnedAt:new Date().toISOString(),output_hint:r.output_hint||null,actualModel:null,actualQuality:null};
 await tools.apply_patch("*** Begin Patch\n*** Add File: "+path+"\n+"+JSON.stringify(receipt,null,2).split("\n").join("\n+")+"\n*** End Patch");
 if(!native)throw Error("Native path unavailable");
 text(await tools.exec_command({cmd:"& "+q(py)+" -X utf8 "+q(root+"/provenance/run-north/save_frame.py")+" "+d+" "+f+" "+prep.attempt+" "+q(native[1]),max_output_tokens:1000}));
 }catch(e){
 await tools.apply_patch("*** Begin Patch\n*** Add File: "+prep.request.replace(/\.request\.json$/,".error.json")+"\n+"+JSON.stringify({failedAt:new Date().toISOString(),error:String(e)},null,2).split("\n").join("\n+")+"\n*** End Patch");throw e;
 }
}
