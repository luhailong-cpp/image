from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,sys
B=Path(__file__).resolve().parents[1];tile,apath,tag=sys.argv[1:];ap=Path(apath);assert ap.is_relative_to(B/tile)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
a=read(ap);assert a['tile']==tile and a['verifiedNativeCount']==16
for key,size in [('output',(4096,4096)),('contextOutput',(4326,4326))]:
 assert sha(a[key]['file'])==a[key]['sha256']
 with Image.open(a[key]['file']) as z:assert z.size==size
im=Image.open(a['output']['file']).convert('RGB');q=ap.parent/tag;assert not q.exists();q.mkdir()
regions=[];panels=[]
def save(name,panel):p=q/(name+'.png');panel.save(p);panels.append({'name':name,'file':str(p),'sha256':sha(p),'nativeResampling':False})
for row in range(4):
 panel=Image.new('RGB',(840,1048),'white');dr=ImageDraw.Draw(panel)
 for k,x in enumerate([1024,2048,3072]):
  box=[x-128,row*1024,x+128,(row+1)*1024];panel.paste(im.crop(box),(k*280,24));dr.text((k*280+3,3),f'V{k+1} row{row+1}',fill='black');regions.append({'name':f'V{k+1}-row{row+1}','box':box,'panel':f'V-row{row+1}'})
 save(f'V-row{row+1}',panel)
for k,y in enumerate([1024,2048,3072]):
 panel=Image.new('RGB',(1024,1120),'white');dr=ImageDraw.Draw(panel)
 for col in range(4):
  box=[col*1024,y-128,(col+1)*1024,y+128];panel.paste(im.crop(box),(0,col*280+24));dr.text((3,col*280+3),f'H{k+1} col{col+1}',fill='black');regions.append({'name':f'H{k+1}-col{col+1}','box':box,'panel':f'H{k+1}'})
 save(f'H{k+1}',panel)
panel=Image.new('RGB',(840,840),'white');dr=ImageDraw.Draw(panel)
for r,y in enumerate([1024,2048,3072]):
 for c,x in enumerate([1024,2048,3072]):
  box=[x-128,y-128,x+128,y+128];panel.paste(im.crop(box),(c*280,r*280+24));dr.text((c*280+3,r*280+3),f'corner H{r+1} V{c+1}',fill='black');regions.append({'name':f'corner-H{r+1}-V{c+1}','box':box,'panel':'nine-corners'})
save('nine-corners',panel)
cat=read(B/'current-candidates.json')['tiles'];rr,cc=int(tile[1:3]),int(tile[5:7]);neighbors={}
for side,nt in [('left',f'r{rr:02d}_c{cc-1:02d}'),('top',f'r{rr-1:02d}_c{cc:02d}')]:
 if nt not in cat:neighbors[side]={'tile':nt,'available':False};continue
 e=cat[nt]['candidate'];assert sha(e['file'])==e['sha256'];other=Image.open(e['file']).convert('RGB');assert other.size==(4096,4096);neighbors[side]={'tile':nt,'available':True,'candidate':e,'formalAccepted':False}
 if side=='left':
  panel=Image.new('RGB',(1120,1048),'white');dr=ImageDraw.Draw(panel)
  for r in range(4):
   part=Image.new('RGB',(256,1024));part.paste(other.crop((3968,r*1024,4096,(r+1)*1024)),(0,0));part.paste(im.crop((0,r*1024,128,(r+1)*1024)),(128,0));panel.paste(part,(r*280,24));dr.text((r*280+3,3),f'LEFT row{r+1}',fill='black')
 else:
  panel=Image.new('RGB',(1024,1120),'white');dr=ImageDraw.Draw(panel)
  for c in range(4):
   part=Image.new('RGB',(1024,256));part.paste(other.crop((c*1024,3968,(c+1)*1024,4096)),(0,0));part.paste(im.crop((c*1024,0,(c+1)*1024,128)),(0,128));panel.paste(part,(0,c*280+24));dr.text((3,c*280+3),f'TOP col{c+1}',fill='black')
 save(side+'-native-boundary',panel)
overview=q/'overview-QA-only-1600.png';im.resize((1600,1600),Image.Resampling.LANCZOS).save(overview)
manifest={'tile':tile,'assembly':str(ap),'assemblySha256':sha(ap),'candidate':a['output'],'context':a['contextOutput'],'internalNativeRegions':regions,'internalNativeRegionCount':len(regions),'panels':panels,'neighbors':neighbors,'externalNativeRegionCount':sum(4 for n in neighbors.values() if n['available']),'overview':{'file':str(overview),'sha256':sha(overview),'qaOnly':True,'resized':True,'finalArtwork':False},'nativePanelsResampled':False,'formalAccepted':False,'visualReview':'pending actual viewing'}
(q/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'qa':str(q),'nativePanels':[p['file'] for p in panels],'internalNativeRegions':len(regions),'externalNativeRegions':manifest['externalNativeRegionCount'],'overview':str(overview),'coreSha256':a['output']['sha256']}))

