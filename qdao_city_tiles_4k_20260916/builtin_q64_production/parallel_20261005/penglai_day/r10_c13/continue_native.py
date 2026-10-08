import sys, json
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import helper as h
R=h.ROOT

def ingest(source,name,callname,note):
    dest=R/'native'/(name+'.png')
    assert not dest.exists()
    call=h.p.read(R/'prompts'/(callname+'.call.json'))
    dest=h.p.ingest(source,name,R/'prompts'/(callname+'.prompt.txt'),call['referenced_image_paths'],'native_detail')
    assert Image.open(dest).size==(1254,1254)
    rec=h.p.read(str(dest)+'.generation.json')
    rec['configSnapshot']=h.p.read(R/'evidence/model-verification.json')['configSnapshot']
    rec['evidence']['toolOutputHintFile']=str(R/'evidence'/(callname+'.tool-result.json'))
    rec['visualInspection']={'at':h.p.stamp(),'status':'native_patch_usable_pending_seam_qa','note':note}
    h.p.write(str(dest)+'.generation.json',rec)
    h.update()
    print(str(dest),h.p.sha(dest))

if __name__=='__main__':
    if sys.argv[1]=='ingest':ingest(*sys.argv[2:])
