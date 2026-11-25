using System.Globalization;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using StiForms.Models;
using StiForms.Services;
using Wpf.Ui.Controls;
using UiButton = Wpf.Ui.Controls.Button;
using UiTextBox = Wpf.Ui.Controls.TextBox;

namespace StiForms;

public partial class MainWindow : FluentWindow
{
    private enum FieldKind
    {
        Text,
        Integer,
        Date,
        TextArea,
        Dropdown,
        Radio,
        Boolean,
        ArrayChecklist,
    }

    private sealed class ArrayRowEntry
    {
        public required CheckBox Check { get; init; }
        public required Border RowBorder { get; init; }
        public required string Label { get; init; }
    }

    private sealed class FieldBinding
    {
        public required string Name { get; init; }
        public required string Title { get; init; }
        public required bool Required { get; init; }
        public required FieldKind Kind { get; init; }
        public required FrameworkElement Container { get; init; }
        public UiTextBox? TextBox { get; init; }
        public ComboBox? ComboBox { get; init; }
        public List<RadioButton>? RadioButtons { get; init; }
        public CheckBox? CheckBox { get; init; }
        public List<ArrayRowEntry>? ArrayEntries { get; init; }
        public StackPanel? ArrayListPanel { get; init; }
        public System.Windows.Controls.TextBlock? ArrayCounterText { get; init; }
        public UiTextBox? ArrayAddInput { get; init; }
        public FrameworkElement? FocusTarget { get; init; }
    }

    private readonly LoadedForm _loaded;
    private readonly bool _jsonOutput;
    private readonly Dictionary<string, FieldBinding> _bindings = new(StringComparer.Ordinal);
    private readonly Dictionary<FrameworkElement, UiElement> _elementContainers = new();

    public string? RenderedOutput { get; private set; }

    public MainWindow(LoadedForm loaded, bool jsonOutput)
    {
        _loaded = loaded;
        _jsonOutput = jsonOutput;

        InitializeComponent();

        Title = loaded.DisplayTitle;
        AppTitleBar.Title = loaded.DisplayTitle;

        try
        {
            var iconUri = new Uri("pack://application:,,,/Assets/app.ico", UriKind.Absolute);
            Icon = System.Windows.Media.Imaging.BitmapFrame.Create(iconUri);
        }
        catch
        {
            // Mantém o ícone padrão caso Assets/app.ico ainda não exista
        }

        BuildFormUi();
        UpdateVisibility();

        Loaded += (_, _) =>
        {
            Activate();
            FocusFirstVisibleControl();
        };
    }

    private void BuildFormUi()
    {
        foreach (var el in _loaded.LayoutElements)
        {
            var ui = BuildElement(el);
            if (ui is not null)
            {
                if (ui is FrameworkElement fe)
                {
                    fe.Margin = new Thickness(0, 0, 0, 12);
                }
                FormContainer.Children.Add(ui);
            }
        }
    }

    private UIElement? BuildElement(UiElement el)
    {
        switch (el.ElementType)
        {
            case "HorizontalLayout":
            {
                if (el.Elements.Count == 0)
                {
                    return null;
                }

                var grid = new Grid();
                for (int i = 0; i < el.Elements.Count; i++)
                {
                    grid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
                    var childUi = BuildElement(el.Elements[i]);
                    if (childUi is FrameworkElement fe)
                    {
                        fe.Margin = new Thickness(i == 0 ? 0 : 6, 0, i == el.Elements.Count - 1 ? 0 : 6, 0);
                        Grid.SetColumn(fe, i);
                        grid.Children.Add(fe);
                    }
                }
                _elementContainers[grid] = el;
                return grid;
            }
            case "VerticalLayout":
            {
                if (el.Elements.Count == 0)
                {
                    return null;
                }

                var stack = new StackPanel();
                foreach (var child in el.Elements)
                {
                    var childUi = BuildElement(child);
                    if (childUi is FrameworkElement fe)
                    {
                        fe.Margin = new Thickness(0, 0, 0, 10);
                        stack.Children.Add(fe);
                    }
                }
                _elementContainers[stack] = el;
                return stack;
            }
            default:
            {
                if (string.IsNullOrEmpty(el.Scope))
                {
                    return null;
                }

                var fieldName = el.Scope.StartsWith("#/properties/", StringComparison.Ordinal)
                    ? el.Scope["#/properties/".Length..]
                    : el.Scope;

                if (!_loaded.Config.Schema.Properties.TryGetValue(fieldName, out var prop))
                {
                    return null;
                }

                var opts = _loaded.FieldOptions.TryGetValue(fieldName, out var o) ? o : new UiOptions();
                _loaded.ResolvedDefaults.TryGetValue(fieldName, out var defVal);
                bool required = _loaded.Config.Schema.Required.Contains(fieldName);

                var binding = CreateFieldBinding(fieldName, prop, opts, defVal, required);
                _bindings[fieldName] = binding;
                return binding.Container;
            }
        }
    }

    private FieldBinding CreateFieldBinding(
        string name,
        SchemaProperty prop,
        UiOptions opts,
        ResolvedDefault? defaultVal,
        bool required)
    {
        var title = prop.Title ?? name;
        var kind = DetermineFieldKind(prop, opts);

        var wrapper = new StackPanel();
        var labelText = required ? $"{title.TrimEnd(':')} *" : title;
        var label = new System.Windows.Controls.TextBlock
        {
            Text = labelText,
            FontWeight = FontWeights.SemiBold,
            FontSize = 13,
            Margin = new Thickness(0, 0, 0, 6),
        };
        label.SetResourceReference(System.Windows.Controls.TextBlock.ForegroundProperty, "TextFillColorPrimaryBrush");
        wrapper.Children.Add(label);

        var placeholder = opts.Placeholder ?? "Digite aqui...";

        switch (kind)
        {
            case FieldKind.Text:
            case FieldKind.Integer:
            {
                var tb = new UiTextBox
                {
                    PlaceholderText = placeholder,
                    Text = defaultVal is ResolvedDefault.Text t ? t.Value : string.Empty,
                };

                if (kind == FieldKind.Integer)
                {
                    tb.PreviewTextInput += (_, e) =>
                    {
                        e.Handled = !e.Text.All(c => char.IsAsciiDigit(c) || c == '-');
                    };
                }

                tb.TextChanged += (_, _) => OnFieldChanged();
                tb.KeyDown += (_, e) =>
                {
                    if (e.Key == Key.Enter)
                    {
                        e.Handled = true;
                        SubmitForm();
                    }
                };

                wrapper.Children.Add(tb);
                return new FieldBinding
                {
                    Name = name,
                    Title = title,
                    Required = required,
                    Kind = kind,
                    Container = wrapper,
                    TextBox = tb,
                    FocusTarget = tb,
                };
            }

            case FieldKind.Date:
            {
                var initialDate = defaultVal is ResolvedDefault.Text dt && !string.IsNullOrWhiteSpace(dt.Value)
                    ? FormValidator.IsoToBrDate(dt.Value)
                    : string.Empty;

                var dateGrid = new Grid();
                dateGrid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
                dateGrid.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });
                dateGrid.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });

                var tb = new UiTextBox
                {
                    PlaceholderText = "DD/MM/AAAA",
                    Text = initialDate,
                    Margin = new Thickness(0, 0, 6, 0),
                };
                tb.TextChanged += (_, _) => OnFieldChanged();
                tb.KeyDown += (_, e) =>
                {
                    if (e.Key == Key.Enter)
                    {
                        e.Handled = true;
                        SubmitForm();
                    }
                };
                Grid.SetColumn(tb, 0);

                var btnToday = new UiButton
                {
                    Content = "Hoje",
                    Margin = new Thickness(0, 0, 6, 0),
                    Padding = new Thickness(12, 6, 12, 6),
                };
                btnToday.Click += (_, _) =>
                {
                    tb.Text = DateTime.Now.ToString("dd/MM/yyyy", CultureInfo.InvariantCulture);
                };
                Grid.SetColumn(btnToday, 1);

                var btnTomorrow = new UiButton
                {
                    Content = "Amanhã",
                    Padding = new Thickness(12, 6, 12, 6),
                };
                btnTomorrow.Click += (_, _) =>
                {
                    tb.Text = DateTime.Now.AddDays(1).ToString("dd/MM/yyyy", CultureInfo.InvariantCulture);
                };
                Grid.SetColumn(btnTomorrow, 2);

                dateGrid.Children.Add(tb);
                dateGrid.Children.Add(btnToday);
                dateGrid.Children.Add(btnTomorrow);
                wrapper.Children.Add(dateGrid);

                return new FieldBinding
                {
                    Name = name,
                    Title = title,
                    Required = required,
                    Kind = kind,
                    Container = wrapper,
                    TextBox = tb,
                    FocusTarget = tb,
                };
            }

            case FieldKind.TextArea:
            {
                int rows = Math.Max(opts.Rows ?? 4, 3);
                double height = Math.Min(rows * 24.0 + 18.0, 240.0);
                var tb = new UiTextBox
                {
                    PlaceholderText = placeholder,
                    Text = defaultVal is ResolvedDefault.Text t ? t.Value : string.Empty,
                    AcceptsReturn = true,
                    TextWrapping = TextWrapping.Wrap,
                    VerticalScrollBarVisibility = ScrollBarVisibility.Auto,
                    VerticalContentAlignment = VerticalAlignment.Top,
                    Height = height,
                };
                tb.TextChanged += (_, _) => OnFieldChanged();

                wrapper.Children.Add(tb);
                return new FieldBinding
                {
                    Name = name,
                    Title = title,
                    Required = required,
                    Kind = kind,
                    Container = wrapper,
                    TextBox = tb,
                    FocusTarget = tb,
                };
            }

            case FieldKind.Dropdown:
            {
                var options = prop.EnumValues ?? new List<string>();
                var combo = new ComboBox
                {
                    ItemsSource = options,
                    HorizontalAlignment = HorizontalAlignment.Stretch,
                };

                if (defaultVal is ResolvedDefault.Text defText)
                {
                    int idx = options.IndexOf(defText.Value);
                    combo.SelectedIndex = idx >= 0 ? idx : (options.Count > 0 ? 0 : -1);
                }
                else if (options.Count > 0)
                {
                    combo.SelectedIndex = 0;
                }

                combo.SelectionChanged += (_, _) => OnFieldChanged();
                wrapper.Children.Add(combo);

                return new FieldBinding
                {
                    Name = name,
                    Title = title,
                    Required = required,
                    Kind = kind,
                    Container = wrapper,
                    ComboBox = combo,
                    FocusTarget = combo,
                };
            }

            case FieldKind.Radio:
            {
                var options = prop.EnumValues ?? new List<string>();
                string? defText = defaultVal is ResolvedDefault.Text dt ? dt.Value : null;
                var radios = new List<RadioButton>();

                Panel panel = options.Count <= 4
                    ? new WrapPanel { Orientation = Orientation.Horizontal }
                    : new StackPanel();

                for (int i = 0; i < options.Count; i++)
                {
                    var opt = options[i];
                    var rb = new RadioButton
                    {
                        Content = opt,
                        GroupName = $"group_{name}",
                        Margin = new Thickness(0, 2, 16, 4),
                        IsChecked = defText is not null ? string.Equals(opt, defText, StringComparison.Ordinal) : i == 0,
                    };
                    rb.Checked += (_, _) => OnFieldChanged();
                    radios.Add(rb);
                    panel.Children.Add(rb);
                }

                if (radios.Count > 0 && !radios.Any(r => r.IsChecked == true))
                {
                    radios[0].IsChecked = true;
                }

                wrapper.Children.Add(panel);
                return new FieldBinding
                {
                    Name = name,
                    Title = title,
                    Required = required,
                    Kind = kind,
                    Container = wrapper,
                    RadioButtons = radios,
                    FocusTarget = radios.FirstOrDefault(),
                };
            }

            case FieldKind.Boolean:
            {
                var chk = new CheckBox
                {
                    Content = "Ativado",
                    IsChecked = defaultVal is ResolvedDefault.Bool b && b.Value,
                };
                chk.Checked += (_, _) => OnFieldChanged();
                chk.Unchecked += (_, _) => OnFieldChanged();
                wrapper.Children.Add(chk);

                return new FieldBinding
                {
                    Name = name,
                    Title = title,
                    Required = required,
                    Kind = kind,
                    Container = wrapper,
                    CheckBox = chk,
                    FocusTarget = chk,
                };
            }

            default: // ArrayChecklist
            {
                var card = new Border
                {
                    Padding = new Thickness(10),
                    CornerRadius = new CornerRadius(8),
                    BorderThickness = new Thickness(1),
                };
                card.SetResourceReference(Border.BackgroundProperty, "CardBackgroundFillColorDefaultBrush");
                card.SetResourceReference(Border.BorderBrushProperty, "CardStrokeColorDefaultBrush");

                var cardStack = new StackPanel();
                var entries = new List<ArrayRowEntry>();
                var listPanel = new StackPanel();

                var counterText = new System.Windows.Controls.TextBlock
                {
                    FontSize = 12,
                    VerticalAlignment = VerticalAlignment.Center,
                };
                counterText.SetResourceReference(System.Windows.Controls.TextBlock.ForegroundProperty, "TextFillColorSecondaryBrush");

                var toolbar = new Grid { Margin = new Thickness(0, 0, 0, 6) };
                toolbar.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
                toolbar.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });
                toolbar.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });

                Grid.SetColumn(counterText, 0);
                toolbar.Children.Add(counterText);

                var btnAll = new UiButton
                {
                    Content = "Todos",
                    Appearance = ControlAppearance.Transparent,
                    Padding = new Thickness(8, 2, 8, 2),
                    Margin = new Thickness(0, 0, 4, 0),
                };
                Grid.SetColumn(btnAll, 1);
                toolbar.Children.Add(btnAll);

                var btnNone = new UiButton
                {
                    Content = "Nenhum",
                    Appearance = ControlAppearance.Transparent,
                    Padding = new Thickness(8, 2, 8, 2),
                };
                Grid.SetColumn(btnNone, 2);
                toolbar.Children.Add(btnNone);

                cardStack.Children.Add(toolbar);
                cardStack.Children.Add(listPanel);

                void RefreshCounter()
                {
                    int checkedCount = entries.Count(e => e.Check.IsChecked == true);
                    counterText.Text = $"{checkedCount}/{entries.Count} selecionados";
                    toolbar.Visibility = entries.Count > 0 ? Visibility.Visible : Visibility.Collapsed;
                }

                void AddItemRow(string itemLabel, bool isChecked)
                {
                    var rowGrid = new Grid();
                    rowGrid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
                    rowGrid.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });

                    var chk = new CheckBox
                    {
                        Content = itemLabel,
                        IsChecked = isChecked,
                        VerticalAlignment = VerticalAlignment.Center,
                    };
                    chk.Checked += (_, _) => { RefreshCounter(); OnFieldChanged(); };
                    chk.Unchecked += (_, _) => { RefreshCounter(); OnFieldChanged(); };
                    Grid.SetColumn(chk, 0);
                    rowGrid.Children.Add(chk);

                    var rowBorder = new Border
                    {
                        Margin = new Thickness(0, 2, 0, 2),
                        Child = rowGrid,
                    };

                    var entry = new ArrayRowEntry
                    {
                        Check = chk,
                        RowBorder = rowBorder,
                        Label = itemLabel,
                    };

                    var btnRemove = new UiButton
                    {
                        Content = "×",
                        Appearance = ControlAppearance.Transparent,
                        Padding = new Thickness(8, 2, 8, 2),
                        ToolTip = "Remover item",
                    };
                    btnRemove.Click += (_, _) =>
                    {
                        entries.Remove(entry);
                        listPanel.Children.Remove(rowBorder);
                        RefreshCounter();
                        OnFieldChanged();
                    };
                    Grid.SetColumn(btnRemove, 1);
                    rowGrid.Children.Add(btnRemove);

                    entries.Add(entry);
                    listPanel.Children.Add(rowBorder);
                }

                if (defaultVal is ResolvedDefault.List listDef)
                {
                    foreach (var item in listDef.Items)
                    {
                        AddItemRow(item, true);
                    }
                }

                btnAll.Click += (_, _) =>
                {
                    foreach (var entry in entries) entry.Check.IsChecked = true;
                    RefreshCounter();
                };
                btnNone.Click += (_, _) =>
                {
                    foreach (var entry in entries) entry.Check.IsChecked = false;
                    RefreshCounter();
                };

                var addGrid = new Grid { Margin = new Thickness(0, 6, 0, 0) };
                addGrid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
                addGrid.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });

                var addInput = new UiTextBox
                {
                    PlaceholderText = "Adicionar item e pressionar Enter...",
                    Margin = new Thickness(0, 0, 6, 0),
                };
                Grid.SetColumn(addInput, 0);

                void CommitNewItem()
                {
                    var trimmed = addInput.Text.Trim();
                    if (!string.IsNullOrEmpty(trimmed))
                    {
                        AddItemRow(trimmed, true);
                        addInput.Text = string.Empty;
                        RefreshCounter();
                        OnFieldChanged();
                    }
                }

                addInput.KeyDown += (_, e) =>
                {
                    if (e.Key == Key.Enter)
                    {
                        e.Handled = true;
                        CommitNewItem();
                    }
                };

                var btnAdd = new UiButton
                {
                    Content = "+",
                    Padding = new Thickness(14, 6, 14, 6),
                };
                btnAdd.Click += (_, _) => CommitNewItem();
                Grid.SetColumn(btnAdd, 1);

                addGrid.Children.Add(addInput);
                addGrid.Children.Add(btnAdd);
                cardStack.Children.Add(addGrid);

                RefreshCounter();
                card.Child = cardStack;
                wrapper.Children.Add(card);

                return new FieldBinding
                {
                    Name = name,
                    Title = title,
                    Required = required,
                    Kind = kind,
                    Container = wrapper,
                    ArrayEntries = entries,
                    ArrayListPanel = listPanel,
                    ArrayCounterText = counterText,
                    ArrayAddInput = addInput,
                    FocusTarget = addInput,
                };
            }
        }
    }

    private static FieldKind DetermineFieldKind(SchemaProperty prop, UiOptions opts)
    {
        if (prop.EnumValues is { Count: > 0 })
        {
            return string.Equals(opts.Format, "radio", StringComparison.OrdinalIgnoreCase)
                ? FieldKind.Radio
                : FieldKind.Dropdown;
        }

        return prop.FieldType switch
        {
            "array" => FieldKind.ArrayChecklist,
            "boolean" => FieldKind.Boolean,
            "integer" => FieldKind.Integer,
            _ when string.Equals(prop.Format, "date", StringComparison.OrdinalIgnoreCase) => FieldKind.Date,
            _ when opts.Multi == true => FieldKind.TextArea,
            _ => FieldKind.Text,
        };
    }

    private Dictionary<string, string> CollectCurrentRawValues()
    {
        var map = new Dictionary<string, string>(StringComparer.Ordinal);
        foreach (var (name, binding) in _bindings)
        {
            string val = binding.Kind switch
            {
                FieldKind.Text or FieldKind.Integer => binding.TextBox?.Text.Trim() ?? string.Empty,
                FieldKind.Date => SafeNormalizeDate(binding.TextBox?.Text.Trim() ?? string.Empty),
                FieldKind.TextArea => binding.TextBox?.Text.Trim() ?? string.Empty,
                FieldKind.Dropdown => binding.ComboBox?.SelectedItem as string ?? string.Empty,
                FieldKind.Radio => binding.RadioButtons?.FirstOrDefault(r => r.IsChecked == true)?.Content as string ?? string.Empty,
                FieldKind.Boolean => binding.CheckBox?.IsChecked == true ? "true" : "false",
                FieldKind.ArrayChecklist => CollectArrayValue(binding),
                _ => string.Empty,
            };
            map[name] = val;
        }
        return map;
    }

    private static string CollectArrayValue(FieldBinding binding)
    {
        var lines = (binding.ArrayEntries ?? new List<ArrayRowEntry>())
            .Where(e => e.Check.IsChecked == true && !string.IsNullOrWhiteSpace(e.Label))
            .Select(e => e.Label.Trim())
            .ToList();

        var pending = binding.ArrayAddInput?.Text.Trim();
        if (!string.IsNullOrEmpty(pending))
        {
            lines.Add(pending);
        }

        return string.Join("\n", lines);
    }

    private static string SafeNormalizeDate(string raw)
    {
        try
        {
            return FormValidator.NormalizeDateToIso(raw);
        }
        catch
        {
            return raw;
        }
    }

    private void OnFieldChanged()
    {
        ErrorBanner.Visibility = Visibility.Collapsed;
        UpdateVisibility();
    }

    private Dictionary<string, bool> ComputeVisibility()
    {
        var current = CollectCurrentRawValues();
        var vis = new Dictionary<string, bool>(StringComparer.Ordinal);
        foreach (var name in _loaded.FieldOrder)
        {
            vis[name] = RuleEngine.IsFieldVisible(name, _loaded.FieldRules, current);
        }
        return vis;
    }

    private void UpdateVisibility()
    {
        var visibility = ComputeVisibility();
        foreach (var (name, binding) in _bindings)
        {
            bool visible = !visibility.TryGetValue(name, out var v) || v;
            binding.Container.Visibility = visible ? Visibility.Visible : Visibility.Collapsed;
        }

        foreach (var (fe, el) in _elementContainers)
        {
            if (el.ElementType == "HorizontalLayout")
            {
                bool anyVisible = el.Elements.Any(child => IsElementTreeVisible(child, visibility));
                fe.Visibility = anyVisible ? Visibility.Visible : Visibility.Collapsed;
            }
        }
    }

    private static bool IsElementTreeVisible(UiElement el, IReadOnlyDictionary<string, bool> visibility)
    {
        if (!string.IsNullOrEmpty(el.Scope))
        {
            var fieldName = el.Scope.StartsWith("#/properties/", StringComparison.Ordinal)
                ? el.Scope["#/properties/".Length..]
                : el.Scope;
            return !visibility.TryGetValue(fieldName, out var v) || v;
        }
        return el.Elements.Any(child => IsElementTreeVisible(child, visibility));
    }

    private void FocusFirstVisibleControl()
    {
        var visibility = ComputeVisibility();
        foreach (var name in _loaded.FieldOrder)
        {
            if ((!visibility.TryGetValue(name, out var vis) || vis) &&
                _bindings.TryGetValue(name, out var binding) &&
                binding.FocusTarget is not null)
            {
                binding.FocusTarget.Focus();
                if (binding.FocusTarget is UiTextBox tb)
                {
                    tb.CaretIndex = tb.Text.Length;
                }
                break;
            }
        }
    }

    private void SubmitForm()
    {
        var visibility = ComputeVisibility();
        var values = CollectCurrentRawValues();

        foreach (var (name, visible) in visibility)
        {
            if (!visible)
            {
                values[name] = string.Empty;
            }
        }

        var error = FormValidator.ValidateSubmission(_loaded.FormName, _loaded.Config, values, visibility);
        if (error is not null)
        {
            TxtErrorBanner.Text = $"⚠ {error}";
            ErrorBanner.Visibility = Visibility.Visible;
            return;
        }

        RenderedOutput = OutputFormatter.FormatOutput(_loaded.Config, _loaded.FieldOrder, values, _jsonOutput);
        DialogResult = true;
        Close();
    }

    private void BtnSubmit_Click(object sender, RoutedEventArgs e) => SubmitForm();

    private void BtnCancel_Click(object sender, RoutedEventArgs e)
    {
        DialogResult = false;
        Close();
    }

    private void Window_PreviewKeyDown(object sender, KeyEventArgs e)
    {
        if (e.Key == Key.Escape)
        {
            e.Handled = true;
            DialogResult = false;
            Close();
        }
    }
}
