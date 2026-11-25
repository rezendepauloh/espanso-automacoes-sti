using System.Net;
using System.Runtime.InteropServices;
using System.Text;
using System.Text.RegularExpressions;
using System.Windows;

namespace StiForms.Services;

public static class ClipboardService
{
    private static readonly Regex BreakTagRegex = new(@"<br\s*/?>", RegexOptions.IgnoreCase | RegexOptions.Compiled);
    private static readonly Regex BlockCloseRegex = new(@"</(p|div|li|h[1-6]|tr)>", RegexOptions.IgnoreCase | RegexOptions.Compiled);
    private static readonly Regex ListItemOpenRegex = new(@"<li\b[^>]*>", RegexOptions.IgnoreCase | RegexOptions.Compiled);
    private static readonly Regex AnyTagRegex = new(@"<[^>]+>", RegexOptions.Compiled);

    public static string BuildCfHtml(string htmlFragment)
    {
        const string headerTemplate =
            "Version:0.9\r\n" +
            "StartHTML:0000000000\r\n" +
            "EndHTML:0000000000\r\n" +
            "StartFragment:0000000000\r\n" +
            "EndFragment:0000000000\r\n";

        const string prefix = "<html>\r\n<body>\r\n<!--StartFragment-->";
        const string suffix = "<!--EndFragment-->\r\n</body>\r\n</html>";

        var utf8 = Encoding.UTF8;
        int startHtml = utf8.GetByteCount(headerTemplate);
        int startFragment = startHtml + utf8.GetByteCount(prefix);
        int endFragment = startFragment + utf8.GetByteCount(htmlFragment);
        int endHtml = endFragment + utf8.GetByteCount(suffix);

        var header =
            "Version:0.9\r\n" +
            $"StartHTML:{startHtml:D10}\r\n" +
            $"EndHTML:{endHtml:D10}\r\n" +
            $"StartFragment:{startFragment:D10}\r\n" +
            $"EndFragment:{endFragment:D10}\r\n";

        return header + prefix + htmlFragment + suffix;
    }

    public static string StripHtmlToPlainText(string html)
    {
        if (string.IsNullOrEmpty(html))
        {
            return string.Empty;
        }

        var text = BreakTagRegex.Replace(html, "\r\n");
        text = ListItemOpenRegex.Replace(text, "• ");
        text = BlockCloseRegex.Replace(text, "\r\n");
        text = AnyTagRegex.Replace(text, string.Empty);
        text = WebUtility.HtmlDecode(text);
        return text.Trim();
    }

    public static bool LooksLikeHtml(string content) =>
        content.Contains("<br", StringComparison.OrdinalIgnoreCase) ||
        content.Contains("<strong", StringComparison.OrdinalIgnoreCase) ||
        content.Contains("<ul", StringComparison.OrdinalIgnoreCase) ||
        content.Contains("<ol", StringComparison.OrdinalIgnoreCase) ||
        content.Contains("<a ", StringComparison.OrdinalIgnoreCase) ||
        content.Contains("<p", StringComparison.OrdinalIgnoreCase);

    public static string? ReadClipboardText()
    {
        for (int attempt = 0; attempt < 5; attempt++)
        {
            try
            {
                if (Clipboard.ContainsText())
                {
                    return Clipboard.GetText();
                }
                return null;
            }
            catch (COMException)
            {
                Thread.Sleep(25);
            }
        }
        return null;
    }

    public static void SetClipboardContent(string content, bool? forceHtml = null)
    {
        bool asHtml = forceHtml ?? LooksLikeHtml(content);
        var dataObj = new DataObject();

        if (asHtml)
        {
            var plain = StripHtmlToPlainText(content);
            var cfHtml = BuildCfHtml(content);
            dataObj.SetData(DataFormats.Html, cfHtml);
            dataObj.SetData(DataFormats.UnicodeText, plain);
            dataObj.SetData(DataFormats.Text, plain);
        }
        else
        {
            dataObj.SetData(DataFormats.UnicodeText, content);
            dataObj.SetData(DataFormats.Text, content);
        }

        for (int attempt = 0; attempt < 6; attempt++)
        {
            try
            {
                Clipboard.SetDataObject(dataObj, true);
                return;
            }
            catch (COMException)
            {
                Thread.Sleep(30);
            }
        }
    }
}
