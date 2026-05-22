"""PDF generation via WeasyPrint."""
import io
from datetime import datetime, timezone
from typing import Optional

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS

from app.models.incident import Incident


def render_incident_pdf(incident: Incident, base_url: str = "") -> bytes:
    env = Environment(loader=FileSystemLoader("app/templates"), autoescape=True)
    template = env.get_template("pdf/incident_report.html")

    html_str = template.render(
        incident=incident,
        now=datetime.now(timezone.utc),
        base_url=base_url,
    )
    buf = io.BytesIO()
    HTML(string=html_str, base_url=base_url or ".").write_pdf(buf)
    return buf.getvalue()
