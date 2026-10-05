import json,pathlib,datetime
out=pathlib.Path(__file__).parent
p=out/'source-evidence.json';e=json.loads(p.read_text(encoding='utf8'))
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
for c in e['characters'].values():
    for g in c['groups'].values():
        g['staticViewed']=True;g['reviewedAtUtc']=now;g['viewScope']='Actual QA contact sheet: fixed sequence union crop whole-body + fixed lower-body detail; static only. Occluded joints are not certified.'
p.write_text(json.dumps(e,ensure_ascii=False,indent=2),encoding='utf8')
changes=json.loads((out/'concurrent-changes.json').read_text(encoding='utf8'))
for f in changes['changedSinceViewedSnapshot']:
    f['currentExtraReview']=True;f['extraReviewScope']='Viewed concurrent-latest contact sheet whole-frame thumbnail only; no full sequence dynamic acceptance.'
(out/'concurrent-changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf8')
def sha(cid,g,frame):
    return next(f['sha256'] for f in e['characters'][cid]['groups'][g]['frames'] if f['frame']==frame)
ids=list(e['characters'])
def bound(cid,g,frames):
    return [{'group':g,'frame':n,'sha256':sha(cid,g,n)} for n in frames]
findings=[
 {'character':ids[4],'severity':'confirmed_spec_mismatch','group':'run/NW','frames':bound(ids[4],'run/NW',['01','02','03','04','10','11','14','15']),'observation':'NW10 has screen-left leg planted and screen-right leg rear-raised with sole visible; NW11 has screen-left leg raised showing sole and screen-right leg planted. Whole-leg continuity was checked again in native runtime/NW/10 and 11. NW01/02 versus 03/04 also changes supporting side. This contradicts current handoff: anatomical left 07/08→09/10→11/12→13/14, right15/16→01/02→03/04→05/06. NW15 returns to screen-left planted state.','action':'Trace real leg identity and arrange four relative support positions, each with two independent poses. First assess phase/ordering repair; preserve anatomically correct pictures, do not label every visible sole as wrong or redraw blindly.'},
 {'character':ids[2],'severity':'continuity_review_required','group':'cast/W','frames':bound(ids[2],'cast/W',['06','07']),'observation':'06 places screen-right knife hand above head, 07 places screen-left knife hand above head. Each frame retains two hands/two knives, but high/low arms exchange within one frame.','action':'Inspect clip at existing cast timing; decide whether arm motion needs a transition pose. This is a continuity concern, not a confirmed hand-anatomy failure.'},
 {'character':ids[0],'severity':'continuity_review_required','group':'run/N','frames':bound(ids[0],'run/N',['10','11','12']),'observation':'Head/hip elevation and head silhouette differ more abruptly around 11 than adjacent steady pairs.','action':'Review 1200ms playback and seam; preserve natural bobbing. Contact sheets alone do not prove a dynamic defect.'},
 {'character':ids[0],'severity':'continuity_review_required','group':'run/E','frames':bound(ids[0],'run/E',['04','05']),'observation':'Support position/body compression changes noticeably across04→05. Similar transition visible in W04→05.','action':'Review actual 1200ms run; no forced redraw from this static clue.'},
 {'character':ids[4],'severity':'continuity_review_required','group':'run/NE','frames':bound(ids[4],'run/NE',['03','04']),'observation':'Supporting boot projected shape/size changes noticeably from03 to04.','action':'Review at75ms and slow motion; normal heel lift/perspective must not be falsely called out-turn.'},
 {'character':ids[4],'severity':'continuity_review_required','group':'run/E','frames':bound(ids[4],'run/E',['09','10']),'observation':'Bow angle changes noticeably09→10; full elbow/wrist chain is partly behind sleeve/body.','action':'Review bow/hand continuity at75ms; there is no confirmed detached wrist from the seen static frames.'}
]
report={'completedAtUtc':now,'role':'independent current-image static audit, group-b','sourceEvidence':str(p),'concurrentChanges':str(out/'concurrent-changes.json'),'reviewedSnapshotFrames':980,'reviewedSnapshotGroups':70,'allSnapshotManifestHashesMatchedAtBuild':True,'currentSnapshotEqualsEntireDelivery':False,'findings':findings,'characters':{},'limits':['Static observed version only; concurrent different SHA revisions do not inherit this result.','No normal-speed browser dynamic visual acceptance, client integration, world foot lock, sliding or skill synchronization tested in this audit.','Occluded hip roots, far arms and wrists cannot be certified; toe exposure or natural flexion is not automatically eversion.','Same movement plane from hip through knee/ankle/foot is required; knee must not be locked straight.','No additional definite static hand/foot-axis rejection was established for the observed05–08 frames; this is not blanket approval of all direction axes.']}
for cid,c in e['characters'].items():
    report['characters'][cid]={'viewedGroups':list(c['groups']),'viewedFrames':sum(len(g['frames']) for g in c['groups'].values()),'missingOrUnviewedSnapshotGroups':[],'nativeSingleFramesAdditionallyViewed':(['run/NW/10','run/NW/11'] if cid==ids[4] else []),'concurrentChangedFramesExtraThumbnailViewed':[f['group']+'/'+f['frame'] for f in changes['changedSinceViewedSnapshot'] if f['character']==cid],'normalSpeedDynamicPassed':False,'clientPassed':False}
report['falsePositiveExcluded']={'character':ids[3],'group':'run/NW','frames':['07','08'],'observation':'07→08 is the expected support swap in current08 cycle: right16/01→02/03→04/05→06/07, left08/09→10/11→12/13→14/15. Do not impose another character\'s01–08 layout. Viewed boot exposure does not establish off-axis foot twisting.'}
(out/'review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('980 snapshot PNGs /70 groups viewed;22 changed PNG thumbnail supplements; final review.json saved')
