from pathlib import Path
import hashlib,json,datetime,shutil
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=next(t['source'] for t in json.loads((R/'sources.json').read_text(encoding='utf-8'))['tiles'] if t['city']=='lanxian_spring' and t['tile']=='r08_c06')
assert sha(source['file'])==source['sha256']
style=Path('D:/work/image/designs/gameplay-ui/04-guild.png');cfg=json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8'))
tasks=[('upper-umbrella',[0,397,1254,1651],'''Repair ONLY the broken thin white curved ribs and rings in the pink canopy on the left, local x=0..500,y=410..860. A curved line ends around x=310,y=670 and another segment begins nearby instead of joining; a radial white rib is offset/disconnected around x=230,y=650. Reconnect each existing rib/ring into one smooth single continuous line on the pink canopy. Retain the correct umbrella structure and existing line endpoints. Remove disconnected short duplicate stubs. Do not add or remove ribs or change the outer canopy silhouette. Preserve the blue roof, red fabric and architecture, including their exact positions and scale.''','pink'),('grout-x2048',[1421,0,2675,1254],'''Repair ONLY the broken diagonal stone grout/bevel behind the red ornament, near local x=620..735,y=265..345. Its lower-left segment stops abruptly near x=660,y=325 while its upper-right continuation begins around x=670,y=280; connect these into ONE continuous thin warm beige groove with a white bevel highlight, matching the slope and thickness of the adjoining original stone boundary. Remove the hard gap and dangling duplicate edge. Keep all stone corners and every other grout line exactly in place. Keep the red banner, gold emblem, blue roof, shadows, texture and framing unchanged. Do not create new cracks, lines, patterns or objects.''','rect')]
for name,box,note,kind in tasks:
 O=R/f'lanxian_spring/{name}-repair';O.mkdir(exist_ok=True)
 context=O/'context.png';shutil.copy2(R/f'lanxian_spring/baseline/{name}.png',context)
 prompt='''Edit reference image 1, an exact native 1254x1254 crop from an existing Chinese fantasy Q-style town map. Return one opaque 1254x1254 image with identical framing, scale and object placement. Reference image 2 is the approved PRIMARY PAINTING STYLE only: bright clean rounded hand-painted Chinese fantasy game finish, warm ivory, rich blue ceramic, red lacquer and gold, no UI or text.
'''+note+'''
Make the smallest precise local structural repair. Preserve every unrelated pixel region and outer 64px attachment context as closely as possible. Crisp single contours, no blur, no doubled lines, no zoom or crop, no global color change. Highest host-managed quality goal, without assuming tool model or quality selectors.'''
 (O/'prompt.txt').write_text(prompt,encoding='utf-8')
 req={'prompt':prompt,'referenced_image_paths':[str(context),str(style)],'transparent_background':False}
 (O/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 prep={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':source,'cropLTRB':box,'configSnapshot':cfg,'references':[{'file':str(context),'sha256':sha(context),'role':'native edit target'},{'file':str(style),'sha256':sha(style),'role':'approved primary painting style'}],'maskKind':kind,'maskRect':[420,120,900,540] if kind=='rect' else None,'status':'prepared_not_submitted'}
 (O/'preparation.json').write_text(json.dumps(prep,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Prepared two verified structural repairs')
