const fs=require('fs'),crypto=require('crypto');
const root=__dirname,client='E:/work/mmorpg-client',dest='Assets/Scripts/UI/Ugui/Guild/GuildWindow.cs',source=client+'/'+dest;
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
let code=fs.readFileSync(source,'utf8').replaceAll('\r\n','\n');
const before=`            var upgradeFundsText = FidelityLabel(_rail, "GuildUpgradeFundsValue", info.UpgradeCostFunds == 0 ? "已满级" :
                GuildClient.FormatAmount(info.Funds) + " / " + GuildClient.FormatAmount(info.UpgradeCostFunds), 149, 343, 365, 27, 17,
                Cream, align: TextAlignmentOptions.Center);
            Battle.BattleUiWidgets.ApplyOutline(upgradeFundsText, .12f, new Color32(41, 79, 65, 255));`;
const after=`            var upgradeFundsText = FidelityLabel(_rail, "GuildUpgradeFundsValue", info.UpgradeCostFunds == 0 ? "已满级" :
                GuildClient.FormatAmount(info.Funds) + " / " + GuildClient.FormatAmount(info.UpgradeCostFunds), 149, 343, 365, 27, 17,
                Ink, align: TextAlignmentOptions.Center);
            if (ratio > 0)
            {
                // Keep identical full text geometry; only the actual green fill reveals ivory glyphs.
                var filledClip = QdaoUguiFactory.CreateRect("GuildUpgradeFundsFilledClip", _rail, 147, 346, (float)(368 * ratio), 21);
                filledClip.gameObject.AddComponent<RectMask2D>();
                var filledText = FidelityLabel(filledClip, "GuildUpgradeFundsFilledValue", upgradeFundsText.text,
                    2, -3, 365, 27, 17, Cream, align: TextAlignmentOptions.Center);
                filledText.font = upgradeFundsText.font;
                filledText.fontStyle = upgradeFundsText.fontStyle;
            }`;
if(!code.includes(before))throw Error('Current installed funds-outline block drifted');code=code.replace(before,after);
fs.mkdirSync(root+'/progress-dual-text-patch',{recursive:true});fs.writeFileSync(root+'/progress-dual-text-patch/GuildWindow.cs',code);
const manifest={status:'frozen-ready-for-install',checkedAtUtc:new Date().toISOString(),guards:[{source,sha256:hash(source)}],files:[{source:'progress-dual-text-patch/GuildWindow.cs',destination:dest,sha256:hash(root+'/progress-dual-text-patch/GuildWindow.cs')}],scope:'Only replace outline-dependent funds caption with real progress-width clipped twin text. Base GuildUpgradeFundsValue remains unique and Ink. Identical full text rect and font in ivory is clipped to actual fill147,346,368*ratio,21. Exact funds values and existing ratio retained. No event/permission/state change.',clientModified:false,unityLaunched:false};
fs.writeFileSync(root+'/progress-dual-text-patch-install-manifest.json',JSON.stringify(manifest,null,2)+'\n');
const rsp=fs.readFileSync(root+'/qa/readability-patch/height-only.rsp','utf8').split(/\r?\n/).filter(x=>x&&!x.startsWith('-out:')&&!/\.cs"$/.test(x));rsp.push('-out:"'+root+'/qa/readability-patch/GuildReadability.DualText.dll"','"'+root+'/progress-dual-text-patch/GuildWindow.cs"','"'+client+'/Assets/Scripts/UI/Ugui/Guild/GuildUiArt.cs"');fs.writeFileSync(root+'/qa/readability-patch/dual-text-only.rsp',rsp.join('\n'));
console.log(JSON.stringify(manifest,null,2));
