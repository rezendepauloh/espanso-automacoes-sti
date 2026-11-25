using System.Text;
using System.Text.RegularExpressions;

namespace StiForms.Services;

public static class PdfCleaner
{
    private static readonly Regex LegalAbbrevRegex = new(
        @"\b(art|arts|inc|fls|n|nº|doc|pg|pag|pág)\.$",
        RegexOptions.IgnoreCase | RegexOptions.Compiled);

    private static readonly Regex MarkerStartRegex = new(
        @"^(Art\.|§|Parágrafo|CAPÍTULO|TÍTULO|SEÇÃO|CONSIDERANDO|RESOLVE|O PROCURADOR|[IVXLCDM]+\s*[-–]|[a-z]\)|[A-Z]\s*[-–]|\d+\.)",
        RegexOptions.IgnoreCase | RegexOptions.Compiled);

    private static readonly Regex UpperOrDigitStartRegex = new(@"^[A-Z0-9]", RegexOptions.Compiled);
    private static readonly Regex MultiSpaceRegex = new(@" {2,}", RegexOptions.Compiled);

    public static string CleanPdfText(string texto)
    {
        if (string.IsNullOrWhiteSpace(texto))
        {
            return texto;
        }

        var normalized = texto.Replace("\r", string.Empty, StringComparison.Ordinal);
        var linhas = normalized.Split('\n');
        var sb = new StringBuilder();

        for (int i = 0; i < linhas.Length; i++)
        {
            var linhaAtual = linhas[i].Trim();
            if (linhaAtual.Length == 0)
            {
                continue;
            }

            bool separacaoSilabica = false;
            if (linhaAtual.EndsWith('-') || linhaAtual.EndsWith('–'))
            {
                linhaAtual = linhaAtual[..^1];
                separacaoSilabica = true;
            }

            sb.Append(linhaAtual);

            if (i < linhas.Length - 1)
            {
                var proximaLinha = linhas[i + 1].Trim();
                if (proximaLinha.Length == 0)
                {
                    sb.Append("\r\n\r\n");
                    i++;
                }
                else
                {
                    char lastChar = linhaAtual.Length > 0 ? linhaAtual[^1] : '\0';
                    bool terminaComPontuacao = (lastChar is '.' or ';' or ':' or '!' or '?') &&
                                               !LegalAbbrevRegex.IsMatch(linhaAtual);

                    bool proximaComecaComMarcador = MarkerStartRegex.IsMatch(proximaLinha);
                    bool proximaComecaComMaiuscula = UpperOrDigitStartRegex.IsMatch(proximaLinha);

                    if ((terminaComPontuacao && proximaComecaComMaiuscula) || proximaComecaComMarcador)
                    {
                        sb.Append("\r\n\r\n");
                    }
                    else if (!separacaoSilabica)
                    {
                        sb.Append(' ');
                    }
                }
            }
        }

        return MultiSpaceRegex.Replace(sb.ToString(), " ");
    }
}
