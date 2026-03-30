from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from io import BytesIO
import json
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile

import pandas as pd

from ledger.db import BASE_DIR, DB_PATH, execute, execute_many, fetch_all, fetch_one, get_connection


VALID_COLUMN_TYPES = ("income", "expense", "text")
VALID_REGIONS = ("北京", "外地")


@dataclass
class ProjectColumn:
    id: int
    project_id: int
    name: str
    column_type: str
    sort_order: int
    is_active: int


@dataclass
class TemplateColumn:
    id: int
    template_id: int
    name: str
    column_type: str
    sort_order: int
    is_active: int


def list_projects() -> list[dict[str, Any]]:
    rows = fetch_all(
        """
        SELECT id, name, region, description, template_id, created_at
        FROM projects
        ORDER BY CASE region WHEN '北京' THEN 1 ELSE 2 END, name COLLATE NOCASE
        """
    )
    return [dict(row) for row in rows]


def list_projects_by_region() -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {region: [] for region in VALID_REGIONS}
    for project in list_projects():
        grouped.setdefault(project["region"], []).append(project)
    return grouped


def list_templates() -> list[dict[str, Any]]:
    rows = fetch_all(
        """
        SELECT id, name, description, created_at
        FROM project_templates
        ORDER BY name COLLATE NOCASE
        """
    )
    return [dict(row) for row in rows]


def get_template(template_id: int) -> dict[str, Any] | None:
    row = fetch_one(
        """
        SELECT id, name, description, created_at
        FROM project_templates
        WHERE id = ?
        """,
        (template_id,),
    )
    return dict(row) if row else None


def list_template_columns(template_id: int, include_inactive: bool = False) -> list[TemplateColumn]:
    query = """
        SELECT id, template_id, name, column_type, sort_order, is_active
        FROM template_columns
        WHERE template_id = ?
    """
    if not include_inactive:
        query += " AND is_active = 1"
    query += " ORDER BY sort_order, id"
    rows = fetch_all(query, (template_id,))
    return [TemplateColumn(**dict(row)) for row in rows]


def create_template(name: str, description: str = "") -> int:
    return execute(
        """
        INSERT INTO project_templates (name, description)
        VALUES (?, ?)
        """,
        (name.strip(), description.strip()),
    )


def add_template_column(template_id: int, name: str, column_type: str) -> int:
    if column_type not in VALID_COLUMN_TYPES:
        raise ValueError(f"Unsupported column type: {column_type}")

    next_order = fetch_one(
        """
        SELECT COALESCE(MAX(sort_order), 0) + 1 AS next_order
        FROM template_columns
        WHERE template_id = ?
        """,
        (template_id,),
    )["next_order"]

    return execute(
        """
        INSERT INTO template_columns (template_id, name, column_type, sort_order)
        VALUES (?, ?, ?, ?)
        """,
        (template_id, name.strip(), column_type, next_order),
    )


def deactivate_template_column(column_id: int) -> None:
    execute(
        """
        UPDATE template_columns
        SET is_active = 0
        WHERE id = ?
        """,
        (column_id,),
    )


def create_template_from_project(project_id: int, template_name: str, description: str = "") -> int:
    template_id = create_template(template_name, description)
    columns = list_project_columns(project_id)
    for column in columns:
        add_template_column(template_id, column.name, column.column_type)
    return template_id


def create_project(name: str, region: str, description: str = "", template_id: int | None = None) -> int:
    if region not in VALID_REGIONS:
        raise ValueError(f"Unsupported region: {region}")

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO projects (name, region, description, template_id)
            VALUES (?, ?, ?, ?)
            """,
            (name.strip(), region, description.strip(), template_id),
        )
        project_id = cursor.lastrowid

        if template_id:
            template_columns = list_template_columns(template_id)
            conn.executemany(
                """
                INSERT INTO project_columns (project_id, name, column_type, sort_order)
                VALUES (?, ?, ?, ?)
                """,
                [(project_id, col.name, col.column_type, col.sort_order) for col in template_columns],
            )
        conn.commit()
    return project_id


def update_project_name(project_id: int, name: str) -> None:
    execute(
        """
        UPDATE projects
        SET name = ?
        WHERE id = ?
        """,
        (name.strip(), project_id),
    )


def get_project(project_id: int) -> dict[str, Any] | None:
    row = fetch_one(
        """
        SELECT p.id, p.name, p.region, p.description, p.template_id, p.created_at,
               pt.name AS template_name
        FROM projects p
        LEFT JOIN project_templates pt ON pt.id = p.template_id
        WHERE p.id = ?
        """,
        (project_id,),
    )
    return dict(row) if row else None


def list_project_columns(project_id: int, include_inactive: bool = False) -> list[ProjectColumn]:
    query = """
        SELECT id, project_id, name, column_type, sort_order, is_active
        FROM project_columns
        WHERE project_id = ?
    """
    if not include_inactive:
        query += " AND is_active = 1"
    query += " ORDER BY sort_order, id"
    rows = fetch_all(query, (project_id,))
    return [ProjectColumn(**dict(row)) for row in rows]


def add_project_column(project_id: int, name: str, column_type: str) -> int:
    if column_type not in VALID_COLUMN_TYPES:
        raise ValueError(f"Unsupported column type: {column_type}")

    next_order = fetch_one(
        """
        SELECT COALESCE(MAX(sort_order), 0) + 1 AS next_order
        FROM project_columns
        WHERE project_id = ?
        """,
        (project_id,),
    )["next_order"]

    return execute(
        """
        INSERT INTO project_columns (project_id, name, column_type, sort_order)
        VALUES (?, ?, ?, ?)
        """,
        (project_id, name.strip(), column_type, next_order),
    )


def deactivate_project_column(column_id: int) -> None:
    execute(
        """
        UPDATE project_columns
        SET is_active = 0
        WHERE id = ?
        """,
        (column_id,),
    )


def list_monthly_records(project_id: int | None = None) -> list[dict[str, Any]]:
    query = """
        SELECT mr.id, mr.project_id, p.name AS project_name, p.region, mr.record_month,
               mr.total_income, mr.total_expense, mr.net_income, mr.notes,
               mr.created_at, mr.updated_at
        FROM monthly_records mr
        JOIN projects p ON p.id = mr.project_id
    """
    params: list[Any] = []
    if project_id is not None:
        query += " WHERE mr.project_id = ?"
        params.append(project_id)
    query += " ORDER BY mr.record_month DESC, p.name COLLATE NOCASE"
    rows = fetch_all(query, params)
    return [dict(row) for row in rows]


def get_record_with_values(project_id: int, record_month: str) -> tuple[dict[str, Any] | None, dict[int, str]]:
    record = fetch_one(
        """
        SELECT id, project_id, record_month, total_income, total_expense, net_income, notes
        FROM monthly_records
        WHERE project_id = ? AND record_month = ?
        """,
        (project_id, record_month),
    )
    if not record:
        return None, {}

    values = fetch_all(
        """
        SELECT column_id, value_text
        FROM monthly_record_values
        WHERE monthly_record_id = ?
        """,
        (record["id"],),
    )
    value_map = {row["column_id"]: row["value_text"] for row in values}
    return dict(record), value_map


def _parse_numeric(value: Any) -> Decimal:
    if value in (None, ""):
        return Decimal("0")
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, AttributeError) as exc:
        raise ValueError(f"Invalid numeric value: {value}") from exc


def save_monthly_record(project_id: int, record_month: str, notes: str, values: dict[int, Any]) -> int:
    columns = list_project_columns(project_id, include_inactive=True)
    column_map = {column.id: column for column in columns}

    total_income = Decimal("0")
    total_expense = Decimal("0")
    normalized_values: list[tuple[int, str]] = []

    for column_id, raw_value in values.items():
        if column_id not in column_map:
            continue

        column = column_map[column_id]
        if column.column_type == "text":
            normalized_values.append((column_id, str(raw_value or "").strip()))
            continue

        number = _parse_numeric(raw_value)
        if column.column_type == "income":
            total_income += number
        elif column.column_type == "expense":
            total_expense += number
        normalized_values.append((column_id, f"{number:.2f}"))

    net_income = total_income - total_expense

    existing = fetch_one(
        """
        SELECT id
        FROM monthly_records
        WHERE project_id = ? AND record_month = ?
        """,
        (project_id, record_month),
    )

    if existing:
        record_id = existing["id"]
        execute(
            """
            UPDATE monthly_records
            SET notes = ?, total_income = ?, total_expense = ?, net_income = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (notes.strip(), float(total_income), float(total_expense), float(net_income), record_id),
        )
        execute("DELETE FROM monthly_record_values WHERE monthly_record_id = ?", (record_id,))
    else:
        record_id = execute(
            """
            INSERT INTO monthly_records (
                project_id, record_month, notes, total_income, total_expense, net_income
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (project_id, record_month, notes.strip(), float(total_income), float(total_expense), float(net_income)),
        )

    if normalized_values:
        execute_many(
            """
            INSERT INTO monthly_record_values (monthly_record_id, column_id, value_text)
            VALUES (?, ?, ?)
            """,
            [(record_id, column_id, value_text) for column_id, value_text in normalized_values],
        )

    return record_id


def build_export_dataframe(project_id: int | None = None) -> pd.DataFrame:
    records = list_monthly_records(project_id)
    rows: list[dict[str, Any]] = []

    for record in records:
        project_columns = list_project_columns(record["project_id"], include_inactive=True)
        _, value_map = get_record_with_values(record["project_id"], record["record_month"])

        row: dict[str, Any] = {
            "project_name": record["project_name"],
            "region": record["region"],
            "record_month": record["record_month"],
        }
        for column in project_columns:
            row[column.name] = value_map.get(column.id, "")
        row["total_income"] = record["total_income"]
        row["total_expense"] = record["total_expense"]
        row["net_income"] = record["net_income"]
        row["notes"] = record["notes"]
        rows.append(row)

    if not rows:
        return pd.DataFrame(
            columns=[
                "project_name",
                "region",
                "record_month",
                "total_income",
                "total_expense",
                "net_income",
                "notes",
            ]
        )
    return pd.DataFrame(rows)


def build_record_editor_dataframe(project_id: int) -> pd.DataFrame:
    project = get_project(project_id)
    project_columns = list_project_columns(project_id, include_inactive=True)
    records = list_monthly_records(project_id)
    rows: list[dict[str, Any]] = []

    for record in records:
        _, value_map = get_record_with_values(project_id, record["record_month"])
        row: dict[str, Any] = {
            "record_month": record["record_month"],
            "project_name": project["name"],
        }
        for column in project_columns:
            row[column.name] = value_map.get(column.id, "")
        row["notes"] = record["notes"]
        row["total_income"] = record["total_income"]
        row["total_expense"] = record["total_expense"]
        row["net_income"] = record["net_income"]
        rows.append(row)

    if not rows:
        return pd.DataFrame(
            columns=["record_month", "project_name", "notes", "total_income", "total_expense", "net_income"]
        )
    return pd.DataFrame(rows)


def build_trend_dataframe(project_id: int) -> pd.DataFrame:
    records = list_monthly_records(project_id)
    rows = [
        {
            "record_month": record["record_month"],
            "income": record["total_income"],
            "expense": record["total_expense"],
            "profit": record["net_income"],
        }
        for record in sorted(records, key=lambda item: item["record_month"])
    ]
    return pd.DataFrame(rows)


def list_record_months(project_id: int) -> list[str]:
    rows = fetch_all(
        """
        SELECT DISTINCT record_month
        FROM monthly_records
        WHERE project_id = ?
        ORDER BY record_month DESC
        """,
        (project_id,),
    )
    return [row["record_month"] for row in rows]


def build_category_breakdown(project_id: int, record_month: str, column_type: str) -> pd.DataFrame:
    if column_type not in ("income", "expense"):
        raise ValueError("column_type must be income or expense")

    columns = [col for col in list_project_columns(project_id, include_inactive=True) if col.column_type == column_type]
    _, value_map = get_record_with_values(project_id, record_month)
    rows: list[dict[str, Any]] = []

    for column in columns:
        raw_value = value_map.get(column.id, "0")
        amount = float(_parse_numeric(raw_value))
        if amount == 0:
            continue
        rows.append({"category": column.name, "value": amount})

    dataframe = pd.DataFrame(rows)
    if dataframe.empty:
        return pd.DataFrame(columns=["category", "value", "share"])

    total = dataframe["value"].sum()
    dataframe["share"] = dataframe["value"] / total
    return dataframe.sort_values("value", ascending=False).reset_index(drop=True)


def save_record_editor_dataframe(project_id: int, dataframe: pd.DataFrame) -> None:
    columns = list_project_columns(project_id, include_inactive=True)
    name_to_id = {column.name: column.id for column in columns}

    for row in dataframe.to_dict(orient="records"):
        record_month = str(row.get("record_month", "")).strip()
        if not record_month:
            continue
        values = {column_id: row.get(name, "") for name, column_id in name_to_id.items()}
        save_monthly_record(project_id, record_month, str(row.get("notes", "")).strip(), values)


def export_project_bundle(project_id: int) -> bytes:
    project = get_project(project_id)
    if not project:
        raise ValueError("Project not found")

    template = get_template(project["template_id"]) if project.get("template_id") else None
    template_columns = (
        [dict(row) for row in fetch_all("SELECT * FROM template_columns WHERE template_id = ? ORDER BY sort_order, id", (project["template_id"],))]
        if project.get("template_id")
        else []
    )
    columns = [dict(row) for row in fetch_all("SELECT * FROM project_columns WHERE project_id = ? ORDER BY sort_order, id", (project_id,))]
    records = [dict(row) for row in fetch_all("SELECT * FROM monthly_records WHERE project_id = ? ORDER BY record_month, id", (project_id,))]
    record_ids = [record["id"] for record in records]
    values: list[dict[str, Any]] = []
    for record_id in record_ids:
        values.extend(
            [dict(row) for row in fetch_all("SELECT * FROM monthly_record_values WHERE monthly_record_id = ? ORDER BY id", (record_id,))]
        )

    payload = {
        "project": project,
        "template": template,
        "template_columns": template_columns,
        "columns": columns,
        "records": records,
        "values": values,
    }

    output = BytesIO()
    with ZipFile(output, "w", ZIP_DEFLATED) as zip_file:
        zip_file.writestr("project_bundle.json", json.dumps(payload, ensure_ascii=False, indent=2))
        zip_file.writestr("project_ledger.csv", build_export_dataframe(project_id).to_csv(index=False))
    return output.getvalue()


def import_project_bundle(bundle_bytes: bytes, new_project_name: str | None = None, region: str | None = None) -> int:
    with ZipFile(BytesIO(bundle_bytes), "r") as zip_file:
        payload = json.loads(zip_file.read("project_bundle.json").decode("utf-8"))

    project_payload = payload["project"]
    target_name = (new_project_name or project_payload["name"]).strip()
    target_region = region or project_payload["region"]
    target_description = project_payload.get("description", "")
    target_template_id = None

    with get_connection() as conn:
        template_payload = payload.get("template")
        if template_payload:
            existing_template = conn.execute(
                "SELECT id FROM project_templates WHERE name = ?",
                (template_payload["name"],),
            ).fetchone()
            if existing_template:
                target_template_id = existing_template["id"]
            else:
                template_cursor = conn.execute(
                    """
                    INSERT INTO project_templates (name, description)
                    VALUES (?, ?)
                    """,
                    (template_payload["name"], template_payload.get("description", "")),
                )
                target_template_id = template_cursor.lastrowid
                for template_column in payload.get("template_columns", []):
                    conn.execute(
                        """
                        INSERT INTO template_columns (template_id, name, column_type, sort_order, is_active)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            target_template_id,
                            template_column["name"],
                            template_column["column_type"],
                            template_column["sort_order"],
                            template_column["is_active"],
                        ),
                    )

        cursor = conn.execute(
            """
            INSERT INTO projects (name, region, description, template_id)
            VALUES (?, ?, ?, ?)
            """,
            (target_name, target_region, target_description, target_template_id),
        )
        project_id = cursor.lastrowid

        source_to_new_column: dict[int, int] = {}
        for column in payload["columns"]:
            new_cursor = conn.execute(
                """
                INSERT INTO project_columns (project_id, name, column_type, sort_order, is_active)
                VALUES (?, ?, ?, ?, ?)
                """,
                (project_id, column["name"], column["column_type"], column["sort_order"], column["is_active"]),
            )
            source_to_new_column[column["id"]] = new_cursor.lastrowid

        source_to_new_record: dict[int, int] = {}
        for record in payload["records"]:
            new_cursor = conn.execute(
                """
                INSERT INTO monthly_records (
                    project_id, record_month, notes, total_income, total_expense, net_income, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    record["record_month"],
                    record["notes"],
                    record["total_income"],
                    record["total_expense"],
                    record["net_income"],
                    record["created_at"],
                    record["updated_at"],
                ),
            )
            source_to_new_record[record["id"]] = new_cursor.lastrowid

        for value in payload["values"]:
            conn.execute(
                """
                INSERT INTO monthly_record_values (monthly_record_id, column_id, value_text)
                VALUES (?, ?, ?)
                """,
                (
                    source_to_new_record[value["monthly_record_id"]],
                    source_to_new_column[value["column_id"]],
                    value["value_text"],
                ),
            )
        conn.commit()
    return project_id


def export_system_bundle() -> bytes:
    snapshot = {
        "projects": [dict(row) for row in fetch_all("SELECT * FROM projects ORDER BY id")],
        "project_templates": [dict(row) for row in fetch_all("SELECT * FROM project_templates ORDER BY id")],
        "template_columns": [dict(row) for row in fetch_all("SELECT * FROM template_columns ORDER BY id")],
        "project_columns": [dict(row) for row in fetch_all("SELECT * FROM project_columns ORDER BY id")],
        "monthly_records": [dict(row) for row in fetch_all("SELECT * FROM monthly_records ORDER BY id")],
        "monthly_record_values": [dict(row) for row in fetch_all("SELECT * FROM monthly_record_values ORDER BY id")],
    }

    output = BytesIO()
    with ZipFile(output, "w", ZIP_DEFLATED) as zip_file:
        if Path(DB_PATH).exists():
            zip_file.write(DB_PATH, arcname="parking_ledger.db")
        zip_file.write(BASE_DIR / "sql" / "schema.sql", arcname="schema.sql")
        zip_file.write(BASE_DIR / "sql" / "seed.sql", arcname="seed.sql")
        zip_file.writestr("settings_snapshot.json", json.dumps(snapshot, ensure_ascii=False, indent=2))
    return output.getvalue()


def import_system_bundle(bundle_bytes: bytes) -> None:
    """Replace the current local system with the exported full-system bundle."""
    with ZipFile(BytesIO(bundle_bytes), "r") as zip_file:
        snapshot = json.loads(zip_file.read("settings_snapshot.json").decode("utf-8"))

    with get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("DELETE FROM monthly_record_values")
        conn.execute("DELETE FROM monthly_records")
        conn.execute("DELETE FROM project_columns")
        conn.execute("DELETE FROM projects")
        conn.execute("DELETE FROM template_columns")
        conn.execute("DELETE FROM project_templates")

        for row in snapshot.get("project_templates", []):
            conn.execute(
                """
                INSERT INTO project_templates (id, name, description, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (row["id"], row["name"], row.get("description", ""), row["created_at"]),
            )

        for row in snapshot.get("template_columns", []):
            conn.execute(
                """
                INSERT INTO template_columns (id, template_id, name, column_type, sort_order, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["id"],
                    row["template_id"],
                    row["name"],
                    row["column_type"],
                    row["sort_order"],
                    row["is_active"],
                    row["created_at"],
                ),
            )

        for row in snapshot.get("projects", []):
            conn.execute(
                """
                INSERT INTO projects (id, name, region, description, template_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    row["id"],
                    row["name"],
                    row["region"],
                    row.get("description", ""),
                    row.get("template_id"),
                    row["created_at"],
                ),
            )

        for row in snapshot.get("project_columns", []):
            conn.execute(
                """
                INSERT INTO project_columns (id, project_id, name, column_type, sort_order, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["id"],
                    row["project_id"],
                    row["name"],
                    row["column_type"],
                    row["sort_order"],
                    row["is_active"],
                    row["created_at"],
                ),
            )

        for row in snapshot.get("monthly_records", []):
            conn.execute(
                """
                INSERT INTO monthly_records (
                    id, project_id, record_month, notes, total_income, total_expense, net_income, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["id"],
                    row["project_id"],
                    row["record_month"],
                    row.get("notes", ""),
                    row["total_income"],
                    row["total_expense"],
                    row["net_income"],
                    row["created_at"],
                    row["updated_at"],
                ),
            )

        for row in snapshot.get("monthly_record_values", []):
            conn.execute(
                """
                INSERT INTO monthly_record_values (id, monthly_record_id, column_id, value_text)
                VALUES (?, ?, ?, ?)
                """,
                (
                    row["id"],
                    row["monthly_record_id"],
                    row["column_id"],
                    row.get("value_text", ""),
                ),
            )

        conn.execute("PRAGMA foreign_keys = ON")
        conn.commit()
