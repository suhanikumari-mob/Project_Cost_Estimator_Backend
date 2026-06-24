import re
import json
import tempfile
from jinja2 import Template
from xhtml2pdf import pisa


TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  @page { size: A4 landscape; margin: 15mm; }
  body { font-family: Arial, sans-serif; font-size: 8pt; color: #333; }

  h1 { background: #1F4E79; color: white; text-align: center; padding: 10px; font-size: 14pt; margin-bottom: 4px; }
  h2 { background: #2E75B6; color: white; padding: 6px 10px; font-size: 10pt; margin: 18px 0 6px 0; }

  table { width: 100%; border-collapse: collapse; margin-bottom: 12px; }
  th { background: #1F4E79; color: white; padding: 5px 4px; text-align: center; font-size: 7.5pt; }
  td { padding: 4px; border: 0.5pt solid #BFBFBF; vertical-align: top; font-size: 7.5pt; }
  tr:nth-child(even) td { background: #F2F7FB; }

  .module-cell { background: #D6E4F0 !important; font-weight: bold; text-align: center; }
  .center { text-align: center; }
  .total-row td { background: #1E7145 !important; color: white; font-weight: bold; text-align: center; }

  .summary-key { font-weight: bold; color: #1F4E79; background: #D6E4F0; padding: 6px 8px; }
  .summary-val { text-align: center; padding: 6px 8px; }

  .note { font-size: 7pt; color: #888; margin-top: 8px; font-style: italic; }
</style>
</head>
<body>

<h1>{{ title }}</h1>

<!-- Cost Breakdown -->
<h2>Cost Breakdown</h2>
<table>
  <tr>
    <th style="width:12%">Module</th>
    <th style="width:13%">Sub Module</th>
    <th style="width:20%">Description</th>
    <th style="width:17%">Deliverables</th>
    <th style="width:17%">Assumptions</th>
    <th style="width:6%">FE Hrs</th>
    <th style="width:6%">BE Hrs</th>
    <th style="width:9%">Cost (Rs.)</th>
  </tr>
  {% for row in cost_breakdown %}
  <tr>
    <td class="module-cell">{{ row.module }}</td>
    <td>{{ row.sub_module }}</td>
    <td>{{ row.description }}</td>
    <td>{{ row.deliverables }}</td>
    <td>{{ row.notes }}</td>
    <td class="center">{{ row.frontend_hours }}</td>
    <td class="center">{{ row.backend_hours }}</td>
    <td class="center">Rs. {{ "{:,}".format(row.cost) }}</td>
  </tr>
  {% endfor %}
  <tr class="total-row">
    <td colspan="5">TOTAL</td>
    <td>{{ total_fe }}</td>
    <td>{{ total_be }}</td>
    <td>Rs. {{ "{:,}".format(total_cost) }}</td>
  </tr>
</table>

<!-- Cost Summary -->
<h2>Cost Summary</h2>
<table>
  <tr>
    <th style="width:5%">#</th>
    <th style="width:70%">Category</th>
    <th style="width:25%">Cost (Rs.)</th>
  </tr>
  {% for row in cost_summary %}
  <tr>
    <td class="center">{{ loop.index }}</td>
    <td>{{ row.category }}</td>
    <td class="center">Rs. {{ "{:,}".format(row.cost) }}</td>
  </tr>
  {% endfor %}
  <tr class="total-row">
    <td></td>
    <td>TOTAL</td>
    <td>Rs. {{ "{:,}".format(summary_total) }}</td>
  </tr>
</table>

<!-- Timeline -->
<h2>Project Timeline</h2>
<table>
  <tr>
    <th style="width:5%">#</th>
    <th style="width:70%">Phase</th>
    <th style="width:25%">Duration</th>
  </tr>
  {% for row in timeline_phases %}
  <tr>
    <td class="center">{{ loop.index }}</td>
    <td>{{ row.phase }}</td>
    <td class="center">{{ row.duration }}</td>
  </tr>
  {% endfor %}
  {% if timeline_total %}
  <tr class="total-row">
    <td></td>
    <td>{{ timeline_total.phase }}</td>
    <td>{{ timeline_total.duration }}</td>
  </tr>
  {% endif %}
</table>

<!-- Project Summary -->
<h2>Project Summary</h2>
<table>
  <tr><td class="summary-key" style="width:50%">Total Cost</td><td class="summary-val">Rs. {{ "{:,}".format(proj.total_cost) }}</td></tr>
  <tr><td class="summary-key">Currency</td><td class="summary-val">{{ proj.currency }}</td></tr>
  <tr><td class="summary-key">Applicable Taxes</td><td class="summary-val">{{ "Yes" if proj.applicable_taxes else "No" }}</td></tr>
  <tr><td class="summary-key">Estimated Project Duration</td><td class="summary-val">{{ proj.estimated_project_duration }}</td></tr>
  <tr><td class="summary-key">Estimated Development Effort</td><td class="summary-val">{{ proj.estimated_development_effort }}</td></tr>
</table>

<p class="note">* All costs are in INR and exclude applicable taxes.</p>
</body>
</html>
"""


def generator_pdf(data, pdf_path: str = None) -> str:
    """
    Generate a PDF from cost estimation JSON using Jinja2 + xhtml2pdf.

    Args:
        data: dict or raw JSON string (with optional ```json fences)
        pdf_path: output path; if None, a temp file is created.

    Returns:
        Path to the saved PDF file.
    """
    if isinstance(data, str):
        raw = re.sub(r"^```[a-zA-Z]*\n?", "", data.strip())
        raw = re.sub(r"```$", "", raw.strip())
        data = json.loads(raw)

    if not pdf_path:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf_path = tmp.name
        tmp.close()

    tables   = data["tables"]
    cb_rows  = tables["cost_breakdown"]
    cs_rows  = [r for r in tables["cost_summary"] if r["category"].lower() != "total"]
    tl_all   = tables["timeline_estimate"]

    html = Template(TEMPLATE).render(
        title          = data.get("title", "Cost Estimation"),
        cost_breakdown = cb_rows,
        total_fe       = sum(r["frontend_hours"] for r in cb_rows),
        total_be       = sum(r["backend_hours"]  for r in cb_rows),
        total_cost     = sum(r["cost"]           for r in cb_rows),
        cost_summary   = cs_rows,
        summary_total  = sum(r["cost"]           for r in cs_rows),
        timeline_phases= [r for r in tl_all if "total" not in r["phase"].lower()],
        timeline_total = next((r for r in tl_all if "total" in r["phase"].lower()), None),
        proj           = data["summary"],
    )

    with open(pdf_path, "wb") as f:
        pisa.CreatePDF(html, dest=f)

    return pdf_path
