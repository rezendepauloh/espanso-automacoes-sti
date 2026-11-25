using System.Text;
using System.Text.Json;
using StiForms.Models;

namespace StiForms.Services;

public static class OutputFormatter
{
    public static Dictionary<string, string> FinalizeOutputValues(
        FormConfig config,
        IReadOnlyDictionary<string, string> values)
    {
        var finalValues = new Dictionary<string, string>(values, StringComparer.Ordinal);

        if (config.Template.Contains("{% if data == 'hoje' %}", StringComparison.Ordinal))
        {
            var dataVal = finalValues.TryGetValue("data", out var d) ? d : string.Empty;
            var horaFinal = string.Equals(dataVal, "hoje", StringComparison.Ordinal)
                ? (finalValues.TryGetValue("hora_hoje", out var hh) ? hh : string.Empty)
                : (finalValues.TryGetValue("hora", out var h) ? h : string.Empty);

            finalValues["hora"] = horaFinal;
        }

        return finalValues;
    }

    public static string FormatOutput(
        FormConfig config,
        IReadOnlyList<string> fieldOrder,
        IReadOnlyDictionary<string, string> values,
        bool asJson)
    {
        var finalValues = FinalizeOutputValues(config, values);

        if (asJson)
        {
            var ordered = new SortedDictionary<string, string>(StringComparer.Ordinal);
            foreach (var key in fieldOrder)
            {
                ordered[key] = finalValues.TryGetValue(key, out var v) ? v : string.Empty;
            }
            return JsonSerializer.Serialize(ordered, new JsonSerializerOptions { WriteIndented = true });
        }

        IReadOnlyList<string> orderedKeys = config.Template.Contains("{% if data == 'hoje' %}", StringComparison.Ordinal)
            ? new[] { "data", "data_manual", "hora", "local", "demandas", "passageiros" }
            : fieldOrder;

        var sb = new StringBuilder();
        foreach (var key in orderedKeys)
        {
            sb.Append("===FIELD:").Append(key).Append("===\n");
            if (finalValues.TryGetValue(key, out var val) && !string.IsNullOrEmpty(val))
            {
                sb.Append(val.Replace("\r\n", "\n")).Append('\n');
            }
        }
        sb.Append("===END===\n");
        return sb.ToString();
    }
}
