"""Keep the existing regression suite; update only the changed sprite/font presentation contract."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent
CLIENT=Path('E:/work/mmorpg-client')
source=CLIENT/'Assets/Tests/EditMode/Guild/GuildUiTests.cs'
s=source.read_text(encoding='utf-8-sig')
old='''            Assert.That(crest.sprite, Is.SameAs(Resources.Load<Sprite>("UI/Ugui/GuildV2/crest")));
            var images = _root.GetComponentsInChildren<Image>();
            Assert.That(images.Single(i => i.name == "title_plate").preserveAspect, Is.True);
            Assert.That(images.Single(i => i.name == "close_tassel").raycastTarget, Is.False);
            Assert.That(images.Single(i => i.name == "window_frame").sprite.border, Is.EqualTo(new Vector4(97, 74, 97, 99)));'''
new='''            Assert.That(crest.sprite, Is.SameAs(Resources.Load<Sprite>("UI/Ugui/GuildFidelity20261016/guild_crest")));
            Assert.That(crest.preserveAspect, Is.True);
            var images = _root.GetComponentsInChildren<Image>();
            var shell = images.Single(i => i.name == "guild_empty_shell");
            Assert.That(shell.raycastTarget, Is.False);
            Assert.That(shell.sprite.rect.size, Is.EqualTo(new Vector2(1932, 814)));
            foreach (string key in new[] { "guild_tab_selected", "guild_tab_normal", "guild_announcement", "guild_button_primary",
                "guild_button_secondary", "guild_row_normal", "guild_row_self", "guild_progress_track", "guild_progress_fill" })
                Assert.That(Resources.Load<Sprite>("UI/Ugui/GuildFidelity20261016/" + key), Is.Not.Null, key);
            Assert.That(Resources.Load<Sprite>("UI/Ugui/GuildFidelity20261016/guild_announcement").border,
                Is.EqualTo(new Vector4(18, 15, 18, 15)));'''
if old not in s:raise RuntimeError('Expected original sprite assertion changed; merge test presentation update manually')
s=s.replace(old,new,1)
old_font='''if (!text.gameObject.activeInHierarchy || string.IsNullOrEmpty(text.text) || text.font != body
                    || text.textWrappingMode != TextWrappingModes.NoWrap) continue;'''
new_font='''if (!text.gameObject.activeInHierarchy || string.IsNullOrEmpty(text.text)
                    || (text.font != body && text.font != QdaoUguiTheme.ResolveFont())
                    || text.textWrappingMode != TextWrappingModes.NoWrap) continue;'''
if old_font not in s:raise RuntimeError('Expected original typography helper changed; merge test font update manually')
s=s.replace(old_font,new_font,1)
out=ROOT/'client/Assets/Tests/EditMode/Guild/GuildUiTests.cs'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(s,encoding='utf-8')
out.with_name(out.name+'.meta').write_bytes(source.with_name(source.name+'.meta').read_bytes())
record={'source':str(source),'sourceSha256Before':hashlib.sha256(source.read_bytes()).hexdigest(),'staged':str(out.relative_to(ROOT)).replace('\\','/'),'changes':['Sprite presentation assertion uses original-matched 24 Sprite package and full shell','Body-line-fit helper checks both shared body font and mail/guild SimKai; it does not skip new font text'],'allBusinessAssertionsPreserved':True,'testsRun':False}
(ROOT/'staged-tests-manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
