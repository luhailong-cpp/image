#include "player_skill.h"

#include <algorithm>
#include <unordered_set>

#include "muduo/base/Logging.h"
#include "table/code/class_table.h"
#include "table/code/skill_table.h"
#include "table/proto/tip/common_error_tip.pb.h"
#include "proto/common/component/player_skill_comp.pb.h"
#include "proto/common/component/player_comp.pb.h"
#include "proto/common/component/actor_comp.pb.h"
#include "proto/scene/player_skill.pb.h"
#include "modules/currency/system/currency_system.h"
#include "player/comp/player_frozen_comp.h"
#include "player/comp/player_ownership_comp.h"
#include "player/system/player_lifecycle.h"
#include "battle/system/player_battle.h"
#include "services/battle/system/class_skill_rules.h"
#include <thread_context/ecs_context.h>

namespace {
uint32_t ClassId(entt::entity player) {
    const auto* id = tlsEcs.actorRegistry.try_get<PlayerUint32Comp>(player);
    return id ? id->class_() : 0;
}
uint32_t Level(entt::entity player) {
    const auto* level = tlsEcs.actorRegistry.try_get<LevelComp>(player);
    return level ? std::max(1u, level->level()) : 1;
}
bool Writable(entt::entity player) {
    return tlsEcs.actorRegistry.valid(player) &&
        !tlsEcs.actorRegistry.any_of<PlayerFrozenComp, PlayerTravelHandoffComp>(player) &&
        !PlayerBattleSystem::IsInBattle(player);
}
bool FitsClass(const SkillTable& row, uint32_t classId) {
    if (classId >= 1 && classId <= 4) return row.class_id() == classId;
    return row.class_id() == 0;
}
uint32_t StoredRank(entt::entity player, uint32_t id) {
    const auto* list = tlsEcs.actorRegistry.try_get<PlayerSkillListComp>(player);
    if (!list) return 0;
    for (const auto& skill : list->skill_list()) {
        if (skill.skill_table_id() == id) return skill.rank();
    }
    return 0;
}
}

void PlayerSkillSystem::RegisterPlayer(entt::entity player) {
    SanitizeSkillList(player);
    auto& list = tlsEcs.actorRegistry.get_or_emplace<PlayerSkillListComp>(player);
    const auto classId = ClassId(player);
    if (classId >= 1 && classId <= 4) {
        for (const auto& row : SkillTableManager::Instance().FindAll().data()) {
            if (row.class_id() != classId || !row.initial_learned() ||
                Level(player) < row.unlock_level() || StoredRank(player,row.id()) != 0) continue;
            auto* skill = list.add_skill_list();
            skill->set_skill_table_id(row.id());
            skill->set_rank(1);
        }
        return;
    }
    // 非四职业历史实体保留原来的职业表种子，不再遍历所有职业。
    const auto* row = ClassTableManager::Instance().FindByIdSilent(classId).first;
    if (!row) return;
    for (auto id : row->skill()) {
        if (!id || !SkillTableManager::Instance().Exists(id) || StoredRank(player,id)) continue;
        auto* skill = list.add_skill_list();skill->set_skill_table_id(id);skill->set_rank(1);
    }
}

uint32_t PlayerSkillSystem::EffectiveRank(entt::entity player, uint32_t id) {
    if (!tlsEcs.actorRegistry.valid(player)) return 0;
    const auto* row = SkillTableManager::Instance().FindByIdSilent(id).first;
    if (!row || !FitsClass(*row,ClassId(player))) return 0;
    const auto rank = StoredRank(player,id);
    if (!row->class_id()) {
        const auto* list=tlsEcs.actorRegistry.try_get<PlayerSkillListComp>(player);
        if (list) for (const auto& skill:list->skill_list()) if(skill.skill_table_id()==id) return std::max(1u,rank);
        return 0;
    }
    return std::min(rank,classskill::RankLimit(Level(player),row->unlock_level()));
}

bool PlayerSkillSystem::HasSkill(entt::entity player, uint32_t id) { return EffectiveRank(player,id)>0; }

void PlayerSkillSystem::SanitizeSkillList(entt::entity player) {
    auto* list = tlsEcs.actorRegistry.try_get<PlayerSkillListComp>(player);
    if (!list) return;
    PlayerSkillListComp clean;
    std::unordered_set<uint32_t> seen;
    for (const auto& skill : list->skill_list()) {
        const auto* row = SkillTableManager::Instance().FindByIdSilent(skill.skill_table_id()).first;
        if (!row || !FitsClass(*row,ClassId(player)) || !seen.emplace(row->id()).second) continue;
        if (row->class_id() && !skill.rank()) continue;
        auto* kept=clean.add_skill_list();kept->CopyFrom(skill);
        kept->set_rank(std::clamp(skill.rank(),1u,classskill::kMaxRank));
    }
    list->Swap(&clean);
}

void PlayerSkillSystem::BuildSkillBook(entt::entity player, ListSkillsResponse& response) {
    response.Clear();
    const auto classId=ClassId(player),level=Level(player);
    response.set_class_id(classId);response.set_player_level(level);
    response.set_currency_balance(CurrencySystem::GetBalance(player,kCurrencyGold));
    if (const auto* list=tlsEcs.actorRegistry.try_get<PlayerSkillListComp>(player))
        response.mutable_skill_list()->CopyFrom(*list);
    else response.mutable_skill_list();
    for (const auto& row : SkillTableManager::Instance().FindAll().data()) {
        if (!row.class_id() || row.class_id()!=classId) continue;
        const auto rank=StoredRank(player,row.id()),limit=classskill::RankLimit(level,row.unlock_level());
        auto* view=response.add_catalog();
        view->set_skill_table_id(row.id());view->set_name(row.name());view->set_description(row.description());
        view->set_icon_key(row.icon_key());view->set_class_id(classId);view->set_category(row.category());
        view->set_passive(!row.passive_stat().empty());view->set_target_team(row.target_team());
        view->set_max_targets(row.max_targets());view->set_unlock_level(row.unlock_level());
        view->set_max_rank(classskill::kMaxRank);view->set_rank(rank);view->set_rank_limit(limit);
        view->set_mana_percent(row.mana_percent());view->set_cooldown_rounds(row.cooldown_rounds());
        if (rank<classskill::kMaxRank) view->set_next_rank_cost(classskill::UpgradeCost(rank+1,row.unlock_level()));
        if (!Writable(player)) view->set_upgrade_block_reason("战斗或传送中不可修习");
        else if (rank>=classskill::kMaxRank) view->set_upgrade_block_reason("已达十重");
        else if (rank>=limit) view->set_upgrade_block_reason("角色等级不足");
        else if (response.currency_balance()<view->next_rank_cost()) view->set_upgrade_block_reason("金币不足");
    }
}

void PlayerSkillSystem::UpgradeSkill(entt::entity player,const UpgradeSkillRequest& request,
                                     UpgradeSkillResponse& response) {
    response.Clear();
    const auto finish=[&](uint32_t error,const char* reason) {
        response.mutable_error_message()->set_id(error);response.set_stop_reason(reason);
        BuildSkillBook(player,*response.mutable_state());
    };
    if (!tlsEcs.actorRegistry.valid(player)) { response.mutable_error_message()->set_id(kEntityIsNull);return; }
    if (!Writable(player)) { finish(kInvalidParameter,"战斗或传送中不可修习");return; }
    if (request.count()!=1 && request.count()!=10) { finish(kInvalidParameter,"修习次数只能为1或10");return; }
    const auto* row=SkillTableManager::Instance().FindByIdSilent(request.skill_table_id()).first;
    if (!row || !row->class_id() || row->class_id()!=ClassId(player)) { finish(kInvalidTableId,"技能不属于当前职业");return; }
    const auto rank=StoredRank(player,row->id());
    if (rank!=request.expected_rank()) { finish(kInvalidParameter,"技能等级已变化，请按最新状态操作");return; }
    auto* list=tlsEcs.actorRegistry.try_get<PlayerSkillListComp>(player);
    if (!list) { finish(kInvalidParameter,"技能列表尚未加载");return; }
    const auto limit=classskill::RankLimit(Level(player),row->unlock_level());
    uint32_t target=rank,steps=0;
    uint64_t total=0,balance=CurrencySystem::GetBalance(player,kCurrencyGold);
    const char* stop="";
    while (steps<request.count()) {
        if (target>=classskill::kMaxRank) { stop="已达十重";break; }
        if (target>=limit) { stop="角色等级不足";break; }
        const auto cost=classskill::UpgradeCost(target+1,row->unlock_level());
        if (cost>balance-total) { stop="金币不足";break; }
        total+=cost;++target;++steps;
    }
    if (!steps) { finish(kInvalidParameter,stop);return; }
    // scene EventLoop 内连续提交；一次扣费与技能等级进入同一 player_database 快照。
    if (const auto error=CurrencySystem::DeductCurrency(player,kCurrencyGold,static_cast<int64_t>(total));error!=kSuccess) {
        finish(error,"扣费未成功，技能保持原等级");return;
    }
    PlayerSkillComp* owned=nullptr;
    for (auto& skill:*list->mutable_skill_list()) if(skill.skill_table_id()==row->id()) { owned=&skill;break; }
    if (!owned) { owned=list->add_skill_list();owned->set_skill_table_id(row->id()); }
    owned->set_rank(target);response.set_upgraded_count(steps);
    PlayerLifecycleSystem::SavePlayerToRedis(player);
    finish(kSuccess,stop);
}
