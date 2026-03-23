"""
Bass Pro Shops - Automated Weekly KPI Narrative
Task 4.3: Automated Report Narratives with Claude
"""

import os
import smtplib
import textwrap
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

import pandas as pd
import anthropic

EXCEL_FILE = "BassProShops_Weekly_KPI_Report.xlsx"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "YOUR_API_KEY_HERE")
MODEL = "claude-sonnet-4-20250514"
EMAIL_SENDER = os.environ.get("EMAIL_SENDER", "")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")
EMAIL_RECIPIENTS = os.environ.get("EMAIL_RECIPIENTS", "")
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def load_kpis(filepath):
    df = pd.read_excel(filepath, sheet_name="Data for Python", header=None)
    header_row = None
    for i, row in df.iterrows():
        if any(str(v).strip().lower() == 'kpi_key' for v in row.values):
            header_row = i
            break
    df.columns = df.iloc[header_row]
    df = df[header_row + 1:].reset_index(drop=True)
    df.columns = ["kpi_key", "this_week", "last_week", "target", "unit"]
    df = df[df["kpi_key"].notna() & (df["kpi_key"].astype(str).str.strip() != "nan")]

    kpis = {}
    for _, row in df.iterrows():
        key = str(row["kpi_key"]).strip()
        if key and key != "nan":
            try:
                kpis[key] = {
                    "this_week": float(row["this_week"]),
                    "last_week": float(row["last_week"]),
                    "target":    float(row["target"]),
                    "unit":      str(row["unit"]),
                }
            except (ValueError, TypeError):
                pass

    issues_df = pd.read_excel(filepath, sheet_name="Issues & Actions", header=None)
    issues_df.columns = issues_df.iloc[1]
    issues_df = issues_df[2:].reset_index(drop=True)
    issues = []
    for _, row in issues_df.iterrows():
        area  = str(row.get("Area", "")).strip()
        issue = str(row.get("Issue / Risk", "")).strip()
        status = str(row.get("Status", "")).strip()
        if area and area != "nan":
            issues.append(f"[{area}] {issue} -- {status}")

    return {"kpis": kpis, "issues": issues}


def format_kpi_block(data):
    lines = ["KPI                        | This Week | Last Week | Target"]
    lines.append("-" * 65)
    for key, v in data["kpis"].items():
        tw, lw, tg, unit = v["this_week"], v["last_week"], v["target"], v["unit"]
        pvt = ((tw - tg) / tg * 100) if tg else 0
        pvl = ((tw - lw) / lw * 100) if lw else 0
        lines.append(f"{key:<30} | {tw:>9} | {lw:>9} | {tg:>9}  ({pvt:+.1f}% vs target, {pvl:+.1f}% WoW)  [{unit}]")
    lines.append("")
    lines.append("Open Issues:")
    for issue in data["issues"]:
        lines.append(f"  - {issue}")
    return "\n".join(lines)


def generate_master_narrative(client, kpi_block):
    prompt = f"""You are a senior Business Analyst at Bass Pro Shops.

Given these weekly KPIs:

{kpi_block}

Write a 200-word executive commentary:
- Highlight the 2 most important positive trends
- Identify 1 key risk that needs immediate attention
- Be specific: use actual numbers from the data
- Tone: confident, concise, boardroom-ready
"""
    message = client.messages.create(
        model=MODEL,
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


def adapt_for_audience(client, master_narrative, audience, instructions):
    prompt = f"""Rewrite this weekly performance commentary for a {audience} audience.

Original commentary:
{master_narrative}

Instructions for {audience} audience:
{instructions}

Keep all key numbers. Rewrite, do not just summarise.
"""
    message = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


AUDIENCE_INSTRUCTIONS = {
    "Executive (C-Suite)": (
        "3-4 sentences maximum. Focus on revenue impact and strategic risk. "
        "Avoid operational detail. Lead with the headline number. "
        "Recommend one decision or action."
    ),
    "Technical (Analysts and Engineers)": (
        "150-200 words. Include percentage changes, WoW deltas, and root-cause "
        "hypotheses. Call out the checkout abandonment regression specifically. "
        "Use precise metric names. Suggest 2-3 diagnostic next steps."
    ),
    "Frontline (Store Teams)": (
        "Use plain English, no jargon. 3-4 short sentences. "
        "Tell them what went well this week and one thing they can do differently. "
        "Be encouraging and action-oriented."
    ),
}


def build_html_report(master, adaptations, week_ending):
    sections = ""
    for audience, text in adaptations.items():
        paragraphs = "".join(f"<p>{p}</p>" for p in text.split("\n") if p.strip())
        sections += f"""
        <h3 style="color:#1a6c3c; border-bottom:1px solid #ccc; padding-bottom:4px;">{audience}</h3>
        <div style="background:#f9f9f9; padding:12px; border-radius:6px; margin-bottom:20px;">
            {paragraphs}
        </div>
        """

    master_html = "".join(f"<p>{p}</p>" for p in master.split("\n") if p.strip())

    return f"""<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif; max-width:700px; margin:auto; color:#222;">
    <div style="background:#1a6c3c; color:white; padding:16px 20px; border-radius:8px 8px 0 0;">
        <h1 style="margin:0; font-size:20px;">Bass Pro Shops - Weekly Performance Report</h1>
        <p style="margin:4px 0 0; font-size:13px; opacity:.85;">Week Ending: {week_ending}</p>
    </div>
    <div style="border:1px solid #ccc; border-top:none; padding:20px; border-radius:0 0 8px 8px;">
        <h2 style="color:#333;">Master Commentary</h2>
        <div style="background:#eaf4ee; padding:14px; border-left:4px solid #1a6c3c; border-radius:4px;">
            {master_html}
        </div>
        <h2 style="color:#333; margin-top:28px;">Audience-Adapted Versions</h2>
        {sections}
        <p style="color:#888; font-size:11px; margin-top:30px;">
            Generated automatically by weekly_report.py - Powered by Claude API
        </p>
    </div>
</body>
</html>"""


def send_email(subject, html_body, recipients):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, recipients, msg.as_string())
    print(f"Email sent to: {', '.join(recipients)}")


def main():
    week_ending = datetime.today().strftime("%B %d, %Y")
    print(f"\n{'='*60}")
    print(f"  Bass Pro Shops Weekly Report -- {week_ending}")
    print(f"{'='*60}\n")

    print("Loading KPI data from Excel...")
    data = load_kpis(EXCEL_FILE)
    kpi_block = format_kpi_block(data)
    print(kpi_block)

    print("\nCalling Claude -> master narrative...")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    master = generate_master_narrative(client, kpi_block)
    print("\n-- MASTER NARRATIVE --")
    print(textwrap.fill(master, width=70))

    adaptations = {}
    for audience, instructions in AUDIENCE_INSTRUCTIONS.items():
        print(f"\nAdapting for: {audience}...")
        adaptations[audience] = adapt_for_audience(client, master, audience, instructions)
        print(f"\n-- {audience.upper()} --")
        print(textwrap.fill(adaptations[audience], width=70))

    html = build_html_report(master, adaptations, week_ending)
    out_path = f"weekly_report_{datetime.today().strftime('%Y%m%d')}.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\nReport saved: {out_path}")

    if EMAIL_SENDER and EMAIL_PASSWORD and EMAIL_RECIPIENTS:
        print("\nSending email...")
        recipients = [r.strip() for r in EMAIL_RECIPIENTS.split(",") if r.strip()]
        try:
            send_email(
                subject=f"[Bass Pro Shops] Weekly KPI Report -- {week_ending}",
                html_body=html,
                recipients=recipients,
            )
        except Exception as e:
            print(f"Email failed: {e}")
    else:
        print("\nEmail skipped (no credentials set)")

    print("\nPipeline complete.\n")


if __name__ == "__main__":
    main()
