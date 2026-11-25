using System.Diagnostics;
using System.IO;
using System.Text;

namespace StiForms.Services;

public static class ActionRunner
{
    private sealed record ActionSpec(string ScriptRelPath, string[] ExtraArgs, bool ShouldPaste, bool ForceHtml);

    private static readonly Dictionary<string, ActionSpec> ActionMap = new(StringComparer.OrdinalIgnoreCase)
    {
        ["ola"] = new("scripts/python/dispatcher.py", Array.Empty<string>(), true, true),
        ["celular"] = new("scripts/python/celular.py", Array.Empty<string>(), true, true),
        ["devolucao_chamado"] = new("scripts/python/devolucao_chamado.py", Array.Empty<string>(), true, true),
        ["devolu"] = new("scripts/python/devolucao_chamado.py", Array.Empty<string>(), true, true),
        ["devolucao"] = new("scripts/python/devolucao_chamado.py", Array.Empty<string>(), true, true),
        ["devolução_chamado"] = new("scripts/python/devolucao_chamado.py", Array.Empty<string>(), true, true),
        ["transporte_urbano"] = new("scripts/python/transporte_urbano.py", Array.Empty<string>(), true, true),
        ["transporte"] = new("scripts/python/transporte_urbano.py", Array.Empty<string>(), true, true),
        ["transporte_material"] = new("scripts/python/transporte_material.py", Array.Empty<string>(), true, true),
        ["transdevo"] = new("scripts/python/transporte_material.py", Array.Empty<string>(), true, true),
        ["transporte_viagem"] = new("scripts/python/transporte_viagem.py", Array.Empty<string>(), true, true),
        ["viagem"] = new("scripts/python/transporte_viagem.py", Array.Empty<string>(), true, true),
        ["diaria_viagem"] = new("scripts/python/diaria_viagem.py", Array.Empty<string>(), true, true),
        ["diaria"] = new("scripts/python/diaria_viagem.py", Array.Empty<string>(), true, true),
        ["analisador"] = new("scripts/python/executar_admin.py", new[] { "analisador" }, false, false),
        ["manutencao"] = new("scripts/python/executar_admin.py", new[] { "manutencao" }, false, false),
        ["removeruser"] = new("scripts/python/executar_admin.py", new[] { "removeruser" }, false, false),
        ["remove_profiles"] = new("scripts/python/executar_admin.py", new[] { "removeruser" }, false, false),
        ["deluser"] = new("scripts/python/executar_admin.py", new[] { "removeruser" }, false, false),
        ["ia_arrumar"] = new("scripts/python/ia_arrumar.py", Array.Empty<string>(), true, false),
        ["arrumar"] = new("scripts/python/ia_arrumar.py", Array.Empty<string>(), true, false),
        ["maiuscula"] = new("scripts/python/maiuscula.py", Array.Empty<string>(), true, false),
        ["minuscula"] = new("scripts/python/minuscula.py", Array.Empty<string>(), true, false),
    };

    public static async Task<int> ExecuteAsync(string actionRaw, bool? pasteOverride, IntPtr previousHwnd)
    {
        var action = actionRaw.Trim().TrimStart(':');
        var repoRoot = EnvStore.DiscoverRepoRoot();

        if (string.Equals(action, "limpa_pdf", StringComparison.OrdinalIgnoreCase) ||
            string.Equals(action, "limpar_pdf", StringComparison.OrdinalIgnoreCase))
        {
            var clipText = ClipboardService.ReadClipboardText();
            if (string.IsNullOrWhiteSpace(clipText))
            {
                return 0;
            }

            var cleaned = PdfCleaner.CleanPdfText(clipText);
            ClipboardService.SetClipboardContent(cleaned, forceHtml: false);

            if (pasteOverride ?? true)
            {
                PasteBackToWindow(previousHwnd);
            }
            return 0;
        }

        if (!ActionMap.TryGetValue(action, out var spec))
        {
            Console.Error.WriteLine($"Ação desconhecida: {actionRaw}");
            return 2;
        }

        var scriptPath = Path.Combine(repoRoot, spec.ScriptRelPath.Replace('/', Path.DirectorySeparatorChar));
        if (!File.Exists(scriptPath))
        {
            Console.Error.WriteLine($"Script não encontrado: {scriptPath}");
            return 1;
        }

        var (pythonExe, pythonPrefixArgs) = ResolvePythonExecutable();
        var psi = new ProcessStartInfo
        {
            FileName = pythonExe,
            WorkingDirectory = repoRoot,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            StandardOutputEncoding = Encoding.UTF8,
            StandardErrorEncoding = Encoding.UTF8,
            UseShellExecute = false,
            CreateNoWindow = true,
        };

        foreach (var prefixArg in pythonPrefixArgs)
        {
            psi.ArgumentList.Add(prefixArg);
        }
        psi.ArgumentList.Add(scriptPath);
        foreach (var extra in spec.ExtraArgs)
        {
            psi.ArgumentList.Add(extra);
        }

        psi.Environment["ESPANSO_CONFIG_DIR"] = repoRoot;
        psi.Environment["PYTHONIOENCODING"] = "utf-8";
        var selfExe = Environment.ProcessPath;
        if (!string.IsNullOrEmpty(selfExe))
        {
            psi.Environment["STI_FORMS_BIN"] = selfExe;
        }

        using var process = Process.Start(psi);
        if (process is null)
        {
            return 1;
        }

        var stdoutTask = process.StandardOutput.ReadToEndAsync();
        var stderrTask = process.StandardError.ReadToEndAsync();
        await process.WaitForExitAsync();

        var output = await stdoutTask;
        var stderr = await stderrTask;

        if (!string.IsNullOrWhiteSpace(stderr))
        {
            Console.Error.WriteLine(stderr.TrimEnd());
        }

        if (process.ExitCode != 0)
        {
            return process.ExitCode;
        }

        if (string.IsNullOrEmpty(output))
        {
            return 0;
        }

        bool shouldPaste = pasteOverride ?? spec.ShouldPaste;
        if (!spec.ShouldPaste && pasteOverride != true)
        {
            return 0;
        }

        ClipboardService.SetClipboardContent(output, spec.ForceHtml);

        if (shouldPaste)
        {
            PasteBackToWindow(previousHwnd);
        }

        return 0;
    }

    private static void PasteBackToWindow(IntPtr previousHwnd)
    {
        Win32Helper.RestoreForegroundWindow(previousHwnd);
        Thread.Sleep(120);
        Win32Helper.SendCtrlV();
    }

    private static (string Exe, string[] PrefixArgs) ResolvePythonExecutable()
    {
        foreach (var candidate in new[] { "python", "python3" })
        {
            var resolved = FindRealExecutableInPath(candidate);
            if (resolved is not null)
            {
                return (resolved, Array.Empty<string>());
            }
        }

        var pyLauncher = FindRealExecutableInPath("py");
        if (pyLauncher is not null)
        {
            return (pyLauncher, new[] { "-3" });
        }

        var localPrograms = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "Programs",
            "Python");
        if (Directory.Exists(localPrograms))
        {
            foreach (var dir in Directory.GetDirectories(localPrograms, "Python3*").OrderByDescending(d => d))
            {
                var pyExe = Path.Combine(dir, "python.exe");
                if (File.Exists(pyExe))
                {
                    return (pyExe, Array.Empty<string>());
                }
            }
        }

        return ("python", Array.Empty<string>());
    }

    private static string? FindRealExecutableInPath(string command)
    {
        var pathEnv = Environment.GetEnvironmentVariable("PATH") ?? string.Empty;
        foreach (var dir in pathEnv.Split(Path.PathSeparator, StringSplitOptions.RemoveEmptyEntries))
        {
            var trimmedDir = dir.Trim();
            if (trimmedDir.Contains("WindowsApps", StringComparison.OrdinalIgnoreCase))
            {
                continue;
            }

            foreach (var ext in new[] { ".exe", ".cmd", ".bat", string.Empty })
            {
                var full = Path.Combine(trimmedDir, command + ext);
                if (File.Exists(full))
                {
                    return full;
                }
            }
        }
        return null;
    }
}
