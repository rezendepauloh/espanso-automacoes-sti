using System.Globalization;
using StiForms.Models;

namespace StiForms.Services;

public static class FormValidator
{
    public static string NormalizeDateToIso(string raw)
    {
        var trimmed = raw.Trim();
        if (string.IsNullOrEmpty(trimmed))
        {
            return string.Empty;
        }

        if (DateOnly.TryParseExact(trimmed, "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out var isoDate))
        {
            return isoDate.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture);
        }

        if (DateOnly.TryParseExact(trimmed, "dd/MM/yyyy", CultureInfo.InvariantCulture, DateTimeStyles.None, out var brDate))
        {
            return brDate.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture);
        }

        throw new FormatException($"Data inválida: '{trimmed}'. Use DD/MM/AAAA (ex: 25/11/2026) ou AAAA-MM-DD.");
    }

    public static string IsoToBrDate(string raw)
    {
        var trimmed = raw.Trim();
        if (DateOnly.TryParseExact(trimmed, "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out var isoDate))
        {
            return isoDate.ToString("dd/MM/yyyy", CultureInfo.InvariantCulture);
        }

        return trimmed;
    }

    public static bool IsSafeIdentifier(string value)
    {
        var trimmed = value.Trim();
        return !string.IsNullOrEmpty(trimmed) &&
               trimmed.All(c => char.IsAsciiLetterOrDigit(c) || c is '.' or '_' or '-' or ':');
    }

    public static bool IsSafePathArg(string value)
    {
        return !value.Any(c => c is ';' or '&' or '|' or '`' or '$' or '(' or ')' or '<' or '>' or '"' or '\'' or '\r' or '\n');
    }

    public static string? ValidateSubmission(
        string formName,
        FormConfig config,
        IReadOnlyDictionary<string, string> visibleValues,
        IReadOnlyDictionary<string, bool> visibility)
    {
        foreach (var reqField in config.Schema.Required)
        {
            var isVisible = !visibility.TryGetValue(reqField, out var vis) || vis;
            if (!isVisible)
            {
                continue;
            }

            var val = visibleValues.TryGetValue(reqField, out var v) ? v : string.Empty;
            if (string.IsNullOrWhiteSpace(val))
            {
                var label = config.Schema.Properties.TryGetValue(reqField, out var prop) && !string.IsNullOrEmpty(prop.Title)
                    ? prop.Title
                    : reqField;
                return $"O campo obrigatório \"{label.TrimEnd(':')}\" precisa ser preenchido.";
            }
        }

        foreach (var (field, prop) in config.Schema.Properties)
        {
            var isVisible = !visibility.TryGetValue(field, out var vis) || vis;
            if (!isVisible)
            {
                continue;
            }

            var val = visibleValues.TryGetValue(field, out var v) ? v.Trim() : string.Empty;
            if (string.IsNullOrEmpty(val))
            {
                continue;
            }

            var err = ValidateFieldType(formName, field, prop, val);
            if (err is not null)
            {
                return err;
            }
        }

        return null;
    }

    private static string? ValidateFieldType(string formName, string field, SchemaProperty prop, string val)
    {
        var label = (prop.Title ?? field).TrimEnd(':');

        if (string.Equals(prop.FieldType, "integer", StringComparison.Ordinal) &&
            !long.TryParse(val, NumberStyles.Integer, CultureInfo.InvariantCulture, out _))
        {
            return $"O campo \"{label}\" deve conter um número inteiro válido.";
        }

        if (string.Equals(prop.Format, "date", StringComparison.Ordinal))
        {
            try
            {
                NormalizeDateToIso(val);
            }
            catch (FormatException ex)
            {
                return ex.Message;
            }
        }

        if (formName is "analisador" or "manutencao" or "remove_profiles")
        {
            if (string.Equals(field, "computer_name", StringComparison.Ordinal) && !IsSafeIdentifier(val))
            {
                return $"O campo \"{label}\" contém caracteres não permitidos para hostname/IP.";
            }

            if (string.Equals(field, "output_folder", StringComparison.Ordinal) && !IsSafePathArg(val))
            {
                return $"O campo \"{label}\" contém caracteres de shell não permitidos.";
            }

            if (string.Equals(field, "users_to_purge", StringComparison.Ordinal))
            {
                foreach (var user in val.Split(',').Select(s => s.Trim()).Where(s => !string.IsNullOrEmpty(s)))
                {
                    if (!IsSafeIdentifier(user))
                    {
                        return $"Usuário inválido em \"{label}\": '{user}'.";
                    }
                }
            }
        }

        return null;
    }
}
