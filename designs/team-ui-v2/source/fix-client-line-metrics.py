from pathlib import Path
p=Path('E:/work/mmorpg-client/Assets/Scripts/UI/Ugui/Team/TeamWindow.cs')
s=p.read_text(encoding='utf-8-sig')
s=s.replace('var label = Text(parent, value, x, y, w, h, size, color ?? BodyInk, alignment: alignment);','// Noto CJK line metrics exceed the old KaiTi boxes; Ellipsis otherwise hides a whole line.\n            h = Mathf.Max(h, size * 1.6f);\n            var label = Text(parent, value, x, y, w, h, size, color ?? BodyInk, alignment: alignment);')
s=s.replace('Level(role), 628, 22, 144, 56, 30)','Level(role), 628, 22, 144, 56, role.Level > 0 ? 30 : 26)')
p.write_text(s,encoding='utf8')
p=Path('E:/work/mmorpg-client/Assets/Editor/TeamUiVerification.cs');s=p.read_text(encoding='utf-8-sig')
s=s.replace('foreach (var label in go.GetComponentsInChildren<TMP_Text>(true)) label.ForceMeshUpdate(true, true);','''foreach (var label in go.GetComponentsInChildren<TMP_Text>(true))
                    {
                        label.ForceMeshUpdate(true, true);
                        if (!label.gameObject.activeInHierarchy || string.IsNullOrWhiteSpace(label.text)) continue;
                        bool visibleGlyph = false;
                        for (int character = 0; character < label.textInfo.characterCount; character++)
                            visibleGlyph |= label.textInfo.characterInfo[character].isVisible;
                        if (!visibleGlyph)
                            throw new InvalidOperationException("组队文字未渲染：" + label.name + " / " + label.text);
                    }''')
p.write_text(s,encoding='utf8')
