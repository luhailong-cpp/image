from pathlib import Path
import json,shutil,hashlib
ROOT=Path(__file__).resolve().parent
T=ROOT/'r07_c15'; name='r02_c04'
D=T/'rejected/r02_c04-contact-highlight-removed';D.mkdir(parents=True,exist_ok=True)
record=json.loads((T/'native'/f'{name}.png.generation.json').read_text(encoding='utf-8'))
oldprompt=T/'prompts'/f'{name}.txt'
shutil.copy2(oldprompt,D/'prompt.txt')
record['originalPromptPath']=record['prompt'];record['prompt']=str(D/'prompt.txt')
record['rejection']='Generation removed required existing white/cyan piling-water contact rim and the actual right-neighbor contact/shadow. No downstream guide uses this rejected native.'
(D/'generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prompt='Use case: precise-object-edit. IMAGE 1 is the exact edit target for a native-pixel fishing-village map crop. Preserve EVERY existing silhouette, location, water highlight and cast shadow. Especially preserve the broad pale white/cyan water contact rim around the large left piling bottom AND the already crisp cyan/white contact flare and dark blue cast shadow around the cropped RIGHT piling at y800..1254. These are real required scene features and actual adjacent tile context; do not remove, fade, recolor, shrink or move them. Polish only the existing wooden pier front, warm left piling and dark little hanging structure under the pier. Keep the whole rightmost230 pixels geometry and hues intact, smoothly extending leftward. Keep actual top230-pixel neighboring timber colors and grain continuation. Remove only artificial sharp/soft resolution boundaries by completing the same object. Retain the broad quiet blue/cyan water elsewhere; add no new streaks, foam, ripples, caustic cells, poles, planks, rope or objects. IMAGE 2 supplies approved bright rounded Q-style hand-painted materials, no UI. Exact original crop and viewpoint, opaque native1254x1254, no text, border, blur filter or scaling.'
oldprompt.write_text(prompt,encoding='utf-8')
print(json.dumps({'name':name,'prompt':prompt,'references':[str(T/'guides'/f'{name}.png'),'D:/work/image/designs/gameplay-ui/04-guild.png']}))
