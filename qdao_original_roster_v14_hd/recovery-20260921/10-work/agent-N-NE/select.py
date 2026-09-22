from pathlib import Path
import argparse,json

HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('slots',nargs='+')
parser.add_argument('--review',default='provisional: identity, direction and intended limb phase observed; edges and complete30ms cycle pending main review')
args=parser.parse_args();dest=HERE/'selection.json'
selection=json.loads(dest.read_text(encoding='utf-8')) if dest.exists() else {}
for assignment in args.slots:
    slot,archive=assignment.split('=',1)
    assert slot.startswith('N') and not slot.startswith('NW')
    raw=HERE.parents[1]/'10-generation'/archive/'raw.png'
    assert raw.is_file(),raw
    selection[slot]={'archive':archive,'review':args.review}
dest.write_text(json.dumps(selection,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'selectedSlots':len(selection),'path':str(dest)}))
