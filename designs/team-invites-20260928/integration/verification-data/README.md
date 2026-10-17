# Invitation directory verification

Run `dotnet run --project designs/team-invites-20260928/integration/verification-data/DirectoryTests.csproj` from the image workspace. The harness reads existing Google.Protobuf and NUnit DLLs from the client checkout; it does not download packages or write into that checkout. Override `-p:ClientRoot=...` and `-p:NUnitPath=...` on another machine.

The same NUnit tests are included in `client/Assets/Tests/EditMode/Tianyong/TeamInvitationDirectoryTests.cs` for Unity EditMode. The standalone harness executes real directory logic and real generated protobuf classes, with only the Unity portrait resolver and generated handler ID holders replaced by explicit seams. It cannot prove rendering, actor-world integration or live server availability; the full client compilation and running-client checks cover those separately.

Cases cover friend online status, authoritative profile fields, nickname/ID filtering, chat presence uncertainty, old-server online-directory rejection, empty-page continuation, cursor validation, deduplication, single-flight query coalescing, source-switch races, reconnect/character-change isolation, timeout quarantine, definitive errors, disposal, not-ready state and protocol round trips.
