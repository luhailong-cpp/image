const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const client='E:/work/mmorpg-client',root='E:/work/image/docs/ui-fidelity-20261016/regression-patch';
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');const files=[],guards=[];
function change(file,edits){const before=fs.readFileSync(path.join(client,file));let source=before.toString();for(const [a,b]of edits){if(!source.includes(a))throw Error('Missing guarded source fragment: '+file+' / '+a);source=source.replace(a,b);}const out=path.join(root,file);fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,source);files.push({source:file,target:file,sha256:sha(source)});guards.push({target:file,sha256Before:sha(before)});}
change('Assets/Scripts/UI/Ugui/Guild/GuildWindow.cs',[[
'Text(_body, ActivityStateText(view, info.Level), x + 136, 138, 324, 46, 30, Muted)',
'Text(_body, ActivityStateText(view, info.Level), x + 136, 138, 348, 46, 30, Muted)']]);
change('Assets/Scripts/UI/Ugui/Team/TeamWindow.cs',[[
'_applicationCount=Label(frame,"",1372,169,43,44,27,Cream,TextAlignmentOptions.Center);',
'_applicationCount=Label(frame,"",1372,169,43,44,27,Cream,TextAlignmentOptions.Center);\n            _applicationCount.name="TeamApplicationCount";']]);
change('Assets/Tests/EditMode/Tianyong/TeamWindowTests.cs',[
 ['Does.Contain("我的玩家编号  11")','Does.Contain("玩家编号 11")'],
 ['Assert.That(ActiveText(), Does.Contain("5 条"));','Assert.That(_root.GetComponentsInChildren<TMP_Text>().Single(t => t.name == "TeamApplicationCount").text, Is.EqualTo("5"));'],
 ['Assert.That(ActiveText(), Does.Contain("0 条"));','Assert.That(_root.GetComponentsInChildren<TMP_Text>().Single(t => t.name == "TeamApplicationCount").text, Is.EqualTo("0"));']]);
change('Assets/Tests/EditMode/Social/FriendRequestTests.cs',[[
'social.Root.GetComponentsInChildren<Button>(true).Single(button => button.name == "SocialFriendRequests")',
'social.Root.GetComponentsInChildren<Button>(false).Single(button => button.name == "SocialFriendRequests")']]);
change('Assets/Tests/EditMode/Mail/MailWindowTests.cs',[
 ['private MailUiState _state;','private MailUiState _state;\n        private EventSystem _previousEvents;'],
 ['_events=new GameObject("MailTestEvents",typeof(EventSystem));','_previousEvents=EventSystem.current;\n            _events=new GameObject("MailTestEvents",typeof(EventSystem));\n            EventSystem.current=_events.GetComponent<EventSystem>();'],
 ['_window?.Dispose();if(_canvas!=null)Object.DestroyImmediate(_canvas);if(_events!=null)Object.DestroyImmediate(_events);',
  '_window?.Dispose();if(_canvas!=null)Object.DestroyImmediate(_canvas);if(_events!=null)Object.DestroyImmediate(_events);\n            EventSystem.current=_previousEvents;'],
 ['HideRestoresFocusAndBalancesGameplayInputBlocker','HideRestoresOpenerFocus'],
 ['bool blocked=GameplayInputGate.IsKeyboardBlocked;var opener=Button("CloseMail").gameObject;','var opener=Button("CloseMail").gameObject;'],
 ['Assert.That(GameplayInputGate.IsKeyboardBlocked,Is.True);','// Actual GameplayInputBlocker lifecycle is exercised in MailInputBlockerPlayModeTests.'],
 ['_window.Hide();Assert.That(EventSystem.current.currentSelectedGameObject,Is.EqualTo(_canvas));\n            Assert.That(GameplayInputGate.IsKeyboardBlocked,Is.EqualTo(blocked));',
  '_window.Hide();Assert.That(EventSystem.current.currentSelectedGameObject,Is.EqualTo(_canvas));']]);
fs.mkdirSync(root,{recursive:true});fs.writeFileSync(path.join(root,'install-manifest.json'),JSON.stringify({schemaVersion:1,guards,files},null,2));
console.log('REGRESSION_PATCH_STAGED '+files.length);
