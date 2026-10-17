using System;
using System.Linq;
using System.Reflection;
using MmorpgClient.Tests.EditMode.Tianyong;
using NUnit.Framework;

int passed = 0, failed = 0;
foreach (var test in typeof(TeamInvitationDirectoryTests).GetMethods().Where(m => m.GetCustomAttribute<TestAttribute>() != null))
{
    var instance = new TeamInvitationDirectoryTests();
    try { instance.SetUp(); test.Invoke(instance, null); ++passed; Console.WriteLine("PASS " + test.Name); }
    catch (Exception ex) { ++failed; Console.WriteLine("FAIL " + test.Name + ": " + (ex.InnerException ?? ex)); }
    finally { instance.TearDown(); }
}
Console.WriteLine($"Directory tests: {passed} passed, {failed} failed");
return failed == 0 ? 0 : 1;
