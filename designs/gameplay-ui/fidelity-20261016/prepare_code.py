from pathlib import Path
ROOT=Path(__file__).resolve().parent
src=Path('E:/work/mmorpg-client/Assets/Scripts/UI/Ugui/Gameplay/GameplayWindow.cs').read_text(encoding='utf-8-sig')
out=ROOT/'staged/Assets/Scripts/UI/Ugui/Gameplay'
out.mkdir(parents=True,exist_ok=True)

def method(text, signature, replacement):
    start=text.index(signature)
    brace=text.index('{',start)
    level=1; p=brace+1
    while level:
        if text[p]=='{': level+=1
        elif text[p]=='}': level-=1
        p+=1
    return text[:start]+replacement+text[p:]

src=src.replace('public sealed class GameplayWindow : IDisposable','public sealed partial class GameplayWindow : IDisposable')
src=method(src,'        public GameplayWindow(UnityEngine.Transform parent, EquipForgeUiState forge = null)', '''        public GameplayWindow(UnityEngine.Transform parent, EquipForgeUiState forge = null)
        {
            _root = QdaoUguiFactory.CreateStretch("PlayerFeaturesWindow", parent, Vector4.zero);
            var shade = _root.gameObject.AddComponent<Image>();
            shade.color = new Color(.025f, .10f, .08f, .68f); shade.raycastTarget = true;
            _root.gameObject.AddComponent<MmorpgClient.World.Tianyong.GameplayInputBlocker>();
            var frame = QdaoUguiFactory.CreateCenteredRect("NativeGameplayDesign", _root, NativeWidth, NativeHeight);
            frame.gameObject.AddComponent<GameplayDesignFit>();
            _frameControls = frame.gameObject.AddComponent<CanvasGroup>();
            _nativeFrame = QdaoUguiFactory.CreateImage("PageArtwork", frame, 0, 0, NativeWidth, NativeHeight, NativeSprite("inventory-frame"));
            _title = NativeText(frame, "背 包", 755, 27, 420, 67, 52, Cream, TextAlignmentOptions.Center);
            _subtitle = NativeText(frame, "", 0, 0, 1, 1, 1); _subtitle.gameObject.SetActive(false);
            NativeHit(frame, "CloseWindow", "", 1779, 24, 84, 80, Hide);
            _body = QdaoUguiFactory.CreateRect("PageContent", frame, 0, 0, NativeWidth, NativeHeight);
            _search = QdaoUguiFactory.CreateInputField("BagSearch", frame, 732, 708, 260, 40,
                "搜索名称或编号", 80, NativeSprite("bag-tab-normal"));
            _search.textComponent.color = Ink; _search.textComponent.fontSize = 22;
            ((TMP_Text)_search.placeholder).color = Muted;
            _search.onValueChanged.AddListener(value => { _query = value; _bagScroll = 1; if (Page == GameplayPage.Bag) Render(); });
            _tooltip = new EquipTooltip(frame, 1255, 145); _tooltip.Hide();
            _actions = new EquipActionsDialog(_root); _wish = new EquipWishDialog(_root);
            _forge = forge; _forgeDialog = forge == null ? null : new EquipForgeDialog(_root, forge);
            Hide();
        }''')
src=method(src,'        public void Show(GameplayPage page)', '''        public void Show(GameplayPage page)
        {
            CloseEquipmentModals(); _equipmentNotice = null;
            Page = page; _root.gameObject.SetActive(true);
            _missionFilterMenu = false;
            _nativeFrame.sprite = NativeSprite(page == GameplayPage.Bag ? "inventory-frame" : page == GameplayPage.Missions ? "quests-frame" : "activities-frame");
            _title.text = page == GameplayPage.Bag ? "背 包" : page == GameplayPage.Missions ? "任 务" : "活 动";
            _search.gameObject.SetActive(page == GameplayPage.Bag);
            Render(); Refresh();
        }''')
src=method(src,'        private void Render()', '''        private void Render()
        {
            if (HasEquipmentModal && (Page != GameplayPage.Bag || FindEquipment(_modalItemId) == null)) CloseEquipmentModals();
            _tooltip.Hide(); Clear(_body);
            if (Page == GameplayPage.Bag) RenderBag();
            else if (Page == GameplayPage.Missions) RenderMissions();
            else RenderActivities();
        }''')
for sig in ('        private void RenderBag()', '        private void RenderEquipColumn(', '        private void ShowTooltip(', '        private void RenderMissions()', '        private void RenderActivities()'):
    src=method(src,sig,'')
# Pages use scrolling, including opening a linked activity mission below the fold.
src=method(src,'        private void ShowMission(PlayerMissionInfo mission)', '''        private void ShowMission(PlayerMissionInfo mission)
        {
            _missionFilter = 0; _objectivePage = 0; _selectedMission = MissionKey(mission);
            var ordered = _missions.Missions.OrderBy(m => m.MissionId).ToList();
            int index = Math.Max(0, ordered.FindIndex(m => MissionKey(m) == _selectedMission));
            _missionScroll = ordered.Count <= 5 ? 1 : 1f - Mathf.Clamp01(index * 101f / Math.Max(1, ordered.Count * 101f - 492));
            Show(GameplayPage.Missions);
        }''')
src=src.replace('_bagFilter = _missionFilter = _activityFilter = 0; _query = string.Empty;', '_bagFilter = _missionFilter = _activityFilter = 0; _query = string.Empty;\n            _bagScroll = _missionScroll = _activityScroll = 1;')
(out/'GameplayWindow.cs').write_text(src,encoding='utf-8')
print(out/'GameplayWindow.cs')
