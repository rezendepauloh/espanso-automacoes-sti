using System.IO;
using System.Text.RegularExpressions;

namespace StiForms.Services;

public sealed class EnvStore
{
    private readonly Dictionary<string, string> _primary;
    private readonly Dictionary<string, string> _fallback;

    private static readonly Regex VarPattern = new(@"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", RegexOptions.Compiled);
    private static readonly Regex ExactVarPattern = new(@"^\s*\$\{([A-Za-z_][A-Za-z0-9_]*)\}\s*$", RegexOptions.Compiled);

    public EnvStore(Dictionary<string, string> primary, Dictionary<string, string> fallback)
    {
        _primary = primary;
        _fallback = fallback;
    }

    public static EnvStore LoadFromRepoRoot(string repoRoot)
    {
        var primary = ParseEnvFile(Path.Combine(repoRoot, ".env"));
        var fallback = ParseEnvFile(Path.Combine(repoRoot, ".env.example"));
        return new EnvStore(primary, fallback);
    }

    public string Get(string key, string defaultValue = "")
    {
        var envVal = Environment.GetEnvironmentVariable(key);
        if (!string.IsNullOrEmpty(envVal))
        {
            return envVal;
        }

        if (_primary.TryGetValue(key, out var pVal) && !string.IsNullOrEmpty(pVal))
        {
            return pVal;
        }

        if (_fallback.TryGetValue(key, out var fVal) && !string.IsNullOrEmpty(fVal))
        {
            return fVal;
        }

        return defaultValue;
    }

    public List<string> GetList(string key)
    {
        var raw = Get(key, string.Empty);
        if (string.IsNullOrEmpty(raw))
        {
            return new List<string>();
        }

        return raw.Split('|')
            .Select(s => s.Trim())
            .Where(s => !string.IsNullOrEmpty(s))
            .ToList();
    }

    public string InterpolateStr(string input)
    {
        if (string.IsNullOrEmpty(input) || !input.Contains("${", StringComparison.Ordinal))
        {
            return input;
        }

        return VarPattern.Replace(input, match => Get(match.Groups[1].Value, string.Empty));
    }

    public static string? ExtractExactVar(string input)
    {
        if (string.IsNullOrEmpty(input))
        {
            return null;
        }

        var match = ExactVarPattern.Match(input);
        return match.Success ? match.Groups[1].Value : null;
    }

    public static Dictionary<string, string> ParseEnvFile(string path)
    {
        var map = new Dictionary<string, string>(StringComparer.Ordinal);
        if (!File.Exists(path))
        {
            return map;
        }

        foreach (var rawLine in File.ReadAllLines(path))
        {
            var line = rawLine.Trim();
            if (string.IsNullOrEmpty(line) || line.StartsWith('#'))
            {
                continue;
            }

            if (line.StartsWith("export ", StringComparison.Ordinal))
            {
                line = line[7..].Trim();
            }

            var eqIdx = line.IndexOf('=');
            if (eqIdx < 0)
            {
                continue;
            }

            var key = line[..eqIdx].Trim();
            var val = line[(eqIdx + 1)..].Trim();

            if (val.Length >= 2)
            {
                var first = val[0];
                var last = val[^1];
                if ((first == '"' && last == '"') || (first == '\'' && last == '\''))
                {
                    var inner = val[1..^1];
                    val = first == '"'
                        ? inner.Replace("\\\"", "\"").Replace("\\\\", "\\")
                        : inner;
                }
            }

            map[key] = val;
        }

        return map;
    }

    public static string DiscoverRepoRoot(string? hintPath = null)
    {
        if (!string.IsNullOrWhiteSpace(hintPath))
        {
            var found = WalkUpForRepo(Path.GetFullPath(hintPath));
            if (found is not null)
            {
                return found;
            }
        }

        var espansoDir = Environment.GetEnvironmentVariable("ESPANSO_CONFIG_DIR");
        if (!string.IsNullOrWhiteSpace(espansoDir) && Directory.Exists(Path.Combine(espansoDir, "forms")))
        {
            return espansoDir;
        }

        var fromCwd = WalkUpForRepo(Directory.GetCurrentDirectory());
        if (fromCwd is not null)
        {
            return fromCwd;
        }

        var fromExe = WalkUpForRepo(AppContext.BaseDirectory);
        if (fromExe is not null)
        {
            return fromExe;
        }

        var appDataEspanso = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
            "espanso");
        if (Directory.Exists(Path.Combine(appDataEspanso, "forms")))
        {
            return appDataEspanso;
        }

        return Directory.GetCurrentDirectory();
    }

    private static string? WalkUpForRepo(string startPath)
    {
        var current = File.Exists(startPath)
            ? Directory.GetParent(startPath)?.FullName
            : startPath;

        while (!string.IsNullOrEmpty(current))
        {
            if (Directory.Exists(Path.Combine(current, "forms")) &&
                (Directory.Exists(Path.Combine(current, "match")) || Directory.Exists(Path.Combine(current, "scripts"))))
            {
                return current;
            }

            current = Directory.GetParent(current)?.FullName;
        }

        return null;
    }
}
