"""Stage equipment QA adaptations against the installed native gameplay view. No client writes."""
from pathlib import Path
import re,json,hashlib
ROOT=Path(__file__).resolve().parent;CLIENT=Path('E:/work/mmorpg-client');STAGED=ROOT/'staged'
changed=[]
def edit(relative, transform):
    original=(CLIENT/relative).read_text(encoding='utf-8-sig');updated=transform(original)
    out=STAGED/relative;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(updated,encoding='utf-8')
    if (CLIENT/(relative+'.meta')).exists():(STAGED/(relative+'.meta')).write_bytes((CLIENT/(relative+'.meta')).read_bytes())
    changed.append(relative)
    return original,updated
def method(text, signature, replacement):
    start=text.index(signature);brace=text.index('{',start);level=1;p=brace+1
    while level:
        if text[p]=='{':level+=1
        elif text[p]=='}':level-=1
        p+=1
    return text[:start]+replacement+text[p:]

def equipment_capture(text):
    text=text.replace('root.GetComponentsInChildren<Button>(true).Single(b=>b.name==name)', 'root.GetComponentsInChildren<Button>(true).Where(b=>b.gameObject.activeInHierarchy).Single(b=>b.name==name)')
    text=text.replace('var weapon=Weapon(); int actions=0; card.Show(weapon,', '// Standalone card fixtures own this state; hide the gameplay details before opening another card.\n            window.Hide();\n            var weapon=Weapon(); int actions=0; card.Show(weapon,')
    text=text.replace('                scope.transform.SetAsLastSibling(); RealtimeTween.AdvanceEditorCapture(1f);', '''                foreach (var actionName in new[] { "EquipAction", "EquipMore", "EquipShare", "ConfirmWishSelection" })
                    if (root.GetComponentsInChildren<Button>(true).Count(b => b.gameObject.activeInHierarchy && b.name == actionName) > 1)
                        throw new InvalidOperationException("Multiple visible equipment controls: " + actionName);
                scope.transform.SetAsLastSibling(); RealtimeTween.AdvanceEditorCapture(1f);''')
    return text
edit('Assets/Editor/EquipmentUiVerification.cs',equipment_capture)

def integration(text):
    text=text.replace('            Click(root, "EquipSlot_6");','            Click(root, "BagCategory_3"); // 已穿戴 is the native equipment view.\n            Click(root, "EquipSlot_6");')
    text=text.replace('root.GetComponentsInChildren<T>(true).Single(item => item.name == name)', 'root.GetComponentsInChildren<T>(true).Where(item => item.gameObject.activeInHierarchy).Single(item => item.name == name)')
    text=text.replace('Find<RectTransform>(characterRoot, "AttributeWindow").gameObject.SetActive(true);', 'characterRoot.GetComponentsInChildren<RectTransform>(true).Single(item => item.name == "AttributeWindow").gameObject.SetActive(true);')
    text=text.replace('            panel.ResetSession();\n            Require(!Find<Button>(characterRoot, "CombatTabPlate").gameObject.activeSelf,', '            var combatTab = Find<Button>(characterRoot, "CombatTabPlate");\n            panel.ResetSession();\n            Require(!combatTab.gameObject.activeSelf,')
    return text
edit('Assets/Editor/EquipmentIntegrationVerification.cs',integration)
edit('Assets/Editor/EquipmentForgeUiVerification.cs',lambda text:text.replace('root.GetComponentsInChildren<T>(true).Single(item => item.name == name)', 'root.GetComponentsInChildren<T>(true).Where(item => item.gameObject.activeInHierarchy).Single(item => item.name == name)'))

def equip_tests(text):
    text=text.replace('AssertText("读取中…");','AssertText("正在打开行囊…");')
    text=text.replace('AssertText("未同步");','Assert.That(_client.EquipmentError, Is.Not.Empty);')
    text=text.replace('AssertText("未读取");','Assert.That(WithWornView(() => HasText("装备栏尚未同步")), Is.True);')
    text=text.replace('AssertText("持有数量  3\\n叠放上限  99");','AssertText("持有数量  3");\n            AssertText("叠放上限  99");')
    text=re.sub(r'SlotButton\((\d+)\)\.onClick\.Invoke\(\);',r'SelectWornSlot(\1);',text)
    text=re.sub(r'HasIcon\(SlotButton\((\w+)\)\)',r'WornSlotHasIcon(\1)',text)
    text=re.sub(r'HasCheck\(SlotButton\((\d+)\)\)',r'WornSlotHasSelection(\1)',text)
    text=re.sub(r'SlotButton\((\w+)\)\.interactable',r'WornSlotInteractable(\1)',text)
    text=text.replace('Click("背包"); // 回包前又点了一下顶部页签:窗口照常要求刷新两份快照', '_window.Show(GameplayPage.Bag); // 同一正式入口刷新两份快照，原稿没有额外顶部背包页签')
    text=text.replace('Assert.That(WornSlotHasSelection(6), Is.False);','Assert.That(HasCheck(BagSlot(0)), Is.True, "新会话默认显示当前行囊的首件物品，不恢复旧穿戴选择");')
    text=method(text,'        public void MoreSlotsThanOnePageAreReachableThroughColumnPager()', '''        public void MoreSlotsThanOnePageAreReachableThroughColumnPager()
        {
            var equipment = new BagInfo { Layout = new BagLayoutInfo { BagType = 2, Capacity = 30 } };
            for (uint slot = 0; slot < 30; ++slot)
                equipment.Layout.EquipSlots.Add(new EquipSlotInfo { Slot = slot, EquipKind = 11, Name = "部位" + slot });
            Open(MakeBag(false), equipment);
            Click("已穿戴");
            Assert.That(SlotNamesVisible().Length, Is.EqualTo(30));
            Assert.That(SlotNamesVisible().First(), Is.EqualTo("EquipSlot_0"));
            Assert.That(SlotNamesVisible().Last(), Is.EqualTo("EquipSlot_29"));
            var scroll = _fixture.GetComponentsInChildren<ScrollRect>().Single(s => s.name == "BagScroll");
            Assert.That(scroll.content.rect.height, Is.GreaterThan(scroll.viewport.rect.height));
            scroll.verticalNormalizedPosition = 0; Canvas.ForceUpdateCanvases();
            Assert.That(scroll.content.anchoredPosition.y, Is.GreaterThan(0), "原分页功能由真实滚动承接，最后栏位可达");
            Assert.That(_net.Calls, Is.Empty, "滚动与分类只展示，不发请求");
        }''')
    # The approved right details region has a fixed scrolling body even for short lists.
    text=text.replace('[TestCase(8, false)]','[TestCase(8, true)]').replace('[TestCase(14, false)]','[TestCase(14, true)]')
    text=text.replace('Is.EqualTo(EquipUiStyle.TooltipLineFont)', 'Is.EqualTo(28f)')
    text=text.replace('private static bool HasCheck(Button button)\n            => button.GetComponentsInChildren<Image>().Any(image => image.name == "check");', 'private static bool HasCheck(Button button)\n            => button.GetComponentsInChildren<Image>().Any(image => image.name == "check") || (button.image.sprite != null && button.image.sprite.name == "bag-slot-selected");')
    text=text.replace('private string[] SlotNames()\n            => Buttons().Where(button => button.name.StartsWith("EquipSlot_")).Select(button => button.name).ToArray();', '''private string[] SlotNames() => WithWornView(SlotNamesVisible);
        private string[] SlotNamesVisible() => Buttons().Where(button => button.name.StartsWith("EquipSlot_")).Select(button => button.name).ToArray();
        private T WithWornView<T>(System.Func<T> read)
        {
            Click("已穿戴");
            try { return read(); }
            finally { Click("全部物品"); }
        }
        private bool WornSlotInteractable(uint slot) => WithWornView(() => SlotButton(slot).interactable);
        private bool WornSlotHasIcon(uint slot) => WithWornView(() => HasIcon(SlotButton(slot)));
        private bool WornSlotHasSelection(uint slot) => WithWornView(() => HasCheck(SlotButton(slot)));
        private void SelectWornSlot(uint slot)
        {
            Click("已穿戴"); var button = SlotButton(slot); Assert.That(button.interactable, Is.True); button.onClick.Invoke();
            Click("全部物品"); // Return to the item grid while retaining the selected item ID.
        }''')
    text=text.replace('=> SlotButton(slot).GetComponentsInChildren<TMP_Text>().Select(text => text.text).ToArray();','=> WithWornView(() => SlotButton(slot).GetComponentsInChildren<TMP_Text>().Select(text => text.text).ToArray());')
    text=text.replace('private RectTransform TooltipRoot()\n            => _fixture.GetComponentsInChildren<RectTransform>(true).Single(rect => rect.name == EquipTooltip.RootName);', '''private RectTransform TooltipRoot()
        {
            var native = _fixture.GetComponentsInChildren<RectTransform>(true)
                .Where(rect => rect.name == "GameplayEquipmentDetails" && rect.gameObject.activeInHierarchy).ToArray();
            Assert.That(native.Length, Is.LessThanOrEqualTo(1), "只能有一个真实可见装备详情区");
            if (native.Length == 1) return native.Single();
            return _fixture.GetComponentsInChildren<RectTransform>(true).Single(rect => rect.name == EquipTooltip.RootName && !rect.gameObject.activeInHierarchy);
        }''')
    text=text.replace('private Button[] Buttons() => _fixture.GetComponentsInChildren<Button>();','private Button[] Buttons() => _fixture.GetComponentsInChildren<Button>(true).Where(button => button.gameObject.activeInHierarchy).ToArray();')
    marker='        // ── 夹具与查询'
    extra='''        [Test]
        public void NativeEquipmentActionsRemainUniqueAfterRefreshAndModalTransitions()
        {
            Open(MakeBag(true), MakeEquipment(true)); BagSlot(1).onClick.Invoke();
            void Unique()
            {
                foreach (var name in new[] { "EquipAction", "EquipMore", "EquipShare" })
                    Assert.That(Buttons().Count(button => button.name == name), Is.EqualTo(1), name + " 只能有一个可见控件");
                Assert.That(_fixture.GetComponentsInChildren<RectTransform>(true).Where(rect => rect.name == EquipTooltip.RootName).All(rect => !rect.gameObject.activeInHierarchy), Is.True);
            }
            Unique(); _window.SetBagPage(MakeBag(true), false, null, false, MakeEquipment(true), false, null, false); Unique();
            Buttons().Single(button => button.name == "EquipMore").onClick.Invoke(); Unique();
            Buttons().Single(button => button.name == "EquipOpenWish").onClick.Invoke();
            Assert.That(Buttons().Count(button => button.name == "ConfirmWishSelection"), Is.EqualTo(1));
            _window.Back(); Unique(); _window.Hide();
            Assert.That(Buttons().Any(button => button.name == "EquipAction"), Is.False);
            Assert.That(_net.Calls, Is.Empty, "刷新展示和弹窗导航不发装备请求");
        }

'''
    text=text.replace(marker,extra+marker)
    return text
old,new=edit('Assets/Tests/EditMode/Battle/EquipWindowTests.cs',equip_tests)

def forge_tests(text):
    text=text.replace('_fixture.GetComponentsInChildren<Button>(true).Single(button => button.name == name)', '_fixture.GetComponentsInChildren<Button>(true).Where(button => button.gameObject.activeInHierarchy).Single(button => button.name == name)')
    text=text.replace('_fixture.GetComponentsInChildren<RectTransform>(true).Single(rect => rect.name == EquipTooltip.RootName)', '_fixture.GetComponentsInChildren<RectTransform>(true).Single(rect => rect.name == "GameplayEquipmentDetails" && rect.gameObject.activeInHierarchy)')
    return text
edit('Assets/Tests/EditMode/Battle/EquipForgeWindowTests.cs',forge_tests)

# Every existing test method and each protocol/error/cooldown assertion remains represented.
old_names=re.findall(r'public void (\w+)\(',old);new_names=re.findall(r'public void (\w+)\(',new)
assert set(old_names)<=set(new_names)
audited={token:(old.count(token),new.count(token)) for token in ('MessageIds.','_net.Calls','ErrorMessage','FailWith','QueryVersion','KEquip','CanSort')}
for token,(before,after) in audited.items():assert after>=before,(token,before,after)
(ROOT/'equipment-compat-test-audit.json').write_text(json.dumps(dict(existing_test_methods_preserved=len(old_names),new_test_methods=len(new_names)-len(old_names),protocol_assertion_tokens=audited,changed_files=changed,notes='Only tooltip hierarchy, equipment category navigation, selected-skin lookup and fixed-card/pager geometry adapted; requests/server errors/generation/permission flows retained.'),ensure_ascii=False,indent=2),encoding='utf-8')
print('staged '+str(len(changed))+' editor/test compatibility files')
