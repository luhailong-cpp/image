const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=__dirname,scene='E:/work/image/designs/scene-select-ui-v1/fidelity-20261016',client='E:/work/mmorpg-client';
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const sources=[['Battle/AttributePanelDisplayTests.cs',root],['Tianyong/SceneChannelWindowTests.cs',scene]];
for(const [relative,out] of sources){
 const source=client+'/Assets/Tests/EditMode/'+relative,name=path.basename(relative);let code=fs.readFileSync(source,'utf8').replaceAll('\r\n','\n');
 if(name==='AttributePanelDisplayTests.cs')code=code.replaceAll('170<color=#7FD98A>+1</color>(+15)','170<color=#28734E>+1</color>(+15)').replaceAll('135<color=#7FD98A>+1</color>','135<color=#28734E>+1</color>');
 else{
  code=code.replace('Show_BuildsOneNamedRowPerLine_LeftThenRightThenNextRow','Show_BuildsOneNamedRowPerLine_ThreeColumnsThenNextRow')
   .replace('GameplayUiArt.Load("tab_selected")','QdaoUguiTheme.RequireSprite("UI/Ugui/SceneSelectV1/Fidelity20261016/row_selected")')
   .replace('GameplayUiArt.Load("tab_normal")','QdaoUguiTheme.RequireSprite("UI/Ugui/SceneSelectV1/Fidelity20261016/row_normal")');
  code=code.replace('Assert.That(third.x, Is.EqualTo(first.x));\n            Assert.That(third.y, Is.LessThan(first.y), "界面坐标 y 向下为负");',
   'Assert.That(third.x, Is.GreaterThan(second.x));\n            Assert.That(third.y, Is.EqualTo(first.y));\n            Vector2 fourth=Position(LineName(4));\n            Assert.That(fourth.x, Is.EqualTo(first.x));\n            Assert.That(fourth.y, Is.LessThan(first.y), "界面坐标 y 向下为负");\n            Assert.That(SceneChannelWindow.Columns, Is.EqualTo(3));\n            Assert.That(SceneChannelWindow.LinesPerPage, Is.EqualTo(24));');
  code=code.replace('两列:1线 左上,2线 在它右边同一行,3线 回到左边下一行。','三列:1/2/3线从左向右,4线回到左边下一行。');
 }
 const file=path.join(out,'integration',name);fs.writeFileSync(file,code);
 fs.writeFileSync(path.join(out,'presentation-tests-patch-install-manifest.json'),JSON.stringify({status:'ready-for-install',checkedAtUtc:new Date().toISOString(),clientModified:false,sourceGuard:{source,sha256:hash(source)},
  scope:name==='AttributePanelDisplayTests.cs'?'Only approved readable delta color; +1 and +15 numeric semantics unchanged.':'Only selected/normal same-source sprite and three-column geometry; capacity24, order, restrictions and all transactions preserved.',
  files:[{source:'integration/'+name,destination:'Assets/Tests/EditMode/'+relative,sha256:hash(file)}]},null,2)+'\n');
}
console.log('Independent attribute and scene presentation test patches staged.');
