from pathlib import Path
root = Path('E:/work/mmorpg-client/Assets/Scripts/UI/Ugui')
p = root / 'QdaoServerSelectView.cs'
s = p.read_text(encoding='utf-8-sig')
s = s.replace('            var zone = FindZone(zoneId);\n            if (zone != null) return zone;\n            foreach (var visible in _filtered)', '            foreach (var visible in _filtered)')
guard = '''            if (_serverListLoading) { SetStatus("正在获取区服列表，请稍候…"); return; }
            var zone = FindRenderedZone(_selectedZoneId);
            if (zone == null) { SetStatus("请先选择区服"); return; }
            if (zone.status == "MAINTENANCE") { SetStatus(FallbackMsg(zone.maintenance_msg, "该区服正在维护中")); return; }
            if (zone.status == "CLOSED") { SetStatus(FallbackMsg(zone.maintenance_msg, "该区服已关闭")); return; }
            if (zone.status == "PREVIEW") { SetStatus($"该区服尚未开放{OpenTimeSuffix(zone)}"); return; }
'''
old = '''            var zone = FindRenderedZone(_selectedZoneId);
            if (zone == null) { SetStatus("请先选择区服"); return; }
            if (zone.status == "MAINTENANCE") { SetStatus(FallbackMsg(zone.maintenance_msg, "该区服正在维护中")); return; }
            if (zone.status == "CLOSED") { SetStatus(FallbackMsg(zone.maintenance_msg, "该区服已关闭")); return; }
            if (zone.status == "PREVIEW") { SetStatus($"该区服尚未开放{OpenTimeSuffix(zone)}"); return; }
'''
assert s.count(old) == 1
s = s.replace(old, '')
token = '            if (_busy) { SetStatus("正在进入中,请稍候…"); return; }\n'
assert token in s
s = s.replace(token, token + guard)
s = s.replace('_landingEnter.interactable = canInteract && !_serverListLoading;', '_landingEnter.interactable = canInteract && !_serverListLoading && (chosen == null || enterable);')
s = s.replace('            var invalid = _screenArtSprite == null ||', '''            var invalid = _landingRoot == null || _serverRoot == null ||
                          _landingServers == null || _landingEnter == null || _landingAccount == null ||
                          _landingServerText == null || _landingStatusText == null || _emptyListText == null ||
                          _serverBadges == null || _serverBadges.Length != PageSize ||
                          _screenArtSprite == null ||''')
s = s.replace('                invalid = Array.Exists(_topImages, value => value == null) ||', '''                invalid = Array.Exists(_serverBadges, value => value == null || value.sprite == null) ||
                          !HasRaycastTarget(_landingServers) || !HasRaycastTarget(_landingEnter) ||
                          !HasRaycastTarget(_landingAccount) ||
                          Array.Exists(_topImages, value => value == null) ||''')
p.write_text(s, encoding='utf-8')

p = root / 'QdaoRefreshArt.cs'
s = p.read_text(encoding='utf-8-sig')
s = s.replace('            image.pixelsPerUnitMultiplier = Mathf.Max(1f,\n                sprite.rect.height / Mathf.Max(1f, image.rectTransform.rect.height));', '''            float minimum = asset == "main_frame" || asset == "content_panel" ? 1f : 0.01f;
            image.pixelsPerUnitMultiplier = Mathf.Max(minimum,
                sprite.rect.height / Mathf.Max(1f, image.rectTransform.rect.height));''')
p.write_text(s, encoding='utf-8')

p = root / 'QdaoServerSelectView.Visuals.cs'
s = p.read_text(encoding='utf-8-sig')
s = s.replace('            text = Label(name + "Text", button.transform, 28f, 0f, w - 56f, h, label,', '''            float sourceHeight = QdaoRefreshArt.Load(asset).rect.height;
            float padding = 78f * h / sourceHeight;
            text = Label(name + "Text", button.transform, padding, 0f, w - padding * 2f, h, label,''')
s = s.replace('            _screenArtSprite = QdaoRefreshArt.Load("sanctuary_background");', '''            _screenArtSprite = Resources.Load<Sprite>(QdaoRefreshArt.Root + "login_background");
            if (_screenArtSprite == null) _screenArtSprite = QdaoRefreshArt.Load("sanctuary_background");''')
s = s.replace('"五行奇谈", 112f, true', '"五行奇谈", 140f, true')
s = s.replace('"选择服务器", 51f, true', '"选择服务器", 62f, true')
s = s.replace('                _serverNames[i] = Label("ServerName_" + i, parent, 116f, 19f, 330f, 52f, "", 34f);', '                _serverNames[i] = Label("ServerName_" + i, parent, 116f, 19f, 330f, 52f, "", 38f);')
s = s.replace('            ((TMP_Text)_searchInput.placeholder).fontSize = 25f;', '''            ((TMP_Text)_searchInput.placeholder).fontSize = 25f;
            SetInputInsets(_searchInput, 70f);''')
s = s.replace('                ((TMP_Text)input.placeholder).fontSize = 28f;', '''                ((TMP_Text)input.placeholder).fontSize = 28f;
                SetInputInsets(input, 78f);''')
needle = '        public void ShowLanding(bool show)'
s = s.replace(needle, '''        private static void SetInputInsets(TMP_InputField input, float height)
        {
            float scale = height / 84f;
            input.textViewport.offsetMin = new Vector2(70f * scale, 12f * scale);
            input.textViewport.offsetMax = new Vector2(-64f * scale, -12f * scale);
        }

''' + needle)
p.write_text(s, encoding='utf-8')
print('Fixed filtered selection, entry guards, prefab validation and image/text sizing contracts.')
