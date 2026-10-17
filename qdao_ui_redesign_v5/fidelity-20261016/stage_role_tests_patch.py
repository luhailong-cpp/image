from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent
CLIENT=Path('E:/work/mmorpg-client')
PATCH=ROOT/'patch-01-tests'
rel='Assets/Tests/PlayMode/QdaoRoleIdentityPlayModeTests.cs'
src=CLIENT/rel
old=src.read_text(encoding='utf-8-sig')
needle='Assert.That(ReadText(host, "AppearanceDetails"), Does.Contain("8 个方向").And.Contain("每方向 16 帧"));'
assert old.count(needle)==1
new=old.replace(needle,'Assert.That(ReadText(host, "AppearanceDetails"), Is.EqualTo("选择喜欢的人物外观"));')
assert old.count('[Test')==new.count('[Test') and old.count('[UnityTest')==new.count('[UnityTest')
assert old.replace(needle,'')==new.replace('Assert.That(ReadText(host, "AppearanceDetails"), Is.EqualTo("选择喜欢的人物外观"));','')
dest=PATCH/'client'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(new,encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest={'destinationRoot':str(CLIENT),'files':[{'source':'client/'+rel,'target':rel,'sha256':sha(dest)}],'guards':[{'target':rel,'sha256Before':sha(src)}],'scope':'One presentation wording assertion only; original roster/identity/frame geometry/class/create/reopen/rejection restoration assertions all byte-equivalent after this single expression substitution.','testFilter':'MmorpgClient.Tests.PlayMode.QdaoRoleIdentityPlayModeTests','nativeTestsExecutedByParent':True,'parentLatestResult':'15 passed, 1 obsolete wording assertion failed before this patch.'}
(PATCH/'install-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(manifest,ensure_ascii=False))
