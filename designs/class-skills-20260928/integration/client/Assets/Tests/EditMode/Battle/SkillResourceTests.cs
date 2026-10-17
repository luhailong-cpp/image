using System.Collections.Generic;
using MmorpgClient.Game.Skills;
using MmorpgClient.UI.Ugui.Battle;
using NUnit.Framework;
using UnityEngine;

namespace MmorpgClient.Tests.EditMode.Battle
{
    public sealed class SkillResourceTests
    {
        [Test] public void AllThirtyTwoSkillsHaveUniqueNamesAndProductionSprites()
        {
            var names = new HashSet<string>();
            for (uint classId = 1; classId <= 4; classId++)
            {
                var skills = SkillCatalog.ForClass(classId);
                Assert.That(skills.Count, Is.EqualTo(8));
                int active = 0, passive = 0;
                foreach (var skill in skills)
                {
                    Assert.That(names.Add(skill.name), Is.True, skill.name);
                    Assert.That(Resources.Load<Sprite>(skill.IconResource), Is.Not.Null, skill.IconResource);
                    if (skill.IsPassive) passive++;
                    else
                    {
                        active++;
                        Assert.That(BattleArtCatalog.ResolveSkillFx(skill.skillId, false).FxId, Is.Not.Null.And.Not.Empty);
                    }
                }
                Assert.That(active, Is.EqualTo(5));
                Assert.That(passive, Is.EqualTo(3));
            }
            Assert.That(names.Count, Is.EqualTo(32));
        }
    }
}
