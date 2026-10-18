from workflow import *
pid='r09_c10_p24';v='v03'
base=ROOT/'native'/f'{pid}_v02.png';north=ROOT/'native'/'r09_c10_p14_v01.png';east=ROOT/'tiles'/'r09_c11.candidate-v05.png'
im=Image.open(base).convert('RGB')
im.paste(Image.open(north).convert('RGB').crop((0,1024,1254,1139)),(0,0))
im.paste(Image.open(east).convert('RGB').crop((0,909,115,2163)),(1139,0))
guide=ROOT/'guides'/f'{pid}.selected-core-halo-wall16-{v}.png';assert not guide.exists();im.save(guide)
parts=[{'file':str(x),'sha256':sha(x)} for x in [base,north,east]]
write(Path(str(guide)+'.generation.json'),{'file':str(guide),'sha256':sha(guide),'derivedFrom':parts,'operation':'unscaled integer crops of true selected N/E core pixels over current repair candidate; guide only','usableAsFinalArt':False})
prompt='''Use case: precise-object-edit. Output a single opaque native 1254 x 1254 close-up. Image 1 is exact edit target. Fix the visible false vertical rectangle at x1024: the underside of the TOP wooden rail has a sharp hanging squared step there, and some paving joints change at the same vertical line. Repaint ONLY the narrow transition zone around x800..1139 so the upper rail has one continuous straight diagonal underside and the paving below has continuous joints. The topmost 115 rows and rightmost 115 columns now contain the ACTUAL selected neighboring map pixels; match them exactly at the crop seam. Earlier erroneous guides froze 230px and left a false line at1024: remove that line entirely from the interior. Preserve the main upright post and its carved ivory pedestal at left, small golden double-bulbed gourd and red tassel at center, the large golden instrument cropped at right, all leaves, and the corrected open paving at bottom-right. Do not add lower crossbars. The result must keep exact camera framing and scale, no zoom out, no other objects, no text, no UI, no blur. Crisp Q Daoist hand-painted daytime map. Only seam geometry correction.'''
pf=ROOT/'prompts'/f'{pid}_{v}.prompt.txt';pf.write_text(prompt,encoding='utf-8')
refs=[{'file':str(guide),'sha256':sha(guide),'role':'Exact local edit target with true selected neighboring core pixels only in top/right halo'}]
write(ROOT/'prompts'/f'{pid}_{v}.request.json',{'promptPath':str(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}})
write(ROOT/'prompts'/f'{pid}_{v}.args.json',{'prompt':prompt,'referenced_image_paths':[str(guide)],'transparent_background':False})
print(guide)
