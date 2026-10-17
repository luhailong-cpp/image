const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=__dirname,dir=path.join(root,'integration');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'runtime-assets.json'),'utf8'));
// Single sprites have no legacy multi-sprite rectangle, old names or stale file IDs.
function singleMeta(guid){return `fileFormatVersion: 2
guid: ${guid}
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {}
  serializedVersion: 13
  mipmaps:
    mipMapMode: 0
    enableMipMap: 0
    sRGBTexture: 1
    linearTexture: 0
    fadeOut: 0
    borderMipMap: 0
    mipMapsPreserveCoverage: 0
    alphaTestReferenceValue: 0.5
    mipMapFadeDistanceStart: 1
    mipMapFadeDistanceEnd: 3
  isReadable: 0
  streamingMipmaps: 0
  streamingMipmapsPriority: 0
  vTOnly: 0
  ignoreMipmapLimit: 0
  grayScaleToAlpha: 0
  generateCubemap: 6
  cubemapConvolution: 0
  seamlessCubemap: 0
  textureFormat: 1
  maxTextureSize: 4096
  textureSettings:
    serializedVersion: 2
    filterMode: 1
    aniso: 1
    mipBias: 0
    wrapU: 1
    wrapV: 1
    wrapW: 1
  nPOTScale: 0
  lightmap: 0
  compressionQuality: 100
  spriteMode: 1
  spriteExtrude: 1
  spriteMeshType: 0
  alignment: 0
  spritePivot: {x: 0.5, y: 0.5}
  spritePixelsToUnits: 100
  spriteBorder: {x: 0, y: 0, z: 0, w: 0}
  spriteGenerateFallbackPhysicsShape: 0
  alphaUsage: 1
  alphaIsTransparency: 1
  spriteTessellationMethod: 0
  spriteTessellationDetail: -1
  spriteGeometrySubdivision: -1
  textureType: 8
  textureShape: 1
  singleChannelComponent: 0
  flipbookRows: 1
  flipbookColumns: 1
  maxTextureSizeSet: 0
  compressionQualitySet: 0
  textureFormatSet: 0
  ignorePngGamma: 0
  applyGammaDecoding: 0
  swizzle: 50462976
  cookieLightType: 0
  platformSettings:
  - serializedVersion: 4
    buildTarget: DefaultTexturePlatform
    maxTextureSize: 4096
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 0
    compressionQuality: 100
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  spriteSheet:
    serializedVersion: 2
    sprites: []
    outline: []
    customData:
    physicsShape: []
    bones: []
    spriteID: 5e97eb03825dee720800000000000000
    internalID: 0
    vertices: []
    indices:
    edges: []
    weights: []
    secondaryTextures: []
    spriteCustomMetadata:
      entries: []
    nameFileIdTable: {}
  mipmapLimitGroupName:
  pSDRemoveMatte: 0
  userData:
  assetBundleName:
  assetBundleVariant:
`;}
for(const asset of manifest.images){
 fs.writeFileSync(path.join(root,'runtime-assets',asset.file+'.meta'),singleMeta(asset.guid));
 for(const suffix of ['.generation.json','.sprite.json']){
  const recordFile=path.join(root,'runtime-assets',asset.file+suffix),record=JSON.parse(fs.readFileSync(recordFile,'utf8'));
  record.derivedFromPathBase='fidelity-20261016 package root';
  if(suffix==='.generation.json')record.originalGenerationEvidence='../../source/generation.json';
  fs.writeFileSync(recordFile,JSON.stringify(record,null,2)+'\n');
 }
}
let art=fs.readFileSync(path.join(dir,'TeamUiArt.cs'),'utf8');
art=art.replace('Text(button.transform, label, 18, (h - textHeight) * .5f, w - 36, textHeight, fontSize,',
  'float padding = Mathf.Min(18f, w * .1f);\n            Text(button.transform, label, padding, (h - textHeight) * .5f, w - padding * 2, textHeight, fontSize,');
fs.writeFileSync(path.join(dir,'TeamUiArt.cs'),art);
// Derive the isolated native rendering harness already used for Social, preserving its geometry records.
let capture=fs.readFileSync('E:/work/mmorpg-client/Assets/Editor/Social/SocialFidelityVerification.cs','utf8')
 .replaceAll('MmorpgClient.Game.Social','MmorpgClient.Game.Team').replaceAll('MmorpgClient.UI.Ugui.Social','MmorpgClient.UI.Ugui.Team')
 .replaceAll('SocialFidelity','TeamFidelity').replaceAll('socialFidelity','teamFidelity').replaceAll('SocialWindow','TeamWindow')
 .replaceAll('SocialFidelity','TeamFidelity').replaceAll('social-ui-v1','team-ui-v2').replaceAll('UI/Social/','UI/Team/')
 .replaceAll('SOCIAL_FIDELITY','TEAM_FIDELITY').replaceAll('Social fidelity','Team fidelity').replaceAll('SocialFidelityCanvas','TeamFidelityCanvas')
 .replaceAll('UI/Ugui/SocialV1','UI/Ugui/TeamV2').replace('shots.Count == 8','shots.Count == 10')
 .replace('            QdaoUguiFactory.CreateImage("Backdrop", design, 0, 0, 2560, 1080, QdaoUguiTheme.RequireSprite("UI/Ugui/TeamV2/main-city"));','');
const a=capture.indexOf('            CapturePage("01-preview-groups"'),b=capture.indexOf('            void CapturePage(',a);
capture=capture.slice(0,a)+`            CapturePage("01-approved-preview", true, 0);
            CapturePage("02-native-authoritative-portrait", false, 0);
            CapturePage("03-member-permissions", false, 1);
            CapturePage("04-received-invites", false, 2);
            CapturePage("05-production-unavailable", false, 3);

`+capture.slice(b);
capture=capture.replace('void CapturePage(string name, bool preview, SocialPage page)','void CapturePage(string name, bool preview, int scenario)')
 .replace('page = page.ToString(), fixtureNowMs = FixedNowMs,','page = scenario == 2 ? "ReceivedInvites" : "MembersAndApplications", fixtureNowMs = FixedNowMs,')
 .replace('                    var state = new SocialState(preview: preview, clock: () => FixedNowMs);\n                    window = new TeamWindow(design, state);\n                    window.Show(page, refreshHistory: false);\n                    window.Tick();',`                    var state = Fixture(preview, scenario);
                    window = new TeamWindow(design);
                    window.SetState(state);
                    window.Show();`);
const ca=capture.indexOf('                    bool hasComposer ='),cb=capture.indexOf('\n                }\n                catch',ca);
capture=capture.slice(0,ca)+`                    bool previewPortrait = shot.activeImages.Any(record => record.resourceKey.Contains("/preview_portrait_"));
                    bool membersManaged = buttons.Any(button => button.name.StartsWith("Kick_", StringComparison.Ordinal));
                    var teamFrame = canvasObject.GetComponentsInChildren<RectTransform>(false).First(rect => rect.name == "TeamFrame");
                    shot.checks = new[]
                    {
                        new Check { name = "native window visible", passed = window.IsVisible },
                        new Check { name = "native close and refresh exist", passed = HasButton("CloseTeamWindow") && HasButton("RefreshTeam") },
                        new Check { name = "original art rectangle is 1931 by 814", passed = Mathf.Abs(teamFrame.rect.width-1931)<.01f && Mathf.Abs(teamFrame.rect.height-814)<.01f },
                        new Check { name = "original art has one uniform scale", passed = Mathf.Abs(teamFrame.localScale.x-teamFrame.localScale.y)<.0001f && Mathf.Abs(teamFrame.localScale.x-2560f/1931f)<.0001f },
                        new Check { name = "approved preview portraits require explicit fixture marker", passed = previewPortrait == preview },
                        new Check { name = "member state has no management buttons", passed = scenario != 1 || !membersManaged && !HasButton("StartTeamMatch") },
                        new Check { name = "no team state uses invitation list", passed = scenario != 2 || !state.HasTeam && HasButton("AcceptInvite_2001") },
                        new Check { name = "production unavailable state has no invented identities", passed = scenario != 3 || !previewPortrait && state.Snapshot.Members.Count == 0 && state.Snapshot.Applications.Count == 0 && state.Invites.Count == 0 }
                    };`+capture.slice(cb);
capture=capture.replace('                        GameObject root = window.Root.gameObject;\n                        window.Dispose();\n                        UnityEngine.Object.DestroyImmediate(root);',`                        window.Hide();
                        var windowRoot = design.Find("TeamWindow");
                        if (windowRoot != null) UnityEngine.Object.DestroyImmediate(windowRoot.gameObject);`);
const fi=capture.indexOf('    private static RectRecord DesignRect');
capture=capture.slice(0,fi)+`    // All identities and presence below are labeled offline fixtures; production never manufactures them.
    private static TeamUiState Fixture(bool preview, int scenario)
    {
        var state = new TeamUiState(() => 0f);
        if (scenario == 3) { state.Reset(101); state.SetUnavailable("组队服务尚未连接，等待同步真实队伍信息。"); return state; }
        TeamRole Role(ulong id, string name, uint level, string school, uint classId, uint gender, int portrait, bool online = true) =>
            new TeamRole { PlayerId = id, Name = name, Level = level, SchoolName = school, ClassId = classId,
                Gender = gender, CharacterId = preview ? TeamUiArt.PreviewPortraitPrefix + portrait : null,
                IsOnline = online, OnlineStatusKnown = true };
        var snapshot = new TeamSnapshot { TeamId = 10248, LeaderId = 101, LocalPlayerId = scenario == 1 ? 102UL : 101UL,
            Capacity = 5, MembershipEpoch = 1, Version = 1, ApplicationCount = 2, MatchFillSupported = true };
        snapshot.Members.Add(Role(101, "青云小道", 28, "道童", 1, 1, 1));
        snapshot.Members.Add(Role(102, "清铃", 26, "灵修", 2, 2, 2));
        snapshot.Members.Add(Role(103, "长风", 30, "剑修", 2, 1, 3, false));
        if (scenario != 1)
        {
            snapshot.Applications.Add(Role(201, "桂枝", 27, "医师", 3, 2, 4));
            snapshot.Applications.Add(Role(202, "云游子", 29, "符师", 4, 1, 5));
        }
        if (scenario == 2)
        {
            snapshot = new TeamSnapshot { LocalPlayerId = 101, Capacity = 5 };
            state.Sync(snapshot, new List<TeamInvite> { new TeamInvite { TeamId = 2001, LeaderId = 201, MemberCount = 3,
                Inviter = Role(201, "桂枝", 27, "医师", 3, 2, 4), ExpiresAt = 300f } }, true, true, TeamAction.None, 0, 0, "");
        }
        else state.SetSnapshot(snapshot);
        return state;
    }

`+capture.slice(fi);
fs.writeFileSync(path.join(dir,'TeamFidelityVerification.cs'),capture);
const metaFile=path.join(dir,'TeamFidelityVerification.cs.meta');
if(!fs.existsSync(metaFile))fs.writeFileSync(metaFile,`fileFormatVersion: 2\nguid: ${crypto.randomBytes(16).toString('hex')}\n`);
console.log(JSON.stringify({singleSpriteMeta:manifest.images.length,captureFile:'integration/TeamFidelityVerification.cs',screenshots:10}));
