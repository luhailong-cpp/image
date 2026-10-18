"""Native-only shared repair windows; image creation stays in the built-in tool.

Reference crops may magnify approved layout. Delivered pixels never use layout.
"""
from pathlib import Path
from PIL import Image, ImageChops
import batch_production as b


def intersection(a, c):
    box = [max(a[0], c[0]), max(a[1], c[1]), min(a[2], c[2]), min(a[3], c[3])]
    return box if box[0] < box[2] and box[1] < box[3] else None


def prepare(tag, world, mutable, prompt):
    assert world[2]-world[0] == world[3]-world[1] == 1254
    folder = b.OUT/'joint-repairs'/tag
    folder.mkdir(parents=True, exist_ok=False)
    s = b.state(); canvas = Image.new('RGB', (1254,1254)); covered = 0; input_pastes=[]
    for key, rec in s['selected'].items():
        core = rec['geometry']['coreGlobalBox']; box=intersection(core, world)
        if not box: continue
        native=rec['geometry']['nativeGlobalBox']
        crop=[box[0]-native[0],box[1]-native[1],box[2]-native[0],box[3]-native[1]]
        at=[box[0]-world[0],box[1]-world[1]]
        assert b.sha(rec['path'])==rec['sha256']
        with Image.open(rec['path']) as im: canvas.paste(im.convert('RGB').crop(crop),at)
        covered+=(box[2]-box[0])*(box[3]-box[1])
        input_pastes.append({'key':key,'source':rec,'sourceCrop':crop,'pasteAt':at})
    assert covered==1254*1254, 'Input window must be fully covered by existing selected native cores'
    canvas.save(folder/'native-target.png')
    contract=b.read(b.MAP/'production-contract.json')
    with Image.open(contract['layoutReference']) as im:
        guide=im.convert('RGB').transform((1254,1254),Image.Transform.EXTENT,
            tuple(v*1254/57344 for v in world),resample=Image.Resampling.BICUBIC)
    guide.save(folder/'layout-only.png')
    refs=[b.info(folder/'native-target.png','current sharp native joint edit target'),
          b.info(folder/'layout-only.png','same-coordinate approved layout ONLY, never final pixels'),
          b.info(b.ROOT/'designs/mail-ui-v1/01-mail-event.png','primary Daoist Q style only')]
    affected={k:r for k,r in s['selected'].items() if intersection(r['geometry']['nativeGlobalBox'],mutable)}
    q={'key':tag,'worldBox':world,'mutableWorldBox':mutable,'inputPastes':input_pastes,
       'originalSelections':affected,'prompt':prompt,'referenceRolesAndHashes':refs,
       'referenced_image_paths':[r['path'] for r in refs],'ownerGate':b.gate(required=True),
       'rootInstructionsReadBeforeCall':b.info(b.ROOT/'AGENTS.md'),
       'actualModel':None,'actualQuality':None,'paidApiUsed':False,'status':'prepared_not_submitted'}
    b.save(folder/'request.json',q)
    print(str(folder/'request.json'))


def apply(tag):
    folder=b.OUT/'joint-repairs'/tag; q=b.read(folder/'request.json')
    raw=folder/'raw-tool-output.png'; world=q['worldBox']; changed=q['mutableWorldBox']
    with Image.open(raw) as im:
        assert im.size==(1254,1254); joint=im.convert('RGB').copy()
    with b.batch_writer_lock():
        s=b.state(); outputs=[]
        for key,old in q['originalSelections'].items():
            assert s['selected'][key]['sha256']==old['sha256'], 'Selected input changed during native edit'
            n=old['geometry']['nativeGlobalBox']; box=intersection(n,changed)
            crop=[box[0]-world[0],box[1]-world[1],box[2]-world[0],box[3]-world[1]]
            at=[box[0]-n[0],box[1]-n[1]]
            with Image.open(old['path']) as im: out=im.convert('RGB').copy()
            out.paste(joint.crop(crop),at)
            dst=b.OUT/old['geometry']['tile']/'native'/f"{old['geometry']['patch']}-{tag}-derived.png"
            assert not dst.exists(); out.save(dst); dp=dst.with_suffix('.png.derived.json')
            b.save(dp,{'operation':'shared native1254 repair cropped/pasted at integer world coordinates',
                'priorSource':old,'rawToolOutput':b.info(raw),'request':str(folder/'request.json'),
                'jointWorldBox':world,'mutableWorldBox':changed,'sourceCrop':crop,'pasteAt':at,
                'preservedOutsidePaste':True,'resampled':False,'layoutPixelsUsed':False,
                'formalAccepted':False,'selectedNative':b.info(dst)})
            rec=dict(old);rec.update(b.info(dst));rec.update(sourceType='mechanical_derived',
                derivationRecord=str(dp),reviewStatus='native_local_repair_pending_delta_QA')
            s['selected'][key]=rec; outputs.append({'key':key,'selected':rec})
        b.checkpoint(s,'applied native joint repair '+tag)
        b.save(folder/'applied.json',{'outputs':outputs,'formalAccepted':False})
        print([o['key'] for o in outputs])
