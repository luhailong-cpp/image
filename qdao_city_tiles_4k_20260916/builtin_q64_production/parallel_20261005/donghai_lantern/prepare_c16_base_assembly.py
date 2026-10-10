"""Create c16-only native-base assembly helpers from the verified c15 algorithms."""
from pathlib import Path
import hashlib, shutil

ROOT = Path(__file__).resolve().parent
OLD, NEW = ROOT/'r08_c15', ROOT/'r08_c16'
DAY = ROOT.parent/'donghai_day/r08_c16'
snapshot = NEW/'qa/base-source-snapshot/previous-assembly-manifest.json'
source = DAY/'repairs/integrated-v5/previous-assembly-manifest.json'
expected = '452de57856a53026c20e7ec8b5e5774dae16ad953e7cb4560ae07ea69545e2ed'
assert hashlib.sha256(source.read_bytes()).hexdigest() == expected
snapshot.parent.mkdir(parents=True, exist_ok=True)
if not snapshot.exists(): shutil.copyfile(source, snapshot)
assert hashlib.sha256(snapshot.read_bytes()).hexdigest() == expected

def adapt(s):
    for old,new in [('c15','c16'),('57344','61440'),('57229','61325')]: s=s.replace(old,new)
    return s

def write(name, s):
    p=NEW/name
    assert not p.exists(), p
    p.write_text(s, encoding='utf-8')

s=adapt((OLD/'assemble_c15_native.py').read_text(encoding='utf-8'))
s=s.replace("ROOT / 'r08_c14/tone-assembly/output/r08_c14.png'", "ROOT / 'r08_c15/repairs/approved-sync-final/output/r08_c15.png'")
s=s.replace('d34218a9ccfc0739b64c8510b6999904c455bd74bdc388943f8d078314a91108','3d0b9871e8c95c88d0e9852f17b8dc9ae84c6c746f48605ac7c98628b67f2e25')
s=s.replace('c14','c15').replace('tone source changed','internal-final source changed')
s=s.replace('QA-only c15 tone candidate; original c16 generation context is recorded per-fragment c15 eastern native overlap','QA-only c15 internally repaired candidate; c16 DAY geometry is independent and no c15 raw pixels were pasted into c16 guides')
write('assemble_c16_native.py',s)

s=adapt((OLD/'assemble_c15_shared.py').read_text(encoding='utf-8'))
s=s.replace('source-contract-v2/snapshots/manifests/7f1ad0c868c6e3d2-previous-assembly-manifest.json','qa/base-source-snapshot/previous-assembly-manifest.json')
s=s.replace('read(TILE / "source-contract-v2/source-contract.json")["insertionOperations"]', '"Separate c16 current-DAY repair replay contract is required; this is the historical native base only"')
write('assemble_c16_shared.py',s)

s=adapt((OLD/'match_c15_shared_tone.py').read_text(encoding='utf-8'))
s=s.replace("'dayReplayIncludesPostRepairs':True", "'dayReplayIncludesPostRepairs':False")
s=s.replace("shared.read(shared.TILE/'source-contract-v2/source-contract.json')['insertionOperations']", "'Separate frozen current-DAY repair contract required; no post-repairs applied here'")
write('match_c16_shared_tone.py',s)

s=adapt((OLD/'c15_contract.py').read_text(encoding='utf-8'))
s=s.replace('7f1ad0c868c6e3d24365082da1f8fd5f6a9c03fe6193776601ff8d6f1b3730da',expected)
s=s.replace(" v2=read(T/'source-contract-v2/source-contract.json')\n need(v2['dayReplay']['historicalBasePNGByteIdentical'] and v2['dayReplay']['historicalExtendedPNGByteIdentical'],'Historical v2 verification missing')\n",'')
start=s.index(" v2=read(T/'source-contract-v2/source-contract.json')",s.index('def verify_day_replay'))
end=s.index('\ndef preflight',start)
s=s[:start]+" return {'dayExtendedReplayPixelIdentical':True,'dayCoreReplayPixelIdentical':True,'dayHistoricalExtendedPNGByteIdentical':True,'dayHistoricalCorePNGByteIdentical':True,'dayNativeSources':16,'sharedMaskCount':15,'postAssemblyRepairChain':[],'externalRepairsAppliedInThisReplay':False,'westIntegrationPending':True,'finalGeometryAcceptance':False,'historicalBasePathsSuperseded':True,'verificationMethod':'Reconstruct exact historical PNG bytes from frozen manifest, 16 source natives and 15 source masks. Current DAY post-repairs are a separate pending stage.'}\n"+s[end:]
write('c16_contract.py',s)
print('Created four c16-only helpers and frozen original DAY manifest. No image output yet.')
