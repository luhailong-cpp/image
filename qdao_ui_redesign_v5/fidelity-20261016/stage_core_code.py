from pathlib import Path
import re,json,hashlib,shutil
ROOT=Path(__file__).resolve().parent
CLIENT=Path('E:/work/mmorpg-client')
OUT=ROOT/'client/Assets/Scripts/UI/Ugui'
OUT.mkdir(parents=True,exist_ok=True)
guards=[]
def stage(relative,text):
 source=CLIENT/relative;dest=ROOT/'client'/relative;dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(text,encoding='utf-8');shutil.copyfile(source.with_name(source.name+'.meta'),dest.with_name(dest.name+'.meta'))
 guards.append({'target':relative,'sha256Before':hashlib.sha256(source.read_bytes()).hexdigest()})
def method(text,start,end,replace):
 a=text.index(start);b=text.index(end,a);return text[:a]+replace+text[b:]
helper=r'''using TMPro;
using UnityEngine;
using UnityEngine.UI;
namespace MmorpgClient.UI.Ugui
{
    internal static class QdaoCoreFidelityArt
    {
        public const string Root = "UI/Ugui/CoreFidelity20261016/";
        public static readonly Color Ink = QdaoUguiTheme.Html("#244C3E"), Ivory = QdaoUguiTheme.Html("#FFF3D3");
        public static Sprite Load(string key)
        {
            string alias = key switch {
                "server_card_wide_normal" => "server_card_normal", "server_card_wide_selected" => "server_card_selected",
                "server_card_wide_disabled" => "server_card_disabled", "list_row_normal" => "server_category_normal",
                "list_row_selected" => "server_category_selected", "list_row_disabled" => "server_category_normal",
                "search_normal" => "server_search", "tab_normal" => "server_back", "tab_selected" => "server_category_selected",
                "primary_button_normal" => "server_enter", "primary_button_selected" => "server_enter", _ => key };
            return Resources.Load<Sprite>(Root + alias) ?? QdaoRefreshArt.Load(key);
        }
        public static void Skin(Image image, string key)
        {
            if (image == null) return;
            image.sprite = Load(key); image.color = Color.white;
            image.type = image.sprite.border.sqrMagnitude > 0 ? Image.Type.Sliced : Image.Type.Simple;
            image.preserveAspect = false;
            image.pixelsPerUnitMultiplier = Mathf.Max(.01f, image.sprite.rect.height / Mathf.Max(1, image.rectTransform.rect.height));
        }
        public static Image Panel(string name, UnityEngine.Transform parent, float x, float y, float w, float h, string key = "content_panel")
        { var image = QdaoUguiFactory.CreateImage(name,parent,x,y,w,h,Load(key)); Skin(image,key); return image; }
        public static Button Button(string name, UnityEngine.Transform parent,float x,float y,float w,float h,string key,out Image image)
        {
            var button=QdaoUguiFactory.CreateArtButton(name,parent,x,y,w,h,Load(key),out image);Skin(image,key);
            button.navigation=new Navigation { mode=Navigation.Mode.Automatic };
            var colors=button.colors;colors.highlightedColor=new Color(1,.97f,.84f);colors.selectedColor=colors.highlightedColor;button.colors=colors;
            return button;
        }
        public static void ApplyText(TMP_Text text) { if(text!=null){text.font=QdaoUguiTheme.ResolveFont();text.richText=false;} }
        public static Sprite LoadCharacterPortrait(string id)
        {
            // Same-identity standalone portrait only. Unknown ids still remain unknown;
            // this UI path does not approve or activate any animation package.
            return id == "04_mountain_guardian_boy" ? Resources.Load<Sprite>(Root + "portraits/04_mountain_guardian_boy") : null;
        }
    }
    internal static class RoleFidelityArt
    {
        private static string Key(string key) => key switch {
            "server_card_medium_normal" => "role_card_normal", "server_card_medium_selected" => "role_card_selected",
            "list_row_normal" => "role_card_normal", "list_row_selected" => "role_card_selected",
            "primary_button_normal" => "role_enter", "primary_button_selected" => "role_enter",
            "tab_normal" => "role_back", _ => key };
        public static Sprite Load(string key) => QdaoCoreFidelityArt.Load(Key(key));
        public static void Skin(Image image,string key) => QdaoCoreFidelityArt.Skin(image,Key(key));
        public static Image Panel(string name,UnityEngine.Transform parent,float x,float y,float w,float h,string key="content_panel")
            => QdaoCoreFidelityArt.Panel(name,parent,x,y,w,h,Key(key));
        public static Button Button(string name,UnityEngine.Transform parent,float x,float y,float w,float h,string key,out Image image)
            => QdaoCoreFidelityArt.Button(name,parent,x,y,w,h,Key(key),out image);
    }
}
'''
(OUT/'QdaoCoreFidelityArt.cs').write_text(helper,encoding='utf-8')
guid=hashlib.sha256(b'core-fidelity-20261016/QdaoCoreFidelityArt.cs').hexdigest()[:32]
(OUT/'QdaoCoreFidelityArt.cs.meta').write_text('fileFormatVersion: 2\nguid: '+guid+'\n',encoding='utf-8')
relative='Assets/Scripts/UI/Ugui/QdaoServerSelectView.Visuals.cs'
s=(CLIENT/relative).read_text(encoding='utf-8-sig')
s=s.replace('QdaoRefreshArt','QdaoCoreFidelityArt')
for role in ['Default','Heading','Button','Body']:s=s.replace('QdaoUguiTypography.Apply'+role,'QdaoCoreFidelityArt.ApplyText')
s=s.replace('''            _screenArtSprite = Resources.Load<Sprite>(QdaoCoreFidelityArt.Root + "login_background");
            if (_screenArtSprite == null) _screenArtSprite = QdaoCoreFidelityArt.Load("sanctuary_background");''','''            _screenArtSprite = QdaoCoreFidelityArt.Load("login_shell");''',1)
landing=r'''        private void BuildLandingPage()
        {
            // Immutable original logo, boy and landscape are in the cleaned shell;
            // real server data and every action remain separate native controls.
            _landingServers = ArtButton("SelectServer", _landingRoot, 230f, 548f, 810f, 100f,
                "选择服务器", "login_server_bar", out _landingServerText);
            _landingServerText.rectTransform.anchoredPosition = new Vector2(62f,0);
            _landingServerText.rectTransform.sizeDelta = new Vector2(300,100);
            _landingServerText.alignment=TextAlignmentOptions.MidlineLeft;_landingServerText.fontSize=38;
            _landingServerDot=QdaoUguiFactory.CreateImage("CurrentServerDot",_landingServers.transform,367,40,20,20,_statusDotSprite);
            _landingAvailability=Label("CurrentServerAvailability",_landingServers.transform,403,0,150,100,"",34);
            var choose=QdaoCoreFidelityArt.Panel("ChooseServerAction",_landingServers.transform,573,13,211,74,"login_choose");
            Label("ChooseServerActionText",choose.transform,17,0,177,74,"选择服务器",28,true,TextAlignmentOptions.Center);
            _landingEnter=ArtButton("EnterGame",_landingRoot,272,676,733,167,"进入游戏","login_enter",out var enterLabel);
            enterLabel.fontSize=80;enterLabel.color=QdaoCoreFidelityArt.Ivory;
            _landingAccount=QdaoUguiFactory.CreateHitButton("SwitchAccount",_landingRoot,467,856,340,80);
            _landingAccount.navigation=new Navigation{mode=Navigation.Mode.Automatic};
            Label("SwitchAccountText",_landingAccount.transform,0,0,340,80,"切换账号",39,false,TextAlignmentOptions.Center);
            _landingStatusText=Label("LoginStatus",_landingRoot,185,965,860,48,"",30,false,TextAlignmentOptions.Center);
        }
'''
s=method(s,'        private void BuildLandingPage()','        private void BuildServerPage()',landing)
start=s.index('            QdaoCoreFidelityArt.Panel("ServerFrame"')
end=s.index('            _searchInput =',start)
s=s[:start]+'''            var serverTitle = Label("ServerTitle", _serverRoot, 397,236,1040,65,"选择服务器",44,true);
'''+s[end:]
replacements={
'1762f, 149f, 384f, 74f':'371f, 349f, 334f, 66f',
'float width = auxiliary ? 152f : 320f;':'float width = auxiliary ? 160f : 334f;',
'float height = auxiliary ? 76f : 112f;':'float height = auxiliary ? 50f : 70f;',
'float x = auxiliary ? 490f + (i - 4) * 164f : 484f;':'float x = auxiliary ? 371f + (i - 4) * 174f : 371f;',
'float y = auxiliary ? 816f : 246f + i * 138f;':'float y = auxiliary ? 842f : 449f + i * 104.8f;',
'auxiliary ? 25f : 34f':'auxiliary ? 23f : 31f',
'float x = 830f + (i % 2) * 678f, y = 244f + (i / 2) * 159f;':'float x = 768f + (i % 2) * 716f, y = 352f + (i / 2) * 130f;',
'x, y, 650f, 148f':'x, y, 640f, 106f',
'38f, 24f, 102f, 102f':'532f, 6f, 94f, 94f',
'164f, 24f, 277f, 74f, "", 40f':'56f, 7f, 405f, 51f, "", 38f',
'477f, 32f, 108f, 60f, "", 29f':'84f, 61f, 160f, 33f, "", 26f',
'443f, 54f, 23f, 23f':'57f, 70f, 17f, 17f',
'588f, 51f, 38f, 38f':'12f, 46f, 26f, 26f',
'8f, 4f, 97f, 46f':'439f, 6f, 86f, 34f',
'880f, 440f, 1220f, 200f':'830f, 460f, 1220f, 200f',
'830f, 881f, 104f, 62f':'768f, 850f, 72f, 40f',
'944f, 881f, 104f, 62f':'848f, 850f, 72f, 40f',
'1052f, 888f, 118f, 40f':'930f, 850f, 160f, 40f',
'515f, 908f, 300f, 103f':'1630f, 900f, 195f, 69f',
'850f, 985f, 570f, 35f':'1110f, 854f, 570f, 35f',
'1005f, 936f, 625f, 54f':'395f, 911f, 1100f, 45f',
'855f, 1025f, 1260f, 35f':'395f, 1002f, 1750f, 35f',
'1984f, 875f, 170f, 64f':'1980f, 850f, 170f, 42f',
'1670f, 927f, 495f, 115f':'1850f, 897f, 313f, 74f',
'_enterText.fontSize = 48f;':'_enterText.fontSize = 38f;',
}
for a,b in replacements.items():
 if a not in s:raise RuntimeError('Missing visual source '+a)
 s=s.replace(a,b,1)
s=s.replace('''        public void ShowLanding(bool show)
        {
''','''        public void ShowLanding(bool show)
        {
            if (_screenArtImage != null) _screenArtImage.sprite = QdaoCoreFidelityArt.Load(show ? "login_shell" : "server_shell");
''',1)
stage(relative,s)
relative='Assets/Scripts/UI/Ugui/QdaoServerSelectView.cs'
s=(CLIENT/relative).read_text(encoding='utf-8-sig')
s=s.replace('QdaoRefreshArt.Skin(', 'QdaoCoreFidelityArt.Skin(')
s=s.replace('QdaoUguiTypography.RefreshFont(', 'QdaoCoreFidelityArt.ApplyText(')
stage(relative,s)
relative='Assets/Scripts/UI/Ugui/Role/RoleFlowUi.cs'
s=(CLIENT/relative).read_text(encoding='utf-8-sig')
s=s.replace('QdaoRefreshArt','RoleFidelityArt')
for role in ['Default','Heading','Button','Body']:s=s.replace('QdaoUguiTypography.Apply'+role,'QdaoCoreFidelityArt.ApplyText')
start=s.index('            var scene = Resources.Load<Sprite>')
end=s.index('            BuildDetails();',start)
s=s[:start]+r'''            BattleUiWidgets.CreateStretchPanel("InputBlocker", _canvasGo.transform, QdaoUguiTheme.Letterbox);
            _designRoot = QdaoUguiFactory.CreateCenteredRect("RoleDesignRoot", _canvasGo.transform, 2560,1080);
            QdaoUguiFactory.CreateImage("RoleOriginalShell",_designRoot,0,0,2560,1080,RoleFidelityArt.Load("role_shell"));
            _hero=QdaoUguiFactory.CreateImage("CharacterArtwork",_designRoot,805,20,876,960,null);
            _hero.preserveAspect=true;
            _title=Label("Title",_designRoot,180,87,510,84,"选择角色",59,Ivory,TextAlignmentOptions.Center);
            _listHint=Label("ListHint",_designRoot,150,200,540,38,"",26,Wood,TextAlignmentOptions.Center);
'''+s[end:]
details=r'''        private void BuildDetails()
        {
            _classBadge=QdaoUguiFactory.CreateImage("ClassEmblem",_designRoot,2118,96,118,118,null);
            _classBadge.preserveAspect=true;_classBadge.enabled=false;
            _previewTitle=Label("PreviewTitle",_designRoot,1980,250,390,88,"",58,Ink,TextAlignmentOptions.Center);
            _classValue=Label("ClassValue",_designRoot,2070,343,170,48,"",31,Ivory,TextAlignmentOptions.Center);
            _genderValue=DetailRow("Gender","性别",430);
            _zoneValue=DetailRow("Zone","所属区服",502);
            _identityValue=DetailRow("Identity","角色编号",574,out _identityLabel);
            _directionValue=DetailRow("Direction","修行方向",646);
            _previewHint=Label("PreviewHint",_designRoot,1950,813,474,31,"",22,Wood,TextAlignmentOptions.Center);
        }
'''
s=method(s,'        private void BuildDetails()','        private TMP_Text DetailRow(',details)
s=s.replace('DetailRow("RoleName", "角色名", 736f','DetailRow("RoleName", "角色名", 718f',1)
s=s.replace('''        private static Sprite ResolvePortrait(uint classId, uint gender, string appearanceId = null)
            => QdaoCharacterCatalog.LoadPortrait(QdaoCharacterCatalog.ResolveRole(classId, gender, appearanceId));''','''        private static Sprite ResolvePortrait(uint classId, uint gender, string appearanceId = null)
        {
            string id=QdaoCharacterCatalog.ResolveRole(classId,gender,appearanceId);
            return QdaoCharacterCatalog.LoadPortrait(id) ?? QdaoCoreFidelityArt.LoadCharacterPortrait(id);
        }''',1)
s=s.replace('''            _appearanceDetails.text = appearance == null ? string.Empty :
                (appearance.IsHd ? "高清 · " : string.Empty) + $"8 个方向 · 每方向 {appearance.FrameCount} 帧";''','''            _appearanceDetails.text = appearance == null ? string.Empty : "选择喜欢的人物外观";''',1)
s=s.replace('792f, 128f, 300f','772f, 24f, 245f',1).replace('1610f, 128f, 300f','1625f, 24f, 245f',1)
s=s.replace('1096f, 128f, 510f, 126f','1028f, 24f, 580f, 88f',1)
s=s.replace('1100f, 148f, 500f, 56f','1040f, 28f, 556f, 45f',1).replace('1050f, 210f, 600f, 38f','1040f, 74f, 556f, 31f',1)
s=s.replace('string.Empty, 34f, Ink, TextAlignmentOptions.Center);\n            _appearanceDetails','string.Empty, 31f, Ink, TextAlignmentOptions.Center);\n            _appearanceDetails',1)
s=s.replace('string.Empty, 26f, Wood, TextAlignmentOptions.Center);\n            _createBackButton','string.Empty, 21f, Wood, TextAlignmentOptions.Center);\n            _createBackButton',1)
s=s.replace('''            previousAppearance.Button.onClick.AddListener(() => CycleAppearance(-1));''','''            previousAppearance.Rect.sizeDelta=new Vector2(245,88); previousAppearance.Label.rectTransform.sizeDelta=new Vector2(190,70);
            nextAppearance.Rect.sizeDelta=new Vector2(245,88); nextAppearance.Label.rectTransform.sizeDelta=new Vector2(190,70);
            previousAppearance.Button.onClick.AddListener(() => CycleAppearance(-1));''',1)
s=s.replace('''            _createBackButton.Button.onClick.AddListener(() =>''','''            _createBackButton.Rect.anchoredPosition=new Vector2(250,-954);_createBackButton.Rect.sizeDelta=new Vector2(367,105);
            _createBackButton.Button.onClick.AddListener(() =>''',1)
s=s.replace('''            _confirmCreateButton.Button.onClick.AddListener(ResolveCreate);''','''            _confirmCreateButton.Rect.anchoredPosition=new Vector2(1871,-851);_confirmCreateButton.Rect.sizeDelta=new Vector2(572,160);
            _confirmCreateButton.Label.rectTransform.sizeDelta=new Vector2(484,130);_confirmCreateButton.Label.fontSize=51;
            _confirmCreateButton.Button.onClick.AddListener(ResolveCreate);''',1)
s=s.replace('''            _enterButton.Rect.sizeDelta = new Vector2(570f, 146f);''','''            _enterButton.Rect.anchoredPosition=new Vector2(1871,-851);
            _enterButton.Rect.sizeDelta = new Vector2(572f, 160f);''',1)
s=s.replace('new Vector2(482f, 116f)','new Vector2(484f, 130f)',1)
stage(relative,s)
(ROOT/'staged-code-manifest.json').write_text(json.dumps({'guards':guards,'newSources':['Assets/Scripts/UI/Ugui/QdaoCoreFidelityArt.cs'],'modifiedPresentation':['login/server visual tree and native font/resource routing','role background/frames and placement','same-identity portrait fallback independent of full animation package'],'allLoginAndRoleTransactionsPreserved':True,'classAndAppearanceCatalogsUnmodified':True,'stageOnly':True,'nativeValidationPending':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'guards':guards,'stagedRuntimeSources':4},ensure_ascii=False))
