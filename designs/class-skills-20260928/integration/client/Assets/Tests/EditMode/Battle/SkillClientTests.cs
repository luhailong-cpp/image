using MmorpgClient.Game.Skills;
using MmorpgClient.Net;
using NUnit.Framework;

namespace MmorpgClient.Tests.EditMode.Battle
{
    public sealed class SkillClientTests
    {
        private FakeBattleTransport _transport;
        private SkillClient _client;

        [SetUp] public void Setup()
        {
            _transport = new FakeBattleTransport();
            _client = new SkillClient(_transport);
        }

        private static ListSkillsResponse State(uint rank = 1, ulong coins = 10000)
        {
            var response = new ListSkillsResponse { ClassId = 1, PlayerLevel = 40, CurrencyBalance = coins };
            response.Catalog.Add(new SkillCatalogEntry
            {
                SkillTableId = 1101, ClassId = 1, Name = "破阵惊锋", Rank = rank,
                RankLimit = 10, MaxRank = 10, UnlockLevel = 1, NextRankCost = 400,
                TargetTeam = 1, MaxTargets = 1, ManaPercent = 0.03,
            });
            return response;
        }

        private void Load(ListSkillsResponse state = null)
        {
            _client.RequestPanel();
            _transport.Calls[_transport.Calls.Count - 1].Respond(state ?? State());
        }

        [Test] public void ServerSnapshotDefinesOwnershipAndRank()
        {
            var state = State();
            state.Catalog.Add(new SkillCatalogEntry { SkillTableId = 1201, ClassId = 2, Rank = 10 });
            Load(state);
            Assert.That(_client.Snapshot.Entries.Count, Is.EqualTo(1));
            Assert.That(_client.Snapshot.Find(1101).Rank, Is.EqualTo(1));
            Assert.That(_client.Snapshot.Find(1201), Is.Null);
        }

        [Test] public void UpgradeSendsExpectedRankAndDoesNotOptimisticallySpend()
        {
            Load();
            _client.Upgrade(1101, 10);
            var call = _transport.Calls[1];
            Assert.That(call.MessageId, Is.EqualTo(MessageIds.UpgradeSkill));
            var request = (UpgradeSkillRequest)call.Request;
            Assert.That(request.ExpectedRank, Is.EqualTo(1));
            Assert.That(request.Count, Is.EqualTo(10));
            Assert.That(_client.Busy, Is.True);
            Assert.That(_client.Snapshot.CurrencyBalance, Is.EqualTo(10000));
            Assert.That(_client.Snapshot.Find(1101).Rank, Is.EqualTo(1));
        }

        [Test] public void DuplicateClickAndRefreshCannotOvertakePendingWrite()
        {
            Load();
            _client.Upgrade(1101, 1);
            _client.Upgrade(1101, 1);
            _client.RequestPanel();
            Assert.That(_transport.Calls.Count, Is.EqualTo(2));
        }

        [Test] public void PartialBatchAppliesExactReturnedRankAndBalance()
        {
            Load();
            string message = null;
            _client.Message += value => message = value;
            _client.Upgrade(1101, 10);
            _transport.Calls[1].Respond(new UpgradeSkillResponse
            { State = State(3, 800), UpgradedCount = 2, StopReason = "金币不足" });
            Assert.That(_client.Busy, Is.False);
            Assert.That(_client.Snapshot.Find(1101).Rank, Is.EqualTo(3));
            Assert.That(_client.Snapshot.CurrencyBalance, Is.EqualTo(800));
            Assert.That(message, Does.Contain("2级").And.Contain("金币不足"));
        }

        [Test] public void ServerRejectionStillRefreshesAuthoritativeState()
        {
            Load();
            string error = null;
            _client.Error += value => error = value;
            _client.Upgrade(1101, 1);
            _transport.Calls[1].Respond(new UpgradeSkillResponse
            { ErrorMessage = new TipInfoMessage { Id = 1 }, State = State(4, 700), StopReason = "技能状态已变化" });
            Assert.That(_client.Snapshot.Find(1101).Rank, Is.EqualTo(4));
            Assert.That(error, Is.EqualTo("技能状态已变化"));
        }

        [Test] public void DisconnectedReadCannotRestoreOldRoleState()
        {
            _client.RequestPanel();
            _transport.RaiseDisconnected();
            _transport.Calls[0].Respond(State());
            Assert.That(_client.Snapshot, Is.Null);
            Assert.That(_client.Loading, Is.False);
        }

        [Test] public void DisconnectedWriteCannotOverwriteNewSession()
        {
            Load();
            _client.Upgrade(1101, 1);
            _transport.RaiseDisconnected();
            Load(State(5));
            _transport.Calls[1].Respond(new UpgradeSkillResponse { State = State(2), UpgradedCount = 1 });
            Assert.That(_client.Snapshot.Find(1101).Rank, Is.EqualTo(5));
        }

        [Test] public void LearningUsesRankZeroAndOneStep()
        {
            Load(State(0));
            _client.Upgrade(1101, 1);
            var request = (UpgradeSkillRequest)_transport.Calls[1].Request;
            Assert.That(request.ExpectedRank, Is.Zero);
            Assert.That(request.Count, Is.EqualTo(1));
        }

        [Test] public void InsufficientFundsOrInvalidCountDoesNotSend()
        {
            Load(State(1, 399));
            _client.Upgrade(1101, 1);
            _client.Upgrade(1101, 2);
            Assert.That(_transport.Calls.Count, Is.EqualTo(1));
        }

        [Test] public void NetworkFailureClearsBusyWithoutGrantingRank()
        {
            Load();
            _client.Upgrade(1101, 1);
            _transport.Calls[1].FailWith("timeout");
            Assert.That(_client.Busy, Is.False);
            Assert.That(_client.Snapshot.Find(1101).Rank, Is.EqualTo(1));
        }

        [TestCase("enemy", 2, false)]
        [TestCase("enemy", 1, true)]
        [TestCase("ally", 2, true)]
        [TestCase("ally", 1, false)]
        public void TargetsRespectTeams(string mode, uint targetTeam, bool expected)
        {
            Assert.That(SkillRules.IsValidTarget(new SkillDefinition { targetTeam = mode }, 1, 2, 9,
                targetTeam, false, false), Is.EqualTo(expected));
        }

        [Test] public void SelfTargetRejectsOtherAlliesAndDeadTargets()
        {
            var skill = new SkillDefinition { targetTeam = "self" };
            Assert.That(SkillRules.IsValidTarget(skill, 1, 2, 1, 2, false, false), Is.True);
            Assert.That(SkillRules.IsValidTarget(skill, 1, 2, 9, 2, false, false), Is.False);
            Assert.That(SkillRules.IsValidTarget(skill, 1, 2, 1, 2, true, false), Is.False);
        }

        [Test] public void ManaRoundsUpAndFreeSkillRemainsFree()
        {
            var skill = new SkillDefinition { manaPercent = 0.03 };
            Assert.That(SkillRules.ManaCost(skill, 101), Is.EqualTo(4));
            Assert.That(SkillRules.ManaCost(skill, 1), Is.EqualTo(1));
            skill.manaPercent = 0;
            Assert.That(SkillRules.ManaCost(skill, 101), Is.Zero);
        }

        [Test] public void PassiveCannotBeSubmittedAsTargetedSkill()
        {
            var skill = new SkillDefinition { type = "passive", targetTeam = "self" };
            Assert.That(SkillRules.IsValidTarget(skill, 1, 2, 1, 2, false, false), Is.False);
        }

        [Test] public void FledAllyCannotBeHealed()
        {
            var skill = new SkillDefinition { targetTeam = "ally" };
            Assert.That(SkillRules.IsValidTarget(skill, 1, 2, 9, 2, false, true), Is.False);
        }
    }
}
