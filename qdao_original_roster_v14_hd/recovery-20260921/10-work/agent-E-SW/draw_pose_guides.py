"""Draw original non-character pose diagrams solely as generation inputs.

No source image is opened, edited, warped, mirrored, or counted as an action.
"""
from pathlib import Path
from PIL import Image, ImageDraw

out = Path(__file__).parent
im = Image.new('RGB', (1024,1024), '#f4f2eb')
d = ImageDraw.Draw(im)
d.text((45,32),'E01 POSE GUIDE ONLY - RIGHT FACING',fill='#222222',font_size=28)
d.text((45,78),'FAR LEFT leg = orange, FORWARD on higher track',fill='#a95c04',font_size=24)
d.text((45,116),'NEAR RIGHT leg = cyan, BACK on lower track',fill='#046f8b',font_size=24)
d.line((260,918,790,918),fill='#d8b174',width=2)
d.line((240,946,790,946),fill='#85c5cc',width=2)
d.ellipse((390,198,612,420),fill='#d6d2c9',outline='#57534b',width=6)
d.polygon([(606,301),(655,325),(608,337)],fill='#d6d2c9',outline='#57534b')
d.ellipse((573,286,584,301),fill='#222222')
d.rounded_rectangle((450,416,596,698),radius=45,fill='#d6d2c9',outline='#57534b',width=6)
# Far LEFT leg is drawn first, behind near RIGHT thigh.
d.line([(554,674),(604,789),(652,905)],fill='#bc6c13',width=59,joint='curve')
d.ellipse((629,882,674,925),fill='#bc6c13')
d.polygon([(638,889),(659,889),(716,885),(722,904),(645,918)],fill='#e59a45',outline='#76450c')
# Near RIGHT leg occludes the far thigh and reaches backward screen-left.
d.line([(510,683),(480,801),(421,897)],fill='#079ab2',width=66,joint='curve')
d.ellipse((399,874,447,923),fill='#079ab2')
d.polygon([(407,886),(428,878),(457,914),(494,932),(487,943),(447,934),(416,911)],fill='#44c9d7',outline='#045c73')
d.text((660,784),'FAR',fill='#9b5609',font_size=28)
d.text((283,812),'NEAR',fill='#036a7b',font_size=28)
d.text((625,955),'LEFT heel',fill='#9b5609',font_size=24)
d.text((358,972),'RIGHT toe',fill='#036a7b',font_size=24)
d.line((720,365,925,365),fill='#343434',width=10)
d.polygon([(925,365),(887,346),(887,384)],fill='#343434')
im.save(out/'E01-pose-guide.png')
