# 📧 Bulk Email Sender

Send personalized emails to 1000+ people individually using your Gmail account.
Each person gets their own email addressed to them — no CC, no BCC.

---

## ⚠️ Read This Before Anything Else

> **Read all of them before you start.**

- ❌ Your **regular Gmail password will NOT work** — you must generate an App Password (explained below)
- ❌ **2-Step Verification must be ON** in your Google account before you can create an App Password
- ❌ Make sure emails are stored in the `email` column in your CSV — the script looks for it by that exact name
- ❌ Gmail free accounts can send **~500 emails/day max** — do not attempt 1000+ in one go
- ❌ Sending too fast will get your Gmail account **temporarily blocked** — do not remove the delays
- ❌ If your CSV has **blank email cells**, the script skips them automatically — check your log file
- ❌ Placeholders in your template are **case-sensitive** — `{{Name}}` and `{{name}}` are different things

---

## How It Works

```
Your CSV file → script reads each row → fills in the email template
→ logs into your Gmail → sends one individual email per person → logs results
```

No email goes to multiple people at once. Every send is individual.

---

## Requirements

- Python 3.14 or above — check with `python --version` in your terminal
- A Gmail account with 2-Step Verification turned ON
- Internet connection

---

## Step-by-Step Setup

### Step 1 — Clone the repository
```bash
git clone https://github.com/PranavKuppa/Email_Sender.git
cd Email-Sender
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```
If `pip` doesn't work, try `pip3` instead.

### Step 3 — Generate a Gmail App Password

> This is the most important step. Do not skip it.

1. Go to [myaccount.google.com](https://myaccount.google.com)
2. Click **Security** in the left sidebar
3. Under "How you sign in to Google", click **2-Step Verification**
   - If it's OFF, turn it ON first — you cannot proceed without this
4. In the search bar at the top of your Google Account page, search **"App Passwords"**
5. Click on App Passwords
6. Under "App name", type anything (e.g. `Email Sender`) and click **Create**
7. Google will show you a **16-character password** (looks like `abcd efgh ijkl mnop`)
8. **Copy it immediately** — Google will not show it again

### Step 4 — Set up your credentials

```bash
cp .env.example .env
```

Now open `.env` in any text editor and fill in your values:

```
SENDER_EMAIL=your_actual_gmail@gmail.com
SENDER_PASS=abcd efgh ijkl mnop        ← the 16-char App Password, spaces included
```

> ⚠️ The `.env` file is already in `.gitignore`. Never remove it from there.

### Step 5 — Prepare your student CSV


Add your CSV into the folder. Rules:
- The column named **`email`** is mandatory and must be spelled exactly as `email`
- All other columns are up to you — just make sure they match what you put in `placeholders.json`
- Save the file as **CSV format** (not Excel .xlsx) — if editing in Excel, use "Save As → CSV"

Example - 
```csv
name,email,course,exam_date
Rahul Sharma,rahul@gmail.com,Mathematics,2026-06-10
Priya Patel,priya@gmail.com,Physics,2026-06-11
```

### Step 6 — Write your email template

Open `email_template.txt` and write your email. Use `{{placeholder}}` for anything
that changes per person. The placeholder name can be anything you want —
just make sure it matches what you set in `placeholders.json` next.

Example - 
```
Subject: {{subject}}

Hi {{name}},

Your exam for {{course}} is on {{date}}.
Please carry your ID card.

Regards,
Admin Team
```

### Step 7 — Configure placeholders

Open `placeholders.json`. This file tells the script what to replace in your template
and which CSV column to pull the value from.
Add all the placeholders under placeholders in the same format shown.
Example - 
```json
{
    "placeholders": {
        "{{name}}":   "name",
        "{{course}}": "course",
        "{{date}}":   "exam_date"
    },
    "default_subject": "Important Exam Reminder",
    "subject_placeholder": "{{subject}}"
}
```

Left side → what you wrote in the template  
Right side → the exact column name from your CSV

> ⚠️ If the column name in your CSV doesn't match what's written here, that
> placeholder will be left blank in the email.

### Step 8 — Run a dry run first

Before sending any real emails, always run a dry run to preview the output:

```bash
python send_emails.py --dry-run
```

This prints every personalized email to the terminal without sending anything.
Check that names, dates, and all values look correct before the real run.

### Step 9 — Send the real emails

```bash
python send_emails.py
```

You will see live progress in the terminal. A log file is saved in `logs/`
after every run with the status of each email (sent / failed).

---

## Gmail Limits — Important

| Account Type | Daily Limit |
|---|---|
| Free Gmail | ~500 emails/day |
| Google Workspace (paid) | ~2000 emails/day |

If you need to send to 1000+ people:
- Split into two days, **or**
- Use a service like SendGrid (free up to 100/day, paid plans for more)

> Sending too many emails too fast will cause Google to **temporarily lock**
> your account for suspicious activity. The delays in the script exist for
> this exact reason. Do not remove them.

---

## File Guide — What to Edit

| File | Edit it? | Purpose |
|---|---|---|
| `.env` | ✅ Yes | Your Gmail login and settings |
| `email_template.txt` | ✅ Yes | The email content |
| `placeholders.json` | ✅ Yes | Variable → CSV column mapping |
| `students.csv` | ✅ Yes | Your recipient list |
| `send_emails.py` | ❌ Never | Core logic |

---

## Troubleshooting

**"Authentication failed" or "SMTPAuthenticationError"**
→ You used your real Gmail password instead of the App Password.
→ Re-do Step 3 and generate an App Password.

**"App Passwords" option not visible in Google Account**
→ 2-Step Verification is not turned on. Turn it on first, then look again.

**Placeholder showing as `{{name}}` in the email instead of the real name**
→ The column name in your CSV doesn't match what's in `placeholders.json`.
→ They must match exactly, including capitalisation.

**Some emails show "failed" in the log**
→ Open the log file in `logs/` — the error column will tell you why.
→ Common cause: invalid email address format in your CSV.

**Script stops midway**
→ Check the log — whatever was sent before the stop is recorded.
→ Remove already-sent emails from your CSV and run again.

**"pip not found" or "python not found"**
→ Python is not installed. Download it from [python.org](https://python.org).
→ During installation on Windows, check **"Add Python to PATH"**.

---

## Common Mistakes Checklist

Before every run, verify:

- [ ] `.env` has my real Gmail and App Password filled in
- [ ] `students.csv` has an `email` column spelled exactly as `email`
- [ ] No blank rows or missing emails in my CSV
- [ ] Placeholder names in template match keys in `placeholders.json`
- [ ] Column names in `placeholders.json` match headers in `students.csv`
- [ ] I did a `--dry-run` and the output looks correct
- [ ] I am not trying to send more than 500 emails in one day (free Gmail)

---

## Privacy Warning

Your `.csv` contains real email addresses.
- It is already in `.gitignore` — **do not remove it from there**
- Never share or upload your `.csv` anywhere
- The `logs/` folder also contains email addresses — keep it local only