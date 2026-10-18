from workflow import *
import re
ds={'12':'Continue dense existing green garden and small pink/white flowers across the upper part; plain pale grey paving below-left, a few existing scattered red paper scraps at the guide positions. A very narrow crop of the existing ivory balustrade enters the extreme bottom-right corner diagonally; keep it clipped, do not fit a full pillar or fence here. No raised garden edging, pots, extra pillars or medallions.', '21':'Existing pale-grey courtyard paving across the upper half and left, with sparse existing red paper scraps. Lower-left flowering bush. ONE large existing square ivory balustrade post occupies the right/lower portion, with rounded pale cap around x900 y500 and its vertical shaft continuing out the bottom edge into the exact sharp lower overlap. The next ivory wall panel rises diagonally toward the right and leaves the right edge. Continue this actual pillar from the sharp BOTTOM anchor, preserve its cross-section, not a second or miniature pillar. No decorative paving borders, new posts or extra architecture.'}
for rc,d in ds.items():
 stem=f'r08_c13_p{rc}_v01';af=ROOT/'prompts'/f'{stem}.args.json';a=read(af)
 a['prompt']=re.sub(r'LOCAL CONTENT AND GEOMETRY:.*?\n\nKeep','LOCAL CONTENT AND GEOMETRY: '+d+'\n\nKeep',a['prompt'],flags=re.S)
 rf=ROOT/'prompts'/f'{stem}.request.json';rq=read(rf)
 if rc=='21':
  g=ROOT/'guides'/'r08_c13_p21.native-context-v02.png';a['referenced_image_paths'][0]=str(g);rq['references'][0].update(file=str(g),sha256=sha(g))
 Path(rq['promptPath']).write_text(a['prompt'],encoding='utf-8');write(rf,rq);write(af,a)
print('Refined exact local content and added south pillar anchor for 21.')
