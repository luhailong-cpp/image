async function(job){
const b="D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/02_fire_talisman_boy", {id,frame,direction,prompt,refs,native}=job;
const args={prompt,referenced_image_paths:refs.map(x=>x.path),transparent_background:true};
const started=(await tools.clock__curr_time({})).current_time;
const patch=async(path,obj)=>{await tools.apply_patch('*** Begin Patch\n*** Add File: '+b+'/'+path+'\n+'+(typeof obj==='string'?obj:JSON.stringify(obj,null,2)).split('\n').join('\n+')+'\n*** End Patch')};
await patch('prompts/'+id+'.txt',prompt);await patch('records/'+id+'.submitted.json',{startedAt:started,tool:'image_gen.imagegen',model:null,quality:null,...args});
try {
const result=await tools.image_gen__imagegen(args),ended=(await tools.clock__curr_time({})).current_time,source=result.output_hint?.match(/ as (.+?) by default\./)?.[1];
if(!source?.startsWith('C:\\Users\\luyua\\.codex\\generated_images\\'))throw {reason:'Unexpected output structure',keys:Object.keys(result??{}),output_hint:result?.output_hint};
const record={file:native,generatedAt:new Date(new Date(ended.replace(' UTC','Z').replace(' ','T')).getTime()-4*3600000).toISOString().replace('Z','-04:00'),generationStartedAt:started,timeZone:'America/New_York',tool:'image_gen.imagegen',route:'builtin',intent:job.intent||'independent pose repaint',configSnapshot:load('castConfig'),submittedParameters:{model:null,quality:null,...args},actualModel:null,actualQuality:null,unverifiedReason:'宿主管理；工具无 model/quality 选择器，返回未披露实际版本/质量。',prompt:'prompts/'+id+'.txt',references:refs,evidence:{receipt:'records/'+id+'.receipt.json',hostOutput:source,submitted:'records/'+id+'.submitted.json'},visualQA:{status:'not_reviewed'}};
await patch('records/'+id+'.receipt.json',{startedAt:started,completedAt:ended,resultKeys:Object.keys(result),output_hint:result.output_hint});await patch('records/'+id+'.generation.json',record);
text(await tools.exec_command({cmd:"Copy-Item -LiteralPath '"+source+"' -Destination '"+b+'/'+native+"'",max_output_tokens:400}));
generatedImage(result);text({saved:true,id,frame,direction});return true;
}catch(e){const error={raw:e,errorType:typeof e,errorString:String(e),startedAt:started,failedAt:(await tools.clock__curr_time({})).current_time};await patch('records/'+id+'.error.json',error);text({id,error});return false;}
}
