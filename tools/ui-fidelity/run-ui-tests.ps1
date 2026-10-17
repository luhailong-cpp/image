param([ValidateSet('EditMode','PlayMode')][string]$Platform='EditMode')
$ErrorActionPreference='Stop'
$unityPath='C:\Program Files\Unity\Hub\Editor\6000.6.0f1\Editor\Unity.exe'
$outputRoot='E:\work\image\docs\ui-fidelity-20261016'
$filters=@(
 'MmorpgClient.Tests.EditMode.Social',
 'MmorpgClient.Tests.EditMode.Mail',
 'MmorpgClient.Tests.EditMode.Jubaozhai',
 'MmorpgClient.Tests.EditMode.Battle.GameplayWindowTests',
 'MmorpgClient.Tests.EditMode.Battle.EquipWindowTests',
 'MmorpgClient.Tests.EditMode.Battle.EquipForgeWindowTests',
 'MmorpgClient.Tests.EditMode.Battle.AttributePanelDisplayTests',
 'MmorpgClient.Tests.EditMode.Battle.PetPanelInteractionTests',
 'MmorpgClient.Tests.EditMode.Battle.SkillPanelPresentationTests',
 'MmorpgClient.Tests.EditMode.Battle.BattleHudLogicTests',
 'MmorpgClient.Tests.EditMode.Battle.BattleUiLayoutTests',
 'MmorpgClient.Tests.EditMode.Battle.HudCanvasLayeringTests',
 'MmorpgClient.Tests.EditMode.Ugui.QdaoServerSelectPrefabTests',
 'MmorpgClient.Tests.EditMode.Ugui.QdaoLoginPresentationTests',
 'MmorpgClient.Tests.EditMode.Tianyong.TeamWindowTests',
 'MmorpgClient.Tests.EditMode.Tianyong.TeamInvitationWindowTests',
 'MmorpgClient.Tests.EditMode.Tianyong.SceneChannelWindowTests',
 'MmorpgClient.Tests.EditMode.Tianyong.CityTravelWindowTests',
 'MmorpgClient.Tests.EditMode.Tianyong.GuildWindowTests',
 'MmorpgClient.Tests.EditMode.Tianyong.GuildClientTests',
 'MmorpgClient.Tests.EditMode.Tianyong.JubaozhaiModelTests'
)
$testFilter=if($Platform -eq 'PlayMode'){'SocialInputBlockerPlayModeTests;MailInputBlockerPlayModeTests;QdaoRoleIdentityPlayModeTests'}else{$filters -join ';'}
& $unityPath -batchmode -projectPath 'E:\work\mmorpg-client' -runTests -testPlatform $Platform -testFilter $testFilter -testResults (Join-Path $outputRoot ($Platform.ToLowerInvariant()+'-results.xml')) -logFile (Join-Path $outputRoot ($Platform.ToLowerInvariant()+'-tests.log'))
