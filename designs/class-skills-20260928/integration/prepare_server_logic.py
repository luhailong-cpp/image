exec(open('E:/work/image/designs/class-skills-20260928/integration/prepare_server.py',encoding='utf-8').read().split("s=read('proto/common/component/player_skill_comp.proto')")[0])
s=read('cpp/libs/services/scene/player/system/player_database_loader.cpp')
s=replace(s,'\tPlayerSkillSystem::SanitizeSkillList(player);\n','')
s=replace(s,'tlsEcs.actorRegistry.emplace<PlayerUint32Comp>(player, message.uint32_pb_component());','tlsEcs.actorRegistry.emplace<PlayerUint32Comp>(player, message.uint32_pb_component());\n\tPlayerSkillSystem::SanitizeSkillList(player);')
write('cpp/libs/services/scene/player/system/player_database_loader.cpp',s)
s=read('cpp/libs/services/scene/battle/system/player_battle.cpp')
s=replace(s,'#include "player/system/player_pet.h"','#include "player/system/player_pet.h"\n#include "player/system/player_skill.h"')
s=replace(s,'\t\t\tbool castableInTurnBattle = true;','''            const auto rank = PlayerSkillSystem::EffectiveRank(player, skill.skill_table_id());
            if (rank == 0) continue;
            (*snapshot.mutable_skill_ranks())[skill.skill_table_id()] = rank;
\t\t\tbool castableInTurnBattle = true;''')
write('cpp/libs/services/scene/battle/system/player_battle.cpp',s)
s=read('cpp/nodes/scene/handler/rpc/player/player_skill_handler.cpp')
start=s.index('void SceneSkillClientPlayerHandler::ListSkills(')
s=s[:start]+'''void SceneSkillClientPlayerHandler::ListSkills(entt::entity player,const ::ListSkillsRequest* request,
    ::ListSkillsResponse* response)
{
///<<< BEGIN WRITING YOUR CODE
    PlayerSkillSystem::BuildSkillBook(player,*response);
///<<< END WRITING YOUR CODE
}

void SceneSkillClientPlayerHandler::UpgradeSkill(entt::entity player,const ::UpgradeSkillRequest* request,
    ::UpgradeSkillResponse* response)
{
///<<< BEGIN WRITING YOUR CODE
    PlayerSkillSystem::UpgradeSkill(player,*request,*response);
///<<< END WRITING YOUR CODE
}
'''
# 新技能只通过权威回合战斗施放，不能用旧实时接口绕过耗蓝/等级/敌我规则。
s=replace(s,'\tCHECK_PLAYER_REQUEST(request, SkillSystem::ReleaseSkill);','''    const auto* row = SkillTableManager::Instance().FindByIdSilent(skillTableId).first;
    if (row != nullptr && row->class_id() != 0) {
        response->mutable_error_message()->set_id(kInvalidParameter);
        return;
    }
\tCHECK_PLAYER_REQUEST(request, SkillSystem::ReleaseSkill);''')
write('cpp/nodes/scene/handler/rpc/player/player_skill_handler.cpp',s)

p='cpp/libs/services/battle/system/turn_battle_engine.h';s=read(p)
s=replace(s,'uint64_t SkillManaCost(const SkillTable& skillRow) const;','''uint64_t SkillManaCost(const BattleActorState& actor, const SkillTable& skillRow) const;
    uint32_t SkillRank(const BattleActorState& actor, const SkillTable& row) const;
    double PassiveBonus(const BattleActorState& actor, const std::string& stat) const;
    double StatMultiplier(const BattleActorState& actor, const std::string& stat) const;
    std::vector<uint64_t> ClassSkillTargets(const BattleActorState& actor, const SkillTable& row,
                                           uint64_t primary) const;''')
write(p,s)
p='cpp/libs/services/battle/system/turn_battle_engine.cpp';s=read(p)
s=replace(s,'#include "table/proto/tip/skill_error_tip.pb.h"','#include "table/proto/tip/skill_error_tip.pb.h"\n#include "system/class_skill_rules.h"\n#include <limits>')
s=replace(s,'        // 技能只收回合制可施放的(G6)', '''        // 快照中只有职业、等级和学习等级同时合法的条目才进入战斗。
        for (const auto& entry : snapshot.skill_ranks()) {
            const auto* row = dataProvider->FindSkill(entry.first);
            if (!row || row->class_id() != actor.class_id() || !row->class_id()) continue;
            const auto rank = std::min(entry.second, classskill::RankLimit(actor.level(),row->unlock_level()));
            if (rank > 0) (*actor.mutable_skill_ranks())[entry.first] = rank;
        }
        // 气血、法力被动只在战斗内生效；保持入场剩余比例，不能反复进场凭空补血。
        const auto scalePool = [](uint64_t value,double multiplier) {
            return static_cast<uint64_t>(std::min<long double>(
                static_cast<long double>(value)*multiplier,std::numeric_limits<uint64_t>::max()));
        };
        const double hpFactor=1.0+PassiveBonus(actor,"maxHp"),mpFactor=1.0+PassiveBonus(actor,"maxMp");
        actor.set_max_health(scalePool(actor.max_health(),hpFactor));
        actor.mutable_attributes()->set_health(scalePool(actor.attributes().health(),hpFactor));
        actor.set_max_mana(scalePool(actor.max_mana(),mpFactor));
        actor.mutable_attributes()->set_mana(scalePool(actor.attributes().mana(),mpFactor));
        // 技能只收回合制可施放的(G6)''')
s=replace(s,'if (skillRow == nullptr || !IsTurnBattleCastableSkill(*skillRow)) {','if (skillRow == nullptr || !IsTurnBattleCastableSkill(*skillRow) ||\n                (skillRow->class_id() && SkillRank(actor,*skillRow)==0)) {')
s=replace(s,'SkillManaCost(skillRow) > actor.attributes().mana()','SkillManaCost(actor,skillRow) > actor.attributes().mana()')
s=replace(s,'    (void)actor;\n    // 镜像 SkillSystem::ValidateTarget', '''    if (skillRow.class_id()) {
        if (skillRow.class_id()!=actor.class_id() || !SkillRank(actor,skillRow)) return kInvalidParameter;
        if (skillRow.target_team()==3) return targetId==0 || targetId==actor.actor_id() ? kSuccess : kSkillInvalidTarget;
        const auto* target=FindActor(targetId);
        if (!target || !IsActorActive(*target)) return kSkillInvalidTargetId;
        const bool ally=target->team_index()==actor.team_index();
        if ((skillRow.target_team()==1 && ally) || (skillRow.target_team()==2 && !ally)) return kSkillInvalidTarget;
        return kSuccess;
    }
    // 镜像 SkillSystem::ValidateTarget''')
s=replace(s,'    // 状态 map 的键按 proto 契约是 skill_table_id,分组语义靠反查各在冷技能的 cooldown_id。','''    if (skillRow.class_id()) {
        const auto it=actor.skill_cooldown_rounds().find(skillRow.id());
        return it!=actor.skill_cooldown_rounds().end() && it->second>0 ? kSkillCooldownNotReady : kSuccess;
    }
    // 状态 map 的键按 proto 契约是 skill_table_id,分组语义靠反查各在冷技能的 cooldown_id。''')
s=replace(s,'              [](const BattleActorState* lhs, const BattleActorState* rhs) {\n                  if (lhs->attributes().speed() != rhs->attributes().speed()) {\n                      return lhs->attributes().speed() > rhs->attributes().speed();\n                  }','''              [this](const BattleActorState* lhs, const BattleActorState* rhs) {
                  const auto priority=[this](const BattleActorState& actor) {
                      const auto found=pendingActions.find(actor.actor_id());
                      if (found==pendingActions.end() || found->second.action_type()!=BATTLE_ACTION_SKILL ||
                          CheckActionPrerequisites(actor,found->second)!=kSuccess) return 0;
                      const auto* row=dataProvider->FindSkill(found->second.skill_table_id());
                      return row ? row->initiative() : 0;
                  };
                  if (priority(*lhs)!=priority(*rhs)) return priority(*lhs)>priority(*rhs);
                  const auto lhsSpeed=lhs->attributes().speed()*StatMultiplier(*lhs,"speed");
                  const auto rhsSpeed=rhs->attributes().speed()*StatMultiplier(*rhs,"speed");
                  if (lhsSpeed!=rhsSpeed) return lhsSpeed>rhsSpeed;''')
s=replace(s,'    if (IsAreaSkill(*skillRow)) {','''    if (skillRow->class_id()) {
        targetIds=ClassSkillTargets(actor,*skillRow,action.target_id());
        if (targetIds.empty()) return;
    } else if (IsAreaSkill(*skillRow)) {''')
s=replace(s,'    const auto cooldownMs = dataProvider->GetCooldownDurationMs(skillRow->cooldown_id());','''    if (skillRow->class_id() && skillRow->cooldown_rounds()>0)
        (*actor.mutable_skill_cooldown_rounds())[action.skill_table_id()]=skillRow->cooldown_rounds()+1;
    const auto cooldownMs = skillRow->class_id() ? 0 : dataProvider->GetCooldownDurationMs(skillRow->cooldown_id());''')
s=replace(s,'    if (baseDamage > 0) {','''    const double rankFactor=skillRow.class_id() ? classskill::RankFactor(SkillRank(actor,skillRow)) : 1.0;
    if (skillRow.heal_multiplier()>0 || skillRow.heal_per_level()>0) {
        double amount=(actor.magic_attack()*StatMultiplier(actor,"magicAttack")*skillRow.heal_multiplier()+
            actor.level()*skillRow.heal_per_level())*rankFactor*(1.0+PassiveBonus(actor,"outgoingHeal"));
        if (target.max_health()>0 && static_cast<double>(target.attributes().health())/target.max_health()<skillRow.execute_heal_threshold())
            amount*=1.0+skillRow.execute_heal_bonus();
        auto* event=AppendEvent(result,BATTLE_EVENT_HEAL,actor.actor_id(),target.actor_id());
        event->set_skill_table_id(skillRow.id());event->set_value(ApplyHeal(target,amount));
        event->set_target_health_after(target.attributes().health());event->set_target_mana_after(target.attributes().mana());
    }
    if (skillRow.restore_mana_percent()>0) {
        const auto before=target.attributes().mana();
        const auto restored=static_cast<uint64_t>(std::ceil(target.max_mana()*skillRow.restore_mana_percent()));
        target.mutable_attributes()->set_mana(before+std::min(restored,target.max_mana()-before));
        auto* event=AppendEvent(result,BATTLE_EVENT_MANA,actor.actor_id(),target.actor_id());
        event->set_skill_table_id(skillRow.id());event->set_value(target.attributes().mana()-before);
        event->set_target_health_after(target.attributes().health());event->set_target_mana_after(target.attributes().mana());
    }
    uint32_t dispelled=0;
    for (int index=0;index<target.buffs_size() && dispelled<skillRow.dispel_count();) {
        const auto* buff=dataProvider->FindBuff(target.buffs(index).buff_table_id());
        if (buff && (buff->tag().contains("debuff") || buff->buff_type()==kBuffTypePoison ||
            buff->buff_type()==kBuffTypeBurn || buff->buff_type()==kBuffTypeSilence || buff->buff_type()==kBuffTypeStun)) {
            RemoveBuffAt(target,index,result);++dispelled;
        } else ++index;
    }
    if (baseDamage > 0) {''')
s=replace(s,'        const uint64_t attack = combatdamage::SelectAttack(\n            skillRow.damage_type(), actor.physical_attack(), actor.magic_attack());','''        const uint64_t attack = static_cast<uint64_t>(combatdamage::SelectAttack(
            skillRow.damage_type(), actor.physical_attack(), actor.magic_attack())*
            StatMultiplier(actor,skillRow.damage_type()==1 ? "physicalAttack" : "magicAttack"));''')
s=replace(s,'CalculateFinalDamage(actor, target, baseDamage, attack,\n                                                        skillRow.attack_multiplier(), isCritical)','CalculateFinalDamage(actor, target, baseDamage*rankFactor, attack,\n                                                        skillRow.attack_multiplier()*rankFactor, isCritical)')
s=replace(s,'uint64_t TurnBattleEngine::SkillManaCost(const SkillTable& skillRow) const {','''uint64_t TurnBattleEngine::SkillManaCost(const BattleActorState& actor, const SkillTable& skillRow) const {
    if (skillRow.class_id() && skillRow.mana_percent()>0)
        return std::max<uint64_t>(1,static_cast<uint64_t>(std::ceil(actor.max_mana()*skillRow.mana_percent())));''')
s=replace(s,'const uint64_t manaCost = SkillManaCost(skillRow);','const uint64_t manaCost = SkillManaCost(actor,skillRow);')
s=replace(s,'static_cast<double>(caster.attributes().critchance()) / 100.0, 0.0, 1.0','static_cast<double>(caster.attributes().critchance()) / 100.0 + PassiveBonus(caster,"crit"), 0.0, 1.0')
s=replace(s,'target.attributes().armor(), target.defense(), target.attributes().resistance(),','target.attributes().armor(), static_cast<uint64_t>(target.defense()*StatMultiplier(target,"defense")), target.attributes().resistance(),')
# 普攻物伤也吃被动和减攻，技能的物伤则在ApplySkillToTarget处明确处理。
s=replace(s,'actor.physical_attack(), 1.0, isCritical);','static_cast<uint64_t>(actor.physical_attack()*StatMultiplier(actor,"physicalAttack")), 1.0, isCritical);')
s=replace(s,'    if (rawHeal <= 0 || target.is_dead()) {','    if (!std::isfinite(rawHeal) || rawHeal <= 0 || target.is_dead()) {')
s=replace(s,'''    const auto healthAfter = std::min<uint64_t>(
        target.max_health(),
        static_cast<uint64_t>(static_cast<double>(healthBefore) + rawHeal));''','''    const auto healthAfter = healthBefore + static_cast<uint64_t>(std::min<long double>(
        rawHeal,target.max_health()>healthBefore ? target.max_health()-healthBefore : 0));''')
# 定位新增buff,只职业buff参与完整回合持续，旧buff口径不变。
s=replace(s,'    entry->set_buff_table_id(buffTableId);','    entry->set_buff_table_id(buffTableId);\n    if (buffRow->tag().contains("class_skill")) entry->set_applied_round(roundIndex);')
s=replace(s,'        // 刷新持续回合(实时 OnBuffRefresh 为 TODO;回合侧采用"重挂满时"口径)','        if (buffRow.tag().contains("class_skill")) existing.set_applied_round(roundIndex);\n        // 刷新持续回合(实时 OnBuffRefresh 为 TODO;回合侧采用"重挂满时"口径)')
s=replace(s,'        auto* entry = actor.mutable_buffs(index);\n        if (entry->remain_rounds() == 0)', '        auto* entry = actor.mutable_buffs(index);\n        if (entry->applied_round()==roundIndex) continue;\n        if (entry->remain_rounds() == 0)')
s=replace(s,'    settlement.set_health(actor->attributes().health());\n    settlement.set_mana(actor->attributes().mana());','''    // 被动池只在本场生效，按同一倍率折回scene口径，避免重复进场制造生命/法力。
    settlement.set_health(static_cast<uint64_t>(actor->attributes().health()/(1.0+PassiveBonus(*actor,"maxHp"))));
    settlement.set_mana(static_cast<uint64_t>(actor->attributes().mana()/(1.0+PassiveBonus(*actor,"maxMp"))));''')
idx=s.rfind('}  // namespace turnbattle')
extra='''
uint32_t TurnBattleEngine::SkillRank(const BattleActorState& actor,const SkillTable& row) const {
    if (!row.class_id()) return 1;
    if (row.class_id()!=actor.class_id()) return 0;
    const auto it=actor.skill_ranks().find(row.id());
    return it==actor.skill_ranks().end() ? 0 : std::min(it->second,classskill::RankLimit(actor.level(),row.unlock_level()));
}
double TurnBattleEngine::PassiveBonus(const BattleActorState& actor,const std::string& stat) const {
    double sum=0;
    // protobuf map遍历序不稳定；浮点相加按技能ID排序后执行。
    std::map<uint32_t,uint32_t> ranks(actor.skill_ranks().begin(),actor.skill_ranks().end());
    for (const auto& [id,rank]:ranks) {
        const auto* row=dataProvider->FindSkill(id);
        if (row && row->passive_stat()==stat && SkillRank(actor,*row)>0)
            sum+=row->passive_percent()*classskill::PassiveFactor(rank);
    }
    return sum;
}
double TurnBattleEngine::StatMultiplier(const BattleActorState& actor,const std::string& stat) const {
    double positive=0,negative=0;
    const uint32_t type=stat=="defense" ? 11 : stat=="physicalAttack" ? 10 : stat=="speed" ? 13 : 999;
    for (const auto& entry:actor.buffs()) {
        const auto* row=dataProvider->FindBuff(entry.buff_table_id());
        if (!row || !row->tag().contains("class_skill") || row->buff_type()!=type || row->interval_effect_size()==0) continue;
        positive=std::max(positive,row->interval_effect(0));negative=std::min(negative,row->interval_effect(0));
    }
    return std::max(.1,1.0+PassiveBonus(actor,stat)+positive+negative);
}
std::vector<uint64_t> TurnBattleEngine::ClassSkillTargets(const BattleActorState& actor,const SkillTable& row,uint64_t primary) const {
    if (row.target_team()==3) return {actor.actor_id()};
    std::vector<const BattleActorState*> candidates;
    for (const auto& target:actors) {
        if (!IsActorActive(target)) continue;
        const bool ally=actor.team_index()==target.team_index();
        if ((row.target_team()==1 && !ally) || (row.target_team()==2 && ally)) candidates.push_back(&target);
    }
    std::sort(candidates.begin(),candidates.end(),[primary,&row](const auto* a,const auto* b) {
        if ((a->actor_id()==primary)!=(b->actor_id()==primary)) return a->actor_id()==primary;
        if (row.heal_multiplier()>0) {
            const auto ar=static_cast<double>(a->attributes().health())/std::max<uint64_t>(1,a->max_health());
            const auto br=static_cast<double>(b->attributes().health())/std::max<uint64_t>(1,b->max_health());
            if (ar!=br) return ar<br;
        }
        if (a->formation_slot()!=b->formation_slot()) return a->formation_slot()<b->formation_slot();
        return a->actor_id()<b->actor_id();
    });
    std::vector<uint64_t> ids;
    for (const auto* target:candidates) {
        if (ids.size()>=std::max(1u,row.max_targets())) break;
        ids.push_back(target->actor_id());
    }
    return ids;
}
'''
s=s[:idx]+extra+'\n'+s[idx:]
write(p,s)
print('staged scene and battle source')
