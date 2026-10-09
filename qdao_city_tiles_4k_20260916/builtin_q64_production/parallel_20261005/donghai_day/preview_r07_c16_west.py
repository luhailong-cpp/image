from pathlib import Path
import sys
from PIL import Image
import assembly_r07_c16 as a
R=Path(__file__).resolve().parent;T=R/'r07_c16';D=T/'repairs/west-provisional-qa'
W=R/'r07_c15/output/r07_c15.png';E=T/'repairs/integrated-south-v2/candidate.png'
if '--refined' in sys.argv:W=R/'r07_c15/repairs/unified/refined/candidate.png';D=T/'repairs/west-refined-provisional-qa'
ws=a.sha(W);es=a.sha(E);west=Image.open(W).convert('RGB');east=Image.open(E).convert('RGB');assert west.size==east.size==(4096,4096)
band=Image.new('RGB',(256,4096));band.paste(west.crop((3968,0,4096,4096)),(0,0));band.paste(east.crop((0,0,128,4096)),(128,0));sheet=Image.new('RGB',(1024,1024))
for i in range(4):sheet.paste(band.crop((0,i*1024,256,(i+1)*1024)),(i*256,0))
out=a.save_image(D/'west-common-edge-native-full.png',sheet);assert a.sha(W)==ws and a.sha(E)==es
corn=Image.new('RGB',(1024,1024));corn.paste(west.crop((3584,3584,4096,4096)),(0,0));corn.paste(east.crop((0,3584,512,4096)),(512,0));corn.paste(Image.open(R/'r08_c15/output/r08_c15.png').crop((3584,0,4096,512)),(0,512));corn.paste(Image.open(R/'r08_c16/output/r08_c16.png').crop((0,0,512,512)),(512,512));ci=a.save_image(D/'four-way-native-provisional.png',corn)
a.save_json(D/'manifest.json',dict(createdAtUtc=a.utc_now(),west=dict(file=str(W),sha256=ws,status='PROVISIONAL NOT BOUND'),east=dict(file=str(E),sha256=es),commonEdge=out,fourWay=ci,resampling=False,formalAccepted=False,purpose='Read-only provisional geometry localization; regenerate from final west before binding'))
print(ws)
