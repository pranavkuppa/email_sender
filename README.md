# 📧 Bulk Email Sender

Send personalized emails to 1000+ students individually using Gmail.

## Setup

### 1. Clone the repo
    Open VS code and run the following commands in terminal
    
    git clone https://github.com/PranavKuppa/Email_Sender.git
    cd Email-Sender
### 2. Install dependencies
    pip install -r requirements.txt
### 3. Set up Gmail App Password
    - Go to myaccount.google.com
    - Security → 2-Step Verification (must be ON)
    - Search "App Passwords" → create one → copy the 16-char password
### 4. Configure your credentials
    cp .env.example .env
    # Now open .env and fill in your Gmail and App Password
### 5. Add your student data
    Add your excel sheet into the folder
### 6. Edit your email
    # Edit email_template.txt with your message
    # Edit placeholders.json to map {{variables}} to CSV columns
### 7. Run
    python send_emails.py
## File Guide

| File | What to edit |
|---|---|
| `.env` | Your Gmail credentials |
| `email_template.txt` | The email content |
| `placeholders.json` | Variable → CSV column mapping |
| `students.csv` | Student name and email list |