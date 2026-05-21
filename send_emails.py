import smtplib
import pandas as pd
import json
import logging
import time
import os
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

# ─── LOAD ENVIRONMENT VARIABLES ───────────────────────────
load_dotenv()

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASS = os.getenv("SENDER_PASS")

CSV_FILE = os.getenv("CSV_FILE")
TEMPLATE_FILE = os.getenv("TEMPLATE_FILE", "email_template.txt")
PLACEHOLDER_FILE = os.getenv("PLACEHOLDER_FILE", "placeholders.json")

EMAIL_SUBJECT = os.getenv("EMAIL_SUBJECT", "No Subject")

DELAY_BETWEEN_EMAILS = float(os.getenv("DELAY_BETWEEN_EMAILS", 1.5))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 50))
BATCH_PAUSE = int(os.getenv("BATCH_PAUSE", 10))

LOG_DIR = "logs"
LOG_FILE = os.path.join(
    LOG_DIR,
    f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
)
# ──────────────────────────────────────────────────────────

# ─── LOGGING SETUP ────────────────────────────────────────
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)
# ──────────────────────────────────────────────────────────


def validate_env():
    """Check that critical environment variables are set before doing anything."""
    errors = []
    if not SENDER_EMAIL:
        errors.append("SENDER_EMAIL is not set in your .env file")
    if not SENDER_PASS:
        errors.append("SENDER_PASS is not set in your .env file")
    if errors:
        for e in errors:
            logging.error(f"Config error: {e}")
        raise SystemExit(
            "Fix the above errors in your .env file and try again.")


def load_template():
    """Read the email template file."""
    if not os.path.exists(TEMPLATE_FILE):
        raise FileNotFoundError(
            f"Template file '{TEMPLATE_FILE}' not found. "
            f"Check TEMPLATE_FILE in your .env file."
        )
    with open(TEMPLATE_FILE, "r") as f:
        content = f.read()
    if not content.strip():
        raise ValueError(f"Template file '{TEMPLATE_FILE}' is empty.")
    return content


def load_placeholders():
    """Read the placeholders config JSON file."""
    if not os.path.exists(PLACEHOLDER_FILE):
        raise FileNotFoundError(
            f"Placeholder file '{PLACEHOLDER_FILE}' not found. "
            f"Check PLACEHOLDER_FILE in your .env file."
        )
    with open(PLACEHOLDER_FILE, "r") as f:
        config = json.load(f)
    if "placeholders" not in config:
        raise KeyError("'placeholders' key missing from placeholders.json")
    return config


def load_students():
    """Read and validate the CSV file using pandas."""
    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(
            f"CSV file '{CSV_FILE}' not found. "
            f"Copy students.example.csv → students.csv and fill your data."
        )

    df = pd.read_csv(CSV_FILE)

    # Check that the email column exists
    if "email" not in df.columns:
        raise KeyError(
            "Your CSV must have a column named exactly 'email' (lowercase). "
            f"Columns found: {list(df.columns)}"
        )

    original_count = len(df)

    # Drop rows with no email
    df.dropna(subset=["email"], inplace=True)

    # Drop duplicate emails
    df.drop_duplicates(subset=["email"], inplace=True)

    dropped = original_count - len(df)
    if dropped > 0:
        logging.warning(
            f"{dropped} rows removed (blank or duplicate emails). "
            f"{len(df)} valid recipients remaining."
        )

    if len(df) == 0:
        raise ValueError(
            "No valid recipients found in your CSV after cleanup.")

    return df


def build_email(template, row, config):
    body = template

    for placeholder, col_name in config["placeholders"].items():
        if col_name in row and pd.notna(row[col_name]):
            value = str(row[col_name])
        else:
            value = ""
            logging.warning(
                f"Placeholder '{placeholder}' → column '{col_name}' "
                f"not found or empty for {row.get('email', 'unknown')}."
            )
        body = body.replace(placeholder, value)

    return body


def send_email(smtp, to_email, subject, body):
    """Send a single email via the open SMTP connection."""
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    smtp.sendmail(SENDER_EMAIL, to_email, msg.as_string())


def main(dry_run=False):
    # Step 1 — validate config
    if not dry_run:
        validate_env()

    # Step 2 — load all files
    logging.info("Loading template, placeholders and student data...")
    template = load_template()
    config = load_placeholders()
    students = load_students()

    logging.info(f"Loaded {len(students)} valid recipients from '{CSV_FILE}'")

    if dry_run:
        print("\n" + "=" * 60)
        print("  DRY RUN MODE — no emails will be sent")
        print("=" * 60 + "\n")

    results = []

    # Step 3 — connect to Gmail (only for real runs)
    smtp = None
    if not dry_run:
        try:
            logging.info("Connecting to Gmail SMTP...")
            smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            smtp.ehlo()
            smtp.starttls()
            smtp.login(SENDER_EMAIL, SENDER_PASS)
            logging.info("Logged into Gmail SMTP ✓")
        except smtplib.SMTPAuthenticationError:
            raise SystemExit(
                "\nAuthentication failed. Make sure:\n"
                "  1. SENDER_EMAIL and SENDER_PASS are correct in .env\n"
                "  2. SENDER_PASS is your App Password (not your Gmail password)\n"
                "  3. 2-Step Verification is ON in your Google account\n"
            )

    # Step 4 — loop through students
    for i, (_, row) in enumerate(students.iterrows()):
        to_email = str(row["email"]).strip()

        try:
            body = build_email(template, row, config)

            if dry_run:
                print(f"--- Email {i + 1} of {len(students)} ---")
                print(f"TO:      {to_email}")
                print(f"SUBJECT: {EMAIL_SUBJECT}")
                print(f"BODY:\n{body}")
                print()

            else:
                send_email(smtp, to_email, EMAIL_SUBJECT, body)
                results.append({
                    "email":  to_email,
                    "status": "sent",
                    "error":  ""
                })
                logging.info(f"[{i + 1}/{len(students)}] Sent → {to_email}")

                time.sleep(DELAY_BETWEEN_EMAILS)

                # Batch pause every N emails
                if (i + 1) % BATCH_SIZE == 0:
                    logging.info(
                        f"Batch of {BATCH_SIZE} sent. "
                        f"Pausing {BATCH_PAUSE}s to avoid Gmail rate limits..."
                    )
                    time.sleep(BATCH_PAUSE)

        except Exception as e:
            results.append({
                "email":  to_email,
                "status": "failed",
                "error":  str(e)
            })
            logging.error(
                f"[{i + 1}/{len(students)}] FAILED → {to_email} | {e}")

    # Step 5 — wrap up
    if not dry_run:
        if smtp:
            smtp.quit()

        results_df = pd.DataFrame(results)
        results_df.to_csv(LOG_FILE, index=False)

        sent = len(results_df[results_df["status"] == "sent"])
        failed = len(results_df[results_df["status"] == "failed"])

        print("\n" + "=" * 60)
        print(f"  ✅ Sent:   {sent}")
        print(f"  ❌ Failed: {failed}")
        print(f"  📄 Log:    {LOG_FILE}")
        print("=" * 60 + "\n")

        if failed > 0:
            logging.warning(
                f"{failed} emails failed. Check '{LOG_FILE}' "
                f"for error details. Fix and re-run with just the failed rows."
            )
    else:
        print("=" * 60)
        print(f"  Dry run complete — {len(students)} emails previewed.")
        print("  Nothing was sent. Run without --dry-run to send for real.")
        print("=" * 60 + "\n")


# ─── ENTRY POINT ──────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Bulk personalized email sender using Gmail SMTP."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview all emails in the terminal without sending anything."
    )
    args = parser.parse_args()
    main(dry_run=args.dry_run)
