using MmorpgClient.Game.Battle.Presentation;
using NUnit.Framework;

namespace MmorpgClient.Tests.EditMode.Battle
{
    public sealed class SkillManaReplayTests
    {
        private static TurnResultS2C Cast(uint skillId = 1204)
        {
            var result = new TurnResultS2C();
            result.Events.Add(new BattleEventItem
            { EventType = eBattleEventType.BattleEventSkill, SourceId = 1, SkillTableId = skillId, GroupId = 1 });
            return result;
        }

        private static BattleEventItem Mana(ulong target, ulong amount, long delta, ulong after)
            => new BattleEventItem
            {
                EventType = eBattleEventType.BattleEventMana, SourceId = 1, TargetId = target,
                Value = amount, ManaDelta = delta, TargetManaAfter = after, GroupId = 1,
            };

        [Test] public void TaixuChengxinSelfRestoreHasPositiveDeltaAndServerManaAfter()
        {
            var result = Cast();
            result.Events.Add(Mana(1, 0, 0, 30));
            result.Events.Add(Mana(1, 24, 24, 54));
            var plan = TurnPlan.Build(result, 0);
            Assert.That(plan.Count, Is.EqualTo(1));
            Assert.That(plan.Beats[0].SkillId, Is.EqualTo(1204));
            Assert.That(plan.Beats[0].ActorManaDelta, Is.EqualTo(24));
            Assert.That(plan.Beats[0].ActorManaAfter, Is.EqualTo(54));
        }

        [Test] public void CostAndRestoreWithinSameActionAccumulateNetChange()
        {
            var result = Cast();
            result.Events.Add(Mana(1, 8, -8, 22));
            result.Events.Add(Mana(1, 24, 24, 46));
            var beat = TurnPlan.Build(result, 0).Beats[0];
            Assert.That(beat.ActorManaDelta, Is.EqualTo(16));
            Assert.That(beat.ActorManaAfter, Is.EqualTo(46));
        }

        [Test] public void ExplicitTargetDrainKeepsNegativeSign()
        {
            var result = Cast();
            result.Events.Add(Mana(2, 10, -10, 50));
            var target = TurnPlan.Build(result, 0).Beats[0].Targets[0];
            Assert.That(target.Value, Is.EqualTo(-10));
            Assert.That(target.ManaAfter, Is.EqualTo(50));
        }

        [Test] public void ExplicitZeroDoesNotFallBackToUnsignedValue()
        {
            var result = Cast();
            result.Events.Add(Mana(1, 24, 0, 100));
            Assert.That(TurnPlan.Build(result, 0).Beats[0].ActorManaDelta, Is.Zero);
        }

        [Test] public void RepeatedTargetManaChangesAccumulateAndKeepLatestServerValue()
        {
            var result = Cast();
            result.Events.Add(Mana(2, 20, 20, 70));
            result.Events.Add(Mana(2, 10, -10, 60));
            var beat = TurnPlan.Build(result, 0).Beats[0];
            Assert.That(beat.Targets.Count, Is.EqualTo(1));
            Assert.That(beat.Targets[0].Value, Is.EqualTo(10));
            Assert.That(beat.Targets[0].ManaAfter, Is.EqualTo(60));
        }

        [Test] public void OlderCasterCostWithoutSignedFieldRemainsCompatible()
        {
            var result = Cast(1201);
            result.Events.Add(new BattleEventItem
            {
                EventType = eBattleEventType.BattleEventMana, SourceId = 1, TargetId = 1,
                Value = 12, TargetManaAfter = 88, GroupId = 1,
            });
            Assert.That(TurnPlan.Build(result, 0).Beats[0].ActorManaDelta, Is.EqualTo(-12));
        }
    }
}
