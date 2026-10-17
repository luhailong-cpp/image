from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent
CLIENT=Path("E:/work/mmorpg-client")
OUT=ROOT/"client/Assets/Scripts/UI/Ugui/Mail"
OUT.mkdir(parents=True,exist_ok=True)
source=CLIENT/"Assets/Scripts/UI/Ugui/Mail/MailWindow.cs"
s=source.read_text(encoding="utf-8-sig")
s=s.replace("using static MmorpgClient.UI.Ugui.Mail.MailUiArt;","using static MmorpgClient.UI.Ugui.Mail.MailFidelityArt;")
s=s.replace("private bool _disposed;","private bool _disposed;\n        private readonly TMP_Text _unreadCount, _inboxCount;")
constructor=r'''        public MailWindow(UnityEngine.Transform parent,MailUiState state=null)
        {
            State=state??new MailUiState();
            _root=QdaoUguiFactory.CreateStretch("MailWindow",parent,Vector4.zero);
            _root.gameObject.SetActive(false);
            var shade=_root.gameObject.AddComponent<Image>();shade.color=new Color(.03f,.10f,.075f,.65f);shade.raycastTarget=true;
            _root.gameObject.AddComponent<GameplayInputBlocker>();
            // All measurements below are native skin pixels. One uniform parent scale preserves the approved art.
            Frame=QdaoUguiFactory.CreateCenteredRect("MailFrame",_root,1932,814);
            float scale=Mathf.Min(2560f/1932f,1080f/814f);
            Frame.localScale=new UnityEngine.Vector3(scale,scale,1);
            _frameGroup=Frame.gameObject.AddComponent<CanvasGroup>();
            Art(Frame,"mail_empty_frame",0,0,1932,814);
            Label(Frame,"MailTitle","仙 笺",837,37,250,50,32,Cream,title:true,align:TextAlignmentOptions.Center);
            Label(Frame,"MailSubtitle","邮件",875,84,174,27,19,Cream,title:true,align:TextAlignmentOptions.Center);
            _close=Button(Frame,"CloseMail","",1691,48,78,69,Hide,key:"mail_close");
            string[] names={"全部","系统","活动","奖励"};
            float[] tabX={226,374,499,625};
            float[] tabW={147,124,125,128};
            for(int i=0;i<4;i++)
            {
                var category=(MailCategory)i;
                _tabs[i]=Button(Frame,"MailCategory_"+category,names[i],tabX[i],89,tabW[i],56,
                    ()=>{if(DialogIsOpen)return;_notice="";State.SetCategory(category);},
                    size:24,key:"mail_tab_normal");
                var label=_tabs[i].GetComponentInChildren<TMP_Text>();
                label.rectTransform.anchoredPosition=new Vector2(i==0?53:37,-5);
                label.rectTransform.sizeDelta=new Vector2(tabW[i]-(i==0?59:42),46);
                string[] icons={"mail_category_all","mail_category_system","mail_category_event","mail_category_reward"};
                Art(_tabs[i].transform,icons[i],i==0?17:12,12,30,32,true);
            }
            Label(Frame,"MailInboxGlyph","✉",237,157,32,33,24,Muted);
            _summary=Label(Frame,"MailSummary","未读",276,151,65,40,24,Ink);
            _unreadCount=Label(Frame,"MailUnreadCount","",337,151,52,40,26,QdaoUguiTheme.Html("#B33324"));
            _inboxCount=Label(Frame,"MailInboxCount","",553,153,176,36,23,Ink,align:TextAlignmentOptions.MidlineRight);
            ListScroll=Scroll(Frame,"MailListScroll",211,200,542,486,out _listContent);
            _all=Button(Frame,"MailClaimAll","一键领取",232,696,297,70,
                ()=>{if(DialogIsOpen)return;_notice="";State.ClaimAll();},true,27,key:"mail_button_all");
            SetCaptionArea(_all,110,175);
            _clean=Button(Frame,"MailClearRead","清理已读",542,698,191,66,ConfirmClean,size:24,key:"mail_button_clean");
            SetCaptionArea(_clean,54,130);
            _title=Label(Frame,"MailDetailTitle","",797,115,883,55,33,Ink,title:true);
            _meta=Label(Frame,"MailDetailMeta","",798,169,660,37,20,Ink);
            _status=Label(Frame,"MailDetailStatus","",1467,174,241,31,17,Muted,align:TextAlignmentOptions.MidlineRight);
            BodyScroll=Scroll(Frame,"MailBodyScroll",783,205,938,354,out _bodyContent);
            _attachmentHeading=Label(Frame,"AttachmentHeading","随信附赠",1180,555,112,32,17,Muted,align:TextAlignmentOptions.Center);
            _expiry=Label(Frame,"MailExpiry","",838,729,306,41,22,Ink);
            var rewardScrollRoot=QdaoUguiFactory.CreateRect("MailRewardScroll",Frame,813,585,830,122);
            rewardScrollRoot.gameObject.AddComponent<Image>().color=new Color(1,1,1,.001f);
            RewardScroll=rewardScrollRoot.gameObject.AddComponent<ScrollRect>();
            RewardScroll.horizontal=true;RewardScroll.vertical=false;
            RewardScroll.movementType=ScrollRect.MovementType.Clamped;RewardScroll.scrollSensitivity=42;
            var viewport=QdaoUguiFactory.CreateRect("Viewport",rewardScrollRoot,0,0,830,122);
            viewport.gameObject.AddComponent<RectMask2D>();
            _rewards=QdaoUguiFactory.CreateRect("MailRewards",viewport,0,0,830,122);
            RewardScroll.content=_rewards;RewardScroll.viewport=viewport;
            _event=Button(Frame,"MailOpenActivity","前往活动",1156,716,168,56,OpenActivity,size:23,key:"mail_button_event");
            _claim=Button(Frame,"MailClaimSelected","领取附件",1326,709,234,66,
                ()=>{if(DialogIsOpen)return;_notice="";State.ClaimSelected();},true,27,key:"mail_button_claim");
            _delete=Button(Frame,"MailDelete","删除",1560,716,154,56,ConfirmDelete,size:23,key:"mail_button_delete");
            SetCaptionArea(_delete,50,96);
            _footer=Label(Frame,"MailFooter","",795,773,917,25,14,Muted);
            _refresh=Button(Frame,"MailRefresh","刷新",665,156,66,31,
                ()=>{if(!DialogIsOpen)State.Refresh();},size:17,key:"mail_tab_normal");
            State.Changed+=Changed;
        }
        private static void SetCaptionArea(Button button,float left,float width)
        {
            var text=button.GetComponentInChildren<TMP_Text>();
            text.rectTransform.anchoredPosition=new Vector2(left,-4);
            text.rectTransform.sizeDelta=new Vector2(width,button.GetComponent<RectTransform>().rect.height-8);
        }

'''
start=s.index("        public MailWindow(");end=s.index("        public void Show()",start)
s=s[:start]+constructor+s[end:]
render=r'''        private void Render()
        {
            float listPosition=ListScroll.verticalNormalizedPosition;
            float bodyPosition=BodyScroll.verticalNormalizedPosition;
            float rewardPosition=RewardScroll.horizontalNormalizedPosition;
            var focused=EventSystem.current?.currentSelectedGameObject;
            string restore=focused!=null&&focused.transform.IsChildOf(_listContent)?focused.name:null;
            Clear(_listContent);Clear(_bodyContent);Clear(_rewards);
            foreach(var tab in _tabs)
            {
                bool active=tab.name=="MailCategory_"+State.Category;
                tab.image.sprite=Load(active?"mail_tab_selected":"mail_tab_normal");
                var text=tab.GetComponentInChildren<TMP_Text>();if(text!=null)text.color=active?Cream:Ink;
                var allGlyph=tab.transform.Find("mail_category_all");
                if(allGlyph!=null)allGlyph.gameObject.SetActive(active);
            }
            _summary.text="未读";_unreadCount.text=State.UnreadCount.ToString();
            _inboxCount.text="邮件 "+State.Messages.Count;
            var messages=State.VisibleMessages;
            _listContent.sizeDelta=new Vector2(_listContent.sizeDelta.x,Mathf.Max(486,messages.Count*80));
            for(int i=0;i<messages.Count;i++)RenderRow(messages[i],i);
            if(messages.Count==0)
                Label(_listContent,"MailListEmpty","暂无邮件",30,202,470,55,24,Muted,align:TextAlignmentOptions.Center);
            var mail=State.Selected;
            bool changed=mail?.Id!=_renderedId;_renderedId=mail?.Id;
            _title.text=mail?.Title??"云中无新笺";
            _meta.text=mail==null?"":$"寄件人：{mail.Sender}    {Date(mail.SentAt)}";
            _status.text=mail==null?"":Status(mail);
            _expiry.text=mail==null?"":Expiry(mail);
            _claim.gameObject.SetActive(mail?.Rewards.Count>0);
            _claim.interactable=State.CanClaimSelected;
            SetLabel(_claim,mail==null?"领取附件":State.IsExpired(mail)?"已过期":mail.Claimed?"✓ 已领取":"领取附件");
            _event.gameObject.SetActive(mail!=null&&!string.IsNullOrEmpty(mail.ActivityId));
            _event.interactable=mail!=null&&!State.IsExpired(mail)&&(State.IsDemo||ActivityRequested!=null);
            _delete.gameObject.SetActive(mail!=null);
            _delete.interactable=State.CanAct&&mail!=null;
            _all.interactable=State.CanAct&&State.ClaimableCount>0;
            _clean.interactable=State.CanAct&&State.CleanableCount>0;
            _refresh.gameObject.SetActive(!State.IsDemo);_refresh.interactable=State.CanRefresh;
            // Capacity is not exposed by MailUiState; never invent the original art's example "6/50".
            _inboxCount.rectTransform.anchoredPosition=new Vector2(553,-153);
            if(_refresh.gameObject.activeSelf)_inboxCount.rectTransform.sizeDelta=new Vector2(100,36);
            else _inboxCount.rectTransform.sizeDelta=new Vector2(176,36);
            _attachmentHeading.text=mail?.Rewards.Count>7?"随信附赠 · 左右滑动":mail?.Rewards.Count>0?"随信附赠":"仙笺寄语";
            if(mail!=null){RenderBody(mail);RenderRewards(mail);}
            else
            {
                Label(_bodyContent,"MailUnavailableTitle",State.ServiceAvailable||State.IsDemo?"仙笺已整理妥当":"邮件暂未开放",
                    50,105,800,65,32,Ink,title:true,align:TextAlignmentOptions.Center);
                Label(_bodyContent,"MailUnavailableHint",State.ServiceAvailable||State.IsDemo?"道友，暂时没有需要查收的邮件。":"请稍后再来查收仙笺。",
                    50,184,800,54,22,Muted,align:TextAlignmentOptions.Center);
                _bodyContent.sizeDelta=new Vector2(_bodyContent.sizeDelta.x,354);
            }
            _footer.text=!string.IsNullOrEmpty(_notice)?_notice:!string.IsNullOrEmpty(State.Status)?State.Status:"阅读不会领取附件，记得在有效期内查收。";
            ListScroll.verticalNormalizedPosition=listPosition;
            BodyScroll.verticalNormalizedPosition=changed?1:bodyPosition;
            RewardScroll.horizontalNormalizedPosition=changed?0:rewardPosition;
            if(restore!=null&&!DialogIsOpen&&EventSystem.current!=null)
            {
                var next=_listContent.GetComponentsInChildren<Button>().FirstOrDefault(b=>b.name==restore);
                EventSystem.current.SetSelectedGameObject(next!=null?next.gameObject:_close.gameObject);
            }
            else if(focused!=null&&!DialogIsOpen&&focused.transform.IsChildOf(Frame)&&
                (!focused.activeInHierarchy||focused.GetComponent<Button>()?.interactable==false)&&EventSystem.current!=null)
                EventSystem.current.SetSelectedGameObject(_close.gameObject);
        }
        private void RenderRow(MailMessage mail,int index)
        {
            bool selected=mail.Id==State.SelectedId;
            var row=Button(_listContent,"MailRow_"+mail.Id,"",0,index*80,538,80,
                ()=>{if(DialogIsOpen)return;_notice="";State.Select(mail.Id);},
                key:selected?"mail_row_selected":"mail_row_normal");
            Art(row.transform,mail.IsRead?"mail_envelope_read":"mail_envelope_unread",28,9,88,66,true);
            if(!mail.IsRead)
            {
                var dot=QdaoUguiFactory.CreateImage("UnreadDot",row.transform,100,10,14,14,
                    QdaoUguiTheme.LoadSprite(QdaoUguiTheme.StatusDotSpritePath));
                dot.color=QdaoUguiTheme.Html("#C63229");
            }
            Label(row.transform,"MailRowTitle",mail.Title,128,7,354,39,22,Ink,title:true);
            Label(row.transform,"MailRowMeta",Date(mail.SentAt,true),129,46,113,29,17,Muted);
            Label(row.transform,"MailRowState",Status(mail),250,46,260,29,17,
                State.HasValidAttachments(mail)?QdaoUguiTheme.Html("#A04428"):Muted,
                align:TextAlignmentOptions.MidlineRight);
            if(mail.Rewards.Count>0)Art(row.transform,"mail_gift",488,10,28,30,true);
        }
        private void RenderBody(MailMessage mail)
        {
            float top=0;
            if(!string.IsNullOrEmpty(mail.BannerKey)&&Load(mail.BannerKey)!=null)
            {
                bool approvedOriginal=mail.BannerKey=="event-midautumn";
                var sprite=Load(approvedOriginal?"mail_banner":mail.BannerKey);
                var crop=QdaoUguiFactory.CreateRect("MailEventBanner",_bodyContent,0,0,933,267);
                crop.gameObject.AddComponent<RectMask2D>();
                QdaoUguiFactory.CreateAspectFillImage("ActivityArtwork",crop,sprite,sprite.rect.width/sprite.rect.height);
                Label(crop,"MailEventTitle",mail.Title,32,65,520,132,43,Cream,true,true);
                top=278;
            }
            var body=Label(_bodyContent,"MailBodyText",mail.Body,14,top,887,70,21,Ink,true,align:TextAlignmentOptions.TopLeft);
            body.margin=Vector4.zero;body.ForceMeshUpdate();
            float height=body.GetPreferredValues(mail.Body,887,float.PositiveInfinity).y+22;
            body.rectTransform.sizeDelta=new Vector2(887,Mathf.Max(70,height));
            _bodyContent.sizeDelta=new Vector2(_bodyContent.sizeDelta.x,Mathf.Max(354,top+height+12));
        }
        private void RenderRewards(MailMessage mail)
        {
            const float step=145;
            float required=mail.Rewards.Count*step;
            _rewards.sizeDelta=new Vector2(Mathf.Max(830,required),122);
            if(mail.Rewards.Count==0)
            {
                Label(_rewards,"MailNoAttachments","这是一封通知邮件，没有附件。",20,24,790,54,21,Muted,align:TextAlignmentOptions.Center);
                return;
            }
            float start=required<=830?(830-required)*.5f:0;
            for(int i=0;i<mail.Rewards.Count;i++)
            {
                var r=mail.Rewards[i];float x=start+i*step;
                Art(_rewards,"mail_reward_slot",x+13,0,116,98);
                var icon=Art(_rewards,r.IconKey,x+22,7,98,85,true);
                if(State.IsExpired(mail))icon.color=new Color(.68f,.68f,.65f,.75f);
                Label(_rewards,"RewardName_"+i,r.Name+" ×"+r.Count,x-2,97,147,25,17,Ink,align:TextAlignmentOptions.Center);
                if(mail.Claimed)Label(_rewards,"RewardClaimed_"+i,"✓",x+12,-4,34,34,23,Jade);
            }
        }
'''
start=s.index("        private void Render()");end=s.index("        private string Status(",start)
s=s[:start]+render+s[end:]
(OUT/"MailWindow.cs").write_text(s,encoding="utf-8")
art=(CLIENT/"Assets/Scripts/UI/Ugui/Mail/MailUiArt.cs").read_text(encoding="utf-8-sig")
art=art.replace("public static class MailUiArt","internal static class MailFidelityArt")
art=art.replace('public const string Root = "UI/Ugui/MailV1/";','public const string Root = "UI/Ugui/MailV1Fidelity/";')
start=art.index("        private static TMP_FontAsset _body;")
end=art.index("        public static Sprite Load",start)
art=art[:start]+'        public static TMP_FontAsset BodyFont => QdaoUguiTheme.ResolveFont();\n'+art[end:]
art=art.replace("return Resources.Load<Sprite>(Root + key);","return Resources.Load<Sprite>(Root + key) ?? MailUiArt.Load(key);")
art=art.replace('outer,0,0,w-18,h','outer,0,0,w,h').replace('viewport,0,0,w-22,h','viewport,0,0,w,h').replace('outer,w-12,0,9,h','outer,w-3,0,3,h')
(OUT/"MailFidelityArt.cs").write_text(art,encoding="utf-8")
for name in ("MailWindow","MailFidelityArt"):
 guid=hashlib.sha256(("mail-fidelity-source-20261016/"+name).encode()).hexdigest()[:32]
 if name=="MailWindow":
  old=source.with_name(source.name+".meta")
  if old.exists():
   (OUT/(name+".cs.meta")).write_bytes(old.read_bytes());continue
 (OUT/(name+".cs.meta")).write_text(f"fileFormatVersion: 2\nguid: {guid}\n",encoding="utf-8")
manifest={"source":"E:/work/mmorpg-client/Assets/Scripts/UI/Ugui/Mail/MailWindow.cs","sourceSha256Before":hashlib.sha256(source.read_bytes()).hexdigest(),"replacement":"client/Assets/Scripts/UI/Ugui/Mail/MailWindow.cs","newFiles":["client/Assets/Scripts/UI/Ugui/Mail/MailFidelityArt.cs"],"businessMethodsPreservedVerbatim":["Show","Hide","Back","ResetSession","Tick","ConfirmDelete","ConfirmClean","OpenActivity","ShowDialog","CloseDialog","Dispose"],"dataModelUnchanged":"MailUiState","stageOnly":True,"nativeParityVerified":False}
(ROOT/"staged-code-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"stagedRuntimeSources":2,"stage":str(OUT)}))

