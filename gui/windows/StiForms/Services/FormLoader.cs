using System.Globalization;
using System.IO;
using StiForms.Models;
using YamlDotNet.RepresentationModel;

namespace StiForms.Services;

public static class FormLoader
{
    public static string ResolveFormPath(string? formArg, string? configArg)
    {
        if (!string.IsNullOrWhiteSpace(configArg))
        {
            var full = Path.GetFullPath(configArg);
            if (File.Exists(full))
            {
                return full;
            }
            throw new FileNotFoundException($"Arquivo de formulário não encontrado: {full}");
        }

        if (string.IsNullOrWhiteSpace(formArg))
        {
            throw new ArgumentException("Informe --form <nome> ou --form-config <caminho.yml>.");
        }

        var clean = formArg.Trim();
        if (clean.EndsWith(".yml", StringComparison.OrdinalIgnoreCase))
        {
            clean = clean[..^4];
        }
        else if (clean.EndsWith(".yaml", StringComparison.OrdinalIgnoreCase))
        {
            clean = clean[..^5];
        }

        if (string.IsNullOrEmpty(clean) || clean.Contains('/') || clean.Contains('\\') || clean.Contains(".."))
        {
            throw new ArgumentException($"Nome de formulário inválido: '{formArg}'");
        }

        var root = EnvStore.DiscoverRepoRoot();
        var candidate = Path.Combine(root, "forms", $"{clean}.yml");
        if (File.Exists(candidate))
        {
            return candidate;
        }

        throw new FileNotFoundException($"Formulário '{clean}' não encontrado em {candidate}");
    }

    public static LoadedForm LoadFormFromPath(string path, DateTime? nowOverride = null)
    {
        var rawYaml = File.ReadAllText(path);
        var yaml = new YamlStream();
        using (var reader = new StringReader(rawYaml))
        {
            yaml.Load(reader);
        }

        if (yaml.Documents.Count == 0 || yaml.Documents[0].RootNode is not YamlMappingNode rootNode)
        {
            throw new InvalidDataException($"Arquivo YAML inválido: {path}");
        }

        var (config, fieldOrder) = ParseFormConfig(rootNode);
        var repoRoot = EnvStore.DiscoverRepoRoot(path);
        var env = EnvStore.LoadFromRepoRoot(repoRoot);

        var formName = Path.GetFileNameWithoutExtension(path);
        var displayTitle = $"Espanso STI — {PrettifyName(formName)}";

        var layoutElements = config.Uischema is not null && config.Uischema.Elements.Count > 0
            ? config.Uischema.Elements
            : fieldOrder.Select(k => new UiElement
            {
                ElementType = "Control",
                Scope = $"#/properties/{k}",
            }).ToList();

        var fieldRules = new Dictionary<string, List<UiRule>>(StringComparer.Ordinal);
        var fieldOptions = new Dictionary<string, UiOptions>(StringComparer.Ordinal);
        CollectUiMetadata(layoutElements, Array.Empty<UiRule>(), fieldRules, fieldOptions);

        var resolvedDefaults = ResolveDefaults(config, env);
        ApplyDynamicDefaults(formName, resolvedDefaults, nowOverride ?? DateTime.Now);

        return new LoadedForm
        {
            FormName = formName,
            DisplayTitle = displayTitle,
            RepoRoot = repoRoot,
            Config = config,
            FieldOrder = fieldOrder,
            LayoutElements = layoutElements,
            FieldRules = fieldRules,
            ResolvedDefaults = resolvedDefaults,
            FieldOptions = fieldOptions,
        };
    }

    private static (FormConfig Config, List<string> FieldOrder) ParseFormConfig(YamlMappingNode root)
    {
        var config = new FormConfig();
        var fieldOrder = new List<string>();

        if (GetMapping(root, "schema") is { } schemaNode)
        {
            config.Schema.SchemaType = GetScalar(schemaNode, "type") ?? "object";
            if (GetMapping(schemaNode, "properties") is { } propsNode)
            {
                foreach (var entry in propsNode.Children)
                {
                    if (entry.Key is not YamlScalarNode keyScalar || string.IsNullOrEmpty(keyScalar.Value))
                    {
                        continue;
                    }

                    var fieldName = keyScalar.Value;
                    fieldOrder.Add(fieldName);

                    if (entry.Value is YamlMappingNode propMap)
                    {
                        var prop = new SchemaProperty
                        {
                            FieldType = GetScalar(propMap, "type") ?? "string",
                            Title = GetScalar(propMap, "title"),
                            Format = GetScalar(propMap, "format"),
                            EnumValues = GetStringSequence(propMap, "enum"),
                        };
                        config.Schema.Properties[fieldName] = prop;
                    }
                }
            }

            config.Schema.Required = GetStringSequence(schemaNode, "required") ?? new List<string>();
        }

        if (GetMapping(root, "uischema") is { } uiNode)
        {
            config.Uischema = ParseUiElement(uiNode);
        }

        if (GetMapping(root, "data") is { } dataNode)
        {
            foreach (var entry in dataNode.Children)
            {
                if (entry.Key is not YamlScalarNode keyScalar || string.IsNullOrEmpty(keyScalar.Value))
                {
                    continue;
                }

                config.Data[keyScalar.Value] = ConvertYamlNode(entry.Value);
            }
        }

        config.Template = GetScalar(root, "template") ?? string.Empty;
        return (config, fieldOrder);
    }

    private static UiElement ParseUiElement(YamlMappingNode node)
    {
        var element = new UiElement
        {
            ElementType = GetScalar(node, "type") ?? "Control",
            Scope = GetScalar(node, "scope"),
        };

        if (GetMapping(node, "options") is { } optMap)
        {
            element.Options = new UiOptions
            {
                Multi = GetBool(optMap, "multi"),
                Rows = GetInt(optMap, "rows"),
                Placeholder = GetScalar(optMap, "placeholder"),
                Format = GetScalar(optMap, "format"),
                DateFormat = GetScalar(optMap, "dateFormat"),
                DateSaveFormat = GetScalar(optMap, "dateSaveFormat"),
            };
        }

        if (GetMapping(node, "rule") is { } ruleMap)
        {
            var condMap = GetMapping(ruleMap, "condition");
            var condSchemaMap = condMap is not null ? GetMapping(condMap, "schema") : null;
            element.Rule = new UiRule
            {
                Effect = GetScalar(ruleMap, "effect") ?? "SHOW",
                Condition = new RuleCondition
                {
                    Scope = condMap is not null ? (GetScalar(condMap, "scope") ?? string.Empty) : string.Empty,
                    ExpectedValue = condSchemaMap is not null ? GetScalar(condSchemaMap, "const") : null,
                },
            };
        }

        if (TryGetNode(node, "elements") is YamlSequenceNode seq)
        {
            foreach (var child in seq.Children)
            {
                if (child is YamlMappingNode childMap)
                {
                    element.Elements.Add(ParseUiElement(childMap));
                }
            }
        }

        return element;
    }

    private static void CollectUiMetadata(
        IReadOnlyList<UiElement> elements,
        IReadOnlyList<UiRule> inheritedRules,
        Dictionary<string, List<UiRule>> fieldRules,
        Dictionary<string, UiOptions> fieldOptions)
    {
        foreach (var el in elements)
        {
            var activeRules = new List<UiRule>(inheritedRules);
            if (el.Rule is not null)
            {
                activeRules.Add(el.Rule);
            }

            if (!string.IsNullOrEmpty(el.Scope))
            {
                var fieldName = el.Scope.StartsWith("#/properties/", StringComparison.Ordinal)
                    ? el.Scope["#/properties/".Length..]
                    : el.Scope;

                if (!string.IsNullOrEmpty(fieldName))
                {
                    if (activeRules.Count > 0)
                    {
                        fieldRules[fieldName] = activeRules;
                    }

                    if (el.Options is not null)
                    {
                        fieldOptions[fieldName] = el.Options;
                    }
                }
            }

            if (el.Elements.Count > 0)
            {
                CollectUiMetadata(el.Elements, activeRules, fieldRules, fieldOptions);
            }
        }
    }

    private static Dictionary<string, ResolvedDefault> ResolveDefaults(FormConfig config, EnvStore env)
    {
        var result = new Dictionary<string, ResolvedDefault>(StringComparer.Ordinal);
        foreach (var (key, prop) in config.Schema.Properties)
        {
            config.Data.TryGetValue(key, out var rawVal);
            result[key] = ResolveSingleDefault(prop, rawVal, env);
        }
        return result;
    }

    private static ResolvedDefault ResolveSingleDefault(SchemaProperty prop, object? rawVal, EnvStore env)
    {
        switch (prop.FieldType)
        {
            case "array":
            {
                var items = new List<string>();
                if (rawVal is string s)
                {
                    var varName = EnvStore.ExtractExactVar(s);
                    if (varName is not null)
                    {
                        items = env.GetList(varName);
                    }
                    else
                    {
                        var interp = env.InterpolateStr(s);
                        if (!string.IsNullOrEmpty(interp))
                        {
                            items = interp.Split('\n')
                                .Select(l => l.Trim())
                                .Where(l => !string.IsNullOrEmpty(l))
                                .ToList();
                        }
                    }
                }
                else if (rawVal is IEnumerable<string> seq)
                {
                    foreach (var item in seq)
                    {
                        var varName = EnvStore.ExtractExactVar(item);
                        if (varName is not null)
                        {
                            items.AddRange(env.GetList(varName));
                        }
                        else
                        {
                            var interp = env.InterpolateStr(item);
                            if (!string.IsNullOrEmpty(interp))
                            {
                                items.Add(interp);
                            }
                        }
                    }
                }
                return new ResolvedDefault.List(items);
            }
            case "boolean":
            {
                var b = rawVal switch
                {
                    bool bv => bv,
                    string sv => env.InterpolateStr(sv).Trim().ToLowerInvariant() is "true" or "1" or "sim",
                    _ => false,
                };
                return new ResolvedDefault.Bool(b);
            }
            default:
            {
                var text = rawVal switch
                {
                    string sv => env.InterpolateStr(sv),
                    bool bv => bv ? "true" : "false",
                    null => string.Empty,
                    _ => Convert.ToString(rawVal, CultureInfo.InvariantCulture) ?? string.Empty,
                };
                return new ResolvedDefault.Text(text);
            }
        }
    }

    public static void ApplyDynamicDefaults(string formName, Dictionary<string, ResolvedDefault> defaults, DateTime now)
    {
        if (!string.Equals(formName, "transporte_urbano", StringComparison.Ordinal))
        {
            return;
        }

        var shouldFill = !defaults.TryGetValue("hora_hoje", out var existing) ||
                         (existing is ResolvedDefault.Text t && string.IsNullOrWhiteSpace(t.Value));

        if (!shouldFill)
        {
            return;
        }

        var plus30 = now.AddMinutes(30);
        DateTime rounded;
        if (plus30.Minute == 0)
        {
            rounded = new DateTime(plus30.Year, plus30.Month, plus30.Day, plus30.Hour, 0, 0);
        }
        else if (plus30.Minute <= 30)
        {
            rounded = new DateTime(plus30.Year, plus30.Month, plus30.Day, plus30.Hour, 30, 0);
        }
        else
        {
            var nextHour = plus30.AddHours(1);
            rounded = new DateTime(nextHour.Year, nextHour.Month, nextHour.Day, nextHour.Hour, 0, 0);
        }

        defaults["hora_hoje"] = new ResolvedDefault.Text(rounded.ToString("HH:mm", CultureInfo.InvariantCulture));
    }

    private static string PrettifyName(string name)
    {
        var words = name.Split('_', StringSplitOptions.RemoveEmptyEntries);
        return string.Join(" ", words.Select(w =>
            char.ToUpper(w[0], CultureInfo.CurrentCulture) + w[1..]));
    }

    private static YamlNode? TryGetNode(YamlMappingNode map, string key)
    {
        foreach (var entry in map.Children)
        {
            if (entry.Key is YamlScalarNode scalar && string.Equals(scalar.Value, key, StringComparison.Ordinal))
            {
                return entry.Value;
            }
        }
        return null;
    }

    private static YamlMappingNode? GetMapping(YamlMappingNode map, string key) =>
        TryGetNode(map, key) as YamlMappingNode;

    private static string? GetScalar(YamlMappingNode map, string key) =>
        (TryGetNode(map, key) as YamlScalarNode)?.Value;

    private static bool? GetBool(YamlMappingNode map, string key)
    {
        var raw = GetScalar(map, key);
        return bool.TryParse(raw, out var b) ? b : null;
    }

    private static int? GetInt(YamlMappingNode map, string key)
    {
        var raw = GetScalar(map, key);
        return int.TryParse(raw, NumberStyles.Integer, CultureInfo.InvariantCulture, out var i) ? i : null;
    }

    private static List<string>? GetStringSequence(YamlMappingNode map, string key)
    {
        if (TryGetNode(map, key) is not YamlSequenceNode seq)
        {
            return null;
        }

        var list = new List<string>();
        foreach (var item in seq.Children)
        {
            if (item is YamlScalarNode scalar && scalar.Value is not null)
            {
                list.Add(scalar.Value);
            }
        }
        return list;
    }

    private static object? ConvertYamlNode(YamlNode node) => node switch
    {
        YamlScalarNode s => s.Value,
        YamlSequenceNode seq => seq.Children
            .OfType<YamlScalarNode>()
            .Select(s => s.Value ?? string.Empty)
            .ToList(),
        _ => null,
    };
}
