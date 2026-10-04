async function genSouth(d,f){
 const py="C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe";
 const script="D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/09_bamboo_archer_girl/provenance/run-south/produce_v2.py";
 const q=s=>"'"+s.replaceAll("'","''")+"'";
 const prep=await tools.exec_command({cmd:`& ${q(py)} -X utf8 ${q(script)} prepare ${d} ${f}`,max_output_tokens:6000});
 if(prep.exit_code!==0)throw Error(prep.output);
 const job=JSON.parse(prep.output);
 try{
  const result=await tools.image_gen__imagegen(job.args);
  generatedImage(result);
  const match=(result.output_hint||"").match(/ as (.+?\.png) by default/);
  if(!match)throw Error("No native output path in output_hint: "+result.output_hint);
  const receipt=job.request.replace(".request.json",".receipt.json");
  const data={completedAt:new Date().toISOString(),nativeSourcePath:match[1],output_hint:result.output_hint,actualModel:null,actualQuality:null,unverifiedReason:"Host managed builtin; no disclosed model/quality."};
  await tools.apply_patch("*** Begin Patch\n*** Add File: "+receipt.replaceAll("\\","/")+"\n+"+JSON.stringify(data,null,2).replaceAll("\n","\n+")+"\n*** End Patch");
  const reg=await tools.exec_command({cmd:`& ${q(py)} -X utf8 ${q(script)} register ${q(job.request)} ${q(receipt)}`,max_output_tokens:1200});text(reg.output);if(reg.exit_code!==0)throw Error(reg.output);
 } catch(e) {
  const p=job.request.replace(".request.json",".error.json").replaceAll("\\","/");
  await tools.apply_patch("*** Begin Patch\n*** Add File: "+p+"\n+"+JSON.stringify({at:new Date().toISOString(),error:String(e)},null,2).replaceAll("\n","\n+")+"\n*** End Patch");throw e;
 }
}
