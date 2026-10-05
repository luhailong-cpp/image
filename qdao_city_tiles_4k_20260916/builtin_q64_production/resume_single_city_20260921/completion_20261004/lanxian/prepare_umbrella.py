from pathlib import Path
import hashlib,json,datetime,shutil
R=Path(__file__).resolve().parent
O=R/'lanxian_day/umbrella-repair';O.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=next(t['source'] for t in json.loads((R/'sources.json').read_text(encoding='utf-8'))['tiles'] if t['city']=='lanxian_day' and t['tile']=='r08_c06')
assert sha(source['file'])==source['sha256']
context=O/'context.png';shutil.copy2(R/'lanxian_day/baseline/umbrella-y3072.png',context)
style=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
cfg=json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8'))
prompt='''Edit reference image 1, a 1254 by 1254 native-pixel crop of an existing Chinese fantasy Q-style game town map. Produce exactly the same crop and composition, with no resizing or re-framing. Reference image 2 is the approved PRIMARY PAINTING STYLE only: clean, bright, softly rounded, full-bodied handmade game illustration with delicate wood and blue ceramic materials. Do not add UI, text, symbols, new buildings or objects.

Repair ONLY the broken and offset ribs on the pink umbrella in the lower-left/center. Several thin dark-pink rib lines become disconnected or offset around local x=100..650, y=480..800. Join each umbrella rib into one smooth continuous radial line from its existing upper section to its existing lower section, preserving all correct rib endpoints and the existing scalloped umbrella silhouette. Remove short isolated duplicate segments and hard patch-shaped pink shading transitions around that repair. The ribs must be single, crisp, fine lines, no ghost/double edges and no new folds. Preserve the umbrella's original radial fan structure, soft pink shading and the broad diagonal sunlight/shadow band; make the repair look hand-painted and naturally coherent.

Strictly preserve the entire blue roof, eave tiles, wooden walls, green foliage and the outer 64-pixel boundary. Keep their exact geometry, position, scale and color; focus all edits inside the pink canopy. Do not redesign anything. Output one opaque square image at the native reference resolution. Highest visual quality goal follows the project's host-managed ChatGPT Images 2.5 setting; no claim of explicit tool model/quality selectors.'''
(O/'prompt.txt').write_text(prompt,encoding='utf-8')
req={'prompt':prompt,'referenced_image_paths':[str(context),str(style)],'transparent_background':False}
(O/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(O/'preparation.json').write_text(json.dumps({'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':source,'cropLTRB':[0,2445,1254,3699],'configSnapshot':cfg,'references':[{'file':str(context),'sha256':sha(context),'role':'edit target at native scale'},{'file':str(style),'sha256':sha(style),'role':'approved primary painting style'}],'requestSha256':sha(O/'request.json'),'status':'prepared_not_submitted'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(req,ensure_ascii=False))
