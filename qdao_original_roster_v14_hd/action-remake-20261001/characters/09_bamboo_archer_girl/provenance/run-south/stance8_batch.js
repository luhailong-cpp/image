async function stanceBatch(paths){
 const root="D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/09_bamboo_archer_girl",py="C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe";
 const q=s=>"'"+String(s).replace(/'/g,"''")+"'";
 async function shell(cmd){let r=await tools.exec_command({cmd,workdir:root,yield_time_ms:30000,max_output_tokens:4000}),out=r.output;while(r.session_id){r=await tools.write_stdin({session_id:r.session_id,chars:"",yield_time_ms:1000,max_output_tokens:4000});out+=r.output;} if(r.exit_code!==0)throw Error(out);return out;}
 const prepared=[];
 for(const spec of paths){prepared.push(JSON.parse((await shell("& "+q(py)+" -X utf8 "+q(root+"/tools/prepare_repair_frame.py")+" "+q(spec))).trim()));}
 const results=await Promise.allSettled(prepared.map(async p=>{
  const recPath=p.request.replace(/\.request\.json$/,".receipt.json");
  try{
   const result=await tools.image_gen__imagegen(p.args);text({generatedSlot:p.action+'/'+p.direction+'/'+p.frame});generatedImage(result);
   const m=(result.output_hint||"").match(/ as (.+?\.png) by default/);
   if(!m)throw Error("Native path missing");
   const receipt={returnedAt:new Date().toISOString(),output_hint:result.output_hint,actualModel:null,actualQuality:null};
   await tools.apply_patch("*** Begin Patch\n*** Add File: "+recPath+"\n+"+JSON.stringify(receipt,null,2).replaceAll("\n","\n+")+"\n*** End Patch");
   return {p,recPath,native:m[1]};
  }catch(e){text({request:p.request,error:String(e)});throw e;}
 }));
 for(const result of results){
  if(result.status==="fulfilled"){const {p,recPath,native}=result.value;text(await shell("& "+q(py)+" -X utf8 "+q(root+"/tools/register_e_frame.py")+" register --action "+p.action+" --direction "+p.direction+" --frame "+p.frame+" --native "+q(native)+" --request "+q(p.request)+" --receipt "+q(recPath)));}
  else text({failed:String(result.reason)});
 }
}
