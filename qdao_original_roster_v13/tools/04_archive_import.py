import json,subprocess,sys,shutil
from pathlib import Path
from PIL import Image
root=Path(r'E:/work/image/qdao_original_roster_v13'); char='04_mountain_guardian_boy'
for x in json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig')):
 d=root/'generation'/char/x['batch']; d.mkdir(parents=True,exist_ok=True)
 if not (d/'raw.png').exists():shutil.copy2(x['src'],d/'raw.png')
 rec={'tool':'image_gen','model_requested':'GPT Image2 user-authorized builtin','output_hint':x['hint'],'source_tool_path':x['src'],'references':x.get('refs',[]),'output_frames':x['map'],'status':'pending_complete_cycle_visual','actual_visual_notes':x.get('visual_notes','')}
 (d/'receipt.json').write_text(json.dumps(rec,indent=2)+'\n',encoding='utf8')
 args=[sys.executable,'-B',str(root/'tools/pipeline.py'),'import-walk','--character',char,'--direction',x['dir'],'--source',str(d/'raw.png'),'--prompt',str(d/'prompt.txt'),'--receipt',str(d/'receipt.json'),'--batch-id',x['batch'],'--rows',str(x['rows']),'--cols',str(x['cols']),'--output-frames',','.join(map(str,x['map'])),'--common-scale','.84']
 if x.get('select'):args+=['--source-cell-indices',','.join(map(str,x['select']))]
 subprocess.run(args,check=True)
