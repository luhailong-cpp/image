from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
f=ROOT/'r10_c13';qa=f/'qa/first-row';qa.mkdir(exist_ok=True)
sources=[f/f'native/p1{i}.png' for i in range(1,5)]
raw=Image.new('RGB',(4096,1024))
for i,s in enumerate(sources):raw.paste(Image.open(s).convert('RGB').crop((115,115,1139,1139)),(i*1024,0))
preview=qa/'preview.png';raw.resize((2048,512),Image.Resampling.LANCZOS).save(preview)
deriv(preview,sources,dict(kind='unregistered_first_row_preview_only',cropPerPatchLTRB=[115,115,1139,1139],scale=.5,notSeamAcceptance=True))
seams=Image.new('RGB',(960,1024))
for i,x in enumerate([1024,2048,3072]):seams.paste(raw.crop((x-160,0,x+160,1024)),(i*320,0))
out=qa/'internal-raw.png';seams.save(out);deriv(out,sources,dict(kind='three_raw_internal_first_row_seams',positions=[1024,2048,3072],contextEachSide=160,scale=1,registration=False))
plan=read(f/'plan.json');n=Path(plan['northCandidate']);top=Image.new('RGB',(4096,320));top.paste(Image.open(n).convert('RGB').crop((0,3936,4096,4096)),(0,0));top.paste(raw.crop((0,0,4096,160)),(0,160))
sheet=Image.new('RGB',(1024,1280))
for i in range(4):sheet.paste(top.crop((i*1024,0,(i+1)*1024,320)),(0,i*320))
out=qa/'north-raw.png';sheet.save(out);deriv(out,[n]+sources,dict(kind='raw_north_full4096_folded',scale=1,registration=False))
print(str(qa))
