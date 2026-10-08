from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
D=Path(__file__).parent;P=D/'repair-v1';P.mkdir(exist_ok=True)
a=np.array(Image.open(D/'native.png').convert('RGBA'));c=np.array(Image.open(D/'context.png').convert('RGBA'))
a[1100:,:1139]=c[1100:,:1139]
a[780:1100]=0;a[1100:,1139:]=0
Image.fromarray(a).save(P/'target.png')
ref=lambda p:{'file':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
q=json.loads((D/'request.json').read_text(encoding='utf-8-sig'))
q['payload']={'prompt':'''Use case precise local edit / masked inpainting. Return exactly1254 by1254 at original scale. Image1 is the actual edit target with a transparent black band y780..1100 and tiny transparent bottom-right tail. Its opaque upper roof/column and lower true adjoining stone base are immutable geometry anchors. Paint only the missing region, naturally connecting the same green-and-gold cylindrical festive pole body, the red oval hanging pendant and the green-gray stone foot to the EXACT bottom positions now shown. The lower source is authoritative: red pendant tip must remain at its visible exact location, do not shift upward, duplicate it, or float another foot above it. Complete clean solid ornament, no cracks. Preserve upper roof and its existing two right hanging tassels. Connect right stone paving and broad shadow to its known lower edge without a horizontal stripe. The correct exact same-world original layout is image2; image3 supplies approved bright rounded Daoist Q handpainted finish, image4 nearby finished map style only. No zoom, reframe, rotation, warp, rescale, extra object, text or watermark. Output complete opaque1254 square.''','referenced_image_paths':[str(P/'target.png'),str(D/'layout-reference-only.png'),q['payload']['referenced_image_paths'][2],q['payload']['referenced_image_paths'][3]],'transparent_background':False}
q['operation']='native AI seam repair';(P/'request.json').write_text(json.dumps(q,indent=2,ensure_ascii=False),encoding='utf8')
(P/'target.png.generation.json').write_text(json.dumps({'output':ref(P/'target.png'),'sources':[ref(D/'native.png'),ref(D/'context.png')],'maskRectangle':[0,780,1254,1100],'extraMask':[1139,1100,1254,1254],'nativeScale':1,'newModelCalls':0,'operation':'Exact anchor composition with transparent repair gap'}),encoding='utf8')
