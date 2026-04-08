// ============================================================
// CONFIG — Fill these in before running anything
// ============================================================
const CONFIG = {
  SENDER_EMAILS: [
    'email1@youremail.com',   // Add as many as you want
    'email2@youremail.com',   // <-- replace with real emails
  ],
  FOLDER_ID:          'YOUR_FOLDER_ID',
  CLAUDE_API_KEY:     'YOUR_CLAUDE_API_KEY',
  NOTIFY_EMAIL:       'yournotifyemail@gmail.com',
  TELEGRAM_BOT_TOKEN: '---',
  TELEGRAM_CHAT_ID:   '',
  TRIGGER_HOUR:       12,
};

// ============================================================
// MAIN — Loops through each sender and creates a separate doc
// ============================================================
function runDailySummary() {
  const results = [];

  CONFIG.SENDER_EMAILS.forEach(function(sender) {
    const emails = fetchEmails(sender);

    if (emails.length === 0) {
      Logger.log('No emails found from ' + sender + ' today. Skipping.');
      return;
    }

    Logger.log('Found ' + emails.length + ' email(s) from ' + sender + '. Summarizing...');

    const content = buildContentString(emails);
    const summary = summarizeWithClaude(content, sender);
    const docUrl  = createGoogleDoc(summary, emails.length, sender);

    results.push({ sender: sender, count: emails.length, url: docUrl });
    Logger.log('Done for ' + sender + '. Doc: ' + docUrl);
  });

  if (results.length > 0) {
    notifyUser(results);
  } else {
    Logger.log('No emails found from any sender today.');
  }
}

// ============================================================
// GMAIL — Search emails from a sender in the last 24 hours
// ============================================================
function fetchEmails(sender) {
  const since   = new Date();
  since.setDate(since.getDate() - 1);
  const dateStr = Utilities.formatDate(since, Session.getScriptTimeZone(), 'yyyy/MM/dd');

  const query   = 'from:' + sender + ' after:' + dateStr;
  const threads = GmailApp.search(query);
  const emails  = [];

  threads.forEach(function(thread) {
    thread.getMessages().forEach(function(msg) {
      emails.push({
        subject: msg.getSubject(),
        body:    msg.getPlainBody().substring(0, 4000),
        date:    Utilities.formatDate(msg.getDate(), Session.getScriptTimeZone(), 'yyyy-MM-dd HH:mm'),
      });
    });
  });

  return emails;
}

function buildContentString(emails) {
  return emails.map(function(e, i) {
    return '--- Email ' + (i + 1) + ' ---\nSubject: ' + e.subject + '\nDate: ' + e.date + '\n\n' + e.body;
  }).join('\n\n');
}

// ============================================================
// CLAUDE API — Summarize the email content
// ============================================================
function summarizeWithClaude(content, sender) {
  const response = UrlFetchApp.fetch('https://api.anthropic.com/v1/messages', {
    method:      'post',
    contentType: 'application/json',
    headers: {
      'x-api-key':         CONFIG.CLAUDE_API_KEY,
      'anthropic-version': '2023-06-01',
    },
    payload: JSON.stringify({
      model:      'claude-haiku-4-5-20251001',
      max_tokens: 1024,
      messages: [{
        role:    'user',
        content: 'Summarize the following email(s) from ' + sender + '. Include:\n- Key points\n- Action items (if any)\n- Important dates or deadlines\n\n' + content,
      }],
    }),
    muteHttpExceptions: true,
  });

  const result = JSON.parse(response.getContentText());

  if (result.error) {
    throw new Error('Claude API error: ' + result.error.message);
  }

  return result.content[0].text;
}

// ============================================================
// GOOGLE DOCS — Create a separate doc per sender
// ============================================================
function createGoogleDoc(summary, emailCount, sender) {
  const today      = new Date();
  const dateStr    = Utilities.formatDate(today, Session.getScriptTimeZone(), 'yyyy-MM-dd');
  const senderName = sender.split('@')[0];
  const docTitle   = 'Email Summary - ' + senderName + ' - ' + dateStr;

  const doc  = DocumentApp.create(docTitle);
  const body = doc.getBody();

  body.appendParagraph(docTitle).setHeading(DocumentApp.ParagraphHeading.HEADING1);
  body.appendParagraph('Sender: '       + sender);
  body.appendParagraph('Date: '         + dateStr);
  body.appendParagraph('Emails found: ' + emailCount);
  body.appendParagraph('');
  body.appendParagraph('Summary').setHeading(DocumentApp.ParagraphHeading.HEADING2);
  body.appendParagraph(summary);

  doc.saveAndClose();

  const file   = DriveApp.getFileById(doc.getId());
  const folder = DriveApp.getFolderById(CONFIG.FOLDER_ID);
  folder.addFile(file);
  DriveApp.getRootFolder().removeFile(file);

  return doc.getUrl();
}

// ============================================================
// NOTIFICATIONS — One combined email/Telegram for all senders
// ============================================================
function notifyUser(results) {
  const today = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy-MM-dd');
  const subject = 'Email Summaries Ready - ' + today;

  let body = 'Your daily email summaries are ready.\n\n';
  results.forEach(function(r) {
    body += 'Sender: ' + r.sender + '\n';
    body += 'Emails: ' + r.count  + '\n';
    body += 'Doc: '    + r.url    + '\n\n';
  });

  GmailApp.sendEmail(CONFIG.NOTIFY_EMAIL, subject, body);

  if (CONFIG.TELEGRAM_BOT_TOKEN && CONFIG.TELEGRAM_CHAT_ID) {
    let text = 'Email Summaries Ready - ' + today + '\n\n';
    results.forEach(function(r) {
      text += 'Sender: ' + r.sender + '\n' + r.url + '\n\n';
    });

    UrlFetchApp.fetch(
      'https://api.telegram.org/bot' + CONFIG.TELEGRAM_BOT_TOKEN + '/sendMessage',
      {
        method:      'post',
        contentType: 'application/json',
        payload: JSON.stringify({ chat_id: CONFIG.TELEGRAM_CHAT_ID, text: text }),
        muteHttpExceptions: true,
      }
    );
  }
}

// ============================================================
// TRIGGER SETUP — Run this ONE TIME to schedule daily runs
// ============================================================
function setupDailyTrigger() {
  ScriptApp.getProjectTriggers().forEach(function(t) {
    if (t.getHandlerFunction() === 'runDailySummary') {
      ScriptApp.deleteTrigger(t);
    }
  });

  ScriptApp.newTrigger('runDailySummary')
    .timeBased()
    .everyDays(1)
    .atHour(CONFIG.TRIGGER_HOUR)
    .create();

  Logger.log('Daily trigger set for ' + CONFIG.TRIGGER_HOUR + ':00.');
}
