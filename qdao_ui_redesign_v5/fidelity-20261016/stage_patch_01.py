from pathlib import Path
import json,hashlib,re
ROOT=Path(__file__).resolve().parent
CLIENT=Path('E:/work/mmorpg-client')
PATCH=ROOT/'patch-01'
base='Assets/Scripts/UI/Ugui/'
paths=[base+'QdaoCoreFidelityArt.cs',base+'QdaoServerSelectView.Visuals.cs',base+'Role/RoleFlowUi.cs']
original={p:(CLIENT/p).read_text(encoding='utf-8-sig') for p in paths}
text=original.copy()
p=paths[0];s=text[p]
s=s.replace('            string alias = key switch {','''            // Existing approved transparent controls prevent a cropped scenery rectangle
            // around new utility actions that live over the sky or inside a dialog.
            if (key == "clean_tab") return QdaoRefreshArt.Load("tab_normal");
            if (key == "clean_search") return QdaoRefreshArt.Load("search_normal");
            if (key == "clean_primary") return QdaoRefreshArt.Load("primary_button_normal");
            string alias = key switch {''',1)
old='        public static void ApplyText(TMP_Text text) { if(text!=null){text.font=QdaoUguiTheme.ResolveFont();text.richText=false;} }'
new='''        public static void ApplyText(TMP_Text text)
        {
            if (text == null) return;
            text.richText = false;
            bool server = false;
            for (var parent = text.transform.parent; parent != null; parent = parent.parent)
                if (parent.name == "ServerPage") { server = true; break; }
            if (server)
            {
                QdaoUguiTypography.ApplyBody(text);
                if (text.name.StartsWith("ServerName_") || text.name.StartsWith("CategoryText_") ||
                    text.name.StartsWith("TopTabText_") || text.name == "ServerTitle" ||
                    text.name.EndsWith("ButtonText") || text.name == "ServerRecommendedText")
                { text.fontStyle = FontStyles.Bold; text.fontWeight = FontWeight.Bold; }
                return;
            }
            text.font = QdaoUguiTheme.ResolveFont();
            string action = text.transform.parent != null ? text.transform.parent.name : string.Empty;
            if (text.name == "Title" || text.name == "EnterGameText" ||
                action == "EnterSanctuary" || action == "ConfirmCreate")
            {
                text.fontStyle = FontStyles.Bold; text.fontWeight = FontWeight.Bold;
                text.color = QdaoUguiTheme.Html("#E5CC80");
                text.outlineColor = QdaoUguiTheme.Html("#28412B"); text.outlineWidth = .10f;
            }
            else if (text.name == "Name" || text.name == "PreviewTitle")
            { text.fontStyle = FontStyles.Bold; text.fontWeight = FontWeight.Bold; }
        }'''
assert old in s;s=s.replace(old,new,1);text[p]=s
p=paths[1];s=text[p]
s=s.replace('enterLabel.fontSize=80;enterLabel.color=QdaoCoreFidelityArt.Ivory;','enterLabel.fontSize=80;QdaoCoreFidelityArt.ApplyText(enterLabel);',1)
needle='''                    439f, 6f, 86f, 34f, QdaoCoreFidelityArt.Load("recommend_badge"));'''
assert needle in s;s=s.replace(needle,needle+'''
                Label("ServerRecommendedText", _serverRecommendations[i].transform, 0f, 0f, 86f, 34f,
                    "推荐", 18f, false, TextAlignmentOptions.Center).color = QdaoUguiTheme.Html("#795725");''',1)
needle='''                _serverRecommendations[slot].enabled = zone.recommended;'''
assert needle in s;s=s.replace(needle,'''            {
                _serverRecommendations[slot].enabled = zone.recommended;
                var caption = _serverRecommendations[slot].GetComponentInChildren<TMP_Text>(true);
                if (caption != null) caption.gameObject.SetActive(zone.recommended);
            }''',1)
a=s.index('        private void BuildRefreshCredentialPanel()');b=s.index('        private static string CompactAvailability',a)
credential=s[a:b].replace('"search_normal"','"clean_search"').replace('"取消", "tab_normal"','"取消", "clean_tab"').replace('"登录", "primary_button_normal"','"登录", "clean_primary"')
credential=credential.replace('_credentialSubmitText.fontSize = 34f;','_credentialSubmitText.fontSize = 34f;\n            _credentialSubmitText.color = QdaoCoreFidelityArt.Ivory;',1)
s=s[:a]+credential+s[b:];text[p]=s
p=paths[2];s=text[p]
s=s.replace('primary ? "primary_button_normal" : "tab_normal", out button.Plate);','primary ? "primary_button_normal" : "clean_tab", out button.Plate);',1)
s=s.replace('_previewHint=Label("PreviewHint",_designRoot,1950,813,474,31,"",22,Wood,TextAlignmentOptions.Center);','''_previewHint=Label("PreviewHint",_designRoot,1950,784,450,34,"",22,Wood,TextAlignmentOptions.Center);
            _previewHint.enableAutoSizing=true;_previewHint.fontSizeMax=22;_previewHint.fontSizeMin=16;
            _previewHint.overflowMode=TextOverflowModes.Ellipsis;''',1)
s=s.replace('"RoleNameInput", _createRoot, 1940f, 724f, 330f, 84f,','"RoleNameInput", _createRoot, 1940f, 704f, 330f, 72f,',1)
a=s.index('        private void BuildNameEntry()');b=s.index('        private void RefreshNameHint()',a)
name=s[a:b].replace('RoleFidelityArt.Load("list_row_normal")','RoleFidelityArt.Load("clean_search")').replace('RoleFidelityArt.Skin(_nameInput.GetComponent<Image>(), "list_row_normal")','RoleFidelityArt.Skin(_nameInput.GetComponent<Image>(), "clean_search")')
name=name.replace('''            // 竖直中心与输入框对齐(724 + 84/2 = 710 + 112/2 = 766);文字区宽 150 − 88 = 62,放得下两个 26 号字
            var randomName = TextButton("RandomRoleName", _createRoot, 2276f, 710f, 150f, "随机", false, 26f);''','''            // Name input, random action and validation feedback stay inside the details frame.
            var randomName = TextButton("RandomRoleName", _createRoot, 2284f, 704f, 124f, "随机", false, 26f);
            randomName.Rect.sizeDelta = new Vector2(124f,72f);
            randomName.Label.rectTransform.anchoredPosition = new Vector2(12f,0f);
            randomName.Label.rectTransform.sizeDelta = new Vector2(100f,72f);''',1)
s=s[:a]+name+s[b:];text[p]=s
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[];guards=[]
for p in paths:
 assert text[p]!=original[p],p
 dest=PATCH/'client'/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text[p],encoding='utf-8')
 files.append({'source':'client/'+p,'target':p,'sha256':sha(dest)})
 guards.append({'target':p,'sha256Before':sha(CLIENT/p)})
manifest={'destinationRoot':str(CLIENT),'files':files,'guards':guards,'scope':'Native screenshot follow-up: native recommendation text, matching gold bold display text and server sans typography, alpha-clean utility/dialog sprites, contained creation name feedback. Only three presentation sources.','afterInstall':'Rebake production login/server prefab and capture core pages again.','newImages':False,'businessTransactionsModified':False}
(PATCH/'install-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
compile=(ROOT/'compile-staged-core.ps1').read_text(encoding='utf-8-sig')
compile=compile.replace('[string]$Phase="login-server"','[string]$Phase="patch-01"')
(PATCH/'compile-staged.ps1').write_text(compile,encoding='utf-8')
print(json.dumps(manifest,ensure_ascii=False))
