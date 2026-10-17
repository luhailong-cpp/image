const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=__dirname,source='E:/work/mmorpg-client/Assets/Tests/EditMode/Tianyong/SceneChannelWindowTests.cs';
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
let code=fs.readFileSync(source,'utf8').replaceAll('\r\n','\n');
const a=code.indexOf('        public void MoreThanSixteenLines_'),b=code.indexOf('        // ── 状态行',a);
if(a<0||b<0)throw Error('Pagination region missing');
const region=code.slice(a,b).replaceAll('MoreThanSixteenLines','MoreThanTwentyFourLines').replaceAll('ManyLines(20','ManyLines(28')
 .replaceAll('LinesPerPage, Is.EqualTo(16)','LinesPerPage, Is.EqualTo(24)').replaceAll('Names(1, 16)','Names(1, 24)').replaceAll('Names(17, 20)','Names(25, 28)')
 .replaceAll('LineName(17)','LineName(25)').replaceAll('ManyLines(16)','ManyLines(24)').replaceAll('ManyLines(17)','ManyLines(25)').replaceAll('current: 18','current: 26')
 .replace('恰好十六条仍是一页,十七条才有第二页','恰好二十四条仍是一页,二十五条才有第二页');
code=code.slice(0,a)+region+code.slice(b);
const name='SceneChannelWindowTests.cs';fs.writeFileSync(path.join(root,'integration',name),code);
fs.writeFileSync(path.join(root,'pagination-tests-patch-install-manifest.json'),JSON.stringify({status:'ready-for-install',checkedAtUtc:new Date().toISOString(),clientModified:false,unityLaunched:false,
 sourceGuard:{source,sha256:hash(source)},scope:'Only the two pagination fixtures and their expected 24/25/28 boundary values; all permission/cooldown/pending/network assertions unchanged.',
 files:[{source:'integration/'+name,destination:'Assets/Tests/EditMode/Tianyong/'+name,sha256:hash(path.join(root,'integration',name))}]},null,2)+'\n');
console.log('Two pagination fixtures staged for 24-slot pages; all other tests unchanged.');
