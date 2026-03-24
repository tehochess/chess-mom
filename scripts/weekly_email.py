import os
import json
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta

# ── Secrets ──────────────────────────────────────────────────────────────────
SB_URL      = os.environ.get("SUPABASE_URL", "")
SB_KEY      = os.environ.get("SUPABASE_KEY", "")
EMAIL_SENDER   = os.environ.get("EMAIL_SENDER", "")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

SB_HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
}

# ── 1. Fetch last 7 days from Supabase ───────────────────────────────────────
def fetch_entries():
    url = f"{SB_URL}/rest/v1/progress?order=day_number.desc&limit=7"
    r = requests.get(url, headers=SB_HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()

# ── 2. Build Claude prompt ───────────────────────────────────────────────────
def build_prompt(entries):
    lines = []
    for e in entries:
        lines.append(
            f"Day {e.get('day_number')} ({e.get('entry_date', '')}):\n"
            f"  Confidence={e.get('confidence')}  Understanding={e.get('understanding')}  "
            f"Focus={e.get('focus')}  Momentum={e.get('momentum')}\n"
            f"  Worked on: {e.get('worked_on', '')}\n"
            f"  What clicked: {e.get('clicked', '')}\n"
            f"  What confused me: {e.get('confused', '')}\n"
            f"  Takeaway: {e.get('takeaway', '')}\n"
            f"  Concepts practiced: {e.get('concepts', '')}\n"
            f"  Strengths: {e.get('strengths', '')}\n"
            f"  Areas to improve: {e.get('areas', '')}\n"
        )
    return "\n".join(lines)

def call_claude(entries):
    system = (
        "You are Coach Samuel, a warm and encouraging chess coach helping a beginner "
        "named Mom prepare for a match against Dad. Write a weekly report card in a "
        "supportive, conversational tone. Keep it under 250 words. Structure it as:\n"
        "1. A one-sentence overall assessment of the week.\n"
        "2. 2-3 specific highlights or improvements you noticed.\n"
        "3. 1-2 focus areas for next week.\n"
        "4. A short motivational closing line.\n"
        "Do not use bullet points — write in flowing paragraphs."
    )
    journal_text = build_prompt(entries)
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 600,
        "system": system,
        "messages": [
            {
                "role": "user",
                "content": f"Here is Mom's training journal for the week:\n\n{journal_text}",
            }
        ],
    }
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["content"][0]["text"].strip()

# ── 3. Compute averages ───────────────────────────────────────────────────────
def avg(entries, key):
    vals = [e[key] for e in entries if e.get(key) is not None]
    return round(sum(vals) / len(vals)) if vals else 0

# ── 4. Build HTML email ───────────────────────────────────────────────────────
def color_for(val):
    """Return a hex color on a red→amber→green gradient for 0-100."""
    if val >= 70:
        return "#2d6a4f"
    elif val >= 45:
        return "#d4a017"
    else:
        return "#c0392b"

def build_html(entries, ai_report, week_label):
    conf  = avg(entries, "confidence")
    und   = avg(entries, "understanding")
    foc   = avg(entries, "focus")
    mom   = avg(entries, "momentum")

    def stat_box(label, value):
        color = color_for(value)
        return f"""
        <td style="text-align:center;padding:12px 18px;">
          <div style="font-size:32px;font-weight:700;color:{color};">{value}</div>
          <div style="font-size:12px;color:#555;margin-top:4px;text-transform:uppercase;
                      letter-spacing:.06em;">{label}</div>
        </td>"""

    # Journal snippets — takeaway or clicked, max 4
    snippets_html = ""
    shown = 0
    for e in reversed(entries):  # oldest first
        snippet = (e.get("takeaway") or e.get("clicked") or "").strip()
        if snippet and shown < 4:
            day = e.get("day_number", "?")
            date = e.get("entry_date", "")
            snippets_html += f"""
        <blockquote style="margin:12px 0;padding:10px 16px;border-left:4px solid #2d6a4f;
                           background:#f4f9f6;color:#333;font-style:italic;border-radius:0 6px 6px 0;">
          <strong style="font-style:normal;color:#2d6a4f;">Day {day}</strong>
          {f'<span style="color:#888;font-size:12px;"> · {date}</span>' if date else ''}
          <br>{snippet}
        </blockquote>"""
            shown += 1

    ai_paragraphs = "".join(
        f'<p style="margin:0 0 14px;line-height:1.7;color:#222;">{p.strip()}</p>'
        for p in ai_report.split("\n\n") if p.strip()
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Weekly Chess Digest</title>
</head>
<body style="margin:0;padding:0;background:#f0f4f0;font-family:'Segoe UI',Arial,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f4f0;padding:32px 16px;">
<tr><td>

  <!-- Card -->
  <table width="600" align="center" cellpadding="0" cellspacing="0"
         style="background:#ffffff;border-radius:12px;overflow:hidden;
                box-shadow:0 4px 24px rgba(0,0,0,.10);max-width:100%;">

    <!-- Header -->
    <tr>
      <td style="background:#1b4332;padding:36px 40px 28px;text-align:center;">
        <div style="font-size:28px;margin-bottom:6px;">♟</div>
        <h1 style="margin:0;color:#d8f3dc;font-size:22px;font-weight:700;letter-spacing:.04em;">
          Weekly Chess Digest
        </h1>
        <p style="margin:8px 0 0;color:#95d5b2;font-size:14px;">{week_label}</p>
      </td>
    </tr>

    <!-- Stat boxes -->
    <tr>
      <td style="padding:28px 40px 8px;">
        <p style="margin:0 0 14px;font-size:13px;color:#888;text-transform:uppercase;
                  letter-spacing:.08em;font-weight:600;">Week at a Glance</p>
        <table width="100%" cellpadding="0" cellspacing="0"
               style="border:1px solid #e8f0eb;border-radius:8px;overflow:hidden;">
          <tr>
            {stat_box("Confidence", conf)}
            {stat_box("Understanding", und)}
            {stat_box("Focus", foc)}
            {stat_box("Momentum", mom)}
          </tr>
        </table>
      </td>
    </tr>

    <!-- AI Report Card -->
    <tr>
      <td style="padding:28px 40px 8px;">
        <p style="margin:0 0 14px;font-size:13px;color:#888;text-transform:uppercase;
                  letter-spacing:.08em;font-weight:600;">Coach Samuel's Report</p>
        <div style="background:#f7faf8;border-radius:8px;padding:20px 24px;
                    border:1px solid #d8f3dc;">
          {ai_paragraphs}
        </div>
      </td>
    </tr>

    <!-- Journal Snippets -->
    {f'''
    <tr>
      <td style="padding:28px 40px 8px;">
        <p style="margin:0 0 14px;font-size:13px;color:#888;text-transform:uppercase;
                  letter-spacing:.08em;font-weight:600;">From the Journal</p>
        {snippets_html}
      </td>
    </tr>''' if snippets_html else ''}

    <!-- Footer -->
    <tr>
      <td style="padding:24px 40px 32px;text-align:center;border-top:1px solid #e8f0eb;margin-top:16px;">
        <p style="margin:0;font-size:12px;color:#aaa;">
          Sent every Sunday · tehochess.github.io/chess-mom
        </p>
      </td>
    </tr>

  </table>

</td></tr>
</table>
</body>
</html>"""

# ── 5. Send via Gmail SMTP ────────────────────────────────────────────────────
def send_email(subject, html_body, recipients):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"Chess Coach <{EMAIL_SENDER}>"
    msg["To"]      = ", ".join(recipients)
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.sendmail(EMAIL_SENDER, recipients, msg.as_string())

    print(f"Email sent → {recipients}")

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    entries = fetch_entries()

    if not entries:
        print("No entries found for the past 7 days. Skipping email.")
        return

    today      = datetime.utcnow()
    week_start = (today - timedelta(days=6)).strftime("%b %-d")
    week_end   = today.strftime("%b %-d, %Y")
    week_label = f"{week_start} – {week_end}"
    subject    = f"♟ Mom's Chess Week · {week_label}"

    print(f"Fetched {len(entries)} entries. Calling Claude...")
    ai_report = call_claude(entries)

    html = build_html(entries, ai_report, week_label)

    recipients = ["he.samuel300@gmail.com", "lihwang@live.com"]
    send_email(subject, html, recipients)
    print("Done.")

if __name__ == "__main__":
    main()
