from pathlib import Path
import json, hashlib, datetime, uuid, re
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent
PACKAGE = ROOT.parent
CLIENT = Path('E:/work/mmorpg-client')
STAGED = ROOT/'staged'
ART = 'Assets/Resources/UI/Ugui/GameplayFidelity20261016/'
CODE = 'Assets/Scripts/UI/Ugui/Gameplay/'
TEST = 'Assets/Tests/EditMode/Battle/'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(relative, content):
    p=STAGED/relative; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding='utf-8'); return p
def replace(text, before, after):
    assert before in text, before
    return text.replace(before, after)

# Evidence from the existing capture, before this patch or the equipment compatibility installation.
seen=['01-bag-filled_2560x1080.png','01-bag-filled_1920x1080.png',
      '02-missions-filled_2560x1080.png','02-missions-filled_1920x1080.png',
      '03-activities-filled_2560x1080.png','03-activities-filled_1920x1080.png',
      '04-bag-empty_1920x1080.png','05-missions-empty_1920x1080.png',
      '06-activities-empty_1920x1080.png','06-activities-empty_2560x1080.png',
      '07-bag-error_2560x1080.png','08-bag-loading_1920x1080.png',
      '09-mission-accept_2560x1080.png','10-mission-claim_1920x1080.png',
      '11-mission-busy_1920x1080.png','12-mission-error_2560x1080.png',
      '13-activity-participate_2560x1080.png']
native=PACKAGE/'qa/native'
def evidence(p):
    return dict(path=str(p),sha256=sha(p),native_size=list(Image.open(p).size),mtime_utc=datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat())
findings=[
 dict(id='V01',severity='must-fix',page='activities',issue='Empty card area contains four rows of repeated gold border fragments.',evidence=['06-activities-empty_1920x1080.png','06-activities-empty_2560x1080.png'],cause='Paper tile selected from y100..164 crosses the original card border at y161; mirrored tiling repeats it.'),
 dict(id='V02',severity='must-fix',page='missions/activities/bag',issue='Disabled painted buttons show a rectangular gray background outside their painted silhouette.',evidence=['02-missions-filled_1920x1080.png','09-mission-accept_2560x1080.png','11-mission-busy_1920x1080.png','03-activities-filled_2560x1080.png'],cause='ColorTint dims the opaque paper pixels included in the native crop.'),
 dict(id='V03',severity='must-fix',page='bag',issue='Capacity and Refresh text overlap the lower gold frame.',evidence=['01-bag-filled_1920x1080.png','01-bag-filled_2560x1080.png','04-bag-empty_1920x1080.png'],native_bounds=dict(capacity=[732,750,320,25],refresh=[1109,757,72,25])),
 dict(id='V04',severity='must-fix',page='activities/missions',issue='The top of the next text line is visible at the scrolling description/objective viewport edge.',evidence=['03-activities-filled_1920x1080.png','13-activity-participate_2560x1080.png','02-missions-filled_2560x1080.png'],limitation='All text exists in scroll content; the static capture alone does not prove scrolling interaction.'),
 dict(id='V05',severity='must-fix',page='missions/activities',issue='Rectangular paper cleanup patches have visible color seams, especially the activity footer.',evidence=['05-missions-empty_1920x1080.png','06-activities-empty_2560x1080.png']),
 dict(id='V06',severity='must-fix',page='missions',issue='Completed objectives display hollow square glyphs instead of the intended check.',evidence=['10-mission-claim_1920x1080.png','12-mission-error_2560x1080.png'],fixture_evidence='GameplayUiVerification sets all objective.Completed=true before these captures; implementation uses a font glyph.'),
 dict(id='V07',severity='fix',page='missions',issue='Five-character claimable state is ellipsized inside the heading badge.',evidence=['10-mission-claim_1920x1080.png','12-mission-error_2560x1080.png']),
 dict(id='V08',severity='fix',page='bag',issue='The square item icon extends below the first horizontal divider.',evidence=['01-bag-filled_1920x1080.png','01-bag-filled_2560x1080.png'],native_bounds=dict(icon=[1365,216,280,280],divider_y=472)),
 dict(id='V09',severity='fix',page='bag/missions/activities',issue='Empty detail states retain blank action plates; activity schedule/reason text runs across unused baked reward slots.',evidence=['04-bag-empty_1920x1080.png','05-missions-empty_1920x1080.png','13-activity-participate_2560x1080.png'])]
review=dict(schema='qdao.gameplay.visual-review.v1',reviewed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='needs-fixes',method='Direct visual comparison of 17 existing native captures against all 3 approved PNGs; read-only client/code review.',references=[evidence(PACKAGE.parent/p) for p in ['02-inventory.png','01-quests.png','03-activities.png']],captures=[evidence(native/p) for p in seen],capture_inventory=dict(expected_pngs=26,present_pngs=len(list(native.glob('*.png'))),declared_status=(native/'capture-status.txt').read_text(),scope=(native/'fixture-scope.txt').read_text(),capture_json_present=False,existing_qa_json='qa/install-result.json is installation evidence, not capture metadata'),pass_observations=['Frame/title/ornaments preserve original native proportions in both resolutions.','1920 screenshots use a centered letterboxed frame; no non-uniform horizontal compression observed.','Empty/loading/error text is readable.','Fixture names, icons, quantities, protocol-derived missing reward items and schedules are not scored as design deviations.'],findings=findings,limits=['Screenshots are editor visual fixtures, not live game data.','Capture mtime is 2026-10-17 04:24 UTC, earlier than the equipment compatibility installation at 04:55 UTC; these images do not verify that patch.','Static captures do not establish final scroll reachability, long text exhaustiveness or pointer/keyboard interaction.','This review has no post-fix screenshots and makes no pixel-identical claim.'])
(PACKAGE/'qa/visual-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
xml_path=PACKAGE.parents[2]/'docs/ui-fidelity-20261016/editmode-results.xml'
test_run=ET.parse(xml_path).getroot()
selected_failures=[]
for case in test_run.findall('.//test-case'):
    if case.attrib.get('result')=='Failed' and any(n in case.attrib.get('fullname','') for n in ('EquipForgeWindowTests.WornEquipmentCanOpenWhileBagIsMissingAndRefreshAfterReadFailure','GameplayWindowTests.MissionStatusFiltersPreserveUnacceptedActiveAndCompletedStatesWithoutSendingActions')):
        selected_failures.append(dict(fullname=case.attrib['fullname'],message=case.findtext('failure/message'),stack=case.findtext('failure/stack-trace')))
(ROOT/'unity-failure-evidence.json').write_text(json.dumps(dict(source=str(xml_path),source_sha256=sha(xml_path),run_summary=test_run.attrib,assigned_failures=selected_failures),ensure_ascii=False,indent=2),encoding='utf-8')

runtime=(CLIENT/(CODE+'GameplayWindow.Fidelity.cs')).read_text(encoding='utf-8-sig')
# Retain native paper colors when disabled, so opaque crop background cannot form a gray rectangle.
runtime=replace(runtime,'c.selectedColor = Color.white; c.highlightedColor = new Color(1, .97f, .90f); b.colors = c;', 'c.selectedColor = Color.white; c.highlightedColor = new Color(1, .97f, .90f); c.disabledColor = Color.white; b.colors = c;')
runtime=replace(runtime,'if (!string.IsNullOrEmpty(label)) NativeText(b.transform, label, 10, 0, w - 20, h, font, jade ? Cream : Ink, TextAlignmentOptions.Center);', '''if (!string.IsNullOrEmpty(label))
            {
                var text = NativeText(b.transform, label, 10, 0, w - 20, h, font, jade ? Cream : Ink, TextAlignmentOptions.Center);
                if (!enabled) text.color = jade ? new Color(Cream.r, Cream.g, Cream.b, .65f) : Muted;
            }''')
# Snap masked paragraph viewport to complete TMP lines, keeping the entire text in scroll content.
runtime=replace(runtime,'float actual = Math.Max(height, measure.GetPreferredValues(value, width - 8, float.PositiveInfinity).y + 8);', '''float actual = Math.Max(height, measure.GetPreferredValues(value, width - 8, float.PositiveInfinity).y + 8);
            float oneLine = measure.GetPreferredValues("道", width - 8, float.PositiveInfinity).y;
            float advance = Math.Max(1, measure.GetPreferredValues("道\\n道", width - 8, float.PositiveInfinity).y - oneLine);
            int visibleLines = Math.Max(1, Mathf.FloorToInt((height - oneLine) / advance) + 1);
            float viewportHeight = Math.Min(height, oneLine + (visibleLines - 1) * advance);''')
runtime=replace(runtime,'"DescriptionScroll", x, y, width, height, actual, 1', '"DescriptionScroll", x, y, width, viewportHeight, actual, 1')
runtime=replace(runtime,'1109, 757, 72, 25, Refresh, !_bagLoading && !_sorting && !_equipBusy, 20', '948, 741, 46, 20, Refresh, !_bagLoading && !_sorting && !_equipBusy, 17')
runtime=replace(runtime,'732, 750, 320, 25, 21, Muted', '732, 741, 210, 20, 18, Muted')
runtime=replace(runtime,'ItemIcon(panel, item.IconKey, 1365, 216, 280);', 'ItemIcon(panel, item.IconKey, 1380, 216, 250);')
runtime=replace(runtime,'NativeText(panel, equipment ? worn ? "已穿戴" : "未穿戴" : "物品",', 'NativeArt(panel, "bag-item-badge", 1423, 160, 159, 40);\n            NativeText(panel, equipment ? worn ? "已穿戴" : "未穿戴" : "物品",')
runtime=replace(runtime,'NativeText(_body, MissionStatus(detail.Status), badgeX + 2, 131, 122, 45, 25, Ink, TextAlignmentOptions.Center);', '''var badgeText = NativeText(_body, MissionStatus(detail.Status), badgeX + 2, 131, 122, 45, 25, Ink, TextAlignmentOptions.Center);
            badgeText.enableAutoSizing = true; badgeText.fontSizeMin = 18; badgeText.fontSizeMax = 25;''')
runtime=replace(runtime,'854, 337, 872, 111, Math.Max(54, heights.Sum())', '854, 337, 872, 108, Math.Max(54, heights.Sum())')
runtime=replace(runtime,'NativeText(objectives, goal.Completed ? "✓" : "□", 12, goalY, 42, 50, 33, goal.Completed ? Ink : Gold);', '''var stateArt = EquipUiSkin.Art(objectives, goal.Completed ? "checkbox_on" : "checkbox_off", 12, goalY + 7, 32, 32, Gold);
                stateArt.name = "MissionObjectiveState_" + i;''')
runtime=replace(runtime,'if (selected) NativeText(button.transform, "✓", 281, 29, 33, 49, 34, Cream);', 'if (selected) EquipUiSkin.Art(button.transform, "checkbox_on", 278, 31, 32, 32, Gold);')
write(CODE+'GameplayWindow.Fidelity.cs',runtime)
main=(CLIENT/(CODE+'GameplayWindow.cs')).read_text(encoding='utf-8-sig')
main=replace(main,'frame, 732, 708, 260, 40,', 'frame, 732, 708, 260, 30,')
write(CODE+'GameplayWindow.cs',main)

forge=(CLIENT/(TEST+'EquipForgeWindowTests.cs')).read_text(encoding='utf-8-sig')
before='''Assert.That(Text("EquipForgeStage").text, Is.EqualTo("正在同步行囊与装备栏…"));
            Assert.That(Button("EquipForgeEnhance").interactable, Is.False);'''
after='''Assert.That(Text("EquipForgeStage").text, Is.EqualTo("正在同步行囊与装备栏…"));
            var hiddenEnhance = ForgeRoot().GetComponentsInChildren<Button>(true)
                .Single(b => b.name == "EquipForgeEnhance");
            Assert.That(hiddenEnhance.gameObject.activeInHierarchy, Is.False, "未同步时不展示可操作的强化区");
            Assert.That(hiddenEnhance.interactable, Is.False);'''
forge=replace(forge,before,after)
write(TEST+'EquipForgeWindowTests.cs',forge)
gameplay=(CLIENT/(TEST+'GameplayWindowTests.cs')).read_text(encoding='utf-8-sig')
gameplay=replace(gameplay,'Click("筛选·全部任务"); Click("进行中");', 'ClickNamed("MissionFilterMenu"); ClickNamed("MissionStatusFilter_1");')
gameplay=replace(gameplay,'Click("筛选·进行中"); Click("已达成");', 'ClickNamed("MissionFilterMenu"); ClickNamed("MissionStatusFilter_2");')
gameplay=replace(gameplay,'Click("待开启"); AssertText("任务一");', 'ClickNamed("AvailableMissions"); AssertText("任务一");')
gameplay=replace(gameplay,'        private ScrollRect Scroll(string name)', '''        [Test]
        public void CompletedGoalsUsePaintedChecksAndAllObjectivesRemainScrollable()
        {
            var missions = MakeMissions(1);
            missions.Missions[0].Objectives[0].Completed = true;
            for (uint i = 1; i < 5; ++i)
                missions.Missions[0].Objectives.Add(new MissionObjectiveInfo { ObjectiveIndex = i, Description = "目标" + i, Target = 3, Progress = 1 });
            _window.SetMissions(missions, false, null); _window.Show(GameplayPage.Missions);
            var check = _fixture.GetComponentsInChildren<Image>().Single(i => i.name == "MissionObjectiveState_0");
            Assert.That(check.sprite, Is.SameAs(EquipUiSkin.Load("checkbox_on")));
            var scroll = Scroll("MissionObjectivesScroll");
            Assert.That(scroll.content.rect.height, Is.GreaterThan(scroll.viewport.rect.height));
            scroll.verticalNormalizedPosition = 0;
            Assert.That(scroll.content.anchoredPosition.y, Is.GreaterThan(0));
            AssertText("目标4"); Assert.That(_accepts, Is.Empty); Assert.That(_claims, Is.Empty);
        }

        private void ClickNamed(string name)
        {
            var button = _fixture.GetComponentsInChildren<Button>(true)
                .Single(b => b.name == name && b.gameObject.activeInHierarchy);
            Assert.That(button.interactable, Is.True, "按钮应可点击：" + name);
            button.onClick.Invoke();
        }

        private ScrollRect Scroll(string name)''')
write(TEST+'GameplayWindowTests.cs',gameplay)

# Derive paper only from retained clean skins. Match the local paper gradient and retain its grain.
# Center of each erase region is opaque; four-pixel exterior feather avoids leaving border residue.
sources={s:Image.open(PACKAGE/'assets'/f'{s}-clean-skin.png').convert('RGB') for s in ('inventory','quests','activities')}
asset_rows=[]
def paper_clear(image, rect, paper):
    a=np.array(image).astype(np.float32); x0,y0,x1,y1=rect; pad=4
    l=max(0,x0-pad); t=max(0,y0-pad); r=min(image.width,x1+pad); b=min(image.height,y1+pad)
    smooth=np.array(image.filter(ImageFilter.GaussianBlur(1))).astype(np.float32)
    fallback=np.median(np.array(paper).reshape(-1,3),axis=0)
    def paper_edge(values):
        good=(values[:,0]>213)&(values[:,1]>200)&(values[:,2]>170)&((values[:,0]-values[:,1])<25)&((values[:,1]-values[:,2])<35)
        positions=np.flatnonzero(good)
        filtered=np.empty_like(values)
        for channel in range(3):
            filtered[:,channel]=np.interp(np.arange(len(values)),positions,values[positions,channel]) if len(positions)>2 else fallback[channel]
        return np.array(Image.fromarray(np.clip(filtered,0,255).astype('uint8')[None,:,:]).filter(ImageFilter.GaussianBlur(8)))[0].astype(np.float32)
    top=paper_edge(smooth[t,l:r]); bottom=paper_edge(smooth[b-1,l:r]); left=paper_edge(smooth[t:b,l]); right=paper_edge(smooth[t:b,r-1])
    corners=[(top[0]+left[0])/2,(top[-1]+right[0])/2,(bottom[0]+left[-1])/2,(bottom[-1]+right[-1])/2]
    for edge,start,end in [(top,corners[0],corners[1]),(bottom,corners[2],corners[3]),(left,corners[0],corners[2]),(right,corners[1],corners[3])]:
        n=min(20,len(edge)//3); f=np.linspace(0,1,n)[:,None]
        edge[:n]=start*(1-f)+edge[:n]*f; edge[-n:]=edge[-n:]*(1-f)+end*f
    xx=np.linspace(0,1,r-l)[None,:,None]; yy=np.linspace(0,1,b-t)[:,None,None]
    bilinear=(1-yy)*((1-xx)*corners[0]+xx*corners[1])+yy*((1-xx)*corners[2]+xx*corners[3])
    # Coons interpolation matches every exterior edge, unlike a flat tiled rectangle.
    field=(1-yy)*top[None,:,:]+yy*bottom[None,:,:]+(1-xx)*left[:,None,:]+xx*right[:,None,:]-bilinear
    field=np.minimum(np.maximum(field,[213,200,170]),[248,238,221])
    texture=np.array(paper).astype(np.float32)-np.array(paper.filter(ImageFilter.GaussianBlur(6))).astype(np.float32)
    texture=np.tile(texture,(int(np.ceil((b-t)/paper.height)),int(np.ceil((r-l)/paper.width)),1))[:b-t,:r-l]
    field=np.clip(field+texture*.8,0,255)
    gx=np.minimum(np.clip((np.arange(l,r)-l)/pad,0,1),np.clip((r-1-np.arange(l,r))/pad,0,1))
    gy=np.minimum(np.clip((np.arange(t,b)-t)/pad,0,1),np.clip((b-1-np.arange(t,b))/pad,0,1))
    mask=(gy[:,None]*gx[None,:])[:,:,None]
    a[t:b,l:r]=field*mask+a[t:b,l:r]*(1-mask)
    return Image.fromarray(np.clip(a,0,255).astype('uint8'))
def save_asset(name,image,source,operations,rect=None):
    relative=ART+name+'.png'; p=STAGED/relative; p.parent.mkdir(parents=True,exist_ok=True); image.save(p)
    old_meta=CLIENT/(relative+'.meta')
    if old_meta.exists(): meta=old_meta.read_text()
    else:
        meta=(CLIENT/(ART+'mission-badge.png.meta')).read_text()
        meta=re.sub(r'guid: [a-f0-9]+','guid: '+uuid.uuid5(uuid.NAMESPACE_URL,'qdao-gameplay-fidelity-20261016/'+name).hex,meta,count=1)
        meta=re.sub(r'spriteID: [a-f0-9]+','spriteID: '+uuid.uuid5(uuid.NAMESPACE_DNS,'qdao-'+name).hex,meta,count=1)
        # Current global importer may have raised max size; explicit staged metadata still uses 4096.
        meta=re.sub(r'maxTextureSize: \d+','maxTextureSize: 4096',meta)
    meta=re.sub(r'maxTextureSize: \d+','maxTextureSize: 4096',meta)
    Path(str(p)+'.meta').write_text(meta,encoding='utf-8')
    asset_rows.append(dict(path=relative,sha256=sha(p),native_size=list(image.size),source='../assets/'+source+'-clean-skin.png',source_sha256=sha(PACKAGE/'assets'/f'{source}-clean-skin.png'),source_rect=rect,operations=operations,actual_model='not applicable: deterministic derivative; see original clean-skin record',new_ai_generation=False))
areas={
 'inventory':[(175,166,1160,697),(182,91,1165,163),(1417,155,1591,205),(1229,670,1775,758)],
 'quests':[(164,169,770,669),(190,90,721,164),(1101,124,1230,182),(841,316,1751,458),(843,475,1502,665),(854,684,1157,742),(1180,668,1786,756)],
 'activities':[(519,155,1776,654),(163,94,486,529),(790,680,1457,740)]}
for source,rects in areas.items():
    base=sources[source].copy(); paper=sources[source].crop((1290,100,1354,150))
    for rect in rects: base=paper_clear(base,rect,paper)
    if source in ('inventory','quests'):
        lower=758 if source=='inventory' else 754
        base.paste(sources[source].crop((0,lower,base.width,base.height)),(0,lower))
    allowed=np.zeros((base.height,base.width),dtype=bool)
    for x0,y0,x1,y1 in rects: allowed[max(0,y0-4):min(base.height,y1+4),max(0,x0-4):min(base.width,x1+4)]=True
    assert np.array_equal(np.array(base)[~allowed],np.array(sources[source])[~allowed]),source+' protected pixels changed'
    save_asset(source+'-frame',base,source,dict(erase_regions=rects,paper_source_rect=[1290,100,1354,150],local_paper_gradient_and_grain=True,edge_feather_outside_region=4,no_resize=True))
card=sources['activities'].crop((522,159,932,654))
card=paper_clear(card,(25,257,386,411),sources['activities'].crop((1290,100,1354,150)))
save_asset('activity-card',card,'activities',dict(erase_local_rect=[25,257,386,411],purpose='Remove unused reward slots and separator under actual schedule/reason text'),[522,159,932,654])
save_asset('bag-item-badge',sources['inventory'].crop((1423,160,1582,200)),'inventory','Native crop drawn only when an actual item is selected',[1423,160,1582,200])
(ROOT/'asset-manifest.json').write_text(json.dumps(dict(schema='qdao.gameplay.visual-fix.derivatives.v1',assets=asset_rows),ensure_ascii=False,indent=2),encoding='utf-8')

paths=[CODE+'GameplayWindow.cs',CODE+'GameplayWindow.Fidelity.cs',TEST+'EquipForgeWindowTests.cs',TEST+'GameplayWindowTests.cs']
for p in paths:
    (STAGED/(p+'.meta')).write_bytes((CLIENT/(p+'.meta')).read_bytes())
install=[];guard=[]
for p in sorted(STAGED.rglob('*')):
    if not p.is_file():continue
    relative=p.relative_to(STAGED).as_posix(); target=CLIENT/relative
    previous=sha(target) if target.exists() else None
    install.append(dict(path=relative,sha256=sha(p),action='replace' if target.exists() else 'create',expected_target_sha256=previous))
    guard.append(dict(path=relative,sha256=previous))
for p in [CODE+'GameplayUiRoot.cs',CODE+'EquipForgeDialog.cs',CODE+'EquipForgeUiState.cs',CODE+'EquipUiSkin.cs','Assets/Resources/UI/Ugui/EquipmentV1/checkbox_on.png','Assets/Resources/UI/Ugui/EquipmentV1/checkbox_off.png','Assets/Editor/GameplayUiVerification.cs']:
    guard.append(dict(path=p,sha256=sha(CLIENT/p)))
(ROOT/'sourceguard.json').write_text(json.dumps(dict(schema='qdao.gameplay.visual-fix.guard.v1',client_root=str(CLIENT),files=guard),ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'install-manifest.json').write_text(json.dumps(dict(schema='qdao.gameplay.visual-fix.install.v1',staging_root=str(STAGED),client_root=str(CLIENT),source_guard='sourceguard.json',files=install),ensure_ascii=False,indent=2),encoding='utf-8')
# Business callbacks and all original tests remain present, with only view selection and additional assertions.
old_runtime=(CLIENT/(CODE+'GameplayWindow.Fidelity.cs')).read_text(encoding='utf-8-sig')
callbacks=re.findall(r'\w+(?:Requested|Changed)\?\.Invoke\([^;]*',old_runtime)
for callback in callbacks: assert runtime.count(callback)==old_runtime.count(callback),callback
old_main=(CLIENT/(CODE+'GameplayWindow.cs')).read_text(encoding='utf-8-sig')
assert main==old_main.replace('frame, 732, 708, 260, 40,','frame, 732, 708, 260, 30,')
for name,new in [('EquipForgeWindowTests.cs',forge),('GameplayWindowTests.cs',gameplay)]:
    old=(CLIENT/(TEST+name)).read_text(encoding='utf-8-sig')
    methods=re.findall(r'public void (\w+)\(',old)
    assert all('public void '+m+'(' in new for m in methods)
    for token in ('_net.Calls','Respond(','FailWith(','_accepts','_claims','_missionReads'):
        if token in old: assert new.count(token)>=old.count(token),(name,token)
result=dict(status='passed',install_files=len(install),source_guard_files=len(guard),original_test_methods_retained=True,business_callbacks_preserved=True,original_main_changed_only_search_height=True,new_images_generated=False,client_written=False,unity_started=False,post_fix_capture_pending=True)
result.update(frame_pixels_outside_erasure_regions_exact=True,sprite_single_fullrect_uncompressed_ppu100_mipmapfalse_max4096=True,existing_sprite_meta_guids_preserved=True)
(ROOT/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result))
