using System.Text;
using System.Text.Json;
using System.Windows;
using StiForms.Services;

namespace StiForms;

public partial class App : Application
{
    private sealed record CliArgs(
        bool ShowHelp,
        string? FormName,
        string? FormConfig,
        string? ActionName,
        bool? PasteOverride,
        bool JsonOutput,
        bool DumpResolved);

    protected override async void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);
        ShutdownMode = ShutdownMode.OnExplicitShutdown;

        Win32Helper.EnsureConsoleAttachedIfInteractive();

        if (!Console.IsOutputRedirected)
        {
            try
            {
                var stdOut = new System.IO.StreamWriter(Console.OpenStandardOutput(), new UTF8Encoding(false)) { AutoFlush = true };
                Console.SetOut(stdOut);
                var stdErr = new System.IO.StreamWriter(Console.OpenStandardError(), new UTF8Encoding(false)) { AutoFlush = true };
                Console.SetError(stdErr);
            }
            catch
            {
                // Ignore if no console stream is attached
            }
        }

        try
        {
            Console.OutputEncoding = new UTF8Encoding(false);
        }
        catch
        {
            // Ignore when stdout handle cannot change encoding
        }

        CliArgs parsed;
        try
        {
            parsed = ParseArgs(e.Args);
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"Erro: {ex.Message}");
            PrintHelp();
            Shutdown(2);
            return;
        }

        if (parsed.ShowHelp)
        {
            PrintHelp();
            Shutdown(0);
            return;
        }

        if (!string.IsNullOrWhiteSpace(parsed.ActionName))
        {
            IntPtr previousHwnd = Win32Helper.GetForegroundWindow();
            try
            {
                int exitCode = await ActionRunner.ExecuteAsync(parsed.ActionName, parsed.PasteOverride, previousHwnd);
                Shutdown(exitCode);
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"Erro ao executar ação '{parsed.ActionName}': {ex.Message}");
                Shutdown(1);
            }
            return;
        }

        try
        {
            var path = FormLoader.ResolveFormPath(parsed.FormName, parsed.FormConfig);
            var loaded = FormLoader.LoadFormFromPath(path);

            if (parsed.DumpResolved)
            {
                var dump = new
                {
                    form_name = loaded.FormName,
                    display_title = loaded.DisplayTitle,
                    field_order = loaded.FieldOrder,
                    resolved_defaults = loaded.ResolvedDefaults,
                };
                var json = JsonSerializer.Serialize(dump, new JsonSerializerOptions { WriteIndented = true });
                Console.Out.WriteLine(json);
                Console.Out.Flush();
                Shutdown(0);
                return;
            }

            var window = new MainWindow(loaded, parsed.JsonOutput);
            MainWindow = window;
            bool? accepted = window.ShowDialog();

            if (accepted == true && window.RenderedOutput is not null)
            {
                WriteUtf8ToStdOut(window.RenderedOutput);
                Shutdown(0);
            }
            else
            {
                Shutdown(1);
            }
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine(ex.Message);
            Shutdown(1);
        }
    }

    private static CliArgs ParseArgs(string[] args)
    {
        bool showHelp = false;
        string? formName = null;
        string? formConfig = null;
        string? actionName = null;
        bool? pasteOverride = null;
        bool jsonOutput = false;
        bool dumpResolved = false;

        for (int i = 0; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "-h":
                case "--help":
                    showHelp = true;
                    return new CliArgs(true, null, null, null, null, false, false);
                case "--form":
                    if (i + 1 >= args.Length) throw new ArgumentException("Faltou o nome após --form.");
                    formName = args[++i];
                    break;
                case "--form-config":
                    if (i + 1 >= args.Length) throw new ArgumentException("Faltou o caminho após --form-config.");
                    formConfig = args[++i];
                    break;
                case "--action":
                    if (i + 1 >= args.Length) throw new ArgumentException("Faltou o nome após --action.");
                    actionName = args[++i];
                    break;
                case "--paste":
                    pasteOverride = true;
                    break;
                case "--no-paste":
                    pasteOverride = false;
                    break;
                case "--json":
                    jsonOutput = true;
                    break;
                case "--dump-resolved":
                    dumpResolved = true;
                    break;
                default:
                    throw new ArgumentException($"Argumento desconhecido: {args[i]}");
            }
        }

        if (!showHelp && formName is null && formConfig is null && actionName is null)
        {
            throw new ArgumentException("Informe --form <nome>, --form-config <caminho.yml> ou --action <acao>.");
        }

        return new CliArgs(showHelp, formName, formConfig, actionName, pasteOverride, jsonOutput, dumpResolved);
    }

    private static void WriteUtf8ToStdOut(string text)
    {
        var bytes = new UTF8Encoding(false).GetBytes(text);
        using var stdout = Console.OpenStandardOutput();
        stdout.Write(bytes, 0, bytes.Length);
        stdout.Flush();
    }

    private static void PrintHelp()
    {
        Console.Error.WriteLine(
            "Uso: sti-forms.exe (--form <nome> | --form-config <caminho.yml>) [--json] [--dump-resolved]\n" +
            "     sti-forms.exe --action <acao> [--paste | --no-paste]");
    }
}
