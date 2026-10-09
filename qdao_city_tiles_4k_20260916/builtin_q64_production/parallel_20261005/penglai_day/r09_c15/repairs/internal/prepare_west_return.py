import sys
sys.dont_write_bytecode=True
from PIL import Image,ImageDraw
import ai_helper as h
O=h.O
src=O/'joint-candidate-west-v1.png';im=Image.open(src).convert('RGB');p=O/'west-return-edit-input.png';im.crop((0,1024,1254,2278)).save(p);h.derived(p,[src],{'method':'native1254crop','jointOrigin':[0,1024]})
mask=Image.new('L',(1254,1254));d=ImageDraw.Draw(mask);d.rectangle((540,10,780,200),fill=255);d.rectangle((550,930,760,1253),fill=255);m=O/'west-return-target-mask.png';mask.save(m);h.derived(m,[p],{'method':'editing target locator only, white repair regions, no final pixels'})
h.savecall('west-return-ai-v2','Image1 is actual1254x1254 native map crop. Image2 approved painting style, never UI. Image3 is a black and white repair locator only: repair inside WHITE areas while preserving the real Image1 surrounding content. There is still a false vertical paint discontinuity at x627: near the top it visibly splits the golden diagonal wooden rail into lighter and darker halves; near the bottom x627 sharply truncates blue-green leaf forms. Remove this artificial line from these two WHITE regions by reconstructing continuous wood material/highlight and complete existing leaf silhouettes. Keep the exact rail outline and all existing leaf positions/counts, do not introduce new items. Same crop, perspective, scale, color and bright rounded Q hand painting. No blur, no grain, no soft seam blending, no extra shadows. Output exactly1254x1254.',[p,h.STYLE,m],['native joint crop','actual approved style04-guild','binary target locator, never final image'])
