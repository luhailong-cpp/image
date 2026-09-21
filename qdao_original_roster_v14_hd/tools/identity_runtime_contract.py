"""Current persistent-appearance runtime bindings; historical baselines stay fixed."""
SOURCES = (
    "Assets/Scripts/Game/GameClient.cs",
    "Assets/Scripts/UI/Ugui/Role/RoleFlowUi.cs",
    "Assets/Scripts/World/ActorWorld.cs",
    "Assets/Scripts/UI/Ugui/Team/TeamUiRoot.cs",
    "Assets/Scripts/UI/Ugui/Team/TeamWindow.cs",
    "Assets/Scripts/Game/Team/TeamAppearanceTransport.cs",
    "Assets/Scripts/Game/Team/TeamUiState.cs",
    "Assets/Scripts/App/DevAutoPilot.cs",
    "Assets/Tests/EditMode/Tianyong/PersistedAppearanceIdentityTests.cs",
    "Assets/Tests/PlayMode/QdaoRoleIdentityPlayModeTests.cs",
) + tuple("Assets/Scripts/Proto/Generated/" + name + ".cs" for name in
          ("BattleData", "Login", "PlayerScene", "Team", "UserAccounts"))
BINDINGS = SOURCES + tuple(path + ".meta" for path in SOURCES)
REQUIRED_METHODS = {
    "EditMode": ("MmorpgClient.Tests.EditMode.Tianyong.PersistedAppearanceIdentityTests", {
        "SameProfessionAndGender_PreserveDistinctSavedAppearancesAcrossRelogAndEntityChanges": 1,
        "CreateRequest_SeparatesPersistedAppearanceFromGameplayFields": 1,
        "RemoteAoiIdentity_DoesNotNeedTheLocalAccountRoleList_AndClearsOnDisconnect": 1,
        "RemoteLegacyAoi_UsesTransmittedProfessionAndGender": 1,
        "AoiRestoredIdentity_OverridesTheEmptyRoleListReturnedBeforeEnterGameSelfHeal": 1,
        "MissingResources_DoNotChangeThePersistedIdentity": 1,
        "BattleSnapshotIdentity_WinsOverLocalCache_WithoutUsingPetOwnerIdentity": 1,
        "TeamSnapshotAndApplications_UseTheSameIdentityAsWorldAndBattle": 1,
        "LateTeamReplies_CannotRestoreThePreviousMembershipOrAppearance": 1,
        "AvailableOriginals_NeverReintroduceDeletedIds_EvenIfHistoricalResourcesExist": 1,
        "AutoPilotOptions_ParseAppearanceAndStrictRelogWithoutChangingDefaults": 1,
        "StrictRelog_OnlySelectsThePersistedAppearance_AndNeverCreatesAReplacement": 2,
        "BattleWalking_UsesDistanceAndTheWorldReferenceCadence_IndependentOfDisplayScale": 1,
    }),
    "PlayMode": ("MmorpgClient.Tests.PlayMode.QdaoRoleIdentityPlayModeTests", {
        "CreationSelectorAndAccountCards_KeepAppearanceIndependentOfProfessionAndGender": 1,
        "BattleLunge_RendersPublishedWalkGeometry_AndReleasesMovementOnInterruptionAndDestroy": 1,
        "SyntheticHdLunge_IdentitySwapAndDestroyKeepAfterimageLeaseUntilPoolRelease": 1,
    }),
}
