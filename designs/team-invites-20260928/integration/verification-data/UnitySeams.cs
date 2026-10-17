// Only the engine visual catalog and generated handler dispatch are replaced in this
// headless runner. Directory logic, NUnit assertions and protobuf serialization are real.
// The full runtime compile verifies the production catalog and generated handler references.
namespace MmorpgClient.World
{
    public static class QdaoCharacterCatalog
    {
        public static string ResolveRole(uint classId, uint gender, string appearanceId)
            => string.IsNullOrEmpty(appearanceId) ? "catalog:" + classId + ":" + gender : appearanceId;
    }
}
namespace MmorpgClient.Net.Generated
{
    public static class ClientPlayerFriendGetFriendListHandler { public const uint MessageId = 12; }
    public static class ClientPlayerFriendRecommendFriendsHandler { public const uint MessageId = 119; }
}
