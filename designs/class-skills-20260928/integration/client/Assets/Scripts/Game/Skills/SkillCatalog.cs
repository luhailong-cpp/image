using System;
using System.Collections.Generic;
using UnityEngine;

namespace MmorpgClient.Game.Skills
{
    public static class SkillCatalog
    {
        [Serializable] private sealed class CatalogFile { public SkillDefinition[] skills; }
        private static Dictionary<uint, SkillDefinition> s_entries;

        public static SkillDefinition Find(uint id)
        {
            var current = SkillClient.Instance?.Snapshot?.Find(id)?.Definition;
            if (current != null) return current;
            EnsureLoaded();
            return s_entries.TryGetValue(id, out var skill) ? skill : null;
        }

        public static string Name(uint id) => Find(id)?.name ?? $"技能{id}";

        public static IReadOnlyList<SkillDefinition> ForClass(uint classId)
        {
            EnsureLoaded();
            var result = new List<SkillDefinition>();
            foreach (var skill in s_entries.Values)
                if (skill.classId == classId) result.Add(skill);
            result.Sort((a, b) => a.skillId.CompareTo(b.skillId));
            return result;
        }

        private static void EnsureLoaded()
        {
            if (s_entries != null) return;
            s_entries = new Dictionary<uint, SkillDefinition>();
            var asset = Resources.Load<TextAsset>("Skills/catalog");
            if (asset == null) { Debug.LogError("技能目录缺失：Resources/Skills/catalog.json"); return; }
            try
            {
                var data = JsonUtility.FromJson<CatalogFile>(asset.text);
                if (data?.skills == null) throw new FormatException("skills array missing");
                foreach (var skill in data.skills)
                {
                    if (skill == null || skill.skillId == 0 || string.IsNullOrWhiteSpace(skill.name))
                        throw new FormatException("invalid skill metadata");
                    s_entries.Add(skill.skillId, skill);
                }
            }
            catch (Exception error) { Debug.LogError("技能目录读取失败：" + error.Message); }
        }
    }
}
