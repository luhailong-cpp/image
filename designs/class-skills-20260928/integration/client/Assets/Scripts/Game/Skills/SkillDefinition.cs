using System;

namespace MmorpgClient.Game.Skills
{
    /// <summary>Presentation metadata. Learned ranks and wallet values always come from the server.</summary>
    [Serializable]
    public sealed class SkillDefinition
    {
        public uint id;
        public uint classId;
        public string className;
        public string name;
        public string type;
        public uint unlockLevel;
        public uint maxRank;
        public string targetTeam;
        public uint maxTargets;
        public double manaPercent;
        public uint cooldownRounds;
        public uint durationRounds;
        public string description;
        public string iconPath;

        public uint skillId => id;
        public string target => targetTeam;
        public uint targetCount => maxTargets;
        public bool IsPassive => type == "passive";
        public string IconResource => "UI/Skills/" + id;
        public string KindLabel => IsPassive ? "被动" : "主动";
        public string TargetLabel => target == "self" ? "自身" : target == "ally" ? "友方" : "敌方";
    }

    public static class SkillRules
    {
        public static bool IsValidTarget(SkillDefinition skill, ulong casterId, uint casterTeam,
            ulong targetId, uint targetTeam, bool dead, bool fled)
        {
            if (dead || fled || skill?.IsPassive == true) return false;
            if (skill == null) return true; // Legacy skills keep their existing target contract.
            if (skill.target == "self") return casterId == targetId;
            return skill.target == "ally" ? casterTeam == targetTeam : casterTeam != targetTeam;
        }

        public static ulong ManaCost(SkillDefinition skill, ulong maxMana)
        {
            if (skill == null || skill.IsPassive || skill.manaPercent <= 0) return 0;
            // Compute in decimal so large uint64 mana cannot wrap or lose precision.
            decimal cost = Math.Ceiling(maxMana * (decimal)skill.manaPercent);
            return cost >= ulong.MaxValue ? ulong.MaxValue : Math.Max(1UL, (ulong)cost);
        }
    }
}
