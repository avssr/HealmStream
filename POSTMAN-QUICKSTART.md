# Postman Quick Start - Crisis Agent

## 🚀 3-Minute Setup

### Step 1: Get Your API Key (30 seconds)

```bash
cd /Users/arp2247/Desktop/aws-bedrock-challenge/HelmStream
grep "API_KEY_VALUE" .env
```

Copy the key that appears!

---

### Step 2: Configure Postman (1 minute)

1. **Open Postman** → New Request
2. **Set Method:** `POST`
3. **Set URL:**
   ```
   https://l89algnkzd.execute-api.us-east-1.amazonaws.com/prod/crisis-agent
   ```

4. **Add Headers** (click Headers tab):
   ```
   Content-Type: application/json
   x-api-key: <PASTE_YOUR_KEY_HERE>
   ```

5. **Add Body** (click Body → raw → JSON):
   ```json
   {
     "crisis_description": "MV Baltic Trader propeller shaft failure requiring immediate attention",
     "vessel_name": "MV Baltic Trader",
     "action": "analyze"
   }
   ```

---

### Step 3: Send Request (1 minute)

1. Click **Send** button
2. Wait 10-20 seconds (AI is thinking!)
3. View response in "Pretty" tab

---

## ✅ What You Should See

```json
{
  "status": "pending",
  "recommended_option": {
    "title": "Emergency Repair",
    "duration_days": 7,
    "risk_level": "medium"
  },
  "options": [3 options],
  "stakeholder_emails": [3 emails],
  "suggested_actions": [6 actions],
  "messages": [
    "Analysis complete...",
    "Generated 3 options...",
    "Drafted 3 emails...",
    "Awaiting human approval"
  ]
}
```

---

## 🎯 What Triggers the Agent?

The **`action`** field in your JSON body:

| Value | What Happens |
|-------|--------------|
| `"analyze"` | 🤖 Agent analyzes crisis, generates options, drafts emails |
| `"approve"` | ✅ Agent executes the plan (sends emails, updates schedule) |
| `"reject"` | ❌ Agent cancels the plan |

---

## 🧪 Try These Scenarios

### Scenario 1: Propeller Failure ⭐ BEST FOR DEMO
```json
{
  "crisis_description": "MV Baltic Trader propeller shaft failure requiring immediate attention",
  "vessel_name": "MV Baltic Trader",
  "action": "analyze"
}
```

### Scenario 2: Engine Breakdown
```json
{
  "crisis_description": "MV Pacific Star main engine breakdown during port entry. Tugboat assistance required.",
  "vessel_name": "MV Pacific Star",
  "action": "analyze"
}
```

### Scenario 3: Hull Damage
```json
{
  "crisis_description": "MV Coastal Navigator hull damage after collision. Immediate dry docking required.",
  "vessel_name": "MV Coastal Navigator",
  "action": "analyze"
}
```

### Scenario 4: Approve Plan (after analyzing)
```json
{
  "crisis_description": "MV Baltic Trader propeller shaft failure requiring immediate attention",
  "vessel_name": "MV Baltic Trader",
  "action": "approve"
}
```

---

## 📧 View the Drafted Emails

In the response, look for `stakeholder_emails`:

```json
"stakeholder_emails": [
  {
    "recipient_role": "Operations Manager",
    "email_content": "Subject: URGENT: Crisis Response...\n\nDear Operations Team..."
  },
  {
    "recipient_role": "Dock Scheduler",
    "email_content": "..."
  },
  {
    "recipient_role": "Technical Lead",
    "email_content": "..."
  }
]
```

---

## 🎯 View the Suggested Actions

In the response, look for `suggested_actions`:

```json
"suggested_actions": [
  {
    "action": "send_email",
    "description": "Send crisis response email to Operations Manager",
    "recipient": "Operations Manager"
  },
  {
    "action": "update_schedule",
    "description": "Allocate dock for MV Baltic Trader - Emergency Repair",
    "duration_days": 7
  },
  {
    "action": "log_decision",
    "description": "Log crisis resolution decision in system"
  },
  {
    "action": "notify_team",
    "description": "Alert shipyard team of emergency response plan",
    "priority": "high"
  }
]
```

---

## ❌ Common Errors

### Error: "Forbidden"
**Problem:** Missing API key
**Fix:** Add `x-api-key` header

### Error: "Invalid JSON"
**Problem:** Typo in JSON body
**Fix:** Use Postman's JSON validator (bottom of body)

### Taking too long (>30s)
**Normal!** Claude 3 Sonnet takes 10-20 seconds to analyze

---

## 💡 Pro Tips for Hackathon Demo

1. **Save your request** in Postman before presenting
2. **Use "Scenario 1"** for best results
3. **Switch to "Pretty" view** for cleaner JSON
4. **Zoom in** so audience can read the response
5. **Point out:**
   - Status: "pending" (human-in-the-loop)
   - 3 options generated
   - 3 emails drafted
   - 6 actions suggested

---

## 📱 Screenshot Your Setup

Your Postman should look like this:

```
┌─────────────────────────────────────────────┐
│ POST https://l89algnkzd.execute-api...      │
├─────────────────────────────────────────────┤
│ Headers                                     │
│   Content-Type: application/json            │
│   x-api-key: <YOUR_KEY>                     │
├─────────────────────────────────────────────┤
│ Body (raw/JSON)                             │
│   {                                         │
│     "crisis_description": "MV Baltic...",   │
│     "vessel_name": "MV Baltic Trader",      │
│     "action": "analyze"                     │
│   }                                         │
└─────────────────────────────────────────────┘
```

---

## 🔗 Full Documentation

For complete details, see:
- `POSTMAN-GUIDE.md` - Full testing guide
- `HACKATHON-DEMO.md` - Demo script
- `QUICK-REFERENCE.md` - API reference

---

*Ready to impress the judges! 🚀*
