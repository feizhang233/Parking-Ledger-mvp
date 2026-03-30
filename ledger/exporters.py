from __future__ import annotations

from io import BytesIO

import pandas as pd

from ledger.services import build_export_dataframe


def export_excel(project_id: int | None = None) -> bytes:
    """Export monthly records to an in-memory Excel file."""
    dataframe = build_export_dataframe(project_id)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(writer, sheet_name="ledger", index=False)
    return output.getvalue()
