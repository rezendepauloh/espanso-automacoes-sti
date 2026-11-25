using System.Text.Json.Serialization;

namespace StiForms.Models;

public sealed class FormConfig
{
    public FormSchema Schema { get; set; } = new();
    public UiElement? Uischema { get; set; }
    public Dictionary<string, object?> Data { get; set; } = new();
    public string Template { get; set; } = string.Empty;
}

public sealed class FormSchema
{
    public string SchemaType { get; set; } = "object";
    public Dictionary<string, SchemaProperty> Properties { get; set; } = new();
    public List<string> Required { get; set; } = new();
}

public sealed class SchemaProperty
{
    public string FieldType { get; set; } = "string";
    public string? Title { get; set; }
    public string? Format { get; set; }
    public List<string>? EnumValues { get; set; }
}

public sealed class UiElement
{
    public string ElementType { get; set; } = "Control";
    public string? Scope { get; set; }
    public List<UiElement> Elements { get; set; } = new();
    public UiOptions? Options { get; set; }
    public UiRule? Rule { get; set; }
}

public sealed class UiOptions
{
    public bool? Multi { get; set; }
    public int? Rows { get; set; }
    public string? Placeholder { get; set; }
    public string? Format { get; set; }
    public string? DateFormat { get; set; }
    public string? DateSaveFormat { get; set; }
}

public sealed class UiRule
{
    public string Effect { get; set; } = "SHOW";
    public RuleCondition Condition { get; set; } = new();

    public string TriggerField() =>
        Condition.Scope.StartsWith("#/properties/", StringComparison.Ordinal)
            ? Condition.Scope["#/properties/".Length..]
            : Condition.Scope;

    public string ExpectedString() => Condition.ExpectedValue ?? string.Empty;
}

public sealed class RuleCondition
{
    public string Scope { get; set; } = string.Empty;
    public string? ExpectedValue { get; set; }
}

[JsonConverter(typeof(ResolvedDefaultJsonConverter))]
public abstract record ResolvedDefault
{
    public sealed record Text(string Value) : ResolvedDefault;
    public sealed record List(IReadOnlyList<string> Items) : ResolvedDefault;
    public sealed record Bool(bool Value) : ResolvedDefault;
}

public sealed class ResolvedDefaultJsonConverter : JsonConverter<ResolvedDefault>
{
    public override ResolvedDefault? Read(ref System.Text.Json.Utf8JsonReader reader, Type typeToConvert, System.Text.Json.JsonSerializerOptions options)
        => throw new NotSupportedException();

    public override void Write(System.Text.Json.Utf8JsonWriter writer, ResolvedDefault value, System.Text.Json.JsonSerializerOptions options)
    {
        writer.WriteStartObject();
        switch (value)
        {
            case ResolvedDefault.Text t:
                writer.WriteString("Text", t.Value);
                break;
            case ResolvedDefault.List l:
                writer.WritePropertyName("List");
                System.Text.Json.JsonSerializer.Serialize(writer, l.Items, options);
                break;
            case ResolvedDefault.Bool b:
                writer.WriteBoolean("Bool", b.Value);
                break;
        }
        writer.WriteEndObject();
    }
}

public sealed class LoadedForm
{
    public required string FormName { get; init; }
    public required string DisplayTitle { get; init; }
    public required string RepoRoot { get; init; }
    public required FormConfig Config { get; init; }
    public required IReadOnlyList<string> FieldOrder { get; init; }
    public required IReadOnlyList<UiElement> LayoutElements { get; init; }
    public required IReadOnlyDictionary<string, List<UiRule>> FieldRules { get; init; }
    public required IReadOnlyDictionary<string, ResolvedDefault> ResolvedDefaults { get; init; }
    public required IReadOnlyDictionary<string, UiOptions> FieldOptions { get; init; }
}
