from pathlib import Path
import subprocess,sys,json
candidate=Path(__file__).resolve().parent
if candidate.name!='23_lantern_courier' or candidate.parent.name!='candidate-stable-body':raise SystemExit('Separate23candidate only')
common=candidate.parent.parent;review=common/'review/23_lantern_natural_fixes'
commands=[[sys.executable,str(review/'assemble_candidate.py')],[sys.executable,str(common/'process_roster.py'),'--character-dir',str(candidate),'--alignment-version','3','--common-scale','1.0194174757281553','--component-padding','2','--despill-magenta-edge','--despill-radius','4']]
for k in ['s_e','n_w','ne_sw','nw_se']:commands[1]+=['--'+k.replace('_','-'),str(candidate/f'source/{k}.png')]
commands[1]+=['--idle',str(candidate/'source/idle.png'),'--portrait',str(common/'23_lantern_courier/portrait.png')]
commands.append([sys.executable,str(common/'verify_delivery.py'),'--character-dir',str(candidate),'--allow-pending-visual'])
(review/'processing-commands.json').write_text(json.dumps(commands,indent=2)+'\n',encoding='utf-8')
for command in commands:subprocess.run(command,check=True)
