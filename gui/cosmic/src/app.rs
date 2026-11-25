use crate::models::form_schema::{ResolvedDefault, SchemaProperty, UiElement, UiOptions};
use crate::services::form_loader::LoadedForm;
use crate::services::output_formatter::format_output;
use crate::services::rule_engine::is_field_visible;
use crate::services::validator::{iso_to_br_date, normalize_date_to_iso, validate_submission};
use chrono::{Duration, Local};
use cosmic::iced::{Alignment, Length};
use cosmic::prelude::*;
use cosmic::widget::{self, text_editor};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};

#[derive(Debug, Clone)]
pub struct AppFlags {
    pub loaded: LoadedForm,
    pub json_output: bool,
    pub result_slot: Arc<Mutex<Option<String>>>,
}

#[derive(Debug, Clone)]
pub enum FieldKind {
    Text,
    Integer,
    Date,
    TextArea,
    Dropdown(Vec<String>),
    Radio(Vec<String>),
    Boolean,
    ArrayChecklist,
}

#[derive(Debug)]
pub struct ArrayItem {
    pub label: String,
    pub checked: bool,
}

#[derive(Debug)]
pub struct FieldState {
    pub name: String,
    pub title: String,
    pub required: bool,
    pub kind: FieldKind,
    pub options: UiOptions,
    pub text_value: String,
    pub editor_content: text_editor::Content,
    pub selected_idx: Option<usize>,
    pub bool_value: bool,
    pub array_items: Vec<ArrayItem>,
    pub new_array_item: String,
    pub input_id: widget::Id,
}

pub struct AppModel {
    core: cosmic::Core,
    loaded: LoadedForm,
    json_output: bool,
    result_slot: Arc<Mutex<Option<String>>>,
    fields: HashMap<String, FieldState>,
    error_message: Option<String>,
}

#[derive(Debug, Clone)]
pub enum Message {
    TextChanged(String, String),
    EditorAction(String, text_editor::Action),
    DropdownSelected(String, usize),
    RadioSelected(String, usize),
    BooleanToggled(String, bool),
    ArrayItemToggled(String, usize, bool),
    ArraySelectAll(String, bool),
    ArrayItemRemoved(String, usize),
    ArrayNewInputChanged(String, String),
    ArrayNewItemAdded(String),
    SetDateToday(String),
    SetDateTomorrow(String),
    Submit,
    Cancel,
}

impl cosmic::Application for AppModel {
    type Executor = cosmic::executor::Default;
    type Flags = AppFlags;
    type Message = Message;

    const APP_ID: &'static str = "br.dev.rezendepauloh.StiForms";

    fn core(&self) -> &cosmic::Core {
        &self.core
    }

    fn core_mut(&mut self) -> &mut cosmic::Core {
        &mut self.core
    }

    fn init(
        core: cosmic::Core,
        flags: Self::Flags,
    ) -> (Self, Task<cosmic::Action<Self::Message>>) {
        let mut fields = HashMap::new();
        let mut first_focus_id: Option<widget::Id> = None;

        for name in &flags.loaded.field_order {
            if let Some(prop) = flags.loaded.config.schema.properties.get(name) {
                let opts = flags
                    .loaded
                    .field_options
                    .get(name)
                    .cloned()
                    .unwrap_or_default();
                let default_val = flags.loaded.resolved_defaults.get(name);
                let required = flags.loaded.config.schema.required.contains(name);
                let state = build_field_state(name, prop, &opts, default_val, required);
                fields.insert(name.clone(), state);
            }
        }

        let mut app = Self {
            core,
            loaded: flags.loaded,
            json_output: flags.json_output,
            result_slot: flags.result_slot,
            fields,
            error_message: None,
        };

        let visibility = app.compute_visibility();
        for name in &app.loaded.field_order {
            if visibility.get(name).copied().unwrap_or(true)
                && let Some(st) = app.fields.get(name)
                && matches!(st.kind, FieldKind::Text | FieldKind::Integer | FieldKind::Date)
            {
                first_focus_id = Some(st.input_id.clone());
                break;
            }
        }

        let mut tasks = Vec::new();
        if let Some(id) = app.core.main_window_id() {
            let title = app.loaded.display_title.clone();
            tasks.push(app.set_window_title(title, id));
        }
        if let Some(focus_id) = first_focus_id {
            tasks.push(widget::text_input::focus(focus_id));
        }

        (app, Task::batch(tasks))
    }

    fn header_start(&self) -> Vec<Element<'_, Self::Message>> {
        vec![
            widget::text::title4(&self.loaded.display_title)
                .apply(widget::container)
                .padding([0, 8])
                .into(),
        ]
    }

    fn on_escape(&mut self) -> Task<cosmic::Action<Self::Message>> {
        self.cancel_and_exit()
    }

    fn update(&mut self, message: Self::Message) -> Task<cosmic::Action<Self::Message>> {
        self.error_message = None;

        match message {
            Message::TextChanged(name, val) => {
                if let Some(st) = self.fields.get_mut(&name) {
                    if matches!(st.kind, FieldKind::Integer) {
                        let filtered: String = val
                            .chars()
                            .enumerate()
                            .filter(|(idx, c)| c.is_ascii_digit() || (*idx == 0 && *c == '-'))
                            .map(|(_, c)| c)
                            .collect();
                        st.text_value = filtered;
                    } else {
                        st.text_value = val;
                    }
                }
            }
            Message::EditorAction(name, action) => {
                if let Some(st) = self.fields.get_mut(&name) {
                    st.editor_content.perform(action);
                }
            }
            Message::DropdownSelected(name, idx) => {
                if let Some(st) = self.fields.get_mut(&name) {
                    st.selected_idx = Some(idx);
                }
            }
            Message::RadioSelected(name, idx) => {
                if let Some(st) = self.fields.get_mut(&name) {
                    st.selected_idx = Some(idx);
                }
            }
            Message::BooleanToggled(name, val) => {
                if let Some(st) = self.fields.get_mut(&name) {
                    st.bool_value = val;
                }
            }
            Message::ArrayItemToggled(name, idx, val) => {
                if let Some(st) = self.fields.get_mut(&name)
                    && let Some(item) = st.array_items.get_mut(idx)
                {
                    item.checked = val;
                }
            }
            Message::ArraySelectAll(name, checked) => {
                if let Some(st) = self.fields.get_mut(&name) {
                    for item in &mut st.array_items {
                        item.checked = checked;
                    }
                }
            }
            Message::ArrayItemRemoved(name, idx) => {
                if let Some(st) = self.fields.get_mut(&name)
                    && idx < st.array_items.len()
                {
                    st.array_items.remove(idx);
                }
            }
            Message::ArrayNewInputChanged(name, val) => {
                if let Some(st) = self.fields.get_mut(&name) {
                    st.new_array_item = val;
                }
            }
            Message::ArrayNewItemAdded(name) => {
                if let Some(st) = self.fields.get_mut(&name) {
                    let trimmed = st.new_array_item.trim().to_string();
                    if !trimmed.is_empty() {
                        st.array_items.push(ArrayItem {
                            label: trimmed,
                            checked: true,
                        });
                        st.new_array_item.clear();
                    }
                }
            }
            Message::SetDateToday(name) => {
                if let Some(st) = self.fields.get_mut(&name) {
                    st.text_value = Local::now().format("%d/%m/%Y").to_string();
                }
            }
            Message::SetDateTomorrow(name) => {
                if let Some(st) = self.fields.get_mut(&name) {
                    let tomorrow = Local::now() + Duration::days(1);
                    st.text_value = tomorrow.format("%d/%m/%Y").to_string();
                }
            }
            Message::Submit => {
                return self.validate_and_submit();
            }
            Message::Cancel => {
                return self.cancel_and_exit();
            }
        }

        Task::none()
    }

    fn view(&self) -> Element<'_, Self::Message> {
        let space_xs = cosmic::theme::spacing().space_xs;
        let space_s = cosmic::theme::spacing().space_s;
        let space_m = cosmic::theme::spacing().space_m;

        let visibility = self.compute_visibility();

        let mut form_col = widget::column::with_capacity(self.loaded.layout_elements.len() + 1)
            .spacing(space_m)
            .width(Length::Fill);

        for el in &self.loaded.layout_elements {
            if let Some(rendered) = self.render_ui_element(el, &visibility) {
                form_col = form_col.push(rendered);
            }
        }

        let scroll = widget::scrollable(
            widget::container(form_col)
                .padding([space_s, space_m])
                .width(Length::Fill),
        )
        .height(Length::Fill);

        let mut root = widget::column::with_capacity(4)
            .spacing(space_s)
            .width(Length::Fill)
            .height(Length::Fill);

        if let Some(err) = &self.error_message {
            let banner = widget::container(widget::text::body(format!("⚠ {err}")))
                .padding([8, 12])
                .width(Length::Fill)
                .class(cosmic::theme::Container::Primary);
            root = root.push(banner);
        }

        root = root.push(scroll);

        let footer = widget::row::with_capacity(4)
            .spacing(space_s)
            .align_y(Alignment::Center)
            .push(
                widget::text::caption("Esc cancelar · Enter enviar campos simples")
                    .width(Length::Fill),
            )
            .push(widget::button::standard("Cancelar").on_press(Message::Cancel))
            .push(widget::button::suggested("Preencher").on_press(Message::Submit));

        root = root.push(
            widget::container(footer)
                .padding([space_xs, space_m])
                .width(Length::Fill),
        );

        widget::container(root)
            .padding([space_xs, space_s])
            .width(Length::Fill)
            .height(Length::Fill)
            .into()
    }
}

impl AppModel {
    fn current_raw_values(&self) -> HashMap<String, String> {
        let mut map = HashMap::new();
        for (name, st) in &self.fields {
            let value = match &st.kind {
                FieldKind::Text | FieldKind::Integer => st.text_value.trim().to_string(),
                FieldKind::Date => {
                    let raw = st.text_value.trim();
                    normalize_date_to_iso(raw).unwrap_or_else(|_| raw.to_string())
                }
                FieldKind::TextArea => st.editor_content.text().trim().to_string(),
                FieldKind::Dropdown(opts) | FieldKind::Radio(opts) => st
                    .selected_idx
                    .and_then(|idx| opts.get(idx))
                    .cloned()
                    .unwrap_or_default(),
                FieldKind::Boolean => {
                    if st.bool_value {
                        "true".to_string()
                    } else {
                        "false".to_string()
                    }
                }
                FieldKind::ArrayChecklist => {
                    let mut lines: Vec<String> = st
                        .array_items
                        .iter()
                        .filter(|it| it.checked)
                        .map(|it| it.label.trim().to_string())
                        .filter(|s| !s.is_empty())
                        .collect();
                    let pending = st.new_array_item.trim();
                    if !pending.is_empty() {
                        lines.push(pending.to_string());
                    }
                    lines.join("\n")
                }
            };
            map.insert(name.clone(), value);
        }
        map
    }

    fn compute_visibility(&self) -> HashMap<String, bool> {
        let current = self.current_raw_values();
        let mut vis = HashMap::new();
        for name in &self.loaded.field_order {
            let visible = is_field_visible(name, &self.loaded.field_rules, &current);
            vis.insert(name.clone(), visible);
        }
        vis
    }

    fn validate_and_submit(&mut self) -> Task<cosmic::Action<Message>> {
        let visibility = self.compute_visibility();
        let mut values = self.current_raw_values();

        // Campos ocultos por regra condicional são limpos na saída
        for (name, visible) in &visibility {
            if !*visible {
                values.insert(name.clone(), String::new());
            }
        }

        if let Err(err) = validate_submission(
            &self.loaded.form_name,
            &self.loaded.config,
            &values,
            &visibility,
            &self.loaded.field_options,
        ) {
            self.error_message = Some(err);
            return Task::none();
        }

        match format_output(
            &self.loaded.config,
            &self.loaded.field_order,
            &values,
            self.json_output,
        ) {
            Ok(rendered) => {
                if let Ok(mut guard) = self.result_slot.lock() {
                    *guard = Some(rendered);
                }
                cosmic::iced::exit::<cosmic::Action<Message>>()
            }
            Err(err) => {
                self.error_message = Some(err);
                Task::none()
            }
        }
    }

    fn cancel_and_exit(&mut self) -> Task<cosmic::Action<Message>> {
        if let Ok(mut guard) = self.result_slot.lock() {
            *guard = None;
        }
        cosmic::iced::exit::<cosmic::Action<Message>>()
    }

    fn render_ui_element<'a>(
        &'a self,
        el: &'a UiElement,
        visibility: &HashMap<String, bool>,
    ) -> Option<Element<'a, Message>> {
        let space_s = cosmic::theme::spacing().space_s;

        match el.element_type.as_str() {
            "HorizontalLayout" => {
                let children: Vec<Element<'a, Message>> = el
                    .elements
                    .iter()
                    .filter_map(|child| self.render_ui_element(child, visibility))
                    .collect();
                if children.is_empty() {
                    return None;
                }
                let mut row = widget::row::with_capacity(children.len())
                    .spacing(space_s)
                    .width(Length::Fill);
                for child in children {
                    row = row.push(widget::container(child).width(Length::FillPortion(1)));
                }
                Some(row.into())
            }
            "VerticalLayout" => {
                let children: Vec<Element<'a, Message>> = el
                    .elements
                    .iter()
                    .filter_map(|child| self.render_ui_element(child, visibility))
                    .collect();
                if children.is_empty() {
                    return None;
                }
                let mut col = widget::column::with_capacity(children.len())
                    .spacing(space_s)
                    .width(Length::Fill);
                for child in children {
                    col = col.push(child);
                }
                Some(col.into())
            }
            _ => {
                let scope = el.scope.as_deref()?;
                let field_name = scope.trim_start_matches("#/properties/");
                if !visibility.get(field_name).copied().unwrap_or(true) {
                    return None;
                }
                let state = self.fields.get(field_name)?;
                Some(self.render_field(state))
            }
        }
    }

    fn render_field<'a>(&'a self, st: &'a FieldState) -> Element<'a, Message> {
        let space_xs = cosmic::theme::spacing().space_xs;
        let space_s = cosmic::theme::spacing().space_s;
        let fname = st.name.clone();

        let label_str = if st.required {
            format!("{} *", st.title.trim_end_matches(':'))
        } else {
            st.title.clone()
        };

        let mut wrapper = widget::column::with_capacity(3)
            .spacing(space_xs)
            .width(Length::Fill)
            .push(widget::text::heading(label_str));

        let placeholder = st
            .options
            .placeholder
            .as_deref()
            .unwrap_or("Digite aqui...");

        match &st.kind {
            FieldKind::Text | FieldKind::Integer => {
                let fname_input = fname.clone();
                let input = widget::text_input(placeholder, &st.text_value)
                    .id(st.input_id.clone())
                    .on_input(move |v| Message::TextChanged(fname_input.clone(), v))
                    .on_submit(|_| Message::Submit)
                    .width(Length::Fill);
                wrapper = wrapper.push(input);
            }
            FieldKind::Date => {
                let fname_input = fname.clone();
                let fname_today = fname.clone();
                let fname_tomorrow = fname.clone();

                let date_row = widget::row::with_capacity(3)
                    .spacing(space_xs)
                    .align_y(Alignment::Center)
                    .push(
                        widget::text_input("DD/MM/AAAA", &st.text_value)
                            .id(st.input_id.clone())
                            .on_input(move |v| Message::TextChanged(fname_input.clone(), v))
                            .on_submit(|_| Message::Submit)
                            .width(Length::Fill),
                    )
                    .push(
                        widget::button::standard("Hoje")
                            .on_press(Message::SetDateToday(fname_today)),
                    )
                    .push(
                        widget::button::standard("Amanhã")
                            .on_press(Message::SetDateTomorrow(fname_tomorrow)),
                    );
                wrapper = wrapper.push(date_row);
            }
            FieldKind::TextArea => {
                let rows = st.options.rows.unwrap_or(4).max(3) as f32;
                let height = (rows * 24.0 + 18.0).min(240.0);
                let editor = text_editor::text_editor(&st.editor_content)
                    .placeholder(placeholder)
                    .height(Length::Fixed(height))
                    .on_action(move |action| Message::EditorAction(fname.clone(), action));
                wrapper = wrapper.push(widget::container(editor).width(Length::Fill));
            }
            FieldKind::Dropdown(options) => {
                let dd = widget::dropdown(options, st.selected_idx, move |idx| {
                    Message::DropdownSelected(fname.clone(), idx)
                })
                .width(Length::Fill);
                wrapper = wrapper.push(dd);
            }
            FieldKind::Radio(options) => {
                if options.len() <= 4 {
                    let mut r_row = widget::row::with_capacity(options.len())
                        .spacing(space_s)
                        .align_y(Alignment::Center);
                    for (idx, opt) in options.iter().enumerate() {
                        let fname_r = fname.clone();
                        r_row = r_row.push(widget::radio(
                            widget::text::body(opt),
                            idx,
                            st.selected_idx,
                            move |chosen| Message::RadioSelected(fname_r.clone(), chosen),
                        ));
                    }
                    wrapper = wrapper.push(r_row);
                } else {
                    let mut r_col = widget::column::with_capacity(options.len()).spacing(space_xs);
                    for (idx, opt) in options.iter().enumerate() {
                        let fname_r = fname.clone();
                        r_col = r_col.push(widget::radio(
                            widget::text::body(opt),
                            idx,
                            st.selected_idx,
                            move |chosen| Message::RadioSelected(fname_r.clone(), chosen),
                        ));
                    }
                    wrapper = wrapper.push(r_col);
                }
            }
            FieldKind::Boolean => {
                let fname_b = fname.clone();
                let chk_row = widget::row::with_capacity(2)
                    .spacing(space_xs)
                    .align_y(Alignment::Center)
                    .push(
                        widget::checkbox(st.bool_value)
                            .on_toggle(move |v| Message::BooleanToggled(fname_b.clone(), v)),
                    )
                    .push(widget::text::body("Ativado"));
                wrapper = wrapper.push(chk_row);
            }
            FieldKind::ArrayChecklist => {
                let fname_all = fname.clone();
                let fname_none = fname.clone();
                let fname_new = fname.clone();
                let fname_add = fname.clone();

                let mut list_col = widget::column::with_capacity(st.array_items.len() + 2)
                    .spacing(space_xs)
                    .width(Length::Fill);

                if !st.array_items.is_empty() {
                    let toolbar = widget::row::with_capacity(3)
                        .spacing(space_xs)
                        .align_y(Alignment::Center)
                        .push(
                            widget::text::caption(format!(
                                "{}/{} selecionados",
                                st.array_items.iter().filter(|i| i.checked).count(),
                                st.array_items.len()
                            ))
                            .width(Length::Fill),
                        )
                        .push(
                            widget::button::text("Todos")
                                .on_press(Message::ArraySelectAll(fname_all, true)),
                        )
                        .push(
                            widget::button::text("Nenhum")
                                .on_press(Message::ArraySelectAll(fname_none, false)),
                        );
                    list_col = list_col.push(toolbar);
                }

                for (idx, item) in st.array_items.iter().enumerate() {
                    let fname_t = fname.clone();
                    let fname_rm = fname.clone();
                    let item_row = widget::row::with_capacity(3)
                        .spacing(space_xs)
                        .align_y(Alignment::Center)
                        .push(
                            widget::checkbox(item.checked)
                                .on_toggle(move |v| Message::ArrayItemToggled(fname_t.clone(), idx, v)),
                        )
                        .push(widget::text::body(&item.label).width(Length::Fill))
                        .push(
                            widget::button::text("×")
                                .on_press(Message::ArrayItemRemoved(fname_rm, idx)),
                        );
                    list_col = list_col.push(item_row);
                }

                let add_row = widget::row::with_capacity(2)
                    .spacing(space_xs)
                    .align_y(Alignment::Center)
                    .push(
                        widget::text_input("Adicionar item e pressionar Enter...", &st.new_array_item)
                            .on_input(move |v| Message::ArrayNewInputChanged(fname_new.clone(), v))
                            .on_submit(move |_| Message::ArrayNewItemAdded(fname_add.clone()))
                            .width(Length::Fill),
                    )
                    .push(
                        widget::button::standard("+")
                            .on_press(Message::ArrayNewItemAdded(fname)),
                    );

                list_col = list_col.push(add_row);
                wrapper = wrapper.push(
                    widget::container(list_col)
                        .padding(space_s)
                        .width(Length::Fill)
                        .class(cosmic::theme::Container::Card),
                );
            }
        }

        wrapper.into()
    }
}

fn build_field_state(
    name: &str,
    prop: &SchemaProperty,
    opts: &UiOptions,
    default_val: Option<&ResolvedDefault>,
    required: bool,
) -> FieldState {
    let title = prop
        .title
        .clone()
        .unwrap_or_else(|| name.to_string());

    let kind = if let Some(enums) = &prop.enum_values {
        if opts.format.as_deref() == Some("radio") {
            FieldKind::Radio(enums.clone())
        } else {
            FieldKind::Dropdown(enums.clone())
        }
    } else if prop.field_type == "array" {
        FieldKind::ArrayChecklist
    } else if prop.field_type == "boolean" {
        FieldKind::Boolean
    } else if prop.field_type == "integer" {
        FieldKind::Integer
    } else if prop.format.as_deref() == Some("date") {
        FieldKind::Date
    } else if opts.multi == Some(true) {
        FieldKind::TextArea
    } else {
        FieldKind::Text
    };

    let mut text_value = String::new();
    let mut editor_text = String::new();
    let mut selected_idx = None;
    let mut bool_value = false;
    let mut array_items = Vec::new();

    match &kind {
        FieldKind::Dropdown(options) | FieldKind::Radio(options) => {
            if let Some(ResolvedDefault::Text(def)) = default_val {
                selected_idx = options.iter().position(|o| o == def);
            }
            if selected_idx.is_none() && !options.is_empty() {
                selected_idx = Some(0);
            }
        }
        FieldKind::TextArea => {
            if let Some(ResolvedDefault::Text(def)) = default_val {
                editor_text = def.clone();
            }
        }
        FieldKind::Date => {
            if let Some(ResolvedDefault::Text(def)) = default_val
                && !def.trim().is_empty()
            {
                text_value = iso_to_br_date(def);
            }
        }
        FieldKind::Boolean => {
            if let Some(ResolvedDefault::Bool(b)) = default_val {
                bool_value = *b;
            }
        }
        FieldKind::ArrayChecklist => {
            if let Some(ResolvedDefault::List(items)) = default_val {
                array_items = items
                    .iter()
                    .map(|item| ArrayItem {
                        label: item.clone(),
                        checked: true,
                    })
                    .collect();
            }
        }
        FieldKind::Text | FieldKind::Integer => {
            if let Some(ResolvedDefault::Text(def)) = default_val {
                text_value = def.clone();
            }
        }
    }

    FieldState {
        name: name.to_string(),
        title,
        required,
        kind,
        options: opts.clone(),
        text_value,
        editor_content: text_editor::Content::with_text(&editor_text),
        selected_idx,
        bool_value,
        array_items,
        new_array_item: String::new(),
        input_id: widget::Id::new(format!("field_{name}")),
    }
}
