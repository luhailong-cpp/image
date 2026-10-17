package main

// 仅清理 root 明确指定的本次 Unity 验收单人队伍和两个账号之间的好友边。
// 所有状态变化均走正式 RPC；不建角、不换线，不触及其他账号或队伍。
import (
	"errors"
	"fmt"
	"go.uber.org/zap"
	"os"
	friendpb "proto/friend"
	teampb "proto/team"
	"robot/config"
	"robot/generated/pb/game"
	"robot/logic/gameobject"
	"robot/metrics"
)

// 用户已在本会话明确允许清理本轮测试数据。仍只接受日志可证明的两个固定 run。
var cleanupUnityRun, cleanupUnityLeaderAccount, cleanupUnityMemberAccount string
var cleanupUnityLeaderID, cleanupUnityMemberID, cleanupUnityTeamID uint64

func selectCleanupUnityRun(run string) error {
	switch run {
	case "fcf7df80745d4021":
		cleanupUnityLeaderID, cleanupUnityMemberID, cleanupUnityTeamID = 2216, 2217, 74020166459785216
	case "d342a978cc8f456b":
		cleanupUnityLeaderID, cleanupUnityMemberID, cleanupUnityTeamID = 2218, 2219, 74022777799901184
	default:
		return errors.New("清理 run 不在用户授权的本次验收白名单内")
	}
	cleanupUnityRun = run
	cleanupUnityLeaderAccount = "robot_tui_" + run + "_leader"
	cleanupUnityMemberAccount = "robot_tui_" + run + "_member"
	return nil
}

func cleanupUnityCheckIdentity(account string, playerID uint64) error {
	if (account == cleanupUnityLeaderAccount && playerID == cleanupUnityLeaderID) ||
		(account == cleanupUnityMemberAccount && playerID == cleanupUnityMemberID) {
		return nil
	}
	return errors.New("登录返回的账号与角色编号不在精确清理白名单中，拒绝进场")
}

func cleanupUnityCheckTeam(playerID uint64, view *teampb.TeamView) error {
	if view == nil {
		return errors.New("正式队伍接口未返回角色视图，停止清理")
	}
	if view.GetTeamId() == 0 {
		return nil
	}
	if playerID != cleanupUnityLeaderID || view.GetTeamId() != cleanupUnityTeamID ||
		view.GetLeaderId() != cleanupUnityLeaderID || len(view.GetMembers()) != 1 ||
		view.GetMembers()[0].GetPlayerId() != cleanupUnityLeaderID {
		return fmt.Errorf("角色 %d 的队伍状态不符合授权单人队伍，不修改队伍: team_id=%d leader_id=%d members=%d",
			playerID, view.GetTeamId(), view.GetLeaderId(), len(view.GetMembers()))
	}
	return nil
}

func RunTeamInvitesCleanup(cfg *config.Config) (result error) {
	if err := selectCleanupUnityRun(os.Getenv("TEAM_INVITES_CLEANUP_RUN")); err != nil {
		return err
	}
	if cfg.GatewayAddr != "http://127.0.0.1:8081" || cfg.ZoneID != 1 || cfg.UseHttpLogin {
		return errors.New("清理仅允许既定本地 Gateway、区服 1 和现有 Gate 密码登录路径")
	}
	secret := os.Getenv("LOGIN_DEV_PASSWORD_SHARED_SECRET")
	if secret == "" {
		return errors.New("缺少登录凭证环境变量")
	}
	cfg.Password, cfg.AuthType = secret, "password"
	loginTestCfg = cfg
	stats := robotStatsRef
	if stats == nil {
		stats = metrics.NewStats()
	}
	var bots []*teamSmokeBot
	defer func() {
		for _, bot := range bots {
			if err := leaveGame(bot.gc, stats); err != nil {
				result = errors.Join(result, err)
			}
			sendDisconnectBestEffort(bot.gc)
			gameobject.PlayerList.Delete(bot.gc.PlayerId)
			bot.gc.Close()
		}
		if result == nil {
			zap.L().Info("TEAM_INVITES_UNITY_CLEANUP_OK", zap.String("run", cleanupUnityRun))
		}
	}()
	specs := []struct {
		account string
		id      uint64
	}{{cleanupUnityLeaderAccount, cleanupUnityLeaderID}, {cleanupUnityMemberAccount, cleanupUnityMemberID}}
	for _, spec := range specs {
		bot, err := teamSmokeLogin(cfg, "cleanup", spec.account, stats)
		if err != nil {
			return err
		}
		bots = append(bots, bot)
		if bot.gc.PlayerId != spec.id {
			return fmt.Errorf("精确账号与角色编号不符: expected=%d actual=%d", spec.id, bot.gc.PlayerId)
		}
		view, err := bot.myTeam()
		if err != nil {
			return err
		}
		if err := cleanupUnityCheckTeam(spec.id, view); err != nil {
			return err
		}
		zap.L().Info("TEAM_INVITES_UNITY_CLEANUP_IDENTITY_VERIFIED", zap.String("account", spec.account), zap.Uint64("player_id", spec.id), zap.Uint64("team_id", view.GetTeamId()))
	}
	a := bots[0]
	view, err := a.myTeam()
	if err != nil {
		return err
	}
	if err := cleanupUnityCheckTeam(a.gc.PlayerId, view); err != nil {
		return err
	}
	if view.GetTeamId() == cleanupUnityTeamID {
		response := &teampb.TeamResponse{}
		if err := a.expect(game.ClientPlayerTeamDisbandTeamMessageId, &teampb.DisbandTeamRequest{ExpectedTeamId: cleanupUnityTeamID}, response, 0); err != nil {
			return err
		}
		if response.GetTeam() == nil || response.GetTeam().GetTeamId() != 0 {
			return errors.New("正式解散接口未确认队伍已清空")
		}
		zap.L().Info("TEAM_INVITES_UNITY_TEAM_DISBANDED", zap.Uint64("leader", a.gc.PlayerId), zap.Uint64("team_id", cleanupUnityTeamID))
	}
	for i, bot := range bots {
		before := &friendpb.GetFriendListResponse{}
		if err := bot.expect(game.ClientPlayerFriendGetFriendListMessageId, &friendpb.GetFriendListRequest{}, before, 0); err != nil {
			return err
		}
		if friendSmokeFindFriend(before.GetFriends(), bots[1-i].gc.PlayerId) != nil {
			if err := bot.expect(game.ClientPlayerFriendRemoveFriendMessageId, &friendpb.RemoveFriendRequest{TargetPlayerId: bots[1-i].gc.PlayerId}, &friendpb.RemoveFriendResponse{}, 0); err != nil {
				return err
			}
		}
	}
	for i, bot := range bots {
		after := &friendpb.GetFriendListResponse{}
		if err := bot.expect(game.ClientPlayerFriendGetFriendListMessageId, &friendpb.GetFriendListRequest{}, after, 0); err != nil {
			return err
		}
		if friendSmokeFindFriend(after.GetFriends(), bots[1-i].gc.PlayerId) != nil {
			return errors.New("清理后双向好友列表仍有本次关系")
		}
		zap.L().Info("TEAM_INVITES_UNITY_FRIEND_REMOVED", zap.Uint64("viewer", bot.gc.PlayerId), zap.Uint64("peer", bots[1-i].gc.PlayerId))
		view, err := bot.myTeam()
		if err != nil {
			return err
		}
		if view == nil || view.GetTeamId() != 0 {
			return errors.New("清理后正式队伍接口仍有队伍或缺少视图")
		}
		zap.L().Info("TEAM_INVITES_UNITY_NO_TEAM_VERIFIED", zap.Uint64("player_id", bot.gc.PlayerId))
	}
	return nil
}
