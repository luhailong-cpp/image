from ai_helper import *
from PIL import ImageDraw
specs={'roof-return':{'origin':[0,0],'holes':[(858,510,1020,662)],'description':'complete the interrupted smooth golden roof tile curved bevel: the pale highlight and dark brown thin outer contour must flow naturally through the hole with matching tangent and thickness. Do not create a notch or step.'},'paving-return':{'origin':[0,2445],'holes':[(294,560,415,665)],'description':'complete the diagonal cream stone bevel highlight and pale grey vertical bevel face through the hole in one continuous smooth straight diagonal. Its thin white upper lip must have no jagged notch or step.'}}
for n,s in specs.items():
 target=Image.open(O/'joint-candidate-v2.png').crop((s['origin'][0],s['origin'][1],s['origin'][0]+1254,s['origin'][1]+1254)).convert('RGBA');base=O/(n+'-source.png');target.convert('RGB').save(base);derived(base,[O/'joint-candidate-v2.png'],{'nativeCropOrigin':s['origin'],'scale':1})
 d=ImageDraw.Draw(target)
 for box in s['holes']:d.rectangle(box,fill=(0,0,0,0))
 hole=O/(n+'-hole-input.png');target.save(hole);derived(hole,[base],{'method':'transparent repair holes only','holeRectanglesLTRBInclusive':s['holes']})
 prompt=f'''Use case: precise-object-edit. Fill only the small transparent hole in Image 1, which is a native 1254 x 1254 game-map repair input. Return a fully opaque image at exactly 1254 x 1254, with every existing opaque pixel and exact framing preserved. The transparent rectangle is missing art, not a real object. Reconstruct the existing painted structure smoothly between its exact surrounding endpoints: {s['description']} Image 2 is the actual approved visual style reference only, a finished bright rounded Taoist Q-game UI; borrow only its polished painterly material handling, not any UI layout, words or symbols. Keep all objects, shadows, outlines and textures outside the transparent hole unchanged. Match local colors and brush density precisely. No zoom, resize, warp, blur, feathering, new objects, text or watermark.'''
 savecall(n+'-ai-v1',prompt,[hole,STYLE],['native1254 edit target with transparent local repair hole','actual approved 04-guild style reference'])
(O/'local-return-specs.json').write_text(json.dumps(specs,indent=2),encoding='utf8')
print('2 native hole edits prepared')
