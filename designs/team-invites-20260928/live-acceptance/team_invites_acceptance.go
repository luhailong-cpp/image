package main

// 本次接入的独立真实协议验收；只使用随机新账号，不清理或复用历史账号。
import (
	"crypto/rand"
	"encoding/hex"
	"errors"
	"fmt"
	"os"
	"strconv"
	"time"

	"go.uber.org/zap"
	friendpb "proto/friend"
	"proto/scene"
	teampb "proto/team"
	"robot/config"
	"robot/generated/pb/game"
	"robot/logic/gameobject"
	"robot/metrics"
)

func RunTeamInvitesAcceptance(cfg *config.Config) (result error) {
	secret := os.Getenv("LOGIN_DEV_PASSWORD_SHARED_SECRET")
	if secret == "" {
		return errors.New("LOGIN_DEV_PASSWORD_SHARED_SECRET 未设置；不猜测登录凭证")
	}
	cfg.Password = secret
	cfg.AuthType = "password"
	loginTestCfg = cfg
	var nonce [8]byte
	if _, err := rand.Read(nonce[:]); err != nil {
		return err
	}
	prefix := "robot_tinv_" + hex.EncodeToString(nonce[:])
	stats := robotStatsRef
	if stats == nil {
		stats = metrics.NewStats()
	}
	var bots []*teamSmokeBot
	runtimeLevels := map[uint64]uint32{}
	closed := map[*teamSmokeBot]bool{}
	var teamID uint64
	friendPending, friends := false, false
	defer func() {
		if len(bots) == 2 {
			a, b := bots[0], bots[1]
			if teamID != 0 {
				if err := a.expect(game.ClientPlayerTeamDisbandTeamMessageId, &teampb.DisbandTeamRequest{ExpectedTeamId: teamID}, &teampb.TeamResponse{}, 0); err != nil {
					result = errors.Join(result, fmt.Errorf("清理本次队伍: %w", err))
				}
			}
			if friends {
				if err := a.expect(game.ClientPlayerFriendRemoveFriendMessageId, &friendpb.RemoveFriendRequest{TargetPlayerId: b.gc.PlayerId}, &friendpb.RemoveFriendResponse{}, 0); err != nil {
					result = errors.Join(result, fmt.Errorf("清理本次好友关系: %w", err))
				}
			} else if friendPending {
				if err := b.expect(game.ClientPlayerFriendRejectFriendMessageId, &friendpb.RejectFriendRequest{FromPlayerId: a.gc.PlayerId}, &friendpb.RejectFriendResponse{}, 0); err != nil {
					result = errors.Join(result, fmt.Errorf("清理本次好友申请: %w", err))
				}
			}
		}
		for _, bot := range bots {
			if closed[bot] {
				continue
			}
			if err := leaveGame(bot.gc, stats); err != nil {
				result = errors.Join(result, fmt.Errorf("退出 %s: %w", bot.name, err))
			}
			sendDisconnectBestEffort(bot.gc)
			gameobject.PlayerList.Delete(bot.gc.PlayerId)
			bot.gc.Close()
		}
		if result == nil {
			zap.L().Info("TEAM_INVITES_ACCEPTANCE_OK", zap.String("account_prefix", prefix), zap.Int("players", len(bots)))
		}
	}()
	for _, name := range []string{"a", "b"} {
		bot, err := teamSmokeLogin(cfg, name, prefix+"_"+name, stats)
		if err != nil {
			return fmt.Errorf("登录全新账号 %s: %w", name, err)
		}
		bots = append(bots, bot)
		zap.L().Info("TEAM_INVITES_LOGIN_OK", zap.String("account", bot.account), zap.Uint64("player_id", bot.gc.PlayerId), zap.Uint32("zone", cfg.ZoneID))
		panel := &scene.GetAttributePanelResponse{}
		if err := bot.expect(game.SceneAttributeClientPlayerGetAttributePanelMessageId, &scene.GetAttributePanelRequest{}, panel, 0); err != nil {
			return err
		}
		if panel.GetPanel().GetLevel() == 0 {
			return errors.New("新角色自己的实时属性面板等级为 0")
		}
		runtimeLevels[bot.gc.PlayerId] = panel.GetPanel().GetLevel()
		zap.L().Info("TEAM_INVITES_RUNTIME_LEVEL_OK", zap.Uint64("player_id", bot.gc.PlayerId), zap.Uint32("level", panel.GetPanel().GetLevel()))
		view, err := bot.myTeam()
		if err != nil {
			return err
		}
		if view.GetTeamId() != 0 {
			return fmt.Errorf("新账号已有队伍 %d，停止，不操作历史状态", view.GetTeamId())
		}
		list := &friendpb.GetFriendListResponse{}
		if err := bot.expect(game.ClientPlayerFriendGetFriendListMessageId, &friendpb.GetFriendListRequest{}, list, 0); err != nil {
			return err
		}
		if len(list.GetFriends()) != 0 {
			return errors.New("新账号已有好友，停止，不操作历史关系")
		}
	}
	a, b := bots[0], bots[1]
	if err := a.expect(game.ClientPlayerFriendAddFriendMessageId, &friendpb.AddFriendRequest{TargetPlayerId: b.gc.PlayerId}, &friendpb.AddFriendResponse{}, 0); err != nil {
		return err
	}
	friendPending = true
	if err := b.expect(game.ClientPlayerFriendAcceptFriendMessageId, &friendpb.AcceptFriendRequest{FromPlayerId: a.gc.PlayerId}, &friendpb.AcceptFriendResponse{}, 0); err != nil {
		return err
	}
	friendPending, friends = false, true
	var profileB *friendpb.FriendEntry
	for i, bot := range bots {
		peer := bots[1-i]
		list := &friendpb.GetFriendListResponse{}
		if err := bot.expect(game.ClientPlayerFriendGetFriendListMessageId, &friendpb.GetFriendListRequest{}, list, 0); err != nil {
			return err
		}
		entry := friendSmokeFindFriend(list.GetFriends(), peer.gc.PlayerId)
		// 等级来自退出/周期存盘快照；首次存盘前 0 表示未知，身份与在线态仍须完整。
		// 在线目录随后必须与这份资料严格一致，不能把 0 伪造成 1 或隐藏新玩家。
		if entry == nil || !entry.GetIsOnline() || entry.GetName() == "" || entry.GetClassId() == 0 || entry.GetZoneId() != cfg.ZoneID {
			return fmt.Errorf("RPC12 好友真实资料或在线态不完整: %v", entry)
		}
		if entry.GetLevel() != 0 && entry.GetLevel() != runtimeLevels[peer.gc.PlayerId] {
			return fmt.Errorf("好友等级与目标实时属性面板不一致: %v", entry)
		}
		if i == 0 {
			profileB = entry
		}
		zap.L().Info("TEAM_INVITES_FRIEND_LIST_OK", zap.Uint32("rpc", game.ClientPlayerFriendGetFriendListMessageId), zap.Uint64("viewer", bot.gc.PlayerId), zap.Uint64("friend", peer.gc.PlayerId), zap.String("name", entry.GetName()), zap.Uint32("level", entry.GetLevel()), zap.Uint32("class_id", entry.GetClassId()), zap.String("appearance_id", entry.GetAppearanceId()))
	}
	// ID 搜索验证好友也在在线名单；名字搜索验证服务端搜索而非客户端伪名单。
	for _, query := range []string{strconv.FormatUint(b.gc.PlayerId, 10), profileB.GetName()} {
		if err := teamInvitesFindOnline(a, b.gc.PlayerId, cfg.ZoneID, query, profileB, runtimeLevels[b.gc.PlayerId]); err != nil {
			return err
		}
	}
	created := &teampb.TeamResponse{}
	if err := a.expect(game.ClientPlayerTeamCreateTeamMessageId, &teampb.CreateTeamRequest{}, created, 0); err != nil {
		return err
	}
	teamID = created.GetTeam().GetTeamId()
	if teamID == 0 || created.GetTeam().GetLeaderId() != a.gc.PlayerId || created.GetTeam().GetZoneId() != cfg.ZoneID {
		return fmt.Errorf("建队资料错误: %v", created)
	}
	mark := b.mark()
	if err := a.expect(game.ClientPlayerTeamInviteToTeamMessageId, &teampb.InviteToTeamRequest{TargetPlayerId: b.gc.PlayerId, ExpectedTeamId: teamID}, &teampb.TeamResponse{}, 0); err != nil {
		return err
	}
	pushed, err := teamSmokeWaitPush(b, mark, game.ClientPlayerTeamNotifyTeamInviteMessageId, teamSmokePushTimeout, func() *teampb.TeamInviteS2C { return &teampb.TeamInviteS2C{} }, func(p *teampb.TeamInviteS2C) bool {
		return p.GetInvite().GetTeamId() == teamID && p.GetInvite().GetInviter().GetPlayerId() == a.gc.PlayerId
	})
	if err != nil {
		return fmt.Errorf("真实邀请推送: %w", err)
	}
	incoming := &teampb.ListMyInvitesResponse{}
	if err := b.expect(game.ClientPlayerTeamListMyInvitesMessageId, &teampb.ListMyInvitesRequest{}, incoming, 0); err != nil {
		return err
	}
	if !teamSmokeHasIncomingInvite(incoming, teamID) {
		return errors.New("邀请推送已到但邀请列表缺失")
	}
	zap.L().Info("TEAM_INVITES_INVITE_PUSH_OK", zap.Uint64("team_id", teamID), zap.Uint64("inviter", pushed.GetInvite().GetInviter().GetPlayerId()), zap.Uint64("invitee", b.gc.PlayerId))
	joined := &teampb.TeamResponse{}
	if err := b.expect(game.ClientPlayerTeamRespondInviteMessageId, &teampb.RespondInviteRequest{TeamId: teamID, Accept: true}, joined, 0); err != nil {
		return err
	}
	for _, bot := range bots {
		view, err := bot.myTeam()
		if err != nil {
			return err
		}
		if view.GetTeamId() != teamID || len(view.GetMembers()) != 2 {
			return fmt.Errorf("接受后成员数或队伍不一致: %v", view)
		}
		for _, member := range bots {
			m, count := teamSmokeMemberOf(view, member.gc.PlayerId)
			if count != 1 || !m.GetIsOnline() || m.GetZoneId() != cfg.ZoneID {
				return fmt.Errorf("接受后成员视图错误: %v", m)
			}
			if m.GetName() == "" {
				zap.L().Info("TEAM_INVITES_OPTIONAL_TEAM_NAME_UNDEPLOYED", zap.Uint64("member_id", m.GetPlayerId()))
			}
		}
		zap.L().Info("TEAM_INVITES_ACCEPT_OK", zap.Uint64("viewer", bot.gc.PlayerId), zap.Uint64("team_id", teamID), zap.Int("member_count", len(view.GetMembers())))
	}
	if err := a.expect(game.ClientPlayerTeamDisbandTeamMessageId, &teampb.DisbandTeamRequest{ExpectedTeamId: teamID}, &teampb.TeamResponse{}, 0); err != nil {
		return err
	}
	teamID = 0
	if err := leaveGame(b.gc, stats); err != nil {
		return err
	}
	sendDisconnectBestEffort(b.gc)
	gameobject.PlayerList.Delete(b.gc.PlayerId)
	b.gc.Close()
	closed[b] = true
	offline := false
	for attempt := 0; attempt < 10; attempt++ {
		list := &friendpb.GetFriendListResponse{}
		if err := a.expect(game.ClientPlayerFriendGetFriendListMessageId, &friendpb.GetFriendListRequest{}, list, 0); err != nil {
			return err
		}
		entry := friendSmokeFindFriend(list.GetFriends(), b.gc.PlayerId)
		if entry == nil {
			return errors.New("离线后好友关系意外消失")
		}
		if !entry.GetIsOnline() {
			offline = true
			break
		}
		time.Sleep(time.Second)
	}
	if !offline {
		return errors.New("B 退出后 RPC12 仍报告在线")
	}
	cursor := ""
	for page := 0; page < 24; page++ {
		response := &friendpb.RecommendFriendsResponse{}
		if err := a.expect(game.ClientPlayerFriendRecommendFriendsMessageId, &friendpb.RecommendFriendsRequest{OnlineOnly: true, Limit: 1, Cursor: cursor, Query: strconv.FormatUint(b.gc.PlayerId, 10)}, response, 0); err != nil {
			return err
		}
		if !response.GetOnlineDirectory() {
			return errors.New("离线复核时缺少在线目录能力标志")
		}
		for _, candidate := range response.GetCandidates() {
			if candidate.GetCandidatePlayerId() == b.gc.PlayerId {
				return errors.New("在线名单仍含已退出的 B")
			}
		}
		cursor = response.GetNextCursor()
		if cursor == "" {
			break
		}
		if page == 23 {
			return errors.New("离线复核超出扫描预算")
		}
	}
	zap.L().Info("TEAM_INVITES_OFFLINE_OK", zap.Uint64("player_id", b.gc.PlayerId))
	// 清理由 defer 执行；仅清理本次创建的好友边，不删除角色记录。
	return nil
}

func teamInvitesFindOnline(bot *teamSmokeBot, target uint64, zone uint32, query string, expected *friendpb.FriendEntry, runtimeLevel uint32) error {
	cursor := ""
	seenCursors := map[string]bool{}
	for page := 1; page <= 24; page++ {
		// 避免超过服务端每人每分钟 60 次的在线目录限流。
		if page > 1 {
			time.Sleep(time.Second)
		}
		response := &friendpb.RecommendFriendsResponse{}
		request := &friendpb.RecommendFriendsRequest{OnlineOnly: true, Limit: 1, Cursor: cursor, Query: query}
		if err := bot.expect(game.ClientPlayerFriendRecommendFriendsMessageId, request, response, 0); err != nil {
			return err
		}
		if !response.GetOnlineDirectory() {
			return errors.New("RPC119 未返回 online_directory 能力标志，可能是旧服务")
		}
		for _, candidate := range response.GetCandidates() {
			if !candidate.GetIsOnline() || candidate.GetZoneId() != zone || candidate.GetCandidatePlayerId() == bot.gc.PlayerId {
				return fmt.Errorf("在线目录返回非法候选: %v", candidate)
			}
			if candidate.GetCandidatePlayerId() == target {
				// 两次读取之间周期存盘可能把未知 0 补为 1；用本人实时属性面板校验
				// 已知等级，不把合法快照刷新误报成资料不一致。
				if candidate.GetName() != expected.GetName() || (candidate.GetLevel() != 0 && candidate.GetLevel() != runtimeLevel) || candidate.GetClassId() != expected.GetClassId() || candidate.GetAppearanceId() != expected.GetAppearanceId() {
					return fmt.Errorf("在线目录与好友资料不一致: %v", candidate)
				}
				zap.L().Info("TEAM_INVITES_ONLINE_OK", zap.Uint32("rpc", game.ClientPlayerFriendRecommendFriendsMessageId), zap.Uint64("player_id", target), zap.String("query", query), zap.Int("pages", page), zap.String("name", candidate.GetName()), zap.Uint32("cached_level", candidate.GetLevel()), zap.Uint32("runtime_level", runtimeLevel))
				return nil
			}
		}
		cursor = response.GetNextCursor()
		if cursor == "" {
			return fmt.Errorf("在线目录搜索 %q 遍历完毕仍缺少同区在线好友 %d", query, target)
		}
		if seenCursors[cursor] {
			return errors.New("在线目录游标重复")
		}
		seenCursors[cursor] = true
	}
	return errors.New("在线目录 24 页预算内未找到测试好友")
}
