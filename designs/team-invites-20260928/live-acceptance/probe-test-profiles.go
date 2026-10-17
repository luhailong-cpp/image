package main

import (
    "context"
    "fmt"
    "time"
    dbpb "proto/common/database"
    "github.com/redis/go-redis/v9"
    "google.golang.org/protobuf/proto"
)

func main() {
    ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
    defer cancel()
    client := redis.NewClient(&redis.Options{Addr:"127.0.0.1:6379"})
    defer client.Close()
    for _, id := range []uint64{2202, 2203} {
        profile := &dbpb.PlayerAllData{}
        key := fmt.Sprintf("%s:%d",profile.ProtoReflect().Descriptor().FullName(),id)
        raw, err := client.Get(ctx,key).Bytes()
        if err != nil { panic(err) }
        if err = proto.Unmarshal(raw,profile); err != nil { panic(err) }
        player := profile.GetPlayerDatabaseData()
        fmt.Printf("test_player_id=%d cached_level=%d registration_timestamp=%d name=%s class_id=%d\n",player.GetPlayerId(),player.GetLevelComponent().GetLevel(),player.GetUint64PbComponent().GetRegistrationTimestamp(),player.GetProfileComponent().GetName(),player.GetUint32PbComponent().GetClass())
    }
}
