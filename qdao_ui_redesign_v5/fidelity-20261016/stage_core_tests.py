from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parent
CLIENT=Path('E:/work/mmorpg-client')
rel='Assets/Tests/EditMode/Tianyong/QdaoServerSelectPrefabTests.cs'
src=CLIENT/rel
old=src.read_text(encoding='utf-8-sig')
new=old.replace('foreach (var name in new[] { "ScreenArtwork", "Hero", "ServerFrame", "CredentialArt" })','foreach (var name in new[] { "ScreenArtwork", "CredentialArt" })')
new=new.replace('            Assert.That(Invoke("ReferencesValid"), Is.True);','            Assert.That(Invoke("ReferencesValid"), Is.True);\n            _view.ShowLanding(true);',1)
new=new.replace('                StringAssert.StartsWith("Assets/Resources/UI/Ugui/RefreshV8/", AssetDatabase.GetAssetPath(image.sprite), name);','')
new=new.replace('new[] { "SelectServer", "EnterGame", "SwitchAccount", "TopTab_0", "CategoryArt_0",','new[] { "SelectServer", "EnterGame", "TopTab_0", "CategoryArt_0",')
needle='            Assert.That(Required<Image>("ScreenArtwork").raycastTarget, Is.False);'
new=new.replace(needle,needle+'\n            Assert.That(AssetDatabase.GetAssetPath(Required<Image>("ScreenArtwork").sprite),\n                Is.EqualTo("Assets/Resources/UI/Ugui/CoreFidelity20261016/login_shell.png"));\n            Assert.That(Required<Button>("SwitchAccount").targetGraphic, Is.TypeOf<Image>());\n            Assert.That(Required<TMP_Text>("SwitchAccountText").text, Is.EqualTo("切换账号"));')
needle='            Assert.That(Required<RectTransform>("ServerPage").gameObject.activeSelf, Is.True);'
new=new.replace(needle,needle+'\n            Assert.That(AssetDatabase.GetAssetPath(Required<Image>("ScreenArtwork").sprite),\n                Is.EqualTo("Assets/Resources/UI/Ugui/CoreFidelity20261016/server_shell.png"));',1)
needle='            Click("BackButton");'
new=new.replace(needle,needle+'\n            Assert.That(AssetDatabase.GetAssetPath(Required<Image>("ScreenArtwork").sprite),\n                Is.EqualTo("Assets/Resources/UI/Ugui/CoreFidelity20261016/login_shell.png"));',1)
assert old.count('[Test')==new.count('[Test')
dest=ROOT/'tests-client'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
dest.write_text(new,encoding='utf-8');shutil.copyfile(str(src)+'.meta',str(dest)+'.meta')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest={'destinationRoot':str(CLIENT),'files':[{'source':'tests-client/'+p,'target':p,'sha256':sha(ROOT/'tests-client'/p)} for p in [rel,rel+'.meta']], 'guards':[{'target':rel,'sha256Before':sha(src)}], 'scope':'Only obsolete skin/node assertions adapted; all existing semantic action, loading, maintenance, empty search, credentials, serialized references and stale click regression tests retained.','testFilter':'MmorpgClient.Tests.EditMode.Ugui.QdaoServerSelectPrefabTests','requiresRebuiltPrefab':True}
(ROOT/'core-tests-install-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Staged two-file test patch; '+str(new.count('[Test'))+' original test annotations retained.')
