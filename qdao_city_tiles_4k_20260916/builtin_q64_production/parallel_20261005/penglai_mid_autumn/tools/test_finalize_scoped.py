"""Acceptance-gate tests. Synthetic pixels stay in memory; no tile files written."""
from pathlib import Path
from unittest import TestCase, mock, defaultTestLoader, TextTestRunner
from datetime import datetime, timezone
import copy
import hashlib
import json
import io
import sys
from PIL import Image
import finalize_scoped as f


class MemoryReview:
    def __init__(self):
        self.folder=f.ROOT/'_test_memory_only'
        self.candidate=self.folder/'output/r09_c14-candidate.png'
        self.finalsha='a'*64
        self.ctx=dict(folder=self.folder,candidate=self.candidate,finalsha=self.finalsha)
        self.required={};self.images={};self.reports={};self.hashes={}
        for index,(name,flag) in enumerate([('horizontal-review.json','scopedPass'),('external-review.json','externalScopedPass'),('root-review.json','scopedPass')]):
            path=self.folder/'qa/native-candidate'/f'piece-{index}.png'
            pixels=Image.new('RGB',(5,7),(index*40+10,60,90))
            digest=hashlib.sha256(pixels.tobytes()).hexdigest()
            self.images[f.key(path)]=pixels;self.hashes[f.key(path)]=digest
            self.required[f.key(path)]=dict(path=path,image=pixels.copy(),operation={},roles=['current'])
            report_path=self.folder/'qa'/name
            self.reports[f.key(report_path)]={flag:True,'candidate':dict(file=str(self.candidate),sha256=self.finalsha),'items':[dict(file=str(path),sha256=digest,actuallyViewed=True,nativeScale=1,verdict='pass',review='Synthetic fixture only; never a production visual verdict.')],'issueCount':0,'issues':[]}
            self.hashes[f.key(report_path)]=hashlib.sha256(name.encode()).hexdigest()
        self.report_keys=list(self.reports)

    def read(self,path):
        if f.key(path) not in self.reports:raise FileNotFoundError(path)
        return copy.deepcopy(self.reports[f.key(path)])

    def validate(self):
        with mock.patch.object(f,'read',self.read),mock.patch.object(f,'sha',lambda p:self.hashes[f.key(p)]),mock.patch.object(f,'open_image',lambda p:self.images[f.key(p)].copy()),mock.patch.object(f,'write',side_effect=AssertionError('Validation wrote a file')):
            return f.validate_reports(self.ctx,self.required)

    def report(self,index=0):return self.reports[self.report_keys[index]]
    def item(self,index=0):return self.report(index)['items'][0]


class GateTests(TestCase):
    def setUp(self):self.fx=MemoryReview()
    def reject(self,phrase):
        with self.assertRaisesRegex(ValueError,phrase):self.fx.validate()

    def test_valid_reports_read_only(self):
        covered,reports=self.fx.validate()
        self.assertEqual(len(covered),3);self.assertEqual(len(reports),3)
        self.assertTrue(all(i['actuallyViewed'] and i['verifiedAgainstCurrentCandidatePixels'] for i in covered.values()))
        self.assertNotIn('sourceReview',self.fx.item())

    def test_missing_report(self):
        del self.fx.reports[self.fx.report_keys[1]];self.reject('Missing review')

    def test_legacy_mainqa_accepted(self):
        report=self.fx.report(1);report['mainQA']=report.pop('items');self.fx.validate()

    def test_supplemental_reviews_are_not_silently_ignored(self):
        report=self.fx.report(1);extra=copy.deepcopy(report['items'][0]);extra['file']=str(self.fx.folder/'qa/external-details/west-unrotated-1.png');extra['actuallyViewed']=False
        report['supplementalQA']=[extra];self.reject('No actual native-scale')

    def test_stale_candidate(self):
        self.fx.report()['candidate']['sha256']='b'*64;self.reject('Stale or wrong candidate')

    def test_wrong_candidate_path(self):
        self.fx.report()['candidate']['file']=str(self.fx.folder/'different.png');self.reject('Stale or wrong candidate')

    def test_stale_png_sha(self):
        self.fx.item()['sha256']='b'*64;self.reject('SHA changed')

    def test_matching_report_sha_does_not_bypass_pixels(self):
        k=f.key(self.fx.item()['file']);self.fx.images[k].putpixel((2,3),(200,1,2))
        new=hashlib.sha256(self.fx.images[k].tobytes()).hexdigest();self.fx.hashes[k]=new;self.fx.item()['sha256']=new
        self.reject('does not reproduce current')

    def test_not_actually_viewed(self):
        self.fx.item()['actuallyViewed']=False;self.reject('No actual native-scale')

    def test_resized_review(self):
        self.fx.item()['nativeScale']=0.5;self.reject('No actual native-scale')

    def test_boolean_scale_is_not_one(self):
        self.fx.item()['nativeScale']=True;self.reject('No actual native-scale')

    def test_failed_verdict(self):
        self.fx.item()['verdict']='fail';self.reject('Non-passing')

    def test_unverified_verdict_cannot_accept_internal_seam(self):
        self.fx.item()['verdict']='current_pixels_inspected_neighbor_unverified';self.reject('absent-neighbor boundary')

    def test_unverified_verdict_allowed_only_for_missing_boundary(self):
        self.fx.item()['verdict']='current_pixels_inspected_neighbor_unverified'
        self.fx.required[f.key(self.fx.item()['file'])]['operation']['noNeighbor']=True
        self.fx.validate()

    def test_report_has_unresolved_issues(self):
        self.fx.report()['issues']=['visible seam'];self.reject('Unresolved review')

    def test_report_not_passed(self):
        self.fx.report()['scopedPass']=False;self.reject('Review has not passed')

    def test_missing_required_qa(self):
        path=self.fx.folder/'qa/native-candidate/unreviewed.png'
        self.fx.required[f.key(path)]=dict(path=path,image=Image.new('RGB',(1,1)),operation={},roles=['current'])
        self.reject('Required QA missing')

    def test_duplicate_within_report(self):
        self.fx.report()['items'].append(copy.deepcopy(self.fx.item()));self.reject('Duplicate QA')

    def test_path_outside_tile(self):
        self.fx.item()['file']=str(self.fx.folder.parent/'outside.png');self.reject('outside tile')

    def test_unknown_extra_qa_cannot_be_accepted(self):
        del self.fx.required[f.key(self.fx.item()['file'])];self.reject('reproduction recipe')

    def test_no_overwrite_scoped_pass_metadata(self):
        ctx=dict(folder=self.fx.folder)
        with mock.patch.object(Path,'exists',return_value=True),mock.patch.object(f,'read',return_value={'scopedLocalSeamsPassed':True}),mock.patch.object(f,'frozen',side_effect=AssertionError('Reached writes')),mock.patch.object(f,'write',side_effect=AssertionError('Wrote')):
            with self.assertRaisesRegex(ValueError,'Refuse to overwrite scoped-pass'):f.approve(ctx,{},[],[])

    def test_candidate_changed_during_validation(self):
        ctx=dict(candidate=self.fx.candidate,finalsha='a'*64,references={})
        with mock.patch.object(f,'sha',return_value='b'*64):
            with self.assertRaisesRegex(ValueError,'Candidate changed'):f.frozen(ctx)

    def test_neighbor_changed_during_validation(self):
        ctx=dict(candidate=self.fx.candidate,finalsha='a'*64,references={'west':{'file':'west.png','sha256':'b'*64}})
        with mock.patch.object(f,'sha',return_value='a'*64):
            with self.assertRaisesRegex(ValueError,'Source changed'):f.frozen(ctx)

    def test_metadata_changed_during_validation(self):
        ctx=dict(candidate=self.fx.candidate,finalsha='a'*64,references={},immutableMetadata=[{'file':'plan.json','sha256':'b'*64}])
        with mock.patch.object(f,'sha',return_value='a'*64):
            with self.assertRaisesRegex(ValueError,'Source metadata changed'):f.frozen(ctx)

    def test_report_or_qa_changed_after_validation(self):
        record={'file':'review.json','sha256':'b'*64}
        with mock.patch.object(f,'sha',return_value='a'*64):
            with self.assertRaisesRegex(ValueError,'Review input changed'):f.frozen_reviews({},[record])
            with self.assertRaisesRegex(ValueError,'Review input changed'):f.frozen_reviews({'qa':record},[])

    def test_bad_finalsha_and_tile_rejected_before_io(self):
        with mock.patch.object(f,'sha',side_effect=AssertionError('Unexpected file read')):
            for tile,digest,phrase in [('r00_c01','a'*64,'outside16x16'),('not_tile','a'*64,'Invalid tile'),('r09_c14','unknown','finalsha')]:
                with self.subTest(tile=tile,digest=digest):
                    with self.assertRaisesRegex(ValueError,phrase):f.context(tile,digest)


class PixelContractTests(TestCase):
    def test_all_direction_qa_names_counts_and_legacy_aliases(self):
        # Real full-resolution QA derivation; no filesystem image or acceptance writes.
        current=Image.new('RGB',(4096,4096),(13,27,91))
        for name in ['NW','NE','SW','SE']:
            v,h,corner=f.engine.orientation(name)
            for has_corner in [False,True]:
                neighbors={v:Image.new('RGB',(4096,4096),(80,10,20)),h:Image.new('RGB',(4096,4096),(10,90,20))}
                if has_corner:neighbors[corner]=Image.new('RGB',(4096,4096),(10,20,110))
                ctx=dict(folder=f.ROOT/'_test_memory_only',legacy=False,image=current,neighbors=neighbors,name=name,returnDepth=256)
                generated=list(f.engine.qa_images(current,neighbors,name,256));required=f.requirements(ctx)
                self.assertEqual(len(required),28 if has_corner else 27)
                for label,pixels,operation,roles in generated:
                    item=required[f.key(ctx['folder']/'qa/multi-edge-candidate'/(label+'.png'))]
                    self.assertEqual(item['image'].tobytes(),pixels.tobytes());self.assertEqual(item['roles'],roles)
                axis_ret={'x':'minus' if h=='east' else 'plus','y':'minus' if v=='south' else 'plus'}
                for axis,sign in axis_ret.items():self.assertTrue(any(f'internal-{axis}1024-return-{sign}256-full' in k for k in required))
                if name=='NW':
                    ctx['legacy']=True;legacy=f.requirements(ctx)
                    self.assertEqual(len(legacy),len(required));self.assertFalse(any('return-plus' in k for k in legacy))
                    self.assertTrue(any('internal-x1024-return-256-full' in k for k in legacy))
                    if has_corner:self.assertIn(f.key(ctx['folder']/'qa/four-tile-corner.png'),legacy)

    def test_legacy_missing_north_boundary_is_explicit(self):
        ctx=dict(folder=f.ROOT/'_test_memory_only',legacy=True,image=Image.new('RGB',(4096,4096)),neighbors={},name='NW',returnDepth=256)
        required=f.requirements(ctx);self.assertEqual(len(required),27)
        for side in ['north','west']:self.assertIn(f.key(ctx['folder']/'qa'/(side+'-no-neighbor-unverified.png')),required)

    def test_extra_native_recipe_and_reject_holes_overlap_scaling(self):
        source=Image.new('RGB',(4096,4096),(12,34,56));source.putpixel((11,21),(77,88,99))
        ctx=dict(image=source,neighbors={});path=Path('extra.png')
        recipe={'canvasPixels':[2,2],'pieces':[{'source':'current','cropLTRB':[10,20,12,22],'pasteXY':[0,0]}]}
        image=f.extra_image(ctx,path,{'reproduction':recipe});self.assertEqual(image.getpixel((1,1)),(77,88,99))
        bad=copy.deepcopy(recipe);bad['pieces'][0]['cropLTRB']=[10,20,11,22]
        with self.assertRaisesRegex(ValueError,'uncovered'):f.extra_image(ctx,path,{'reproduction':bad})
        bad=copy.deepcopy(recipe);bad['pieces'].append(copy.deepcopy(bad['pieces'][0]))
        with self.assertRaisesRegex(ValueError,'Overlapping'):f.extra_image(ctx,path,{'reproduction':bad})
        bad=copy.deepcopy(recipe);bad['pieces'][0]['transpose']='RESIZE'
        with self.assertRaisesRegex(ValueError,'resampling'):f.extra_image(ctx,path,{'reproduction':bad})

    def test_corner_prepare_refuses_missing_true_diagonal(self):
        with self.assertRaisesRegex(ValueError,'Three true neighboring tiles'):f.prepare_corner({}, {})

    def test_external_details_preserve_actual_side_order(self):
        old=Image.new('RGB',(4096,4096),(100,0,0));current=Image.new('RGB',(4096,4096),(0,100,0))
        for side in ['north','south','east','west']:
            ctx=dict(image=current,neighbors={side:old})
            for kind,depth in [('segment',256),('unrotated',320)]:
                pixels=f.extra_image(ctx,Path('external-details')/f'{side}-{kind}-2.png',{})
                self.assertEqual(pixels.size,(depth*2,1024) if side in ['west','east'] else (1024,depth*2))
                expected_first=(100,0,0) if side in ['north','west'] else (0,100,0)
                expected_last=(0,100,0) if side in ['north','west'] else (100,0,0)
                self.assertEqual(pixels.getpixel((0,0)),expected_first)
                self.assertEqual(pixels.getpixel((pixels.width-1,pixels.height-1)),expected_last)


if __name__=='__main__':
    stream=io.StringIO();suite=defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result=TextTestRunner(stream=stream,verbosity=2).run(suite)
    evidence=dict(createdAt=datetime.now(timezone.utc).isoformat(),testsRun=result.testsRun,passed=result.wasSuccessful(),failures=len(result.failures),errors=len(result.errors),testOutput=stream.getvalue(),scope='Synthetic in-memory report-gate tests plus full4096 QA reconstruction contract in all four directions. No production images generated, no production validation or approval executed.',productionVisualAcceptance=False,sourceFiles=[f.ref(Path(__file__)),f.ref(Path(f.__file__)),f.ref(Path(f.engine.__file__))])
    evidence_path=Path(__file__).with_name('finalize-scoped-test-evidence.json');f.write(evidence_path,evidence)
    print(json.dumps({'passed':result.wasSuccessful(),'testsRun':result.testsRun,'evidence':str(evidence_path)}))
    if not result.wasSuccessful():print(stream.getvalue());sys.exit(1)
