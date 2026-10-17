using System;
using System.Linq;
using System.Reflection;
using System.Xml.Linq;
using NUnit.Framework;
using MmorpgClient.Tests.EditMode.Battle;

// Runs pure client network/rules/replay fixtures without starting a second Unity editor.
internal static class SkillCoreTestRunner
{
    private static int Main(string[] args)
    {
        var suite = new XElement("testsuite", new XAttribute("name", "Class skill tests (standalone core)"));
        int failed = 0, passed = 0;
        foreach (var fixtureType in new[] { typeof(SkillClientTests), typeof(SkillManaReplayTests) })
        foreach (var method in fixtureType.GetMethods())
        {
            var cases = method.GetCustomAttributes<TestCaseAttribute>().ToArray();
            if (cases.Length == 0 && method.GetCustomAttribute<TestAttribute>() == null) continue;
            var arguments = cases.Length > 0 ? cases.Select(c => c.Arguments) : new[] { Array.Empty<object>() };
            foreach (var values in arguments)
            {
                string name = fixtureType.Name + "." + method.Name + (values.Length > 0 ? "(" + string.Join(",", values) + ")" : "");
                var testcase = new XElement("testcase", new XAttribute("name", name));
                try
                {
                    var fixture = Activator.CreateInstance(fixtureType);
                    foreach (var setup in fixtureType.GetMethods().Where(m => m.GetCustomAttribute<SetUpAttribute>() != null))
                        setup.Invoke(fixture, null);
                    var parameters = method.GetParameters();
                    var converted = values.Select((value, i) => Convert.ChangeType(value, parameters[i].ParameterType)).ToArray();
                    method.Invoke(fixture, converted);
                    passed++;
                    Console.WriteLine("PASS " + name);
                }
                catch (Exception error)
                {
                    var cause = error is TargetInvocationException tie ? tie.InnerException : error;
                    testcase.Add(new XElement("failure", cause?.ToString()));
                    failed++;
                    Console.WriteLine("FAIL " + name + ": " + cause?.Message);
                }
                suite.Add(testcase);
            }
        }
        suite.SetAttributeValue("tests", passed + failed);
        suite.SetAttributeValue("failures", failed);
        if (args.Length > 0) new XDocument(suite).Save(args[0]);
        Console.WriteLine($"Client core: {passed} passed, {failed} failed. Unity UI rendering is not covered by this runner.");
        return failed == 0 ? 0 : 1;
    }
}
