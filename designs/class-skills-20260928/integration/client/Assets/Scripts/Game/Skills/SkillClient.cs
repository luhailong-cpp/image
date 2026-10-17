using System;
using MmorpgClient.Game.Battle;
using MmorpgClient.Net;

namespace MmorpgClient.Game.Skills
{
    /// <summary>Single-flight, server-authoritative skill learning and upgrades over the existing gate RPC.</summary>
    public sealed class SkillClient
    {
        public static SkillClient Instance { get; private set; }
        private readonly IBattleTransport _net;
        private uint _generation;
        public SkillBookSnapshot Snapshot { get; private set; }
        public bool Busy { get; private set; }
        public bool Loading { get; private set; }
        public event Action Changed;
        public event Action<string> Error;
        public event Action<string> Message;

        public SkillClient(IBattleTransport transport)
        {
            _net = transport ?? throw new ArgumentNullException(nameof(transport));
            _net.Disconnected += OnDisconnected;
        }

        public static SkillClient Attach(IBattleTransport transport)
        {
            Instance = new SkillClient(transport);
            return Instance;
        }

        public void RequestPanel()
        {
            if (Busy || Loading) return;
            if (!_net.IsReady) { Error?.Invoke("尚未进入游戏，无法查看技能"); return; }
            uint generation = _generation;
            Loading = true;
            Changed?.Invoke();
            _net.Call(MessageIds.ListSkills, new ListSkillsRequest(), ListSkillsResponse.Parser,
                response =>
                {
                    if (generation != _generation) return;
                    Loading = false;
                    if (HasError(response.ErrorMessage))
                    {
                        Changed?.Invoke();
                        Error?.Invoke(DescribeError(response.ErrorMessage));
                        return;
                    }
                    Apply(response);
                    Changed?.Invoke();
                    Message?.Invoke(Snapshot.Entries.Count > 0 ? "技能已同步" : "服务器尚未提供该职业技能目录");
                },
                error => CompleteError(generation, error));
        }

        public void Upgrade(uint skillId, uint count)
        {
            if (Busy || Loading) return;
            if (!_net.IsReady || Snapshot == null) { Error?.Invoke("请先同步技能"); return; }
            var entry = Snapshot.Find(skillId);
            if (entry == null || (count != 1 && count != 10)) { Error?.Invoke("技能修习请求无效"); return; }
            if (!string.IsNullOrEmpty(entry.LockedReason)) { Error?.Invoke(entry.LockedReason); return; }
            if (entry.Rank >= entry.RankLimit) { Error?.Invoke("已达到当前可修习等级"); return; }
            if (entry.NextRankCost > Snapshot.CurrencyBalance) { Error?.Invoke("金币不足"); return; }
            uint generation = _generation;
            Busy = true;
            Changed?.Invoke();
            _net.Call(MessageIds.UpgradeSkill,
                new UpgradeSkillRequest { SkillTableId = skillId, ExpectedRank = entry.Rank, Count = count },
                UpgradeSkillResponse.Parser,
                response =>
                {
                    if (generation != _generation) return;
                    Busy = false;
                    if (response.State != null) Apply(response.State);
                    Changed?.Invoke();
                    if (HasError(response.ErrorMessage))
                    {
                        Error?.Invoke(!string.IsNullOrWhiteSpace(response.StopReason)
                            ? response.StopReason : DescribeError(response.ErrorMessage));
                        return;
                    }
                    string text = response.UpgradedCount > 0 ? $"修习成功，提升{response.UpgradedCount}级" : "技能未发生变化";
                    if (!string.IsNullOrWhiteSpace(response.StopReason)) text += " · " + response.StopReason;
                    Message?.Invoke(text);
                },
                error => CompleteError(generation, error));
        }

        private void Apply(ListSkillsResponse response)
        {
            var next = new SkillBookSnapshot
            {
                ClassId = response.ClassId,
                PlayerLevel = response.PlayerLevel,
                CurrencyBalance = response.CurrencyBalance,
            };
            foreach (var row in response.Catalog)
            {
                // The server owns available skills; a local art manifest never grants a skill.
                if (row.ClassId != next.ClassId) continue;
                next.Entries.Add(new SkillEntryState
                {
                    Id = row.SkillTableId,
                    Rank = row.Rank,
                    RankLimit = row.RankLimit,
                    NextRankCost = row.NextRankCost,
                    LockedReason = row.UpgradeBlockReason,
                    Definition = new SkillDefinition
                    {
                        id = row.SkillTableId, classId = row.ClassId,
                        className = ClassName(row.ClassId), name = row.Name,
                        description = row.Description, type = row.Passive ? "passive" : "active",
                        targetTeam = row.TargetTeam == 3 ? "self" : row.TargetTeam == 2 ? "ally" : "enemy",
                        maxTargets = row.MaxTargets, unlockLevel = row.UnlockLevel, maxRank = row.MaxRank,
                        manaPercent = row.ManaPercent, cooldownRounds = row.CooldownRounds,
                    },
                });
            }
            next.Entries.Sort((a, b) => a.Id.CompareTo(b.Id));
            Snapshot = next;
        }

        private static string ClassName(uint id) => id switch
        { 1 => "破军", 2 => "玄霄", 3 => "丹心", 4 => "逐风", _ => "职业技能" };

        private static bool HasError(TipInfoMessage tip) => tip != null && tip.Id != 0;
        private static string DescribeError(TipInfoMessage tip) => $"服务器未接受修习请求（{tip.Id}），请刷新技能后重试";

        private void CompleteError(uint generation, string error)
        {
            if (generation != _generation) return;
            Busy = false;
            Loading = false;
            Changed?.Invoke();
            Error?.Invoke(error);
        }

        private void OnDisconnected()
        {
            _generation++;
            Snapshot = null;
            Busy = false;
            Loading = false;
            Changed?.Invoke();
        }
    }
}
