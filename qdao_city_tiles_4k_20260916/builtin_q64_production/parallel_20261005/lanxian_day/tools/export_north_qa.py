"""Export full-length native-scale northern neighbor joins, without approval."""
from pathlib import Path
import argparse,json
from PIL import Image
from workflow import candidate_core,load_image,sha256,save_image,safe_output,write_json,now

def run(tile_path,north_file):
    tile,core,own=candidate_core(tile_path)
    path=Path(north_file).resolve(strict=True)
    north=load_image(path,(4096,4096))
    if north.mode!=core.mode:raise ValueError('Neighbor color modes differ')
    source={'file':str(path),'sha256':sha256(path),'role':'north adjacent core4096'}
    checks=[]
    for col in range(4):
        x=col*1024
        board=Image.new(core.mode,(1024,512))
        board.paste(north.crop((x,3840,x+1024,4096)),(0,0))
        board.paste(core.crop((x,0,x+1024,256)),(0,256))
        item=save_image(safe_output(tile/f'qa/external_north_part{col+1}.png'),board)
        item.update(derivedFrom=[source,own],pixelMappings=[
            {'source':str(path),'sourceBox':[x,3840,x+1024,4096],'destinationXY':[0,0]},
            {'source':own['file'],'sourceBox':[x,0,x+1024,256],'destinationXY':[0,256]}],
            resampling='none',operation='integer crop and paste',reviewStatus='pending',
            visualInspectionPerformed=False)
        checks.append(item)
    report={'schemaVersion':1,'createdAt':now(),'edge':'north','source':own,'neighbor':source,
        'fullLength':4096,'stripHeight':512,'seamYInCrop':256,'formalAccepted':False,
        'visualInspectionPerformed':False,'noResampling':True,'status':'awaiting_visual_inspection',
        'checks':checks}
    write_json(safe_output(tile/'qa/external-north.manifest.json'),report)
    print(json.dumps({'northNativeChecks':4,'neighbor':source}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('tile');p.add_argument('north')
    a=p.parse_args();run(a.tile,a.north)
