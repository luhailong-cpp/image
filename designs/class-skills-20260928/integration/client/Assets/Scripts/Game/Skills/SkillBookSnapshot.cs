using System.Collections.Generic;

namespace MmorpgClient.Game.Skills
{
    public sealed class SkillEntryState
    {
        public uint Id;
        public SkillDefinition Definition;
        public uint Rank;
        public uint RankLimit;
        public ulong NextRankCost;
        public string LockedReason;
    }

    /// <summary>A complete server response, never patched optimistically by the UI.</summary>
    public sealed class SkillBookSnapshot
    {
        public uint ClassId;
        public uint PlayerLevel;
        public ulong CurrencyBalance;
        public readonly List<SkillEntryState> Entries = new();
        public SkillEntryState Find(uint id) => Entries.Find(skill => skill.Id == id);
    }
}
