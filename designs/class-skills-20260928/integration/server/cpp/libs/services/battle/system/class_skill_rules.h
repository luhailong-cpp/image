#pragma once
#include <algorithm>
#include <cstdint>
// 学习、面板、战斗共用规则；所有费用用金币，等级只由服务端提交。
namespace classskill {
inline constexpr uint32_t kMaxRank = 10;
inline uint32_t RankLimit(uint32_t level, uint32_t unlock) {
    return level < unlock ? 0u : std::min(kMaxRank, 1u + (level - unlock) / 2u);
}
inline uint64_t UpgradeCost(uint32_t nextRank, uint32_t unlock) {
    return 100ull * nextRank * nextRank + 10ull * unlock;
}
inline double RankFactor(uint32_t rank) { return 1.0 + .02 * (std::clamp(rank,1u,kMaxRank)-1); }
inline double PassiveFactor(uint32_t rank) { return 1.0 + .05 * (std::clamp(rank,1u,kMaxRank)-1); }
}
