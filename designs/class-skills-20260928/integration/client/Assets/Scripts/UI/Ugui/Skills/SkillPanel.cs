using System.Collections.Generic;
using MmorpgClient.Game.Skills;
using MmorpgClient.UI.Ugui.Attribute;
using MmorpgClient.UI.Ugui.Battle;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

namespace MmorpgClient.UI.Ugui.Skills
{
    /// <summary>Character skill book. Decorative artwork is separate from live text and controls.</summary>
    public sealed class SkillPanel
    {
        private sealed class Row
        {
            public uint Id;
            public UiTextButton Button;
            public Image Icon;
            public TMP_Text Name, Rank, Kind, Mana, Target;
        }

        private readonly SkillUiRoot _owner;
        private readonly RectTransform _root;
        private readonly TMP_Text _classLabel, _description, _condition, _balance, _cost, _status;
        private readonly Image _selectedIcon;
        private readonly TMP_Text _selectedName;
        private readonly UiTextButton _upgrade, _upgradeTen, _refresh;
        private readonly List<Row> _rows = new();
        private readonly UiTextButton[] _filters = new UiTextButton[3];
        private SkillBookSnapshot _snapshot;
        private uint _selectedId;
        private int _filter = 1;
        public bool IsVisible => _root.gameObject.activeSelf;

        public SkillPanel(SkillUiRoot owner, UnityEngine.Transform parent)
        {
            _owner = owner;
            var frame = BattleUiWidgets.CreatePanel("CharacterSkillWindow", parent,
                CharacterAttributeVisuals.WindowX, CharacterAttributeVisuals.WindowY,
                CharacterAttributeVisuals.WindowW, CharacterAttributeVisuals.WindowH, Color.white);
            CharacterAttributeVisuals.Skin(frame, "window_frame");
            _root = (RectTransform)frame.transform;
            _root.gameObject.AddComponent<MmorpgClient.World.Tianyong.GameplayInputBlocker>();
            CharacterAttributeVisuals.Panel("TitlePlate", _root, 598f, -64f, 820f, 138f, "title_plate");
            Text("Title", _root, 678f, -22f, 660f, 65f, "角色技能", 44f, QdaoRefreshArt.Ivory,
                TextAlignmentOptions.Center);
            var close = CharacterAttributeVisuals.Button("Close", _root, 1980f, -24f, 88f, 88f, "关闭");
            CharacterAttributeVisuals.Skin(close.Plate, "close_button");
            close.Label.gameObject.SetActive(false);
            close.Button.onClick.AddListener(Hide);
            CharacterAttributeVisuals.Panel("CloseTassel", _root, 2052f, 24f, 32f, 80f, "close_tassel");

            _classLabel = Text("Class", _root, 105f, 76f, 900f, 60f, "正在同步技能…", 32f);
            string[] filters = { "全部", "主动", "被动" };
            for (int i = 0; i < filters.Length; i++)
            {
                int captured = i;
                _filters[i] = CharacterAttributeVisuals.Button("Filter" + i, _root,
                    1270f + i * 210f, 70f, 190f, 70f, filters[i], i == 0);
                _filters[i].Button.onClick.AddListener(() => { _filter = captured; Rebuild(); });
            }

            Text("NameHeader", _root, 240f, 153f, 400f, 48f, "技能名称", 28f);
            Text("RankHeader", _root, 695f, 153f, 180f, 48f, "等级", 28f);
            Text("KindHeader", _root, 940f, 153f, 180f, 48f, "类型", 28f);
            Text("ManaHeader", _root, 1200f, 153f, 340f, 48f, "法力 / 冷却", 28f);
            Text("TargetHeader", _root, 1665f, 153f, 220f, 48f, "作用目标", 28f);
            // Five active rows get larger icons; the all-skills view fits eight rows above the same footer.
            for (int i = 0; i < 8; i++) BuildRow(i);

            _selectedIcon = QdaoUguiFactory.CreateImage("SelectedIcon", _root, 105f, 700f, 112f, 112f, null);
            _selectedName = Text("SelectedName", _root, 242f, 687f, 410f, 52f, "选择一个技能", 32f);
            _condition = Text("Condition", _root, 242f, 742f, 450f, 80f, string.Empty, 25f);
            _condition.textWrappingMode = TextWrappingModes.Normal;
            _description = Text("Description", _root, 720f, 693f, 1170f, 96f, string.Empty, 28f);
            _description.textWrappingMode = TextWrappingModes.Normal;
            _balance = Text("Balance", _root, 105f, 830f, 520f, 48f, "金币：—", 27f);
            _cost = Text("Cost", _root, 635f, 830f, 470f, 48f, "下一级消耗：—", 27f);
            _status = Text("Status", _root, 720f, 794f, 1170f, 32f, string.Empty, 24f);
            _refresh = CharacterAttributeVisuals.Button("Refresh", _root, 1080f, 832f, 220f, 65f, "刷新");
            _refresh.Button.onClick.AddListener(() => _owner.Client?.RequestPanel());
            _upgrade = CharacterAttributeVisuals.Button("Upgrade", _root, 1320f, 832f, 260f, 65f, "学习", true);
            _upgrade.Button.onClick.AddListener(() => _owner.Client?.Upgrade(_selectedId, 1));
            _upgradeTen = CharacterAttributeVisuals.Button("UpgradeTen", _root, 1600f, 832f, 290f, 65f, "升级10次", true);
            _upgradeTen.Button.onClick.AddListener(() => _owner.Client?.Upgrade(_selectedId, 10));

            var attribute = CharacterAttributeVisuals.SideTab("AttributeTab", _root, 116f, "属\n性", false);
            attribute.Button.onClick.AddListener(() => { Hide(); AttributeUiRoot.Instance?.ShowPanel(false); });
            var allocation = CharacterAttributeVisuals.SideTab("AllocationTab", _root, 302f, "加\n点", false);
            allocation.Button.onClick.AddListener(() => { Hide(); AttributeUiRoot.Instance?.ShowPanel(true); });
            CharacterAttributeVisuals.SideTab("SkillTab", _root, 488f, "技\n能", true);
            Hide();
        }

        private void BuildRow(int index)
        {
            var row = new Row();
            row.Button = CharacterAttributeVisuals.Button("SkillRow" + index, _root,
                100f, 206f + index * 60f, 1800f, 60f, string.Empty);
            row.Button.Label.gameObject.SetActive(false);
            row.Icon = QdaoUguiFactory.CreateImage("Icon", row.Button.Rect, 10f, 4f, 52f, 52f, null);
            row.Icon.preserveAspect = true;
            row.Name = Text("Name", row.Button.Rect, 138f, 2f, 440f, 52f, string.Empty, 28f);
            row.Rank = Text("Rank", row.Button.Rect, 593f, 2f, 240f, 52f, string.Empty, 27f);
            row.Kind = Text("Kind", row.Button.Rect, 838f, 2f, 200f, 52f, string.Empty, 27f);
            row.Mana = Text("Mana", row.Button.Rect, 1098f, 2f, 440f, 52f, string.Empty, 26f);
            row.Target = Text("Target", row.Button.Rect, 1563f, 2f, 225f, 52f, string.Empty, 26f);
            row.Button.Button.onClick.AddListener(() => { _selectedId = row.Id; Rebuild(); });
            _rows.Add(row);
        }

        public void Show()
        {
            AttributeUiRoot.Instance?.HidePanel();
            Pet.PetUiRoot.Instance?.HidePanel();
            Guild.GuildUiRoot.Instance?.HidePanel();
            Gameplay.GameplayUiRoot.Instance?.HidePanel();
            _root.gameObject.SetActive(true);
            Apply(_owner.Client?.Snapshot);
            _owner.Client?.RequestPanel();
        }

        public void Hide() => _root.gameObject.SetActive(false);

        public void Apply(SkillBookSnapshot snapshot)
        {
            _snapshot = snapshot;
            Rebuild();
        }

        public void SetStatus(string value, bool error = false)
        {
            _status.text = value ?? string.Empty;
            _status.color = error ? AttributeUiStyle.WarnText : QdaoRefreshArt.Ink;
        }

        public void RefreshBusy()
        {
            bool pending = _owner.Client == null || _owner.Client.Busy || _owner.Client.Loading;
            _refresh.SetInteractable(!pending);
            var state = _snapshot?.Find(_selectedId);
            bool available = state != null && state.Rank < state.RankLimit &&
                string.IsNullOrEmpty(state.LockedReason) && state.NextRankCost <= _snapshot.CurrencyBalance;
            _upgrade.SetInteractable(!pending && available);
            _upgradeTen.SetInteractable(!pending && available && state.Rank > 0);
            if (_owner.Client?.Loading == true) SetStatus("正在同步技能…");
            else if (_owner.Client?.Busy == true) SetStatus("正在修习，请稍候…");
        }

        private void Rebuild()
        {
            for (int i = 0; i < _filters.Length; i++)
            {
                _filters[i].SetText((_filter == i ? "✓ " : string.Empty) + new[] { "全部", "主动", "被动" }[i]);
                CharacterAttributeVisuals.Skin(_filters[i].Plate, _filter == i ? "button_primary" : "button_secondary");
                _filters[i].Label.color = _filter == i ? QdaoRefreshArt.Ivory : QdaoRefreshArt.Ink;
            }
            var entries = new List<SkillDefinition>();
            if (_snapshot != null)
                foreach (var state in _snapshot.Entries)
                {
                    var definition = state.Definition;
                    if (_filter == 0 || (_filter == 2) == definition.IsPassive) entries.Add(definition);
                }
            if (entries.Count > 0 && !entries.Exists(skill => skill.skillId == _selectedId))
                _selectedId = entries[0].skillId;
            for (int i = 0; i < _rows.Count; i++)
            {
                var row = _rows[i];
                row.Button.SetVisible(i < entries.Count);
                if (i >= entries.Count) continue;
                var skill = entries[i];
                var state = _snapshot.Find(skill.skillId);
                float rowHeight = entries.Count <= 5 ? 88f : 60f;
                float rowGap = entries.Count <= 5 ? 6f : 0f;
                row.Button.Rect.anchoredPosition = new Vector2(100f, -(206f + i * (rowHeight + rowGap)));
                row.Button.Rect.sizeDelta = new Vector2(1800f, rowHeight);
                CharacterAttributeVisuals.Skin(row.Button.Plate, "button_secondary");
                row.Icon.rectTransform.sizeDelta = new Vector2(rowHeight - 8f, rowHeight - 8f);
                foreach (var label in new[] { row.Name, row.Rank, row.Kind, row.Mana, row.Target })
                    label.rectTransform.sizeDelta = new Vector2(label.rectTransform.sizeDelta.x, rowHeight - 4f);
                row.Id = skill.skillId;
                row.Icon.sprite = QdaoUguiTheme.LoadSprite(skill.IconResource);
                row.Icon.color = state?.Rank > 0 ? Color.white : new Color(0.70f, 0.70f, 0.70f, 1f);
                row.Name.text = (_selectedId == skill.skillId ? "✓ " : string.Empty) + skill.name;
                row.Rank.text = state == null ? "待同步" : state.Rank == 0 ? "未学习" : $"{state.Rank}/{skill.maxRank}";
                row.Kind.text = skill.KindLabel;
                row.Mana.text = skill.IsPassive ? "常驻 · 无消耗" : $"{skill.manaPercent * 100:0.#}% / {skill.cooldownRounds}回合";
                row.Target.text = skill.IsPassive ? "自身" : $"{skill.TargetLabel} {skill.targetCount}";
                row.Button.Plate.color = _selectedId == skill.skillId ? new Color(0.84f, 0.95f, 0.88f) : Color.white;
            }
            var chosen = _snapshot?.Find(_selectedId)?.Definition;
            var selected = _snapshot?.Find(_selectedId);
            _classLabel.text = _snapshot == null ? "技能尚未同步" :
                $"{(entries.Count > 0 ? entries[0].className : "职业技能")} · {_snapshot.PlayerLevel}级    五式主动 · 三项被动";
            _selectedIcon.sprite = chosen == null ? null : QdaoUguiTheme.LoadSprite(chosen.IconResource);
            _selectedIcon.enabled = chosen != null;
            _selectedName.text = chosen?.name ?? "选择一个技能";
            _description.text = chosen?.description ?? "连接服务器后查看本门派技能。";
            _condition.text = chosen == null ? string.Empty :
                selected == null ? "等待服务器同步" : !string.IsNullOrEmpty(selected.LockedReason) ? selected.LockedReason :
                selected.Rank >= chosen.maxRank ? "已修至圆满" :
                selected.Rank >= selected.RankLimit ? "提升角色等级可继续修习" :
                $"{chosen.unlockLevel}级可学 · 当前可修至{selected.RankLimit}级";
            _balance.text = _snapshot == null ? "金币：—" : $"金币：{_snapshot.CurrencyBalance:N0}";
            _cost.text = selected == null || selected.Rank >= selected.RankLimit ? "下一级消耗：—" : $"下一级消耗：{selected.NextRankCost:N0}";
            _upgrade.SetText(selected?.Rank > 0 ? "升级" : "学习");
            RefreshBusy();
        }

        private static TMP_Text Text(string name, UnityEngine.Transform parent, float x, float y, float w, float h,
            string text, float size, Color? color = null, TextAlignmentOptions alignment = TextAlignmentOptions.MidlineLeft)
        {
            var label = QdaoUguiFactory.CreateText(name, parent, x, y, w, h, text, size,
                color ?? QdaoRefreshArt.Ink, alignment);
            label.raycastTarget = false;
            return label;
        }
    }
}
