from pathlib import Path
ROOT=Path(__file__).resolve().parent
CLIENT=Path('E:/work/mmorpg-client')
src=(CLIENT/'Assets/Scripts/UI/Ugui/Jubaozhai/JubaozhaiWindow.cs').read_text(encoding='utf-8-sig')
def method(signature,replacement):
    global src
    start=src.index(signature);brace=src.index('{',start);level=1;p=brace+1
    while level:
        if src[p]=='{':level+=1
        elif src[p]=='}':level-=1
        p+=1
    src=src[:start]+replacement+src[p:]
src=src.replace('public sealed class JubaozhaiWindow : IDisposable','public sealed partial class JubaozhaiWindow : IDisposable')
method('        public JubaozhaiWindow(UnityEngine.Transform parent, JubaozhaiState state = null)', '''        public JubaozhaiWindow(UnityEngine.Transform parent, JubaozhaiState state = null)
        {
            State = state ?? new JubaozhaiState();
            _root = QdaoUguiFactory.CreateStretch("JubaozhaiWindow", parent, Vector4.zero);
            _root.gameObject.SetActive(false);
            var shade = _root.gameObject.AddComponent<Image>(); shade.color = new Color(.025f, .10f, .08f, .65f); shade.raycastTarget = true;
            _root.gameObject.AddComponent<GameplayInputBlocker>();
            _frame = QdaoUguiFactory.CreateCenteredRect("JubaozhaiFrame", _root, 1932, 814);
            _frame.gameObject.AddComponent<JubaozhaiDesignFit>();
            _frameInput = _frame.gameObject.AddComponent<CanvasGroup>();
            NativeArt(_frame, "native-frame", 0, 0, 1932, 814);
            NativeHit(_frame, "JubaoClose", "", 1735, 60, 65, 62, Hide);
            _topTabs[0] = Button(_frame, "JubaoTab_Consignment", "寄售列表", 507, 136, 253, 56,
                () => State.SetTab(JubaozhaiTab.Consignment), key: "tab_normal", fontSize: 30);
            _topTabs[1] = Button(_frame, "JubaoTab_PublicNotice", "公示列表", 763, 136, 245, 56,
                () => State.SetTab(JubaozhaiTab.PublicNotice), key: "tab_normal", fontSize: 30);
            Button(_frame, "JubaoEstimate", "估价", 1425, 136, 137, 53,
                () => ShowNotice("估价", "估价功能尚未开放，开放后可在此查看商品估价。"), fontSize: 27);
            Button(_frame, "JubaoRules", "规则", 1578, 136, 139, 53,
                () => ShowNotice("聚宝斋规则", "寄售、公示、拍卖和货架规则尚未开放。交易规则以正式开放后的说明为准。"), fontSize: 27);
            var clearSearch = Button(_frame, "JubaoClearSearch", "清空搜索", 200, 198, 263, 50,
                () => { _search.SetTextWithoutNotify(""); State.SetSearch(""); }, key: "tab_normal", fontSize: 28);
            NativeArt(clearSearch.transform, "category-search", 19, 5, 35, 37);
            _favoritesOnly = Button(_frame, "JubaoFavoritesOnly", "收藏", 200, 251, 263, 50,
                () => State.SetFavoritesOnly(!State.FavoritesOnly), key: "tab_normal", fontSize: 29);
            var favoritesLabel = _favoritesOnly.GetComponentInChildren<TMP_Text>(); favoritesLabel.alignment = TextAlignmentOptions.MidlineLeft;
            favoritesLabel.rectTransform.anchoredPosition = new Vector2(65, 0); favoritesLabel.rectTransform.sizeDelta = new Vector2(151, 50);
            NativeArt(_favoritesOnly.transform, "category-favorite", 19, 6, 35, 36);
            Text(_favoritesOnly.transform, "›", 224, 0, 26, 50, 31, Gold, alignment: TextAlignmentOptions.Center).name = "FavoriteMarker";
            _categoryScroll = NativeCategoryScroll(_frame, "JubaoCategories", 200, 304, 263, 431, out _categoryContent);
            NativeArt(_frame, "table-header", 500, 198, 1226, 51);
            _sort = NativeHit(_frame, "JubaoSort", "默认排序 · 切换", 580, 204, 424, 39, CycleSort, 25);
            Text(_frame, "信息", 1097, 204, 191, 39, 27, alignment: TextAlignmentOptions.Center);
            Text(_frame, "剩余时间", 1517, 204, 169, 39, 27, alignment: TextAlignmentOptions.Center);
            _rowScroll = NativeCategoryScroll(_frame, "JubaoRowsViewport", 501, 247, 1224, 451, out _rows);
            string[] sectionLabels = { "寄\\n售", "拍\\n卖", "货\\n架" };
            float[] sectionY = { 188, 351, 512 }, sectionHeight = { 159, 160, 147 };
            for (int i = 0; i < _sections.Length; i++)
            {
                var section = (JubaozhaiSection)i;
                _sections[i] = NativeButton(_frame, "JubaoSection_" + section, sectionLabels[i], i == 2 ? "section-normal-short" : "section-normal", 1737, sectionY[i],
                    93, sectionHeight[i], () => State.SetSection(section), 35);
                _sections[i].GetComponentInChildren<TMP_Text>().textWrappingMode = TextWrappingModes.Normal;
            }
            _search = QdaoUguiFactory.CreateInputField("JubaoSearch", _frame, 504, 712, 331, 56,
                JubaozhaiCatalog.SearchPlaceholder, 64, Load("input"));
            _search.textComponent.fontSize = 25; ((TMP_Text)_search.placeholder).fontSize = 24;
            _search.textComponent.richText = false; ((TMP_Text)_search.placeholder).richText = false;
            _search.onSubmit.AddListener(value => State.SetSearch(value));
            NativeButton(_frame, "JubaoSearchSubmit", "", "search-button", 820, 707, 78, 63, () => State.SetSearch(_search.text));
            _previous = NativeButton(_frame, "JubaoPreviousPage", "", "page-previous", 985, 718, 47, 48, () => State.SetPage(State.PageNumber - 1));
            _pageLabel = Text(_frame, "1 / 1", 1036, 720, 96, 42, 25, alignment: TextAlignmentOptions.Center);
            _next = NativeButton(_frame, "JubaoNextPage", "", "page-next", 1134, 718, 47, 48, () => State.SetPage(State.PageNumber + 1));
            _favorite = Button(_frame, "JubaoFavorite", "收藏", 1295, 710, 170, 58, ToggleSelectedFavorite, fontSize: 29);
            _view = Button(_frame, "JubaoView", "查看", 1475, 704, 249, 67, ShowSelectedDetails, true, fontSize: 36);
            _selection = Text(_frame, "选择商品后可查看详情", 502, 771, 758, 19, 16, Muted);
            _selection.gameObject.SetActive(false);
            NativeCategoryScroll(_frame, "JubaoStatusScroll", 1027, 134, 380, 61, out var statusContent);
            _status = Text(statusContent, "聚宝斋尚未开放", 0, 0, 375, 61, 20, Muted, true, TextAlignmentOptions.Center);
            State.Changed += StateChanged; Render();
        }''')
method('        private void BuildCategories()', '''        private void BuildCategories()
        {
            Clear(_categoryContent); _categoryButtons.Clear(); _subcategoryButtons.Clear();
            float y = 0, selectedY = 0;
            foreach (var category in JubaozhaiCatalog.AllCategories)
            {
                var captured = category;
                var button = Button(_categoryContent, "Category_" + captured, JubaozhaiCatalog.CategoryName(captured), 0, y, 263, 50,
                    () => { if (State.Category == captured) State.SetSubcategory(""); else State.SetCategory(captured); }, key: "tab_normal", fontSize: 29);
                var label = button.GetComponentInChildren<TMP_Text>(); label.alignment = TextAlignmentOptions.MidlineLeft;
                label.rectTransform.anchoredPosition = new Vector2(65, 0); label.rectTransform.sizeDelta = new Vector2(151, 50);
                NativeArt(button.transform, "category-" + captured.ToString().ToLowerInvariant(), 18, 5, 36, 39);
                Text(button.transform, "›", 224, 0, 26, 50, 31, Gold, alignment: TextAlignmentOptions.Center).name = "CategoryMarker";
                _categoryButtons.Add(captured, button);
                if (State.Category == captured) selectedY = y;
                y += 54;
                if (State.Category != captured || JubaozhaiCatalog.SubcategoriesFor(captured).Count == 0) continue;
                // Clicking the active category selects all its subcategories, as in the approved design.
                foreach (var subcategory in JubaozhaiCatalog.SubcategoriesFor(captured))
                {
                    string value = subcategory;
                    _subcategoryButtons[value] = Button(_categoryContent, "Subcategory_" + value, value, 7, y, 249, 43, () => State.SetSubcategory(value), key: "tab_normal", fontSize: 26);
                    y += 46;
                }
                y += 18;
            }
            _categoryContent.sizeDelta = new Vector2(263, Math.Max(431, y));
            Canvas.ForceUpdateCanvases(); LayoutRebuilder.ForceRebuildLayoutImmediate((RectTransform)_categoryScroll.transform);
            _categoryScroll.StopMovement();
            float range = Mathf.Max(0, _categoryContent.rect.height - _categoryScroll.viewport.rect.height);
            // The first category stays at the source's native y=304. Later categories scroll into reach.
            float offset = Mathf.Clamp(selectedY - 54, 0, range);
            _categoryScroll.verticalNormalizedPosition = range > 0 ? 1 - offset / range : 1;
            _builtCategory = State.Category;
        }''')
method('        private void RenderRow(JubaozhaiListing item, int index)', '''        private void RenderRow(JubaozhaiListing item, int index)
        {
            var row = Button(_rows, "JubaoRow_" + item.Id, "", 0, index * 114, 1224, 108,
                () => SelectListing(item.Id), key: item.Id == SelectedId ? "row_selected" : "row_normal");
            _rowButtons[item.Id] = row;
            DrawIcon(row.transform, item, 38, -6, 140);
            var name = Text(row.transform, item.Name, 224, 12, 350, 43, 31); name.fontStyle = FontStyles.Bold;
            name.enableAutoSizing = true; name.fontSizeMin = 24; name.fontSizeMax = 31;
            Text(row.transform, JubaozhaiCatalog.FormatPrice(item.Price), 226, 55, 350, 39, 30, QdaoUguiTheme.Html("#B82D25"));
            NativeSummary(row.transform, item.Summary, 590, 17, 407, 76, 27);
            _remainingLabels[item.Id] = Text(row.transform, State.RemainingTime(item), 1030, 26, 165, 48, 29, Ink, alignment: TextAlignmentOptions.Center);
            var selected = Text(row.transform, item.Id == SelectedId ? "已选择" : State.IsFavorite(item.Id) ? "已收藏" : "", 1040, 77, 145, 24,
                18, Gold, alignment: TextAlignmentOptions.Center);
            selected.name = "RowState";
        }''')
method('        private void RenderEmpty()', '''        private void RenderEmpty()
        {
            Art(_rows, "empty_guide", 187, 53, 409, 341, true);
            NativeArt(_rows, "empty-bubble", 504, 128, 451, 150);
            string title = State.FavoritesOnly ? "当前筛选下暂无收藏" : !string.IsNullOrWhiteSpace(State.Search) ? "未找到符合条件的商品" : JubaozhaiCatalog.EmptyTitle;
            Text(_rows, title, 579, 155, 316, 53, 29, alignment: TextAlignmentOptions.Center);
            Text(_rows, !State.IsDemo && !State.ServiceAvailable ? "聚宝斋服务尚未连接" : JubaozhaiCatalog.EmptyDescription, 579, 210, 316, 43,
                27, Muted, alignment: TextAlignmentOptions.Center);
        }''')
# Stateful query, selection, favorite, modal, timeout, detail and trading paths are otherwise untouched.
src=src.replace('for (int i = 0; i < _sections.Length; i++) Select(_sections[i], (int)State.Section == i);','for (int i = 0; i < _sections.Length; i++) NativeSelect(_sections[i], (int)State.Section == i, i == 2 ? "section-normal-short" : "section-normal", i == 2 ? "section-selected-short" : "section-selected");')
src=src.replace('SetButtonLabel(pair.Value, (active ? "已选 · " : "") + JubaozhaiCatalog.CategoryName(pair.Key));','SetButtonLabel(pair.Value, JubaozhaiCatalog.CategoryName(pair.Key));\n                var marker = pair.Value.transform.Find("CategoryMarker")?.GetComponent<TMP_Text>();\n                if (marker != null) { marker.text = active ? "✓" : "›"; marker.color = active ? Cream : Gold; }')
src=src.replace('Select(pair.Value, active, "button_secondary", "button_primary");','Select(pair.Value, active, "tab_normal", "tab_selected");')
src=src.replace('SetButtonLabel(pair.Value, (active ? "已选 · " : "") + (pair.Key.Length == 0 ? "全部" : pair.Key));','SetButtonLabel(pair.Value, pair.Key.Length == 0 ? "全部" : pair.Key);')
src=src.replace('            _pageItems = page.Items;','            _pageItems = page.Items;\n            PrepareNativeRows(page);')
src=src.replace('else for (int i = 0; i < page.Items.Count && i < 4; i++) RenderRow(page.Items[i], i);','else for (int i = 0; i < page.Items.Count; i++) RenderRow(page.Items[i], i);')
src=src.replace('SetButtonLabel(_favoritesOnly, State.FavoritesOnly ? "已选 · 仅看收藏" : "仅看收藏");','SetButtonLabel(_favoritesOnly, "收藏");\n            var favoriteMarker = _favoritesOnly.transform.Find("FavoriteMarker")?.GetComponent<TMP_Text>();\n            if (favoriteMarker != null) { favoriteMarker.text = State.FavoritesOnly ? "✓" : "›"; favoriteMarker.color = State.FavoritesOnly ? Cream : Gold; }')
src=src.replace('Select(_favoritesOnly, State.FavoritesOnly, "button_secondary", "button_primary");','Select(_favoritesOnly, State.FavoritesOnly, "tab_normal", "tab_selected");')
src=src.replace('SetButtonLabel(_sort, SortLabel(State.Sort) + " · 切换");','SetButtonLabel(_sort, NativeSortLabel(State.Sort));')
src=src.replace(': State.ServiceAvailable ? "收藏仅在本次登录保留" : "聚宝斋尚未开放";', ': State.ServiceAvailable ? "收藏仅在本次登录保留" : "聚宝斋尚未开放";\n            LayoutNativeStatus();')
# Match native original badge holes, retain true level/category rather than inventing elemental fields.
src=src.replace('float levelCenterX = equipment ? .942f : .846f;','float levelCenterX = equipment ? .144f : .846f;')
src=src.replace('x + size * levelCenterX, y + size * .644f, size * .43f, Cream, Ink, size * .185f);','x + size * levelCenterX, y + size * .644f, size * .38f, Ink, Cream, size * .185f);')
src=src.replace('x + size * (equipment ? .144f : .115f), y + size * .644f,','x + size * (equipment ? .942f : .115f), y + size * .644f,')
src=src.replace('size * (equipment ? .41f : .36f), Ink, Cream, size * .20f);','size * (equipment ? .38f : .33f), Gold, Cream, size * .20f);')
out=ROOT/'staged/Assets/Scripts/UI/Ugui/Jubaozhai/JubaozhaiWindow.cs';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(src,encoding='utf-8')
print(out)
