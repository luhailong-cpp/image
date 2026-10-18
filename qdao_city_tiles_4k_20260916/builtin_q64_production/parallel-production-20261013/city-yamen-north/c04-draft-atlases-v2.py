from pathlib import Path
from PIL import Image
B=Path(__file__).resolve().parent;D=B/'r02_c04/qa/draft-native4096-v002'
for c in range(1,4):
 out=D/f'v-c{c}-native100-atlas.png';assert not out.exists()
 a=Image.new('RGB',(1280,1024))
 for r in range(1,5):a.paste(Image.open(D/f'vertical-r{r}-c{c}.png'),((r-1)*320,0))
 a.save(out)
for r in range(1,4):
 out=D/f'h-r{r}-native100-atlas.png';assert not out.exists()
 a=Image.new('RGB',(1024,1280))
 for c in range(1,5):a.paste(Image.open(D/f'horizontal-r{r}-c{c}.png'),(0,(c-1)*320))
 a.save(out)
a=Image.new('RGB',(960,960))
for r in range(1,4):
 for c in range(1,4):a.paste(Image.open(D/f'junction-r{r}-c{c}.png'),((c-1)*320,(r-1)*320))
out=D/'junctions-native100-atlas.png';assert not out.exists();a.save(out)
print(str(D))

