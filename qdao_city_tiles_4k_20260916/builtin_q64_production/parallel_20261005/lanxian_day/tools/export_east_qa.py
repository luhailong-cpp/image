"""Export native-scale eastern neighbor joins; all checks await actual review.

CLI: export_east_qa.py TILE_DIR EAST_CORE4096.png
Each512x1024 board has the target right256 on the left and east neighbor left256
on the right. Only integer crop/paste is used; no resampling or acceptance.
"""
from pathlib import Path
import argparse,json
from PIL import Image
from workflow import candidate_core,load_image,sha256,save_image,safe_output,write_json,now


def run(tile_path,east_file):
    tile,core,own=candidate_core(tile_path)
    path=Path(east_file).resolve(strict=True)
    east=load_image(path,(4096,4096))
    if east.mode!=core.mode:raise ValueError('Neighbor color modes differ')
    if path==Path(own['file']).resolve():raise ValueError('East neighbor cannot be the target itself')
    source={'file':str(path),'sha256':sha256(path),'role':'east adjacent core4096'}

    def destination(relative):
        p=safe_output(tile/relative)
        if not p.is_relative_to(tile):raise ValueError('Output escapes requested tile')
        return p

    outputs=[destination(f'qa/external_east_part{row+1}.png') for row in range(4)]
    report_path=destination('qa/external-east.manifest.json')
    if any(p.exists() for p in outputs+[report_path]):
        raise FileExistsError('Refusing to overwrite existing eastern QA exports')
    checks=[]
    for row in range(4):
        y=row*1024
        board=Image.new(core.mode,(512,1024))
        board.paste(core.crop((3840,y,4096,y+1024)),(0,0))
        board.paste(east.crop((0,y,256,y+1024)),(256,0))
        item=save_image(destination(f'qa/external_east_part{row+1}.png'),board)
        item.update(derivedFrom=[own,source],pixelMappings=[
            {'source':own['file'],'sourceBox':[3840,y,4096,y+1024],'destinationXY':[0,0]},
            {'source':str(path),'sourceBox':[0,y,256,y+1024],'destinationXY':[256,0]}],
            resampling='none',operation='integer crop and paste',reviewStatus='pending',
            visualInspectionPerformed=False)
        checks.append(item)
    report={'schemaVersion':1,'createdAt':now(),'edge':'east','source':own,'neighbor':source,
        'fullLength':4096,'stripWidth':512,'seamXInCrop':256,
        'leftOfSeam':'target right256','rightOfSeam':'east neighbor left256',
        'formalAccepted':False,'visualInspectionPerformed':False,'noResampling':True,
        'status':'awaiting_visual_inspection','checks':checks}
    write_json(destination('qa/external-east.manifest.json'),report)
    print(json.dumps({'eastNativeChecks':4,'manifest':str(report_path),'neighbor':source}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('tile');p.add_argument('east')
    a=p.parse_args();run(a.tile,a.east)
