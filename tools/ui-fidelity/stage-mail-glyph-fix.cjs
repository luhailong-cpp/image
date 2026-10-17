const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const client='E:/work/mmorpg-client',root='E:/work/image/docs/ui-fidelity-20261016/mail-glyph-fix';
const rel='Assets/Scripts/UI/Ugui/Mail/MailWindow.cs',before=fs.readFileSync(path.join(client,rel));let source=before.toString();
for(const [from,to]of[
 ['Label(Frame,"MailInboxGlyph","✉",237,157,32,33,24,Muted);','Art(Frame,"mail_envelope_read",237,163,32,25,true).name="MailInboxGlyph";'],
 ['if(mail.Claimed)Label(_rewards,"RewardClaimed_"+i,"✓",x+12,-4,34,34,23,Jade);','if(mail.Claimed)Art(_rewards,"mail_category_all",x+12,-4,34,34,true).name="RewardClaimed_"+i;']
]){if(!source.includes(from))throw Error('Expected exact source fragment missing');source=source.replace(from,to);}
source=source.replaceAll('"✓ 已领取"','"已领取"');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');fs.mkdirSync(root,{recursive:true});fs.writeFileSync(path.join(root,'MailWindow.cs'),source);
fs.writeFileSync(path.join(root,'install-manifest.json'),JSON.stringify({files:[{source:'MailWindow.cs',target:rel,sha256:sha(source),expected_target_sha256:sha(before)}],scope:'Replace unsupported envelope/check text glyphs with already approved same-source native sprite icons. Claim/read/delete state and all business methods remain unchanged.'},null,2));
console.log('MAIL_GLYPH_FIX_STAGED');
