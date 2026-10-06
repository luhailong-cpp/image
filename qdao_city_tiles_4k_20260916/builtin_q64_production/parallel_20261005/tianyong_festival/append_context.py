"""Add an exact native context crop and a crop-specific prompt to a prepared request."""
from pathlib import Path
import json,hashlib,argparse
from PIL import Image
import numpy as np
T=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('--source',type=Path,required=True);p.add_argument('--crop',nargs=4,type=int,required=True);p.add_argument('--paste',nargs=2,type=int,required=True);p.add_argument('--prompt-file',type=Path,required=True);a=p.parse_args();d=a.directory.resolve();d.relative_to(T)
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
 write=lambda p,o:p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 im=Image.open(d/'context.png').convert('RGBA');im.paste(Image.open(a.source).convert('RGBA').crop(a.crop),a.paste);im.save(d/'context.png')
 prep=read(d/'preparation.json');prep['nativeInputs'].append({'file':str(a.source),'sha256':sha(a.source),'role':'Additional exact same-world native context including original halo'});prep['references'][0]['sha256']=sha(d/'context.png');write(d/'preparation.json',prep)
 r=read(d/'request.json');known=int((np.asarray(im)[:,:,3]==255).sum());r['knownPixels']=known;r['missingPixels']=im.width*im.height-known;r['payload']['prompt']+='\n'+a.prompt_file.read_text(encoding='utf-8-sig');write(d/'request.json',r);(d/'prompt.txt').write_text(r['payload']['prompt'],encoding='utf-8')
 rec=read(d/'context.png.generation.json');rec['sha256']=sha(d/'context.png');rec['derivedFrom'].append({'file':str(a.source),'sha256':sha(a.source)});write(d/'context.png.generation.json',rec)
 print(json.dumps(r))
if __name__=='__main__':main()

