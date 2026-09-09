from pathlib import Path

ROOT = Path('E:/work/mmorpg-client')
p = ROOT / 'Assets/Scripts/UI/Ugui/QdaoServerSelectView.cs'
s = p.read_text(encoding='utf-8-sig')
s = s.replace('public sealed class QdaoServerSelectView', 'public sealed partial class QdaoServerSelectView')
start = s.index('        private void BuildVisualTree()')
end = s.index('        private void ResolveArtSprites()', start)
s = s[:start] + '        private void BuildVisualTree() => BuildRefreshVisualTree();\n\n' + s[end:]
s = s.replace('            _eventsBound = true;', '            BindRefreshEvents();\n            _eventsBound = true;')
s = s.replace('            _eventsBound = false;', '            UnbindRefreshEvents();\n            _eventsBound = false;')
s = s.replace('            _app?.Run(LoadAnnouncements());', '            _app?.Run(LoadAnnouncements());\n            ShowLanding(true);')
s = s.replace('            _previewMode = true;\n            ValidatePrefabReferences();', '            _previewMode = true;\n            ShowLanding(false);\n            ValidatePrefabReferences();')
s = s.replace('            ShowCredentialPanel(true, true);\n            SetStatus("请输入账号和密码");\n        }\n\n        private void OnCredentialCancelClicked()', '            ShowLanding(true);\n            SetStatus(string.Empty);\n        }\n\n        private void OnCredentialCancelClicked()')
s = s.replace('            var zone = FindZone(_selectedZoneId);\n            if (zone == null)', '            var zone = FindRenderedZone(_selectedZoneId);\n            if (zone == null)')
s = s.replace('            // The blocker dims the bottom-bar status line,', '            if (_landingStatusText != null) _landingStatusText.text = value ?? string.Empty;\n            // The blocker dims the bottom-bar status line,')
s = s.replace('"云海宗", "清风谷", "碧落渊", "紫霄峰", "沧浪洲", "昆仑墟", "蓬莱岛", "瀛洲海"', '"青云一服", "蓬莱二服", "昆仑三服", "太和四服", "玉虚五服", "灵溪六服", "云梦七服", "天清八服"')
s = s.replace('                    status = "OPEN",\n                    load_level', '                    status = i == 5 ? "MAINTENANCE" : "OPEN",\n                    load_level')
start = s.index('        private void RefreshVisualState()')
end = s.index('        private static string ZoneDisplayName', start)
s = s[:start] + '''        private void RefreshVisualState()
        {
            var canInteract = !_busy;
            for (var i = 0; i < _topLabels.Length; i++)
            {
                bool active = i == _selectedTopTab;
                _topButtons[i].interactable = canInteract;
                QdaoRefreshArt.Skin(_topImages[i], active ? "tab_selected" : "tab_normal");
                _topLabels[i].color = active ? QdaoRefreshArt.Ivory : QdaoRefreshArt.Ink;
                _topSelectionMarks[i].enabled = false;
            }
            _topDefaultDimmer.enabled = false;
            for (var i = 0; i < _categoryTexts.Length; i++)
            {
                bool active = i == _selectedCategory;
                _categoryButtons[i].interactable = canInteract;
                QdaoRefreshArt.Skin(_categoryImages[i], active ? "list_row_selected" : "list_row_normal");
                _categoryTexts[i].color = active ? QdaoRefreshArt.Ivory : QdaoRefreshArt.Ink;
                _categorySelectionMarks[i].enabled = false;
            }
            _categoryDefaultDimmer.enabled = false;
            int pageCount = PageCount();
            _pageText.text = pageCount > 1 ? $"{_page + 1} / {pageCount}" : string.Empty;
            _prevPageButton.gameObject.SetActive(pageCount > 1);
            _nextPageButton.gameObject.SetActive(pageCount > 1);
            _prevPageButton.interactable = canInteract && _page > 0;
            _nextPageButton.interactable = canInteract && _page < pageCount - 1;
            _emptyListText.gameObject.SetActive(_filtered.Count == 0);
            _emptyListText.text = _serverListLoading ? "正在获取区服列表…"
                : _serverListFailed ? "暂时无法获取服务器\\n点击刷新重试"
                : "没有匹配的服务器\\n请修改搜索或切换分类";
            for (var slot = 0; slot < PageSize; slot++)
            {
                int index = _page * PageSize + slot;
                bool present = index < _filtered.Count;
                _serverButtons[slot].gameObject.SetActive(present);
                _serverEmptyCovers[slot].enabled = false;
                if (!present) continue;
                var zone = _filtered[index];
                bool selected = zone.zone_id == _selectedZoneId;
                bool closed = zone.status == "MAINTENANCE" || zone.status == "CLOSED" || zone.status == "PREVIEW";
                QdaoRefreshArt.Skin(_serverCardImages[slot], "server_card_wide_" +
                    (closed ? "disabled" : selected ? "selected" : "normal"));
                _serverButtons[slot].interactable = canInteract;
                _serverNames[slot].text = CardDisplayName(zone);
                _serverSubtitles[slot].text = ZoneSubtitle(zone);
                var ink = selected && !closed ? QdaoRefreshArt.Ivory : QdaoRefreshArt.Ink;
                _serverNames[slot].color = ink;
                _serverSubtitles[slot].color = ink;
                _serverDots[slot].color = StatusDotColor(zone);
                _serverDots[slot].enabled = true;
                _serverBadges[slot].enabled = !closed;
            }
            var chosen = FindRenderedZone(_selectedZoneId);
            bool enterable = chosen != null && chosen.status != "MAINTENANCE" &&
                chosen.status != "CLOSED" && chosen.status != "PREVIEW";
            _selectedText.text = chosen == null ? "当前选择：请选择区服" : $"当前选择：{CardDisplayName(chosen)}";
            var session = _app?.Session;
            var last = session != null && session.RecentZoneIds.Count > 0 ? FindZone(session.RecentZoneIds[0]) : null;
            _lastLoginText.text = last == null ? string.Empty : $"最近登录：{CardDisplayName(last)}";
            _enterText.text = _busy ? "进入中…" : "进入选角";
            _searchInput.interactable = canInteract;
            _accountInput.interactable = canInteract;
            _passwordInput.interactable = canInteract;
            _backButton.interactable = canInteract;
            _refreshButton.interactable = canInteract && !_serverListLoading;
            _refreshText.gameObject.SetActive(true);
            _enterButton.interactable = canInteract && enterable && !_serverListLoading;
            _credentialCancelButton.interactable = canInteract;
            _credentialSubmitButton.interactable = canInteract;
            _landingServers.interactable = canInteract;
            _landingAccount.interactable = canInteract;
            _landingEnter.interactable = canInteract && !_serverListLoading;
            _landingServerText.text = chosen == null ? "选择服务器  ›" : $"{CardDisplayName(chosen)}   ·   {ZoneSubtitle(chosen)}   ›";
        }

''' + s[end:]
p.write_text(s, encoding='utf-8')

# Every real input now owns its visual surface. Preserve adequate inset from
# ornate, image-authored corners while leaving text independently editable.
p = ROOT / 'Assets/Scripts/UI/Ugui/QdaoUguiFactory.cs'
s = p.read_text(encoding='utf-8-sig')
s = s.replace('new Vector4(12f, 8f, 8f, 8f)', 'new Vector4(backgroundSprite != null ? 40f : 12f, 8f, backgroundSprite != null ? 40f : 8f, 8f)')
p.write_text(s, encoding='utf-8')
print('Updated native login, server selection, credential modal and image-backed visual states.')
