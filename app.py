from __future__ import annotations

from datetime import date

import altair as alt
import pandas as pd
import streamlit as st

from ledger.db import init_db
from ledger.exporters import export_excel
from ledger.services import (
    VALID_COLUMN_TYPES,
    VALID_REGIONS,
    add_project_column,
    add_template_column,
    build_category_breakdown,
    build_record_editor_dataframe,
    build_trend_dataframe,
    create_project,
    create_template,
    create_template_from_project,
    deactivate_project_column,
    deactivate_template_column,
    export_project_bundle,
    export_month_region_metadata_excel,
    export_system_bundle,
    get_project,
    get_record_with_values,
    get_template,
    import_system_bundle,
    import_month_region_metadata_excel,
    import_project_bundle,
    list_monthly_records,
    list_project_columns,
    list_projects_by_region,
    list_record_months,
    list_template_columns,
    list_templates,
    save_monthly_record,
    save_record_editor_dataframe,
    update_project_name,
)


st.set_page_config(page_title="Parking Ledger", layout="wide")
init_db()


I18N = {
    "简体中文": {
        "app_title": "停车管理公司月度经营台账 MVP",
        "app_caption": "支持北京 / 外地分组、多 Project、模板、折线图、历史台账编辑、月度录入与导入导出。",
        "menu": "功能选单",
        "project_ledger": "项目台账",
        "template_center": "Template 设置",
        "template_none": "不使用 Template",
        "new_project": "在 {region} 分组新建 Project",
        "project_name": "Project 名称",
        "rename_project": "编辑项目名称",
        "rename_project_submit": "保存名称",
        "description": "说明",
        "create": "建立",
        "template": "Template",
        "group_empty": "暂无 Project",
        "first_project_hint": "请先在北京或外地分组中建立第一个 Project。",
        "language": "语言",
        "trend": "月度经营趋势",
        "trend_empty": "当前 Project 还没有可用于绘图的月度数据。",
        "trend_metric_select": "趋势指标",
        "trend_metric_labels": "趋势图指标",
        "project_tabs": "项目子页面",
        "page_data_display": "数据展示",
        "page_data_input": "数据输入",
        "page_settings": "设置",
        "settings": "项目设置",
        "analytics": "项目经营分析",
        "analysis_month": "分析月份",
        "income_share": "收入构成占比",
        "expense_share": "支出构成占比",
        "share_empty": "该月份暂无对应数据。",
        "existing_records": "1. 已有台账资料",
        "existing_caption": "表格中的字段可直接编辑，保存后会自动重新计算收入、支出和利润。",
        "save_table": "保存表格修改",
        "record_entry": "2. 月度资料输入",
        "month": "月份",
        "month_note": "月度备注",
        "save_record": "保存月度台账",
        "column_management": "3. 栏位管理",
        "column_name": "栏位名称",
        "column_type": "栏位类型",
        "add_column": "新增栏位",
        "disable_column": "停用选中栏位",
        "template_management": "Template 设定",
        "create_template": "创建 Template",
        "template_name": "Template 名称",
        "create_from_project": "根据当前 Project 生成 Template",
        "template_columns": "Template 栏位",
        "disable_template_column": "停用 Template 栏位",
        "export_settings": "4. 数据导入导出",
        "export_project_excel": "导出当前 Project Excel",
        "export_all_excel": "导出全部 Project Excel",
        "export_project_bundle": "导出当前 Project 设置包",
        "export_system": "导出整个设定体系",
        "import_system": "导入整个设定体系",
        "import_system_file": "上传设定体系包",
        "import_system_submit": "导入设定体系",
        "system_import_done": "设定体系导入成功。",
        "system_import_desc": "导入后会覆盖当前本机的所有模板、项目和台账数据。",
        "import_project": "导入单个 Project",
        "import_file": "上传 Project 包",
        "import_name": "导入后 Project 名称",
        "import_region": "导入后分组",
        "import_submit": "导入 Project",
        "no_records": "目前尚无月度资料。",
        "project_missing_columns": "请先为此 Project 建立栏位后，再录入月度资料。",
        "project_created": "Project 已建立。",
        "project_renamed": "Project 名称已更新。",
        "template_created": "Template 已建立。",
        "template_from_project_done": "已根据当前 Project 创建 Template。",
        "column_added": "栏位已新增。",
        "template_column_added": "Template 栏位已新增。",
        "column_disabled": "栏位已停用，历史资料仍会保留。",
        "template_column_disabled_done": "Template 栏位已停用。",
        "record_saved": "月度台账已保存。",
        "records_saved": "历史台账已更新。",
        "import_done": "Project 导入成功。",
        "name_required": "名称不能为空。",
        "template_desc": "建立好 Template 后，新建 Project 可直接套用栏位。",
        "open_template_settings": "点击左侧功能选单中的 Template 设置后，可选择模板进行编辑或新建模板。",
        "system_export_desc": "整体设定导出包含 SQLite 数据库、建表 SQL、测试数据 SQL 与 JSON 快照。",
        "project_export_desc": "单个 Project 设置包包含项目资料、栏位定义和历史台账。",
        "batch_metadata": "5. 批量月份 Metadata 导入导出",
        "batch_export_desc": "按月份与分组导出全部项目的批量录入模板，填写后可一次性回写。",
        "batch_export_month": "批量模板月份",
        "batch_export_region": "批量模板分组",
        "batch_export_button": "导出批量 Metadata Excel",
        "batch_import_file": "上传批量 Metadata Excel",
        "batch_import_button": "导入批量 Metadata Excel",
        "batch_import_done": "批量导入完成：成功 {imported} 条，跳过 {skipped} 条。",
        "no_template_columns": "此 Template 暂无栏位。",
        "template_select": "选择 Template",
        "current_project": "当前 Project",
        "current_template": "当前 Template",
        "notes_placeholder": "文字栏可直接输入说明，金额栏请输入数字",
    },
    "繁體中文": {
        "app_title": "停車管理公司月度經營台帳 MVP",
        "app_caption": "支援北京 / 外地分組、多 Project、模板、折線圖、歷史台帳編輯、月度錄入與導入導出。",
        "menu": "功能選單",
        "project_ledger": "Project 台帳",
        "template_center": "Template 設定",
        "template_none": "不使用 Template",
        "new_project": "在 {region} 分組新建 Project",
        "project_name": "Project 名稱",
        "rename_project": "編輯 Project 名稱",
        "rename_project_submit": "保存名稱",
        "description": "說明",
        "create": "建立",
        "template": "Template",
        "group_empty": "暫無 Project",
        "first_project_hint": "請先在北京或外地分組中建立第一個 Project。",
        "language": "語言",
        "trend": "月度經營趨勢",
        "trend_empty": "目前 Project 還沒有可用於繪圖的月度資料。",
        "trend_metric_select": "趨勢指標",
        "trend_metric_labels": "趨勢圖指標",
        "project_tabs": "Project 子頁面",
        "page_data_display": "數據展示",
        "page_data_input": "數據輸入",
        "page_settings": "設定",
        "settings": "Project 設定",
        "analytics": "Project 經營分析",
        "analysis_month": "分析月份",
        "income_share": "收入構成占比",
        "expense_share": "支出構成占比",
        "share_empty": "該月份暫無對應資料。",
        "existing_records": "1. 已有台帳資料",
        "existing_caption": "表格中的欄位可直接編輯，保存後會自動重新計算收入、支出和利潤。",
        "save_table": "保存表格修改",
        "record_entry": "2. 月度資料輸入",
        "month": "月份",
        "month_note": "月度備註",
        "save_record": "保存月度台帳",
        "column_management": "3. 欄位管理",
        "column_name": "欄位名稱",
        "column_type": "欄位類型",
        "add_column": "新增欄位",
        "disable_column": "停用選中欄位",
        "template_management": "Template 設定",
        "create_template": "建立 Template",
        "template_name": "Template 名稱",
        "create_from_project": "根據目前 Project 生成 Template",
        "template_columns": "Template 欄位",
        "disable_template_column": "停用 Template 欄位",
        "export_settings": "4. 數據導入導出",
        "export_project_excel": "導出目前 Project Excel",
        "export_all_excel": "導出全部 Project Excel",
        "export_project_bundle": "導出目前 Project 設定包",
        "export_system": "導出整個設定體系",
        "import_system": "導入整個設定體系",
        "import_system_file": "上傳設定體系包",
        "import_system_submit": "導入設定體系",
        "system_import_done": "設定體系導入成功。",
        "system_import_desc": "導入後會覆蓋目前本機的所有模板、Project 與台帳資料。",
        "import_project": "導入單個 Project",
        "import_file": "上傳 Project 包",
        "import_name": "導入後 Project 名稱",
        "import_region": "導入後分組",
        "import_submit": "導入 Project",
        "no_records": "目前尚無月度資料。",
        "project_missing_columns": "請先為此 Project 建立欄位後，再錄入月度資料。",
        "project_created": "Project 已建立。",
        "project_renamed": "Project 名稱已更新。",
        "template_created": "Template 已建立。",
        "template_from_project_done": "已根據目前 Project 建立 Template。",
        "column_added": "欄位已新增。",
        "template_column_added": "Template 欄位已新增。",
        "column_disabled": "欄位已停用，歷史資料仍會保留。",
        "template_column_disabled_done": "Template 欄位已停用。",
        "record_saved": "月度台帳已保存。",
        "records_saved": "歷史台帳已更新。",
        "import_done": "Project 導入成功。",
        "name_required": "名稱不能為空。",
        "template_desc": "建立好 Template 後，新建 Project 可直接套用欄位。",
        "open_template_settings": "點擊左側功能選單中的 Template 設定後，可選擇模板進行編輯或建立模板。",
        "system_export_desc": "整體設定導出包含 SQLite 資料庫、建表 SQL、測試資料 SQL 與 JSON 快照。",
        "project_export_desc": "單個 Project 設定包包含專案資料、欄位定義與歷史台帳。",
        "batch_metadata": "5. 批量月份 Metadata 導入導出",
        "batch_export_desc": "按月份與分組導出全部 Project 的批量錄入模板，填寫後可一次性回寫。",
        "batch_export_month": "批量模板月份",
        "batch_export_region": "批量模板分組",
        "batch_export_button": "導出批量 Metadata Excel",
        "batch_import_file": "上傳批量 Metadata Excel",
        "batch_import_button": "導入批量 Metadata Excel",
        "batch_import_done": "批量導入完成：成功 {imported} 條，跳過 {skipped} 條。",
        "no_template_columns": "此 Template 尚無欄位。",
        "template_select": "選擇 Template",
        "current_project": "目前 Project",
        "current_template": "目前 Template",
        "notes_placeholder": "文字欄可直接輸入說明，金額欄請輸入數字",
    },
    "English": {
        "app_title": "Parking Management Monthly Ledger MVP",
        "app_caption": "Supports Beijing / Other regions grouping, multiple projects, templates, trend chart, editing history, monthly entry, and import/export.",
        "menu": "Menu",
        "project_ledger": "Project Ledger",
        "template_center": "Template Settings",
        "template_none": "No Template",
        "new_project": "Create Project in {region}",
        "project_name": "Project Name",
        "rename_project": "Edit Project Name",
        "rename_project_submit": "Save Name",
        "description": "Description",
        "create": "Create",
        "template": "Template",
        "group_empty": "No project yet",
        "first_project_hint": "Create the first project under Beijing or Other regions.",
        "language": "Language",
        "trend": "Monthly Trend",
        "trend_empty": "No monthly data is available for charting yet.",
        "trend_metric_select": "Trend Metrics",
        "trend_metric_labels": "Trend Legend",
        "project_tabs": "Project Subpages",
        "page_data_display": "Data Display",
        "page_data_input": "Data Input",
        "page_settings": "Settings",
        "settings": "Project Settings",
        "analytics": "Project Analytics",
        "analysis_month": "Analysis Month",
        "income_share": "Income Breakdown",
        "expense_share": "Expense Breakdown",
        "share_empty": "No data is available for this month.",
        "existing_records": "1. Existing Ledger Data",
        "existing_caption": "You can edit table values directly. Saving recalculates income, expense, and profit.",
        "save_table": "Save Table Changes",
        "record_entry": "2. Monthly Data Entry",
        "month": "Month",
        "month_note": "Monthly Notes",
        "save_record": "Save Monthly Ledger",
        "column_management": "3. Column Management",
        "column_name": "Column Name",
        "column_type": "Column Type",
        "add_column": "Add Column",
        "disable_column": "Disable Selected Column",
        "template_management": "Template Settings",
        "create_template": "Create Template",
        "template_name": "Template Name",
        "create_from_project": "Create Template From Current Project",
        "template_columns": "Template Columns",
        "disable_template_column": "Disable Template Column",
        "export_settings": "4. Import / Export",
        "export_project_excel": "Export Current Project Excel",
        "export_all_excel": "Export All Projects Excel",
        "export_project_bundle": "Export Current Project Bundle",
        "export_system": "Export Full System Bundle",
        "import_system": "Import Full System Bundle",
        "import_system_file": "Upload System Bundle",
        "import_system_submit": "Import System Bundle",
        "system_import_done": "System bundle imported successfully.",
        "system_import_desc": "Importing replaces all local templates, projects, and ledger data on this machine.",
        "import_project": "Import Single Project",
        "import_file": "Upload Project Bundle",
        "import_name": "Imported Project Name",
        "import_region": "Imported Region",
        "import_submit": "Import Project",
        "no_records": "No monthly data yet.",
        "project_missing_columns": "Please create columns for this project before entering monthly data.",
        "project_created": "Project created.",
        "project_renamed": "Project name updated.",
        "template_created": "Template created.",
        "template_from_project_done": "Template created from current project.",
        "column_added": "Column added.",
        "template_column_added": "Template column added.",
        "column_disabled": "Column disabled. Historical data is still kept.",
        "template_column_disabled_done": "Template column disabled.",
        "record_saved": "Monthly ledger saved.",
        "records_saved": "Historical ledger updated.",
        "import_done": "Project imported successfully.",
        "name_required": "Name is required.",
        "template_desc": "Once templates are ready, new projects can reuse the same column structure.",
        "open_template_settings": "Open Template Settings from the left menu to create or edit templates.",
        "system_export_desc": "System export includes the SQLite database, schema SQL, seed SQL, and JSON snapshot.",
        "project_export_desc": "Project bundle includes project info, column definitions, and historical ledger data.",
        "batch_metadata": "5. Batch Month Metadata Import / Export",
        "batch_export_desc": "Export all projects in one region for one month, fill values, then import in one go.",
        "batch_export_month": "Template Month",
        "batch_export_region": "Template Region",
        "batch_export_button": "Export Batch Metadata Excel",
        "batch_import_file": "Upload Batch Metadata Excel",
        "batch_import_button": "Import Batch Metadata Excel",
        "batch_import_done": "Batch import finished: {imported} rows saved, {skipped} rows skipped.",
        "no_template_columns": "This template has no columns yet.",
        "template_select": "Select Template",
        "current_project": "Current Project",
        "current_template": "Current Template",
        "notes_placeholder": "Text columns accept notes. Numeric columns should use numbers.",
    }
}

def t(key: str) -> str:
    language = st.session_state.get("language", "简体中文")
    return I18N[language][key]


def render_header() -> None:
    title_col, lang_col = st.columns([6, 1.5])
    with title_col:
        st.title(t("app_title"))
        st.caption(t("app_caption"))
    with lang_col:
        selected_language = st.radio(
            t("language"),
            list(I18N.keys()),
            index=list(I18N.keys()).index(st.session_state.get("language", "简体中文")),
            horizontal=True,  # 設定為水平排列
            label_visibility="collapsed"  # 隱藏 "語言" 標籤，讓排版更對齊頂部
        )

        # 只有當語言真的發生改變時，才觸發更新
        if selected_language != st.session_state.get("language"):
            st.session_state["language"] = selected_language
            st.rerun()  # 強制重新載入畫面以應用新語言


def render_sidebar() -> tuple[str, int | None]:
    st.sidebar.title(t("menu"))
    grouped_projects = list_projects_by_region()
    templates = list_templates()
    template_options = {t("template_none"): None, **{item["name"]: item["id"] for item in templates}}
    current_project_id = st.session_state.get("selected_project_id")
    current_view = st.session_state.get("current_view", "project")

    view = st.sidebar.radio(
        t("menu"),
        options=["project", "template"],
        index=0 if current_view == "project" else 1,
        format_func=lambda item: t("project_ledger") if item == "project" else t("template_center"),
        label_visibility="collapsed",
    )
    st.session_state["current_view"] = view

    if view == "template":
        return "template", None

    for region in VALID_REGIONS:
        with st.sidebar.expander(region, expanded=True):
            projects = grouped_projects.get(region, [])
            if projects:
                for project in projects:
                    is_selected = current_project_id == project["id"]
                    prefix = "• " if is_selected else ""
                    # 移除了 col 劃分與 popover，只保留乾淨的專案切換按鈕
                    if st.button(
                            f"{prefix}{project['name']}",
                            key=f"project_{project['id']}",
                            use_container_width=True,
                    ):
                        st.session_state["selected_project_id"] = project["id"]
                        st.rerun()
            else:
                st.caption(t("group_empty"))

            with st.popover(t("new_project").format(region=region), use_container_width=True):
                with st.form(f"create_project_{region}", clear_on_submit=True):
                    name = st.text_input(t("project_name"), key=f"project_name_{region}")
                    description = st.text_area(t("description"), key=f"project_description_{region}")
                    template_name = st.selectbox(t("template_select"), list(template_options.keys()), key=f"template_{region}")
                    submitted = st.form_submit_button(t("create"))
                    if submitted:
                        if not name.strip():
                            st.error(t("name_required"))
                        else:
                            project_id = create_project(name, region, description, template_options[template_name])
                            st.session_state["selected_project_id"] = project_id
                            st.success(t("project_created"))
                            st.rerun()

    all_projects = [project for projects in grouped_projects.values() for project in projects]
    if not all_projects:
        st.sidebar.info(t("first_project_hint"))
        return "project", None

    if current_project_id is None or not any(project["id"] == current_project_id for project in all_projects):
        current_project_id = all_projects[0]["id"]
        st.session_state["selected_project_id"] = current_project_id
    return "project", current_project_id


def render_trend_chart(project_id: int) -> None:
    st.subheader(t("trend"))
    trend_df = build_trend_dataframe(project_id)
    if trend_df.empty:
        st.info(t("trend_empty"))
        return

    language = st.session_state.get("language", "简体中文")
    labels = {
        "income": "Income" if language == "English" else "收入",
        "expense": "Expense" if language == "English" else "支出",
        "profit": "Profit" if language == "English" else "利润",
    }
    metric_options = ["income", "expense", "profit"]
    metric_key = f"trend_metric_multi_{project_id}"
    if metric_key not in st.session_state:
        st.session_state[metric_key] = ["income", "expense", "profit"]

    default_metrics = [item for item in st.session_state[metric_key] if item in metric_options]
    if not default_metrics:
        default_metrics = ["profit"]

    if hasattr(st, "pills"):
        selected_metrics = st.pills(
            t("trend_metric_select"),
            options=metric_options,
            default=default_metrics,
            format_func=lambda metric: labels[metric],
            selection_mode="multi",
            key=f"trend_metric_pills_{project_id}",
        )
        selected_metrics = list(selected_metrics or [])
    else:
        selected_metrics = st.multiselect(
            t("trend_metric_select"),
            options=metric_options,
            default=default_metrics,
            format_func=lambda metric: labels[metric],
            key=f"trend_metric_multi_select_{project_id}",
            label_visibility="collapsed",
        )

    if not selected_metrics:
        selected_metrics = ["profit"]
    st.session_state[metric_key] = selected_metrics

    trend_df["month_date"] = pd.to_datetime(trend_df["record_month"] + "-01", errors="coerce")
    trend_df = trend_df.dropna(subset=["month_date"]).sort_values("month_date")

    trend_df["month_label"] = trend_df["month_date"].dt.strftime("%Y-%m")

    color_map = {"income": "#4FC3F7", "expense": "#FF8A65", "profit": "#FFD54F"}
    plot_df = trend_df.melt(
        id_vars=["month_date", "month_label"],
        value_vars=selected_metrics,
        var_name="metric",
        value_name="amount",
    )
    plot_df["metric_label"] = plot_df["metric"].map(labels)

    domain = [labels[item] for item in selected_metrics]
    range_colors = [color_map[item] for item in selected_metrics]

    line = (
        alt.Chart(plot_df)
        .mark_line(
            strokeWidth=3,
            point=alt.OverlayMarkDef(filled=True, size=85, strokeWidth=1.2),
        )
        .encode(
            x=alt.X(
                "month_label:N",
                sort=trend_df["month_label"].tolist(),
                axis=alt.Axis(title=None, labelColor="#E5E7EB", labelPadding=8, tickColor="#E5E7EB"),
            ),
            y=alt.Y(
                "amount:Q",
                axis=alt.Axis(
                    title=None,
                    labelColor="#E5E7EB",
                    grid=True,
                    gridColor="#6B7280",
                    gridDash=[6, 4],
                    gridOpacity=0.85,
                    tickCount=6,
                ),
                scale=alt.Scale(zero=True),
            ),
            color=alt.Color(
                "metric_label:N",
                scale=alt.Scale(domain=domain, range=range_colors),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("month_label:N", title="Month"),
                alt.Tooltip("metric_label:N", title="Metric"),
                alt.Tooltip("amount:Q", title="Value", format=",.2f"),
            ],
        )
    )

    chart = (
        line.properties(height=300, padding={"bottom": 8})
        .configure(background="#000000")
        .configure_view(strokeOpacity=0)
        .configure_axis(domainColor="#E5E7EB", domainWidth=1.2)
    )
    st.altair_chart(chart, use_container_width=True)

    legend_items = [
        f'<span style="display:inline-flex;align-items:center;margin:0 10px;color:#E5E7EB;">'
        f'<span style="width:10px;height:10px;border-radius:50%;background:{color_map[item]};display:inline-block;margin-right:6px;"></span>'
        f'{labels[item]}</span>'
        for item in selected_metrics
    ]
    st.markdown(
        f'<div style="display:flex;justify-content:center;align-items:center;margin-top:-2px;">{"".join(legend_items)}</div>',
        unsafe_allow_html=True,
    )


def _build_month_options(project_id: int) -> list[str]:
    existing_months = set(list_record_months(project_id))
    today = date.today()
    generated: list[str] = []
    for offset in range(-6, 7):
        month_index = (today.year * 12 + today.month - 1) + offset
        year = month_index // 12
        month = month_index % 12 + 1
        generated.append(f"{year:04d}-{month:02d}")
    return sorted(existing_months.union(generated), reverse=True)


def _render_breakdown_table(project_id: int, record_month: str, column_type: str, title: str) -> None:
    st.markdown(f"**{title}**")
    breakdown_df = build_category_breakdown(project_id, record_month, column_type)
    if breakdown_df.empty:
        st.info(t("share_empty"))
        return

    display_df = breakdown_df.copy()
    display_df["share"] = display_df["share"].map(lambda value: f"{value:.1%}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    pie_spec = {
        "mark": {"type": "arc", "innerRadius": 0},
        "encoding": {
            "theta": {"field": "value", "type": "quantitative"},
            "color": {"field": "category", "type": "nominal"},
            "tooltip": [
                {"field": "category", "type": "nominal"},
                {"field": "value", "type": "quantitative"},
                {"field": "share", "type": "quantitative", "format": ".1%"},
            ],
        },
    }
    st.vega_lite_chart(breakdown_df, pie_spec, use_container_width=True)


def render_project_analytics(project_id: int) -> None:
    st.subheader(t("analytics"))
    render_trend_chart(project_id)

    month_options = list_record_months(project_id)
    if not month_options:
        return

    selected_month = st.selectbox(t("analysis_month"), month_options, key=f"analysis_month_{project_id}")
    income_col, expense_col = st.columns(2)
    with income_col:
        _render_breakdown_table(project_id, selected_month, "income", t("income_share"))
    with expense_col:
        _render_breakdown_table(project_id, selected_month, "expense", t("expense_share"))


def render_existing_records(project_id: int, key_prefix: str = "records") -> None:
    project = get_project(project_id)
    st.subheader(t("existing_records"))

    template_caption = f"{t('current_template')}: {project.get('template_name') or t('template_none')}"
    st.caption(f"{t('current_project')}: {project['name']} | {template_caption}")
    st.caption(t("existing_caption"))

    dataframe = build_record_editor_dataframe(project_id)
    if dataframe.empty:
        st.info(t("no_records"))
        return

    edited = st.data_editor(
        dataframe,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        disabled=["record_month", "project_name", "total_income", "total_expense", "net_income"],
        key=f"{key_prefix}_records_editor_{project_id}",
    )
    if st.button(t("save_table"), key=f"{key_prefix}_save_editor_{project_id}"):
        save_record_editor_dataframe(project_id, pd.DataFrame(edited))
        st.success(t("records_saved"))
        st.rerun()


def render_record_entry(project_id: int) -> None:
    project = get_project(project_id)
    columns = list_project_columns(project_id)
    st.subheader(t("record_entry"))

    if not columns:
        st.warning(t("project_missing_columns"))
        return

    month_options = _build_month_options(project_id)
    current_month = date.today().strftime("%Y-%m")
    default_index = month_options.index(current_month) if current_month in month_options else 0
    record_month = st.selectbox(t("month"), month_options, index=default_index, key=f"record_month_{project_id}")
    existing_record, existing_values = get_record_with_values(project_id, record_month)

    with st.form("record_form"):
        inputs: dict[int, str] = {}
        st.caption(f"{t('current_project')}: {project['name']} | {record_month}")
        for column in columns:
            inputs[column.id] = st.text_input(
                f"{column.name} [{column.column_type}]",
                value=existing_values.get(column.id, ""),
                placeholder=t("notes_placeholder"),
            )

        notes = st.text_area(t("month_note"), value=(existing_record or {}).get("notes", ""))
        submitted = st.form_submit_button(t("save_record"))
        if submitted:
            try:
                save_monthly_record(project_id, record_month, notes, inputs)
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.success(t("record_saved"))
                st.rerun()


def render_column_management(project_id: int) -> None:
    st.subheader(t("column_management"))
    columns = list_project_columns(project_id, include_inactive=True)

    with st.form("column_form", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        column_name = col1.text_input(t("column_name"))
        column_type = col2.selectbox(t("column_type"), VALID_COLUMN_TYPES)
        submitted = st.form_submit_button(t("add_column"))
        if submitted:
            if not column_name.strip():
                st.error(t("name_required"))
            else:
                add_project_column(project_id, column_name, column_type)
                st.success(t("column_added"))
                st.rerun()

    if columns:
        st.dataframe(
            [{"id": col.id, "name": col.name, "type": col.column_type, "status": "active" if col.is_active else "inactive"} for col in columns],
            use_container_width=True,
            hide_index=True,
        )
        active_columns = [col for col in columns if col.is_active]
        if active_columns:
            removable = {f"{col.name} ({col.column_type})": col.id for col in active_columns}
            selected = st.selectbox(t("disable_column"), list(removable.keys()))
            if st.button(t("disable_column"), type="secondary"):
                deactivate_project_column(removable[selected])
                st.success(t("column_disabled"))
                st.rerun()


def _build_global_month_options() -> list[str]:
    existing_months = {record["record_month"] for record in list_monthly_records()}
    today = date.today()
    generated: list[str] = []
    for offset in range(-6, 7):
        month_index = (today.year * 12 + today.month - 1) + offset
        year = month_index // 12
        month = month_index % 12 + 1
        generated.append(f"{year:04d}-{month:02d}")
    return sorted(existing_months.union(generated), reverse=True)


def render_template_management(project_id: int) -> None:
    st.subheader(t("template_management"))
    st.caption(t("template_desc"))
    templates = list_templates()
    left_col, right_col = st.columns(2)

    with left_col:
        with st.form("template_create_form", clear_on_submit=True):
            name = st.text_input(t("template_name"))
            description = st.text_area(t("description"), key="template_description")
            submitted = st.form_submit_button(t("create_template"))
            if submitted:
                if not name.strip():
                    st.error(t("name_required"))
                else:
                    create_template(name, description)
                    st.success(t("template_created"))
                    st.rerun()

        with st.form("template_from_project_form", clear_on_submit=True):
            generated_name = st.text_input(f"{t('template_name')} ({t('current_project')})")
            generated_desc = st.text_area(t("description"), key="template_from_project_description")
            submitted = st.form_submit_button(t("create_from_project"))
            if submitted:
                if not generated_name.strip():
                    st.error(t("name_required"))
                else:
                    create_template_from_project(project_id, generated_name, generated_desc)
                    st.success(t("template_from_project_done"))
                    st.rerun()

    with right_col:
        if not templates:
            st.info(t("group_empty"))
            return
        selected_template_name = st.selectbox(t("template_select"), [item["name"] for item in templates], key="template_manage_select")
        selected_template_id = next(item["id"] for item in templates if item["name"] == selected_template_name)
        template = get_template(selected_template_id)
        st.caption(f"{t('current_template')}: {template['name']}")

        with st.form("template_column_form", clear_on_submit=True):
            col1, col2 = st.columns([2, 1])
            column_name = col1.text_input(t("column_name"), key="template_column_name")
            column_type = col2.selectbox(t("column_type"), VALID_COLUMN_TYPES, key="template_column_type")
            submitted = st.form_submit_button(t("add_column"))
            if submitted:
                if not column_name.strip():
                    st.error(t("name_required"))
                else:
                    add_template_column(selected_template_id, column_name, column_type)
                    st.success(t("template_column_added"))
                    st.rerun()

        template_columns = list_template_columns(selected_template_id, include_inactive=True)
        if not template_columns:
            st.info(t("no_template_columns"))
            return
        st.dataframe(
            [{"id": col.id, "name": col.name, "type": col.column_type, "status": "active" if col.is_active else "inactive"} for col in template_columns],
            use_container_width=True,
            hide_index=True,
        )
        active_template_columns = [col for col in template_columns if col.is_active]
        if active_template_columns:
            removable = {f"{col.name} ({col.column_type})": col.id for col in active_template_columns}
            selected = st.selectbox(t("disable_template_column"), list(removable.keys()))
            if st.button(t("disable_template_column"), key="disable_template_btn", type="secondary"):
                deactivate_template_column(removable[selected])
                st.success(t("template_column_disabled_done"))
                st.rerun()


def render_export(project_id: int) -> None:
    st.subheader(t("export_settings"))
    records = list_monthly_records(project_id)
    if records:
        st.dataframe(records, use_container_width=True, hide_index=True)
    else:
        st.info(t("no_records"))

    project = get_project(project_id)
    st.download_button(
        t("export_project_excel"),
        data=export_excel(project_id),
        file_name=f"{project['name']}_monthly_ledger.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    st.download_button(
        t("export_all_excel"),
        data=export_excel(),
        file_name="all_projects_monthly_ledger.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    st.caption(t("project_export_desc"))
    st.download_button(
        t("export_project_bundle"),
        data=export_project_bundle(project_id),
        file_name=f"{project['name']}_project_bundle.zip",
        mime="application/zip",
    )
    st.caption(t("system_export_desc"))
    st.download_button(
        t("export_system"),
        data=export_system_bundle(),
        file_name="parking_ledger_system_bundle.zip",
        mime="application/zip",
    )

    st.markdown(f"**{t('import_system')}**")
    st.caption(t("system_import_desc"))
    system_uploaded = st.file_uploader(t("import_system_file"), type=["zip"], key="system_bundle_uploader")
    if st.button(t("import_system_submit"), disabled=system_uploaded is None):
        import_system_bundle(system_uploaded.getvalue())
        st.session_state["selected_project_id"] = None
        st.success(t("system_import_done"))
        st.rerun()

    st.markdown(f"**{t('import_project')}**")
    uploaded = st.file_uploader(t("import_file"), type=["zip"])
    import_col1, import_col2 = st.columns(2)
    imported_name = import_col1.text_input(t("import_name"))
    imported_region = import_col2.selectbox(t("import_region"), VALID_REGIONS)
    if st.button(t("import_submit"), disabled=uploaded is None):
        project_id = import_project_bundle(uploaded.getvalue(), imported_name or None, imported_region)
        st.session_state["selected_project_id"] = project_id
        st.success(t("import_done"))
        st.rerun()

    st.markdown(f"**{t('batch_metadata')}**")
    st.caption(t("batch_export_desc"))
    batch_col1, batch_col2 = st.columns(2)
    month_options = _build_global_month_options()
    default_month = date.today().strftime("%Y-%m")
    default_idx = month_options.index(default_month) if default_month in month_options else 0
    batch_month = batch_col1.selectbox(t("batch_export_month"), month_options, index=default_idx)
    batch_region = batch_col2.selectbox(t("batch_export_region"), VALID_REGIONS)
    st.download_button(
        t("batch_export_button"),
        data=export_month_region_metadata_excel(batch_month, batch_region),
        file_name=f"metadata_{batch_region}_{batch_month}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    batch_uploaded = st.file_uploader(t("batch_import_file"), type=["xlsx"], key="batch_metadata_uploader")
    if st.button(t("batch_import_button"), disabled=batch_uploaded is None):
        try:
            result = import_month_region_metadata_excel(batch_uploaded.getvalue())
        except ValueError as exc:
            st.error(str(exc))
        else:
            st.success(t("batch_import_done").format(imported=result["imported_records"], skipped=result["skipped_rows"]))
            st.rerun()


def render_project_settings(project_id: int) -> None:
    st.subheader(t("settings"))
    project = get_project(project_id)
    with st.form(f"rename_form_{project_id}"):
        new_name = st.text_input(t("project_name"), value=project["name"])
        submitted = st.form_submit_button(t("rename_project_submit"))
        if submitted:
            if not new_name.strip():
                st.error(t("name_required"))
            else:
                update_project_name(project_id, new_name)
                st.success(t("project_renamed"))
                st.rerun()
    render_column_management(project_id)
    render_export(project_id)


def main() -> None:
    if "language" not in st.session_state:
        st.session_state["language"] = "简体中文"

    render_header()
    current_view, selected_project_id = render_sidebar()
    if current_view == "template":
        current_project_id = st.session_state.get("selected_project_id")
        if current_project_id is None:
            projects = list_projects_by_region()
            flat_projects = [project for items in projects.values() for project in items]
            current_project_id = flat_projects[0]["id"] if flat_projects else None
        if current_project_id is None:
            st.info(t("open_template_settings"))
            return
        render_template_management(current_project_id)
        return

    if selected_project_id is None:
        st.info(t("first_project_hint"))
        return

    page_display, page_input, page_settings = st.tabs(
        [t("page_data_display"), t("page_data_input"), t("page_settings")]
    )

    with page_display:
        render_project_analytics(selected_project_id)
        render_existing_records(selected_project_id, key_prefix="display")

    with page_input:
        render_existing_records(selected_project_id, key_prefix="input")
        render_record_entry(selected_project_id)

    with page_settings:
        render_project_settings(selected_project_id)


if __name__ == "__main__":
    main()
