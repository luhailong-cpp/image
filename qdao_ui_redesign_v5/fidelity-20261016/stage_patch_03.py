from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent;CLIENT=Path('E:/work/mmorpg-client');PATCH=ROOT/'patch-03'
base='Assets/Scripts/UI/Ugui/'
rels=[base+'QdaoCoreFidelityArt.cs',base+'QdaoServerSelectView.Visuals.cs']
old={p:(CLIENT/p).read_text(encoding='utf-8-sig') for p in rels};new=old.copy()
p=rels[0];s=new[p]
needle='''                return;
            }
            text.font = QdaoUguiTheme.ResolveFont();'''
assert s.count(needle)==1
s=s.replace(needle,'''                if (text.name.StartsWith("ServerName_") || text.name.StartsWith("ServerStatus_") ||
                    text.name == "SelectedServerText")
                {
                    // The body font's line metrics are taller than SimKai's. Empty
                    // data-bound labels still need a real line box before values arrive.
                    float preferred = text.GetPreferredValues("国", Mathf.Infinity, Mathf.Infinity).y;
                    if (preferred > text.rectTransform.rect.height)
                        text.rectTransform.SetSizeWithCurrentAnchors(RectTransform.Axis.Vertical,
                            Mathf.Ceil(preferred + 2f));
                }
                return;
            }
            text.font = QdaoUguiTheme.ResolveFont();''',1)
new[p]=s
p=rels[1];s=new[p]
s=s.replace('''                "〉", "tab_normal", out _nextPageText);''','''                "〉", "tab_normal", out _nextPageText);
            foreach (var text in new[] { _prevPageText, _nextPageText })
            {
                text.fontSize = 24f;
                text.rectTransform.SetSizeWithCurrentAnchors(RectTransform.Axis.Vertical, 40f);
            }''',1)
s=s.replace('''                "刷新", "tab_normal", out _refreshText);''','''                "刷新", "tab_normal", out _refreshText);
            _refreshText.fontSize = 24f;
            _refreshText.rectTransform.SetSizeWithCurrentAnchors(RectTransform.Axis.Vertical, 42f);''',1)
new[p]=s
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[];guards=[]
for p in rels:
 assert new[p]!=old[p]
 dest=PATCH/'client'/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(new[p],encoding='utf-8')
 files.append({'source':'client/'+p,'target':p,'sha256':sha(dest)})
 guards.append({'target':p,'sha256Before':sha(CLIENT/p)})
manifest={'destinationRoot':str(CLIENT),'files':files,'guards':guards,'scope':'Fix actual Noto line-height clipping of empty then data-bound server names/status/summary using measured GetPreferredValues; fit utility captions within their buttons.','afterInstall':'Rebuild prefab and capture both resolutions; native visible glyph test must pass.','newImages':False,'businessTransactionsModified':False}
(PATCH/'install-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
compile=(ROOT/'compile-staged-core.ps1').read_text(encoding='utf-8-sig').replace('[string]$Phase="login-server"','[string]$Phase="patch-03"')
(PATCH/'compile-staged.ps1').write_text(compile,encoding='utf-8')
# Native geometry regression. Preserve every existing assertion and semantic test.
testrel='Assets/Tests/EditMode/Tianyong/QdaoServerSelectPrefabTests.cs';src=CLIENT/testrel
test=src.read_text(encoding='utf-8-sig')
needle='        private void PrepareDisconnectedSession()'
method='''        [Test]
        public void ServerDataLabels_RenderVisibleGlyphsForSelectedAndUnselectedCardsAndSummary()
        {
            var host = new GameObject("NativeServerTextCanvas", typeof(RectTransform), typeof(Canvas));
            try
            {
                host.GetComponent<Canvas>().renderMode = RenderMode.ScreenSpaceOverlay;
                _instance.transform.SetParent(host.transform, false);
                _view.PrepareForPreview();
                Canvas.ForceUpdateCanvases();
                foreach (var name in new[] { "ServerName_0", "ServerStatus_0", "ServerName_1",
                             "ServerStatus_1", "SelectedServerText", "RefreshButtonText" })
                {
                    var label = Required<TMP_Text>(name);
                    Assert.That(label.text, Is.Not.Empty, name + " must be populated from preview/session data.");
                    label.ForceMeshUpdate(true, true);
                    var info = label.textInfo;
                    bool visible = Enumerable.Range(0, info.characterCount).Any(i =>
                        info.characterInfo[i].isVisible &&
                        info.characterInfo[i].topRight.y > info.characterInfo[i].bottomLeft.y);
                    Assert.That(visible, Is.True, name + " must contain rendered glyphs, not merely a nonempty string.");
                    Assert.That(label.rectTransform.rect.height + .5f,
                        Is.GreaterThanOrEqualTo(label.GetPreferredValues("国", float.PositiveInfinity,
                            float.PositiveInfinity).y), name + " must fit its actual font line height.");
                }
            }
            finally
            {
                _instance.transform.SetParent(null, false);
                Object.DestroyImmediate(host);
            }
        }

'''
assert test.count(needle)==1;test=test.replace(needle,method+needle,1)
dest=PATCH/'tests-client'/testrel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(test,encoding='utf-8')
(PATCH/'tests-install-manifest.json').write_text(json.dumps({'destinationRoot':str(CLIENT),'files':[{'source':'tests-client/'+testrel,'target':testrel,'sha256':sha(dest)}],'guards':[{'target':testrel,'sha256Before':sha(src)}],'testFilter':'MmorpgClient.Tests.EditMode.Ugui.QdaoServerSelectPrefabTests','scope':'One native visible glyph/real-font-height regression added; all original assertions retained.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(manifest,ensure_ascii=False))
