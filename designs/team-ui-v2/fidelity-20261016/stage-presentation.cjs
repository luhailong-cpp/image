const fs=require('fs'),path=require('path');
const root=__dirname,dir=path.join(root,'integration');
let code=fs.readFileSync('E:/work/mmorpg-client/Assets/Scripts/UI/Ugui/Team/TeamWindow.cs','utf8');
function region(start,end,replacement){const a=code.indexOf(start),b=code.indexOf(end,a+start.length);if(a<0||b<0)throw Error('Missing region '+start);code=code.slice(0,a)+replacement+'\n\n'+code.slice(b);}
code=code.replace('private readonly TMP_Text _summary, _status, _memberCount, _applicationCount, _applicationTitle;',
  'private readonly TMP_Text _summary, _status, _memberCount, _applicationCount, _applicationTitle, _leaderState, _footerSync;');
region('        public TeamWindow(UnityEngine.Transform parent)','        public void SetState(TeamUiState state)',`        public TeamWindow(UnityEngine.Transform parent)
        {
            _root=QdaoUguiFactory.CreateStretch("TeamWindow",parent,Vector4.zero);
            _root.gameObject.SetActive(false);
            var shade=_root.gameObject.AddComponent<Image>();shade.color=new Color(.025f,.10f,.08f,.68f);shade.raycastTarget=true;
            _root.gameObject.AddComponent<GameplayInputBlocker>();
            // All main-panel measurements are original-art pixels, with one uniform display scale.
            var frame=QdaoUguiFactory.CreateCenteredRect("TeamFrame",_root,1931,814);
            frame.localScale=UnityEngine.Vector3.one*(2560f/1931f);
            _frameControls=frame.gameObject.AddComponent<CanvasGroup>();
            Art(frame,"team_skin",0,0,1931,814);
            _close=QdaoUguiFactory.CreateHitButton("CloseTeamWindow",frame,1747,32,86,86);
            _close.navigation=new Navigation{mode=Navigation.Mode.Automatic};_close.onClick.AddListener(Hide);
            _summary=Label(frame,"队伍信息尚未同步",1207,112,332,36,20,BodyInk);
            Art(frame,"badge_self",1545,110,159,44);
            _leaderState=Label(frame,"待同步",1553,110,143,44,24,Cream,TextAlignmentOptions.Center);
            _memberCount=Label(frame,"",913,162,134,34,25,BodyMuted,TextAlignmentOptions.MidlineRight);
            _applicationTitle=Text(frame,"申请列表",1185,165,186,49,35,Cream);
            var countDot=QdaoUguiFactory.CreateImage("ApplicationCountBadge",frame,1372,170,43,43,
                QdaoUguiTheme.RequireSprite(QdaoUguiTheme.StatusDotSpritePath));countDot.color=QdaoUguiTheme.Html("#BA4B3C");
            _applicationCount=Label(frame,"",1372,169,43,44,27,Cream,TextAlignmentOptions.Center);
            _members=QdaoUguiFactory.CreateRect("TeamMembers",frame,195,201,851,516);
            _applications=QdaoUguiFactory.CreateRect("TeamApplications",frame,1109,238,619,399);
            _memberPrevious=Control(frame,"上页",638,150,83,37,()=>MovePage(TeamPage.Members,-1),size:20);_memberPrevious.name="MemberPreviousPage";
            _memberPageLabel=Label(frame,"",724,150,85,37,20,BodyMuted,TextAlignmentOptions.Center);
            _memberNext=Control(frame,"下页",812,150,83,37,()=>MovePage(TeamPage.Members,1),size:20);_memberNext.name="MemberNextPage";
            _applicationPrevious=Control(frame,"上页",1529,178,66,37,()=>MovePage(TeamPage.Applications,-1),size:18);_applicationPrevious.name="ApplicationPreviousPage";
            _applicationPageLabel=Label(frame,"",1595,178,60,37,18,BodyMuted,TextAlignmentOptions.Center);
            _applicationNext=Control(frame,"下页",1656,178,66,37,()=>MovePage(TeamPage.Applications,1),size:18);_applicationNext.name="ApplicationNextPage";
            _status=Label(frame,"",1112,667,612,45,23,BodyMuted,TextAlignmentOptions.Center);
            _footerSync=Label(frame,"队伍信息待同步",288,734,258,43,23,BodyMuted);
            // Added gameplay actions retain fixed slots inside the original panel's footer.
            _startMatch=Control(frame,"开始战斗",568,733,166,44,ConfirmStartMatch,true,size:23);_startMatch.name="StartTeamMatch";
            _startMatchLabel=_startMatch.GetComponentInChildren<TMP_Text>(true);
            _invite=Control(frame,"邀请道友",741,733,166,44,PromptInvite,size:23);_invite.name="InviteToTeam";
            _disband=Control(frame,"解散队伍",914,733,166,44,ConfirmDisband,size:23);_disband.name="DisbandTeam";
            _create=Control(frame,"创建队伍",914,733,166,44,()=>{if(CanCreate)CreateRequested?.Invoke();},true,size:23);_create.name="CreateTeam";
            _leave=Control(frame,"离开队伍",1087,733,166,44,ConfirmLeave,size:23);_leave.name="LeaveTeam";
            _apply=Control(frame,"申请入队",1087,733,166,44,PromptApply,size:23);_apply.name="ApplyJoinTeam";
            _refresh=Control(frame,"刷新",1538,725,181,54,()=>{if(CanAct)RefreshRequested?.Invoke();},size:27);_refresh.name="RefreshTeam";
            _refreshLabel=_refresh.GetComponentInChildren<TMP_Text>(true);
            UpdateFooter(false,false,false);
        }`);
const summaryStart=code.indexOf('            _summary.text = hasTeam');
const summaryEnd=code.indexOf('            _applicationTitle.text',summaryStart);
code=code.slice(0,summaryStart)+`            _summary.text=hasTeam ? $"队伍人数 {members}/{capacity}   队伍编号 {data.TeamId}"
                : noTeam ? $"尚未入队 · 玩家编号 {data.LocalPlayerId}" : "队伍信息尚未同步";
            _leaderState.text=hasTeam?(leader?"你是队长":"你是队员"):"尚未入队";
            _footerSync.text=_state?.HasLoaded==true?"队伍信息已同步":"队伍信息待同步";
            _memberCount.text=$"空余 {Math.Max(0,capacity-members)} 席";
`+code.slice(summaryEnd);
code=code.replace('_applicationCount.text = noTeam ? $"{invites} 条" : $"{applicationTotal} 人";',
  '_applicationCount.text = (noTeam ? invites : applicationTotal).ToString();');
region('        private void RenderNoTeam()','        private void RenderMembers(int capacity)',`        private void RenderNoTeam()
        {
            var card=Row(_members,"NoTeamCard",0,0,851,516,"application_card");
            Label(card,"你尚未加入队伍",42,155,767,61,34,BodyInk,TextAlignmentOptions.Center,bold:true);
            Label(card,"可以创建自己的队伍，或输入道友编号申请加入；收到的邀请会显示在右侧。",60,243,731,120,26,
                BodyMuted,TextAlignmentOptions.Center,wrap:true);
        }`);
region('        private void RenderMembers(int capacity)','        private void RenderApplications()',`        private void RenderMembers(int capacity)
        {
            var data=_state?.Snapshot;bool manageRows=_state?.IsLeader==true;
            int start=MemberPageIndex*MaxMemberCards;
            int visible=Math.Min(MaxMemberCards,Math.Max(capacity,data?.Members.Count??0)-start);
            for(int i=0;i<visible;i++)
            {
                int slot=start+i;var role=data!=null&&slot<data.Members.Count?data.Members[slot]:null;
                bool self=role!=null&&role.PlayerId==data.LocalPlayerId;
                bool highlighted=role!=null&&_state.HighlightPlayerId!=0&&role.PlayerId==_state.HighlightPlayerId;
                var row=Row(_members,"TeamMemberSlot_"+slot,0,i*104,851,100,"member_row",
                    highlighted?QdaoUguiTheme.Html("#F6D9D2"):Color.white);
                if(role==null)
                {
                    Art(row,"empty_slot",44,6,88,88,true);
                    Label(row,"空余席位",175,8,430,44,29,BodyInk);
                    Label(row,"等待道友加入",175,56,430,34,23,BodyMuted);
                    continue;
                }
                Portrait(row,role,43,0,100);
                Label(row,DisplayName(role),175,1,232,49,34,bold:false).name="TeamName_"+role.PlayerId;
                Label(row,Level(role)+" · "+School(role),175,57,232,35,24,BodyInk).name="TeamLevel_"+role.PlayerId;
                bool leader=role.PlayerId==data.LeaderId;
                Art(row,"badge_leader",413,30,118,42);
                Label(row,leader?"队长":"队员",421,30,102,42,26,BodyInk,TextAlignmentOptions.Center);
                if(self)
                {
                    Art(row,"badge_self",549,31,86,40);
                    Label(row,"自己",555,31,74,40,23,Cream,TextAlignmentOptions.Center);
                }
                else if(manageRows)
                {
                    ulong id=role.PlayerId;
                    bool transferring=_state.PendingAction==TeamAction.Transfer&&_state.PendingTarget==id;
                    bool kicking=_state.PendingAction==TeamAction.Kick&&_state.PendingTarget==id;
                    var transfer=Control(row,transferring?"处理中":"转让",542,32,76,40,()=>ConfirmTransfer(id),
                        enabled:CanManage&&role.IsOnline,size:transferring?16:21);transfer.name="Transfer_"+id;
                    var kick=Control(row,kicking?"处理中":"请离",624,32,76,40,()=>ConfirmKick(id),
                        enabled:CanManage,size:kicking?16:21);kick.name="Kick_"+id;
                }
                if(role.OnlineStatusKnown)Art(row,role.IsOnline?"status_online":"status_offline",710,38,23,23,true);
                Label(row,!role.OnlineStatusKnown?"待同步":role.IsOnline?(role.InBattle?"战斗中":"在线"):"离线",
                    741,27,95,45,25,role.IsOnline?BodyInk:BodyMuted,TextAlignmentOptions.MidlineRight);
            }
        }`);
region('        private void RenderApplications()','        private void RenderInvites()',`        private void RenderApplications()
        {
            var list=_state?.Snapshot?.Applications;
            if(list==null||list.Count==0)
            {
                bool member=_state!=null&&_state.HasTeam&&!_state.IsLeader;
                Row(_applications,"EmptyApplications",0,0,619,399,"application_card");
                string title=member?"入队申请由队长处理":_state?.IsBusy==true?"正在同步申请…":"暂无入队申请";
                Label(_applications,title,25,120,569,62,33,BodyInk,TextAlignmentOptions.Center,bold:true);
                string detail=member?$"队伍当前有 {_state.Snapshot.ApplicationCount} 条待处理申请。":_state?.ServiceAvailable==true
                    ?"收到申请后，可在这里查看道友资料。":"组队开放后，可在这里查看并处理申请。";
                Label(_applications,detail,52,206,515,93,25,BodyMuted,TextAlignmentOptions.Center,wrap:true);return;
            }
            int start=ApplicationPageIndex*RowsPerPage,count=Math.Min(RowsPerPage,list.Count-start);bool compact=count>2;
            for(int i=0;i<count;i++)
            {
                var role=list[start+i];if(role==null)continue;
                var row=Row(_applications,"TeamRow_"+role.PlayerId,0,i*(compact?101:204),619,compact?94:194,"application_card");
                Portrait(row,role,compact?14:19,compact?9:8,compact?76:130);
                Label(row,DisplayName(role),compact?103:168,compact?5:21,compact?208:420,compact?41:50,
                    compact?27:37,bold:false).name="TeamName_"+role.PlayerId;
                Label(row,Level(role)+" · "+School(role),compact?103:168,compact?49:77,compact?208:420,compact?34:41,
                    compact?20:25,BodyInk).name="TeamDetails_"+role.PlayerId;
                bool pending=_state?.PendingPlayerId==role.PlayerId;float y=compact?25:122;
                var reject=Control(row,"拒绝",compact?326:135,y,compact?123:214,compact?50:57,
                    ()=>Decide(role.PlayerId,false),enabled:CanReject,size:compact?22:30);reject.name="Reject_"+role.PlayerId;
                var approve=Control(row,pending?"处理中":"同意",compact?459:365,y,compact?138:214,compact?50:57,
                    ()=>Decide(role.PlayerId,true),primary:true,enabled:CanApprove,size:pending?23:compact?22:30);approve.name="Approve_"+role.PlayerId;
            }
        }`);
// Invitation intents and state remain unchanged; only their shared row geometry follows the same native panel.
const inviteStart=code.indexOf('        private void RenderInvites()'),inviteEnd=code.indexOf('        private void Decide(',inviteStart);
let invites=code.slice(inviteStart,inviteEnd)
 .replaceAll('846, 514','619, 399').replaceAll('32, 162, 782, 66, 42','25, 120, 569, 62, 33')
 .replaceAll('72, 254, 702, 96, 30','52, 206, 515, 93, 25')
 .replaceAll('i * (compact ? 126 : 264), 846','i * (compact ? 101 : 204), 619')
 .replaceAll('compact ? 114 : 242','compact ? 94 : 194')
 .replaceAll('compact ? 14 : 24, compact ? 16 : 20, compact ? 82 : 132','compact ? 14 : 19, compact ? 9 : 8, compact ? 76 : 130')
 .replaceAll('compact ? 114 : 184, compact ? 10 : 24','compact ? 103 : 168, compact ? 5 : 21')
 .replaceAll('compact ? 114 : 184, compact ? 65 : 91','compact ? 103 : 168, compact ? 49 : 77')
 .replaceAll('compact ? 346 : 622, 56, compact ? 32 : 38','compact ? 208 : 420, 50, compact ? 27 : 33')
 .replaceAll('compact ? 346 : 622, 48, compact ? 26 : 30','compact ? 208 : 420, 41, compact ? 20 : 25')
 .replaceAll('compact ? 24 : 162','compact ? 25 : 122')
 .replaceAll('compact ? 476 : 190','compact ? 326 : 135').replaceAll('compact ? 648 : 512','compact ? 459 : 365')
 .replaceAll('compact ? 158 : 292','compact ? 123 : 214').replaceAll('compact ? 174 : 292','compact ? 138 : 214')
 .replaceAll('compact ? 66 : 64','compact ? 50 : 57').replaceAll('compact ? 28 : 32','compact ? 22 : 30');
code=code.slice(0,inviteStart)+invites+code.slice(inviteEnd);
code=code.replace('            string id = role.CharacterId;',`            string id = role.CharacterId;
            // This marker is issued only by the explicit offline capture fixture, never inferred from a player id.
            if(!string.IsNullOrEmpty(id)&&id.StartsWith(TeamUiArt.PreviewPortraitPrefix,StringComparison.Ordinal))
            {
                string key="preview_portrait_"+id.Substring(TeamUiArt.PreviewPortraitPrefix.Length);
                var sample=Art(parent,key,x,y,size,size,true);sample.name="TeamPortrait_"+role.PlayerId;return;
            }`);
region('        private static TMP_FontAsset BodyFont()','        private static TextMeshProUGUI Label(',`        private static TMP_FontAsset BodyFont()
        {
            // The approved artwork uses a Chinese calligraphic serif; match it in native labels.
            return _bodyFont!=null?_bodyFont:(_bodyFont=QdaoUguiTheme.ResolveFont());
        }`);
code=code.replace('h = Mathf.Max(h, size * 1.6f);','h = Mathf.Max(h, size * 1.18f);');
fs.writeFileSync(path.join(dir,'TeamWindow.cs'),code);
let art=fs.readFileSync('E:/work/mmorpg-client/Assets/Scripts/UI/Ugui/Team/TeamUiArt.cs','utf8');
art=art.replace('public const string Root = "UI/Ugui/TeamV2/";',
  'public const string Root = "UI/Ugui/TeamV2/";\n        public const string FidelityRoot = Root + "Fidelity20261016/";\n        public const string PreviewPortraitPrefix = "preview-team-";');
art=art.replace('string root = key == "lantern" || key == "close_tassel" ? Gameplay.GameplayUiArt.Root : Root;',
  'string root = key == "team_skin" || key.StartsWith("preview_portrait_",StringComparison.Ordinal) ? FidelityRoot\n                : key == "lantern" || key == "close_tassel" ? Gameplay.GameplayUiArt.Root : Root;');
art=art.replace('float textHeight = Mathf.Max(h, fontSize * 1.6f);','float textHeight = Mathf.Max(h, fontSize * 1.18f);');
fs.writeFileSync(path.join(dir,'TeamUiArt.cs'),art);
process.stdout.write(JSON.stringify({staged:dir,modifiedFiles:['TeamWindow.cs','TeamUiArt.cs'],logicFilesModified:false})+'\n');
