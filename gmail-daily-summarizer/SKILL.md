---
name: gmail-daily-summarizer
description: Summarizes daily emails from specific senders using Claude AI and saves them as Google Docs in Google Drive. Built on Google Apps Script — no server required.
---

# Gmail Daily Summarizer

This skill helps you set up an automated daily email summarizer using Google Apps Script and Claude AI. It monitors emails from specific senders, summarizes them with Claude, and saves each summary as a Google Doc.

## What it does

- Monitors Gmail for emails from one or more senders (last 24 hours)
- Summarizes email content using Claude AI (Haiku model)
- Creates a separate Google Doc per sender
- Saves docs to a specified Google Drive folder
- Sends a notification email (and optionally Telegram) with links to summaries
- Runs automatically every day at a scheduled time

## Requirements

- A Google account (Gmail + Google Drive + Google Docs)
- A Claude API key from [console.anthropic.com](https://console.anthropic.com)
- Access to [Google Apps Script](https://script.google.com) (free)

## Setup Instructions

### 1. Open Google Apps Script
Go to [script.google.com](https://script.google.com) and create a new project. Name it `Gmail Daily Summarizer`.

### 2. Paste the script
Copy the full code from `scripts/email_summary_bot.gs` and paste it into the script editor, replacing any existing code.

### 3. Fill in the CONFIG values

```javascript
const CONFIG = {
  SENDER_EMAILS: [
    'email1@youremail.com',   // Emails to monitor — add as many as you want
    'email2@youremail.com',
  ],
  FOLDER_ID:          'YOUR_FOLDER_ID',       // From your Google Drive folder URL
  CLAUDE_API_KEY:     'YOUR_CLAUDE_API_KEY',  // From console.anthropic.com → API Keys
  NOTIFY_EMAIL:       'yournotifyemail@gmail.com',
  TELEGRAM_BOT_TOKEN: '',                     // Optional — leave empty to skip
  TELEGRAM_CHAT_ID:   '',                     // Optional — leave empty to skip
  TRIGGER_HOUR:       12,                     // Hour to run daily (24-hour format)
};
```

**Getting your FOLDER_ID:**
Open your Google Drive folder → copy the ID from the URL:
`drive.google.com/drive/folders/`**THIS_PART**

### 4. Set up the daily trigger
In the script editor, select `setupDailyTrigger` from the function dropdown and click **Run**. Do this only once.

### 5. Grant permissions
Google will ask you to allow access to Gmail, Drive, Docs, and external URLs. Accept all permissions.

### 6. Test it manually
Select `runDailySummary` from the dropdown and click **Run**. Check **View → Logs** to confirm it works.

## Output

Each run creates Google Docs named:
```
Email Summary - sendername - YYYY-MM-DD
```

All docs are saved to your specified Google Drive folder.

## Adding more senders

Add email addresses to the `SENDER_EMAILS` array — the script will create a separate doc for each one:

```javascript
SENDER_EMAILS: [
  'newsletter@example.com',
  'updates@another.com',
  'digest@service.com',
],
```

## Source

Full script and documentation: [github.com/xnomad-dev/gmail-to-docs-summarizer](https://github.com/xnomad-dev/gmail-to-docs-summarizer)
