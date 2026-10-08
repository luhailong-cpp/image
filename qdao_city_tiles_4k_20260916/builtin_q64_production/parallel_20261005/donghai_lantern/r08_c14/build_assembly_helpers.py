"""Create c14-only helper scripts from the existing audited c13 implementation."""
from pathlib import Path
T=Path(__file__).resolve().parent
old=T.parent/'r08_c13'
def transform(s):
 for a,b in [('r08_c13','r08_NEW'),('c13','cNEW'),('r08_c12','r08_c13'),('c12','c13'),('r08_NEW','r08_c14'),('cNEW','c14'),('49037','53133'),('49152','53248')]:s=s.replace(a,b)
 return s
for name in ('assemble_c13_native.py','assemble_c13_shared.py','match_c13_shared_tone.py'):
 target=T/name.replace('c13','c14')
 if not target.exists():target.write_text(transform((old/name).read_text(encoding='utf-8')),encoding='utf-8')
shared=T/'assemble_c14_shared.py'
s=transform((old/'assemble_c13_shared.py').read_text(encoding='utf-8'))
start=s.index('def validate_inputs():');end=s.index('def load_day_masks(',start)
s=s[:start]+'''def validate_inputs():
    import c14_contract
    arrays, day_arrays, entries, manifest, manifest_hash, missing = c14_contract.validate_inputs(sys.modules[__name__])
    return arrays, day_arrays, entries, manifest, manifest_hash


def verify_day_replay(day_arrays, manifest, masks):
    import c14_contract
    return c14_contract.verify_day_replay(sys.modules[__name__], day_arrays, manifest, masks)


'''+s[end:]
start=s.index('def main():');end=s.index('\n\nif __name__ ==',start)
s=s[:start]+'''def main():
    import c14_contract
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight', action='store_true', help='Default: write only c14 JSON preflight evidence, allow missing native files')
    parser.add_argument('--validate-only', action='store_true', help='Alias for preflight; never produces image pixels')
    parser.add_argument('--assemble-base', action='store_true', help='Explicitly export all-16 shared-mask base; current DAY post-repair conversion remains a separate required step')
    args = parser.parse_args()
    if not args.assemble_base:
        print(json.dumps(c14_contract.preflight(sys.modules[__name__]), ensure_ascii=False, indent=2))
        return 0
    arrays, day_arrays, entries, day_manifest, manifest_hash = validate_inputs()
    masks, mask_evidence = load_day_masks(day_manifest)
    proof = verify_day_replay(day_arrays, day_manifest, masks)
    del day_arrays
    combined, operations = assemble(arrays, masks)
    manifest = write_outputs(combined, entries, mask_evidence, manifest_hash, operations, True)
    print(json.dumps({'candidate':manifest['candidate'], 'dayReplay':proof, 'formalAccepted':False},indent=2))
    return 0
'''+s[end:]
s=s.replace('"sourceOwnershipIdenticalToDay": True, "dayReplayPixelIdentical": replay_verified,','"sourceOwnershipIdenticalToDayNativeBase": True, "currentDayPostRepairsAppliedToFestival": False, "dayReplayPixelIdentical": replay_verified,\n                  "requiredPostAssemblyRepairs": read(DAY_MANIFEST).get("postAssemblyRepairChain", []),\n                  "dayReplayIncludesPostRepairs": True, "festivalCandidateIsNativeBaseOnly": True,')
shared.write_text(s,encoding='utf-8')
tone=T/'match_c14_shared_tone.py';s=transform((old/'match_c13_shared_tone.py').read_text(encoding='utf-8'))
start=s.index('    day_replay, _ = shared.assemble(day, masks)');end=s.index('    original, _ = shared.assemble(arrays, masks)',start)
s=s[:start]+"    day_replay_proof = shared.verify_day_replay(day, day_manifest, masks)\n    del day\n"+s[end:]
s=s.replace("'outsideLocalSeamSupportPixelIdentical':True, 'dayReplayPixelIdentical':True,","'outsideLocalSeamSupportPixelIdentical':True, 'dayReplayPixelIdentical':True,\n              'dayReplayIncludesPostRepairs':True,'dayReplayProof':day_replay_proof,\n              'currentDayPostRepairsAppliedToFestival':False,'festivalCandidateIsNativeBaseOnly':True,\n              'requiredPostAssemblyRepairs':day_manifest.get('postAssemblyRepairChain',[]),")
s=s.replace("if __name__=='__main__': main()", "if __name__=='__main__':\n    if '--assemble-base' not in sys.argv: raise SystemExit('Explicit --assemble-base required; this exports only native-base tone candidate, not the separate DAY repair conversions.')\n    main()")
tone.write_text(s,encoding='utf-8')
print('Created c14 helper templates without executing pixel assembly.')
