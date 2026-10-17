#pragma once
#include <cstdint>
#include <entt/src/entt/entity/entity.hpp>
class ListSkillsResponse;
class UpgradeSkillRequest;
class UpgradeSkillResponse;
class PlayerSkillSystem {
public:
    static void RegisterPlayer(entt::entity player);
    static bool HasSkill(entt::entity player,uint32_t skillTableId);
    static uint32_t EffectiveRank(entt::entity player,uint32_t skillTableId);
    static void SanitizeSkillList(entt::entity player);
    static void BuildSkillBook(entt::entity player,ListSkillsResponse& response);
    static void UpgradeSkill(entt::entity player,const UpgradeSkillRequest& request,UpgradeSkillResponse& response);
};
