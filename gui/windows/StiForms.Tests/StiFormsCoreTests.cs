using System.IO;
using System.Text;
using StiForms.Models;
using StiForms.Services;
using Xunit;

namespace StiForms.Tests;

public class StiFormsCoreTests
{
    private static string FindRepoRoot()
    {
        return EnvStore.DiscoverRepoRoot(AppContext.BaseDirectory);
    }

    [Fact]
    public void EnvStore_PrecedenceAndInterpolation_WorksCorrectly()
    {
        var primary = new Dictionary<string, string>
        {
            ["STI_RAMAL"] = "1234",
            ["STI_LOCAIS"] = "Sede|Anexo I|DMP",
        };
        var fallback = new Dictionary<string, string>
        {
            ["STI_RAMAL"] = "0000",
            ["STI_FALLBACK_ONLY"] = "FallbackValue",
        };

        var store = new EnvStore(primary, fallback);
        Assert.Equal("1234", store.Get("STI_RAMAL"));
        Assert.Equal("FallbackValue", store.Get("STI_FALLBACK_ONLY"));
        Assert.Equal(new[] { "Sede", "Anexo I", "DMP" }, store.GetList("STI_LOCAIS"));
        Assert.Equal("Ramal: 1234", store.InterpolateStr("Ramal: ${STI_RAMAL}"));
        Assert.Equal("STI_LOCAIS", EnvStore.ExtractExactVar(" ${STI_LOCAIS} "));
        Assert.Null(EnvStore.ExtractExactVar("Prefixo ${STI_LOCAIS}"));
    }

    [Fact]
    public void RuleEngine_NestedParentAndChildRules_EnforceAndLogic()
    {
        var repoRoot = FindRepoRoot();
        var olaPath = Path.Combine(repoRoot, "forms", "ola.yml");
        if (!File.Exists(olaPath))
        {
            return;
        }

        var loaded = FormLoader.LoadFormFromPath(olaPath);

        var valuesHidden = new Dictionary<string, string>
        {
            ["tipo"] = "🐢 Lentidão",
            ["tipo_material"] = "permanente",
        };
        Assert.False(RuleEngine.IsFieldVisible("patrimonio", loaded.FieldRules, valuesHidden));

        var valuesConsumo = new Dictionary<string, string>
        {
            ["tipo"] = "📦 Material",
            ["tipo_material"] = "consumo",
        };
        Assert.True(RuleEngine.IsFieldVisible("tipo_material", loaded.FieldRules, valuesConsumo));
        Assert.False(RuleEngine.IsFieldVisible("patrimonio", loaded.FieldRules, valuesConsumo));

        var valuesPermanente = new Dictionary<string, string>
        {
            ["tipo"] = "📦 Material",
            ["tipo_material"] = "permanente",
        };
        Assert.True(RuleEngine.IsFieldVisible("patrimonio", loaded.FieldRules, valuesPermanente));
    }

    [Fact]
    public void FormLoader_AllFormsInRepo_LoadWithoutErrors()
    {
        var repoRoot = FindRepoRoot();
        var formsDir = Path.Combine(repoRoot, "forms");
        if (!Directory.Exists(formsDir))
        {
            return;
        }

        var ymlFiles = Directory.GetFiles(formsDir, "*.yml")
            .Where(f => !Path.GetFileName(f).StartsWith(".temp_", StringComparison.Ordinal))
            .ToArray();

        Assert.True(ymlFiles.Length >= 8);
        foreach (var file in ymlFiles)
        {
            var loaded = FormLoader.LoadFormFromPath(file);
            Assert.NotEmpty(loaded.FieldOrder);
            Assert.NotEmpty(loaded.DisplayTitle);
        }
    }

    [Fact]
    public void FormLoader_DynamicHoraHoje_RoundsCorrectly()
    {
        var defaults = new Dictionary<string, ResolvedDefault>
        {
            ["hora_hoje"] = new ResolvedDefault.Text(string.Empty),
        };
        FormLoader.ApplyDynamicDefaults("transporte_urbano", defaults, new DateTime(2026, 11, 25, 10, 5, 0));
        Assert.Equal(new ResolvedDefault.Text("11:00"), defaults["hora_hoje"]);

        defaults["hora_hoje"] = new ResolvedDefault.Text(string.Empty);
        FormLoader.ApplyDynamicDefaults("transporte_urbano", defaults, new DateTime(2026, 11, 25, 10, 40, 0));
        Assert.Equal(new ResolvedDefault.Text("11:30"), defaults["hora_hoje"]);
    }

    [Fact]
    public void FormValidator_ValidatesDatesIntegersAndAdminInputs()
    {
        Assert.Equal("2026-11-25", FormValidator.NormalizeDateToIso("25/11/2026"));
        Assert.Equal("25/11/2026", FormValidator.IsoToBrDate("2026-11-25"));
        Assert.Throws<FormatException>(() => FormValidator.NormalizeDateToIso("31/02/2026"));

        Assert.True(FormValidator.IsSafeIdentifier("MPMS-PC01.local"));
        Assert.False(FormValidator.IsSafeIdentifier("pc01;whoami"));
        Assert.True(FormValidator.IsSafePathArg(@"C:\get-computer-info"));
        Assert.False(FormValidator.IsSafePathArg(@"C:\temp & calc"));
    }

    [Fact]
    public void OutputFormatter_TransporteUrbano_SelectsHoraHojeWhenToday()
    {
        var config = new FormConfig
        {
            Template = "{% if data == 'hoje' %}{{hora_hoje}}{% else %}{{hora}}{% endif %}",
        };
        var fieldOrder = new[] { "data", "data_manual", "hora_hoje", "hora", "local", "demandas", "passageiros" };
        var values = new Dictionary<string, string>
        {
            ["data"] = "hoje",
            ["data_manual"] = "",
            ["hora_hoje"] = "14:30",
            ["hora"] = "",
            ["local"] = "PGJ",
            ["demandas"] = "Chamado #1",
            ["passageiros"] = "Servidor 1",
        };

        var output = OutputFormatter.FormatOutput(config, fieldOrder, values, asJson: false);
        Assert.Contains("===FIELD:hora===\n14:30\n", output);
        Assert.EndsWith("===END===\n", output);
    }

    [Fact]
    public void ClipboardService_BuildCfHtml_UsesExactUtf8ByteOffsets()
    {
        var fragment = "Olá <strong>ação 🚀</strong>!";
        var cfHtml = ClipboardService.BuildCfHtml(fragment);
        var bytes = Encoding.UTF8.GetBytes(cfHtml);

        int ExtractOffset(string key)
        {
            var marker = $"{key}:";
            int idx = cfHtml.IndexOf(marker, StringComparison.Ordinal);
            Assert.True(idx >= 0);
            var numStr = cfHtml.Substring(idx + marker.Length, 10);
            return int.Parse(numStr);
        }

        int startHtml = ExtractOffset("StartHTML");
        int endHtml = ExtractOffset("EndHTML");
        int startFragment = ExtractOffset("StartFragment");
        int endFragment = ExtractOffset("EndFragment");

        Assert.Equal(bytes.Length, endHtml);
        Assert.Equal("<html>", Encoding.UTF8.GetString(bytes, startHtml, 6));
        Assert.Equal(fragment, Encoding.UTF8.GetString(bytes, startFragment, endFragment - startFragment));
        Assert.Equal("Olá ação 🚀!", ClipboardService.StripHtmlToPlainText(fragment));
    }

    [Fact]
    public void PdfCleaner_CleansHyphensMarginsAndLegalParagraphs()
    {
        Assert.Equal("O equipamento foi enviado à STI.", PdfCleaner.CleanPdfText("O equipamen-\nto foi enviado à STI."));
        Assert.Equal(
            "Esta é uma linha de texto que foi cortada pelo PDF de forma artificial.",
            PdfCleaner.CleanPdfText("Esta é uma linha de texto\nque foi cortada pelo PDF de forma artificial."));
        Assert.Equal(
            "O processo foi deferido.\r\n\r\nO Promotor assinará digitalmente.",
            PdfCleaner.CleanPdfText("O processo foi deferido.\nO Promotor assinará digitalmente."));
        Assert.Equal(
            "Nos termos do art. 1º da referida lei.",
            PdfCleaner.CleanPdfText("Nos termos do art.\n1º da referida lei."));
    }
}
