from pathlib import Path
ROOT=Path(__file__).resolve().parent
src=Path('E:/work/mmorpg-client/Assets/Tests/EditMode/Battle/GameplayWindowTests.cs').read_text(encoding='utf-8-sig')
def replace_method(signature, replacement):
    global src
    start=src.index(signature); brace=src.index('{',start); level=1; p=brace+1
    while level:
        if src[p]=='{': level+=1
        elif src[p]=='}': level-=1
        p+=1
    src=src[:start]+replacement+src[p:]

src=src.replace('            Click("已达成");','            Click("筛选·全部任务");\n            Click("已达成");')
replace_method('        public void AllMissionObjectivesCanBeViewedThroughNativeGroupButtons()', '''        public void EveryMissionObjectiveIsReachableThroughTheNativeScrollViewport()
        {
            var missions = MakeMissions(1);
            missions.Missions[0].Objectives.Clear();
            for (uint i = 0; i < 7; ++i)
                missions.Missions[0].Objectives.Add(new MissionObjectiveInfo { ObjectiveIndex = i, Description = "目标内容" + (i + 1), Progress = i, Target = 10 });
            _window.SetMissions(missions, false, null); _window.Show(GameplayPage.Missions);
            for (int i = 1; i <= 7; ++i) AssertText("目标内容" + i);
            var scroll = Scroll("MissionObjectivesScroll");
            Assert.That(scroll.vertical, Is.True); Assert.That(scroll.horizontal, Is.False);
            Assert.That(scroll.content.rect.height, Is.GreaterThan(scroll.viewport.rect.height));
            scroll.verticalNormalizedPosition = 0; Canvas.ForceUpdateCanvases();
            Assert.That(scroll.content.anchoredPosition.y, Is.GreaterThan(0), "最后一项目标必须可滚入可视区");
            Assert.That(_missionReads, Is.EqualTo(1)); Assert.That(_tracking, Is.Empty);
        }''')
replace_method('        public void MissionPaginationSelectsAnEntryOnTheVisiblePageAndChangesDetails()', '''        public void LongMissionListScrollsToTheLastEntryAndSelectionUsesItsRealState()
        {
            _window.SetMissions(MakeMissions(7), false, null); _window.Show(GameplayPage.Missions);
            AssertText("任务说明1"); var scroll = Scroll("MissionListScroll");
            Assert.That(scroll.content.rect.height, Is.GreaterThan(scroll.viewport.rect.height));
            scroll.verticalNormalizedPosition = 0; scroll.onValueChanged.Invoke(new Vector2(0, 0)); Canvas.ForceUpdateCanvases();
            Click("任务七"); AssertText("任务说明7"); Assert.That(HasText("任务说明1"), Is.False);
            Assert.That(Scroll("MissionListScroll").verticalNormalizedPosition, Is.LessThan(.01f));
            Assert.That(_missionReads, Is.EqualTo(1), "滚动与详情选择不得发送额外RPC");
            Assert.That(_accepts, Is.Empty); Assert.That(_claims, Is.Empty);
        }''')
replace_method('        public void ActivityPaginationSelectsAnEntryOnTheVisiblePageAndChangesDetails()', '''        public void LongActivityListUsesHorizontalScrollingWithoutHiddenFixedPageLimits()
        {
            _window.SetActivities(MakeActivities(5), false, null); _window.Show(GameplayPage.Activities);
            for (int i = 1; i <= 5; ++i) AssertText("雅集说明" + i);
            var scroll = Scroll("ActivityCardsScroll");
            Assert.That(scroll.horizontal, Is.True); Assert.That(scroll.vertical, Is.False);
            Assert.That(scroll.content.rect.width, Is.GreaterThan(scroll.viewport.rect.width));
            scroll.horizontalNormalizedPosition = 1; scroll.onValueChanged.Invoke(new Vector2(1, 0)); Canvas.ForceUpdateCanvases();
            Assert.That(scroll.content.anchoredPosition.x, Is.LessThan(0), "第五张真实活动卡必须可滚入可视区");
            Assert.That(_activityReads, Is.EqualTo(1)); Assert.That(_accepts, Is.Empty);
        }''')
src=src.replace('            Assert.That(FindButton("下一页").interactable, Is.False);','            Assert.That(Scroll(_window.Page == GameplayPage.Missions ? "MissionListScroll" : "ActivityCardsScroll").content.childCount, Is.Zero);')
insert='''        [Test]
        public void MissionStatusFiltersPreserveUnacceptedActiveAndCompletedStatesWithoutSendingActions()
        {
            var missions = MakeMissions(3);
            missions.Missions[0].Status = (PlayerMissionStatus)0; missions.Missions[0].CanAccept = true;
            missions.Missions[1].Status = (PlayerMissionStatus)1;
            missions.Missions[2].Status = (PlayerMissionStatus)3; missions.Missions[2].CanClaim = false;
            missions.Missions[2].UnavailableReason = "等待服务器允许领奖";
            _window.SetMissions(missions, false, null); _window.Show(GameplayPage.Missions);
            AssertText("任务一"); AssertText("任务二"); AssertText("任务三");
            Click("筛选·全部任务"); Click("进行中");
            AssertText("任务二"); Assert.That(HasText("任务一"), Is.False); Assert.That(HasText("任务三"), Is.False);
            Click("追踪任务"); Assert.That(_tracking.Last().MissionId, Is.EqualTo(2));
            Click("筛选·进行中"); Click("已达成");
            AssertText("任务三"); AssertText("等待服务器允许领奖"); Assert.That(FindButton("领取奖励").interactable, Is.False);
            Click("待开启"); AssertText("任务一"); Assert.That(FindButton("接取任务").interactable, Is.True);
            Assert.That(_accepts, Is.Empty); Assert.That(_claims, Is.Empty); Assert.That(_missionReads, Is.EqualTo(1));
        }

        private ScrollRect Scroll(string name)
            => _fixture.GetComponentsInChildren<ScrollRect>().Single(s => s.name == name);

'''
src=src.replace('        private TMP_InputField Search()',insert+'        private TMP_InputField Search()')
out=ROOT/'staged/Assets/Tests/EditMode/Battle/GameplayWindowTests.cs'
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(src,encoding='utf-8')
print(out)
