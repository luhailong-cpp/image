"""In-memory regressions for review-only helper source; production file untouched."""
from pathlib import Path
from unittest import TestCase,mock,defaultTestLoader,TextTestRunner,TestSuite
import copy,importlib.util,json,sys,types
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3];helper=ROOT/'tools/finalize_scoped.py'
installed='--installed' in sys.argv
source=helper if installed else OUT/'finalize_scoped.proposed.py'
f=types.ModuleType('finalize_scoped');f.__file__=str(helper);sys.modules['finalize_scoped']=f
exec(compile(source.read_text(encoding='utf-8'),str(helper),'exec'),f.__dict__)
spec=importlib.util.spec_from_file_location('existing_gate_regressions',ROOT/'tools/test_finalize_scoped.py')
existing=importlib.util.module_from_spec(spec);spec.loader.exec_module(existing)

class MetadataTests(TestCase):
    def setUp(self):
        self.folder=ROOT/'_metadata_in_memory_only';self.old=self.folder/'native/retired.png';self.new=self.folder/'native/new-repair.png'
        self.ledger=self.folder/'retention-log.json';self.plan=self.folder/'plan.json';self.ai=self.folder/'repair.png.generation.json'
        self.ctx=dict(folder=self.folder,references={'current':{'file':'candidate.png','sha256':'c'*64},'north':{'file':'north-current.png','sha256':'n'*64}},assembly={'plan':{'file':str(self.plan),'sha256':'a'*64},'neighbors':{'north':{'file':'north-current.png','sha256':'o'*64}},'patches':[{'source':{'file':str(self.old),'sha256':'d'*64}},{'source':{'file':str(self.new),'sha256':'e'*64}}]})
        self.prior={'retentionLog':str(self.ledger),'retentionRecord':{'file':str(self.ledger),'sha256':'l'*64},'sourcePolicy':'Retain all TEXT.','currentAppliedRepair':{'sourceAIRecord':{'file':str(self.ai),'sha256':'i'*64}}}
        self.doc={'removed':[{'file':str(self.old),'sha256':'d'*64,'retiredAfterExport':True,'sourceImageAvailable':False},{'file':str(self.new),'sha256':'e'*64,'retiredAfterExport':False,'sourceImageAvailable':True}]}
        self.hashes={f.key(self.plan):'p'*64,f.key(self.ledger):'l'*64,f.key(self.ai):'i'*64}
        self.available={f.key(self.new)}
    def run_case(self):
        with mock.patch.object(f,'sha',lambda p:self.hashes[f.key(p)]),mock.patch.object(f,'read',lambda p:copy.deepcopy(self.doc)),mock.patch.object(Path,'exists',lambda p:f.key(p) in self.available),mock.patch.object(f,'write',side_effect=AssertionError('Metadata validation wrote')):
            return f.source_metadata(self.ctx,self.prior)
    def test_current_plan_and_neighbors_separate_from_acquisition(self):
        before=copy.deepcopy(self.ctx);d=self.run_case()
        self.assertEqual(d['plan']['sha256'],'p'*64);self.assertEqual(d['assemblyPlan']['sha256'],'a'*64)
        self.assertEqual(d['neighbors']['north']['sha256'],'n'*64);self.assertEqual(d['assemblyNeighbors']['north']['sha256'],'o'*64)
        self.assertTrue(d['assemblyPlan']['historicalAcquisitionReference']);self.assertEqual(before,self.ctx)
    def test_actual_retirement_restored_but_new_repair_not_retired(self):
        d=self.run_case();self.assertTrue(d['patches'][0]['source']['retiredAfterExport']);self.assertFalse(d['patches'][0]['source']['sourceImageAvailable'])
        self.assertNotIn('retiredAfterExport',d['patches'][1]['source']);self.assertEqual(d['currentAppliedRepair'],self.prior['currentAppliedRepair'])
    def test_reference_hash_must_match_retired_bytes(self):
        self.ctx['assembly']['patches'][0]['source']['sha256']='x'*64
        self.assertNotIn('retiredAfterExport',self.run_case()['patches'][0]['source'])
    def test_no_ledger_does_not_invent_retirement(self):
        del self.prior['retentionLog'];d=self.run_case();self.assertNotIn('sourceRecordsHistoricalAfterRetention',d);self.assertNotIn('retiredAfterExport',d['patches'][0]['source'])
    def test_existing_retired_image_fails(self):
        self.available.add(f.key(self.old))
        with self.assertRaisesRegex(ValueError,'unexpectedly available'):self.run_case()
    def test_stale_ledger_hash_fails(self):
        self.prior['retentionRecord']['sha256']='x'*64
        with self.assertRaisesRegex(ValueError,'Stale retention'):self.run_case()
    def test_outside_retired_path_fails(self):
        self.doc['removed'][0]['file']=str(ROOT/'outside.png')
        with self.assertRaisesRegex(ValueError,'outside tile'):self.run_case()
    def test_contradictory_completed_entry_fails(self):
        self.doc['removed'][0]['sourceImageAvailable']=True
        with self.assertRaisesRegex(ValueError,'Contradictory'):self.run_case()
    def test_stale_current_repair_source_fails(self):
        self.prior['currentAppliedRepair']['sourceAIRecord']['sha256']='x'*64
        with self.assertRaisesRegex(ValueError,'Stale retained current source'):self.run_case()

if __name__=='__main__':
    suite=TestSuite([defaultTestLoader.loadTestsFromModule(existing),defaultTestLoader.loadTestsFromTestCase(MetadataTests)])
    result=TextTestRunner(verbosity=1).run(suite)
    print(json.dumps(dict(installedProductionHelperTested=installed,testedSource=str(source),testsRun=result.testsRun,failures=len(result.failures),errors=len(result.errors))))
    sys.exit(not result.wasSuccessful())
