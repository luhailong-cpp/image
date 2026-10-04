async function(direction,frame,prompt,motionRef,attempt=1,editTarget=null) {
const root="D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/02_fire_talisman_boy";
const id="run-"+direction+"-"+String(frame).padStart(2,"0")+"-grounding-v3-20261004-candidate"+attempt;
const refs=[editTarget||root+"/frames/run/"+direction+"/"+String(frame).padStart(2,"0")+".png","D:/work/image/q_daoist_character_pack_4096/02_fire_talisman_boy_transparent_4096.png","D:/work/image/qdao_original_roster_v13/candidate/02_fire_talisman_boy/idle/"+direction+".png","D:/work/image/designs/jubaozhai-ui/02-characters.png",motionRef];
const recordPath=root+"/reviews/"+id+".generation.json",nativePath=root+"/reviews/"+id+".native.png",promptPath=root+"/reviews/"+id+".prompt.txt";
const pre=await tools.exec_command({cmd:"$taskPaths=@("+refs.map(p=>"'"+p+"'").join(",")+"); if(Test-Path -LiteralPath '"+recordPath+"'){throw 'Candidate record exists; choose next attempt'}; $taskRows=@($taskPaths | ForEach-Object { [pscustomobject]@{path=$_;sha256=(Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash.ToLower()} }); [pscustomobject]@{refs=$taskRows;config=(Get-Content -Raw 'D:/work/image/config/image-generation.json'|ConvertFrom-Json)} | ConvertTo-Json -Depth 8",max_output_tokens:3000});
if(pre.exit_code!==0)throw Error(pre.output);
const meta=JSON.parse(pre.output);
const args={prompt,referenced_image_paths:refs,transparent_background:true};
await tools.apply_patch("*** Begin Patch\n*** Add File: "+promptPath+"\n+"+prompt.split("\n").join("\n+")+"\n*** End Patch");
const record={schemaVersion:1,action:"run",direction,frame,status:"pending_candidate_not_imported",file:"reviews/"+id+".native.png",submittedAt:new Date().toISOString(),timezone:"America/New_York",tool:"image_gen.imagegen",route:"builtin",configSnapshot:meta.config,submittedParameters:{...args,model:null,quality:null},actualModel:null,actualQuality:null,unverifiedReason:"宿主管理，工具无model/quality选择器，未披露实际型号与质量。",prompt:"reviews/"+id+".prompt.txt",references:meta.refs.map((x,i)=>({...x,role:["edit_target","identity","direction_identity","confirmed_style","motion_only"][i],viewed:true})),formalImport:false};
let result;
try {
result=await tools.image_gen__imagegen(args);
const match=result.output_hint.match(/as (C:\\[^\n]+?\.png) by default/);
if(!match)throw Error("Tool result did not expose expected native output path: "+String(result.output_hint));
record.evidence={sourcePath:match[1],resultKeys:Object.keys(result),output_hint:result.output_hint};
const save=await tools.exec_command({cmd:"if(Test-Path -LiteralPath '"+nativePath+"'){throw 'Native candidate already exists'}; Copy-Item -LiteralPath '"+match[1]+"' -Destination '"+nativePath+"'; Add-Type -AssemblyName System.Drawing; $taskIm=[System.Drawing.Image]::FromFile('"+nativePath+"'); $taskMeta=[pscustomobject]@{width=$taskIm.Width;height=$taskIm.Height;format='PNG';sha256=(Get-FileHash -LiteralPath '"+nativePath+"' -Algorithm SHA256).Hash.ToLower();generatedAt=[System.TimeZoneInfo]::ConvertTimeBySystemTimeZoneId([DateTimeOffset]::UtcNow,'Eastern Standard Time').ToString('o')}; $taskIm.Dispose(); $taskMeta | ConvertTo-Json",max_output_tokens:1500});
if(save.exit_code!==0)throw Error(save.output);
Object.assign(record,JSON.parse(save.output),{status:"generated_candidate_not_imported",generatedAtMeaning:"复制记录时间，非服务器披露时间"});
} catch(e) {record.status="error";record.error=String(e);record.errorStack=e?.stack||null;}
await tools.apply_patch("*** Begin Patch\n*** Add File: "+recordPath+"\n+"+JSON.stringify(record,null,2).split("\n").join("\n+")+"\n*** End Patch");
text({status:record.status,file:record.file,sha256:record.sha256,width:record.width,height:record.height,error:record.error});
if(result&&record.status!=="error")generatedImage(result);
return record;
}
