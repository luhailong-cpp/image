from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parent
CLIENT=Path('E:/work/mmorpg-client')
OUT=ROOT/'client/Assets/Scripts/UI/Ugui/Guild'
OUT.mkdir(parents=True,exist_ok=True)
source=CLIENT/'Assets/Scripts/UI/Ugui/Guild/GuildWindow.cs'
original=source.read_text(encoding='utf-8-sig')
s=original
def replace_method(text,start_token,end_token,new):
 start=text.index(start_token);end=text.index(end_token,start)
 return text[:start]+new+text[end:]
constructor=r'''        public GuildWindow(UnityEngine.Transform parent)
        {
            _root = QdaoUguiFactory.CreateStretch("GuildWindow", parent, Vector4.zero);
            _root.gameObject.SetActive(false);
            var shade = _root.gameObject.AddComponent<Image>();
            shade.color = new Color(.025f, .10f, .08f, .68f); shade.raycastTarget = true;
            _root.gameObject.AddComponent<GameplayInputBlocker>();
            _frame = QdaoUguiFactory.CreateCenteredRect("GuildFrame", _root, 1932, 814);
            float scale = Mathf.Min(2560f / 1932f, 1080f / 814f);
            _frame.localScale = new UnityEngine.Vector3(scale, scale, 1);
            _frameInput = _frame.gameObject.AddComponent<CanvasGroup>();
            Art(_frame, "guild_empty_shell", 0, 0, 1932, 814);
            FidelityLabel(_frame, "GuildTitle", "帮  会", 836, 28, 260, 55, 39, Cream, align: TextAlignmentOptions.Center);
            string[] titles = { "帮会总览", "帮会成员", "帮会排行", "帮会捐献", "帮会活动", "帮会商店" };
            for (int i = 0; i < _tabs.Length; i++)
            {
                GuildPage page = (GuildPage)i;
                _tabs[i] = NamedButton(_frame, "GuildTab_" + page, titles[i],
                    190 + i * 264, 87, 257, 62, () => Show(page), key: "guild_tab_normal", fontSize: 28);
                _tabMarkers[i] = Line(_tabs[i].transform, "SelectedTabMarker", 110, 54, 37, 2);
                _tabMarkers[i].color = QdaoUguiTheme.Html("#E3C681");
            }
            NamedButton(_frame, "CloseGuild", "", 1782, 25, 83, 78, Hide, key: "guild_close");
            _rail = QdaoUguiFactory.CreateRect("GuildIdentity", _frame, 183, 171, 544, 595);
            _body = QdaoUguiFactory.CreateRect("GuildContent", _frame, 795, 175, 957, 503);
            FidelityLabel(_frame, "GuildContributionFooterLabel", "可用 / 累计帮贡", 798, 701, 315, 22, 17, Muted);
            _summary = FidelityLabel(_frame, "GuildMyContribution", "", 798, 724, 315, 34, 23, Ink);
            _status = FidelityLabel(_frame, "GuildRuntimeStatus", "", 796, 767, 963, 25, 16, Muted);
            NamedButton(_frame, "GuildFooterMembers", "查看同道", 1122, 704, 229, 58, () => Show(GuildPage.Members), fontSize: 27);
            _refresh = NamedButton(_frame, "RefreshGuild", "刷新帮会", 1365, 692, 414, 80, RefreshCurrentPage, true, fontSize: 33);
        }
        // Existing five page renderers retain their original coordinate system and
        // every real callback. Only their uniform presentation scale changes.
        private void ConfigureFidelityBody()
        {
            bool overview = Page == GuildPage.Overview && _client?.Info != null;
            float scale = overview ? 1f : 957f / 1508f;
            _body.localScale = new UnityEngine.Vector3(scale, scale, 1);
            _body.sizeDelta = overview ? new Vector2(957, 503) : new Vector2(1508, 610);
            _body.anchoredPosition = new Vector2(795, overview ? -175 : -197);
        }
        private ulong MyContributionTotal(GuildInfo info)
        {
            foreach (var member in info.Members) if (member.PlayerId == _client.PlayerId) return member.ContributionTotal;
            return 0;
        }
'''
s=replace_method(s,'        public GuildWindow(', '        private bool Busy',constructor)
s=s.replace('            _status.text = _client?.Status', '            ConfigureFidelityBody();\n            _status.text = _client?.Status',1)
s=s.replace('''            _summary.text = _client?.Info == null ? "结一方同道 · 守一盏人间灯" :
                _client.Info.Members.Count + " / " + _client.Info.MaxMembers + " 位同道 · 相聚一堂";''','''            _summary.text = _client?.Info == null ? "结一方同道 · 守一盏人间灯" :
                GuildClient.FormatAmount(MyContributionBalance(_client.Info)) + " / " + GuildClient.FormatAmount(MyContributionTotal(_client.Info));''',1)
s=s.replace('Load(i == (int)Page ? "button_primary" : "button_secondary")','Load(i == (int)Page ? "guild_tab_selected" : "guild_tab_normal")',1)
identity=r'''        private void RenderIdentity()
        {
            Art(_rail, "guild_crest", 29, 0, 207, 188, true).name = "GuildCrest";
            var info = _client?.Info;
            var name = FidelityLabel(_rail, "GuildName", info?.Name ?? "静候同道", 268, 12, 258, 78, 37, Ink, true);
            name.enableAutoSizing = true; name.fontSizeMin = 20; name.fontSizeMax = 37;
            if (info == null)
            {
                FidelityLabel(_rail, "GuildNoMembership", "灯火可亲，同道可期。\n找到一处归属，携手闯荡山海。", 20, 218, 492, 160, 27, Muted, true);
                NamedButton(_rail, "BrowseGuilds", "寻找帮会", 135, 539, 260, 58, () => Show(GuildPage.Ranking), true, fontSize: 27);
                return;
            }
            Art(_rail, "guild_level_plate", 274, 74, 171, 55);
            FidelityLabel(_rail, "GuildLevel", info.Level + " 级帮会", 283, 79, 153, 44, 25, Ink, align: TextAlignmentOptions.Center);
            if (_client.IsOfficerOrLeader)
                NamedButton(_rail, "UpgradeGuild", info.UpgradeCostFunds == 0 ? "已满级" : "升级", 265, 139, 115, 40,
                    ShowUpgrade, enabled: _client.CanUpgrade && !Busy, fontSize: 22);
            if (_client.CanEditAnnouncement)
                NamedButton(_rail, "EditGuildAnnouncement", "编辑公告", 391, 139, 134, 40, ShowAnnouncement, enabled: !Busy, fontSize: 21);
            string leader = string.IsNullOrWhiteSpace(info.LeaderName) ? info.LeaderId.ToString() : info.LeaderName;
            string[] labels = { "帮主", "帮会编号", "成员", "帮会资金" };
            string[] values = { leader, info.GuildId.ToString(), info.Members.Count + " / " + info.MaxMembers, GuildClient.FormatAmount(info.Funds) };
            for (int i = 0; i < labels.Length; i++)
            {
                float y = 181 + i * 38;
                FidelityLabel(_rail, "GuildDetailLabel_" + i, labels[i], 19, y, 200, 34, 23, Muted);
                FidelityLabel(_rail, "GuildDetailValue_" + i, values[i], 241, y, 283, 34, 23, Ink);
                if (i == 2) _rail.Find("GuildDetailValue_" + i).name = "GuildMemberCount";
                if (i == 3) _rail.Find("GuildDetailValue_" + i).name = "GuildFunds";
                Line(_rail, "GuildDetailRule_" + i, 15, y + 34, 511, 1);
            }
            FidelityLabel(_rail, "GuildUpgradeFundsLabel", "升级资金", 16, 340, 119, 31, 21, Ink);
            Art(_rail, "guild_progress_track", 135, 338, 392, 37);
            double ratio = info.UpgradeCostFunds == 0 ? 1 : Math.Min(1d, (double)info.Funds / info.UpgradeCostFunds);
            if (ratio > 0) Art(_rail, "guild_progress_fill", 147, 346, (float)(368 * ratio), 21);
            FidelityLabel(_rail, "GuildUpgradeFundsValue", info.UpgradeCostFunds == 0 ? "已满级" :
                GuildClient.FormatAmount(info.Funds) + " / " + GuildClient.FormatAmount(info.UpgradeCostFunds), 149, 343, 365, 27, 17,
                ratio >= .55 ? Cream : Ink, align: TextAlignmentOptions.Center);
            Art(_rail, "guild_announcement", -2, 388, 546, 144);
            FidelityLabel(_rail, "GuildAnnouncementHeading", "帮会公告", 37, 396, 471, 36, 27, Ink);
            FidelityLabel(_rail, "GuildAnnouncementExcerpt", string.IsNullOrWhiteSpace(info.Announcement) ? "同道相伴，诸事顺遂。" : info.Announcement,
                39, 438, 466, 78, 23, Ink, true);
            NamedButton(_rail, "GuildMembersEntry", "同道", 0, 540, 146, 58, () => Show(GuildPage.Members), fontSize: 25);
            NamedButton(_rail, "ReadGuildAnnouncement", "查看公告", 158, 539, 229, 58, ShowReadAnnouncement, fontSize: 26);
            NamedButton(_rail, "LeaveOrDisbandGuild", _client.IsLeader ? "解散帮会" : "退出帮会", 398, 540, 145, 58,
                () => Confirm(_client.IsLeader ? "确认解散帮会" : "确认退出帮会",
                    _client.IsLeader ? "解散后所有成员都将离开帮会，此操作无法恢复。" : "退出后将失去当前帮会身份。确认要离开同道吗？",
                    () => { if (_client.IsLeader) DisbandRequested?.Invoke(); else LeaveRequested?.Invoke(); }), enabled: !Busy, fontSize: 22);
        }
'''
s=replace_method(s,'        private void RenderIdentity()', '        private void RenderOverview()',identity)
# Preserve the original unavailable/empty business view. The known-guild overview is presentation only.
old_start=s.index('        private void RenderOverview()')
known=s.index('            Heading(_body, "同道相聚"',old_start)
old_end=s.index('        private void OverviewMetric(',known)
overview=r'''            FidelityLabel(_body, "GuildOverviewMembersTitle", "帮会成员", 10, 0, 440, 41, 33, Ink);
            int online = 0;
            foreach (var member in info.Members) if (member.Online) online++;
            FidelityLabel(_body, "GuildOverviewOnlineLabel", "在线", 676, 4, 77, 36, 25, Ink);
            FidelityLabel(_body, "GuildOnlineCount", online + " 位", 753, 4, 95, 36, 25, Ink, align: TextAlignmentOptions.MidlineRight);
            FidelityLabel(_body, "GuildOverviewOnlineTotal", " / " + info.Members.Count, 848, 4, 99, 36, 25, Ink);
            Art(_body, "guild_table_header", 0, 42, 957, 40);
            FidelityLabel(_body, "GuildOverviewMemberColumn", "成员", 142, 43, 280, 36, 23, Muted);
            FidelityLabel(_body, "GuildOverviewRoleColumn", "职位", 409, 43, 110, 36, 23, Muted);
            FidelityLabel(_body, "GuildOverviewContributionColumn", "累计帮贡", 570, 43, 193, 36, 23, Muted);
            FidelityLabel(_body, "GuildOverviewOnlineColumn", "状态", 824, 43, 121, 36, 23, Muted);
            var members = new List<GuildMember>(info.Members);
            members.Sort((a,b) => { int rank = b.Role.CompareTo(a.Role); return rank != 0 ? rank : a.PlayerId.CompareTo(b.PlayerId); });
            for (int i = 0; i < Math.Min(5, members.Count); i++)
            {
                var member = members[i]; float y = 82 + i * 56;
                bool self = member.PlayerId == _client.PlayerId;
                Art(_body, self ? "guild_row_self" : "guild_row_normal", 0, y, 957, 56);
                // No character appearance is present in GuildMember; use approved default portraits.
                Art(_body, "guild_portrait_" + (i + 1), 60, y + 1, 63, 54, true);
                if (self) Art(_body, "guild_self_mark", 13, y + 9, 36, 36, true);
                FidelityLabel(_body, "GuildOverviewMemberName_" + i, MemberDisplayName(member), 142, y + 6, 263, 43, 24, Ink);
                FidelityLabel(_body, "GuildOverviewMemberRole_" + i, RoleName(member.Role), 410, y + 6, 118, 43, 24, Ink);
                FidelityLabel(_body, "GuildOverviewMemberContribution_" + i, GuildClient.FormatAmount(member.ContributionTotal), 570, y + 6, 213, 43, 23, Ink);
                var dot = QdaoUguiFactory.CreateImage("GuildOnlineDot_" + i, _body, 829, y + 23, 16, 16,
                    QdaoUguiTheme.LoadSprite(QdaoUguiTheme.StatusDotSpritePath));
                dot.color = QdaoUguiTheme.Html(member.Online ? "#409951" : "#928772");
                FidelityLabel(_body, "GuildOverviewMemberOnline_" + i, member.Online ? "在线" : "离线", 859, y + 6, 91, 43, 24, member.Online ? Ink : Muted);
            }
            if (members.Count == 0) FidelityLabel(_body, "GuildOverviewNoMembers", "暂无同道信息", 70, 151, 810, 78, 30, Muted, align: TextAlignmentOptions.Center);
            FidelityOverviewEntry("GuildOverviewDonate", "帮会捐献", "guild_entry_donate", GuildPage.Donate, 0, 218);
            FidelityOverviewEntry("GuildOverviewRanking", "帮会排行", "guild_entry_scroll", GuildPage.Ranking, 231, 220);
            FidelityOverviewEntry("GuildOverviewActivities", "帮会活动", "guild_entry_activity", GuildPage.Activities, 469, 219);
            FidelityOverviewEntry("GuildOverviewShop", "帮会商店", "guild_entry_shop", GuildPage.Shop, 701, 245);
        }
        private void FidelityOverviewEntry(string name, string label, string key, GuildPage page, float x, float width)
        {
            var button = QdaoUguiFactory.CreateArtButton(name, _body, x, 377, width, 126, Load(key), out var image);
            image.type = Image.Type.Sliced;
            button.navigation = new Navigation { mode = Navigation.Mode.Automatic };
            button.onClick.AddListener(() => Show(page));
            FidelityLabel(button.transform, name + "Caption", label, 12, 94, width - 24, 31, 23, Ink, align: TextAlignmentOptions.Center);
        }
'''
s=s[:known]+overview+s[old_end:]
s=s.replace('''        private static Sprite GuildSprite(string key) => Resources.Load<Sprite>("UI/Ugui/GuildV2/" + key)
            ?? throw new InvalidOperationException("缺少帮会 Sprite：UI/Ugui/GuildV2/" + key);''','''        private static Sprite GuildSprite(string key) => Load(key);''',1)
(OUT/'GuildWindow.cs').write_text(s,encoding='utf-8')
art_source=CLIENT/'Assets/Scripts/UI/Ugui/Guild/GuildUiArt.cs'
art=art_source.read_text(encoding='utf-8-sig')
art=art.replace('public static Sprite Load(string key) => QdaoUguiTheme.RequireSprite(Root + key);',r'''public const string FidelityRoot = "UI/Ugui/GuildFidelity20261016/";
        public static Sprite Load(string key)
        {
            string alias = key switch {
                "button_primary" => "guild_button_primary", "button_secondary" => "guild_button_secondary",
                "stat_field" => "guild_announcement", "crest" => "guild_crest", _ => key };
            return Resources.Load<Sprite>(FidelityRoot + alias) ?? QdaoUguiTheme.RequireSprite(Root + key);
        }
        public static TextMeshProUGUI FidelityLabel(UnityEngine.Transform parent, string name, string value,
            float x, float y, float w, float h, float size, Color color, bool wrap = false,
            TextAlignmentOptions align = TextAlignmentOptions.MidlineLeft)
        {
            var text = QdaoUguiFactory.CreateText(name, parent, x, y, w, h, value, size, color, align);
            text.font = QdaoUguiTheme.ResolveFont(); text.richText = false;
            text.textWrappingMode = wrap ? TextWrappingModes.Normal : TextWrappingModes.NoWrap;
            text.overflowMode = TextOverflowModes.Ellipsis;
            if (wrap) text.alignment = TextAlignmentOptions.TopLeft;
            return text;
        }''')
art=art.replace('QdaoUguiTypography.ApplyBody(label);','label.font = QdaoUguiTheme.ResolveFont();')
art=art.replace('QdaoUguiTypography.ApplyHeading(label);','label.font = QdaoUguiTheme.ResolveFont();')
art=art.replace('QdaoUguiTypography.ApplyButton(caption);','caption.font = QdaoUguiTheme.ResolveFont();')
# Main and all other guild page buttons keep source ornament caps and use their native labels.
art=art.replace('Mathf.Max(32, fontSize)','fontSize')
art=art.replace('var caption = Text(button.transform, label, 18, 0, w - 36, h, fontSize,','var caption = FidelityLabel(button.transform, "ButtonCaption", label, 18, 0, w - 36, h, fontSize,')
art=art.replace('primary ? Cream : Ink, alignment: TextAlignmentOptions.Center);','primary ? Cream : Ink, align: TextAlignmentOptions.Center);')
(OUT/'GuildUiArt.cs').write_text(art,encoding='utf-8')
for name in ['GuildWindow.cs','GuildUiArt.cs']:
 old=CLIENT/'Assets/Scripts/UI/Ugui/Guild'/name
 (OUT/(name+'.meta')).write_bytes(old.with_name(old.name+'.meta').read_bytes())
modified=['GuildWindow constructor','RenderIdentity','RenderOverview known-guild branch','Render view layout and tab skins','GuildSprite route','GuildUiArt font/resource presentation']
record={'sourceRoot':str(CLIENT),'guards':[{'target':str(p.relative_to(CLIENT)).replace('\\','/'),'sha256Before':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [source,art_source]],'modifiedPresentation':modified,'allSixPagesPreserved':True,'GuildClientUnmodified':True,'stageOnly':True,'nativeUnityParityVerified':False,'dataSemantics':{'missingMemberLevel':'Column uses actual role and cumulative contribution instead of invented level/weekly values','construction':'Progress shows actual guild funds versus UpgradeCostFunds, labelled 升级资金','portraits':'Approved static source portraits are explicit defaults; GuildMember has no appearance identity'}}
(ROOT/'staged-code-manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'stagedRuntimeSources':2,'presentationChanges':modified},ensure_ascii=False))
