from workflow import *
from PIL import Image
q=ROOT/'qa/r08_c13-root-full-20261016-v02';m=read(q/'seams.json');passed={}
for bn in ['batch01','batch02','batch03','batch04-fixed']:
 mf=ROOT/'qa'/f'r08_c13-quick-{bn}/manifest.json'
 for e in read(mf)['entries']:
  if 'pass' in e['status'] and 'not' not in e['status'].lower():
   assert sha(Path(e['file']))==e['sha256']
   if all(sha(Path(x['file']))==x['sha256'] for x in e['inputs']):passed[e['sha256']]=str(mf)
for e in m['entries']:
 if e['sha256'] in passed:e.update(status='passed_hash_reuse_actual_core_strip',evidence=passed[e['sha256']])
write(q/'seams.json',m);print('r08c13 still to view', [e['id'] for e in m['entries'] if e['status']=='pending_visual_review'])
q=ROOT/'qa/r08_c12-v16-foliage-20261016';im=Image.open(ROOT/'tiles/r08_c12.candidate-v16-foliage-20261016.png').convert('RGB');old=Image.open(ROOT/'tiles/r08_c12.candidate-v15.png').convert('RGB')
changed=[];m=read(q/'seams.json')
for e in m['entries']:
 if old.crop(e['sourceCrop']).tobytes()==im.crop(e['sourceCrop']).tobytes():e.update(status='passed_unchanged_previous_v15_pixels',evidence='Previous accepted v15 internal strip unchanged by this local repair')
 else:changed.append(e['id'])
write(q/'seams.json',m);print('r08c12 changed',changed)
a=im.crop((3840,3072,4096,4096));b=Image.open(ROOT/'native/r08_c13_p41_v01.png').convert('RGB').crop((115,115,371,1139));cut=Image.new('RGB',(512,1024));cut.paste(a,(0,0));cut.paste(b,(256,0));cut.save(q/'east4-actual.png')
a=im.crop((3072,3840,4096,4096));b=Image.open(ROOT/'tiles/r09_c12.candidate-v09.png').convert('RGB').crop((3072,0,4096,256));cut=Image.new('RGB',(1024,512));cut.paste(a,(0,0));cut.paste(b,(0,256));cut.save(q/'south4-actual.png')
print('r08c12 new overlay sourceId30; source edges top,left and external E4/S4 require view')
