# Monthly Affiliate Payment Reminder

On the first day of each month, calculate what I owe each affiliate for the
previous month and email me a payment checklist.

Recipient: the single address configured in `EMAIL_SKILL_ALLOWED_RECIPIENTS`.

Include affiliate name, revenue, commission rate, amount owed, payment method
if known, and any missing or suspicious data. Put the total amount owed at the
top.

Send the final email by running:

```bash
cd /absolute/path/to/email-skill/skill
python3 email_skill/send_email.py /absolute/path/to/email_payload.json
```

Create `email_payload.json`:

```json
{
  "subject": "Monthly affiliate payment reminder",
  "body": "<the payment checklist>",
  "confirmed": true
}
```
