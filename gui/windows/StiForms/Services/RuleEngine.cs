using StiForms.Models;

namespace StiForms.Services;

public static class RuleEngine
{
    public static bool IsFieldVisible(
        string fieldName,
        IReadOnlyDictionary<string, List<UiRule>> fieldRules,
        IReadOnlyDictionary<string, string> currentValues)
    {
        if (!fieldRules.TryGetValue(fieldName, out var rules) || rules.Count == 0)
        {
            return true;
        }

        return rules.All(rule => EvaluateSingleRule(rule, currentValues));
    }

    public static bool EvaluateSingleRule(UiRule rule, IReadOnlyDictionary<string, string> currentValues)
    {
        var trigger = rule.TriggerField();
        var expected = rule.ExpectedString().Trim();
        var actual = currentValues.TryGetValue(trigger, out var val) ? val.Trim() : string.Empty;
        var isMatch = string.Equals(actual, expected, StringComparison.Ordinal);

        return string.Equals(rule.Effect, "HIDE", StringComparison.OrdinalIgnoreCase)
            ? !isMatch
            : isMatch;
    }
}
