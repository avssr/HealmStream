# Testing Crisis Agent in Postman

## Quick Setup

### 1. Import to Postman

**Method A: Manual Setup**

1. Open Postman
2. Create new request
3. Name it: "HelmStream - Crisis Agent"

**Method B: Import Collection** (see JSON at bottom)

---

## API Configuration

### Base URL
```
https://l89algnkzd.execute-api.us-east-1.amazonaws.com/prod
```

### Endpoint
```
POST /crisis-agent
```

### Full URL
```
https://l89algnkzd.execute-api.us-east-1.amazonaws.com/prod/crisis-agent
```

---

## Headers Setup

Add these headers in Postman:

| Key | Value |
|-----|-------|
| `Content-Type` | `application/json` |
| `x-api-key` | `<YOUR_API_KEY>` |

**To get your API key:**
```bash
cd /Users/arp2247/Desktop/aws-bedrock-challenge/HelmStream
grep "API_KEY_VALUE" .env
```

**In Postman:**
1. Go to "Headers" tab
2. Click "Add" or type in the key-value pairs
3. Make sure both headers are checked ✓

---

## What Triggers the Agent?

The agent is triggered by a **POST request** with a JSON body containing:

### Required Fields
- `crisis_description`: What happened (string)
- `vessel_name`: Which vessel is affected (string)
- `action`: What to do (string: "analyze", "approve", or "reject")

### Agent Actions

| Action | What It Does |
|--------|--------------|
| `"analyze"` | **Triggers full workflow**: Analyzes crisis, generates options, recommends solution, drafts emails |
| `"approve"` | **Executes the plan**: Sends emails, updates schedule, logs decision |
| `"reject"` | **Cancels the plan**: Marks as rejected, no actions taken |

---

## Test Scenarios

### Scenario 1: Propeller Failure (Recommended)

**Request Body:**
```json
{
  "crisis_description": "MV Baltic Trader propeller shaft failure requiring immediate attention",
  "vessel_name": "MV Baltic Trader",
  "action": "analyze"
}
```

**Expected Response:**
- Status: `pending`
- Options: 3 generated
- Recommendation: Emergency repair solution
- Emails: 3 drafted
- Suggested Actions: 6 actions

---

### Scenario 2: Engine Breakdown

**Request Body:**
```json
{
  "crisis_description": "MV Pacific Star main engine breakdown during port entry. Tugboat assistance required and emergency repair needed.",
  "vessel_name": "MV Pacific Star",
  "action": "analyze"
}
```

**Expected Response:**
- Status: `pending`
- Different options based on engine repair
- Emails drafted for stakeholders
- Actions suggested

---

### Scenario 3: Hull Damage

**Request Body:**
```json
{
  "crisis_description": "MV Coastal Navigator has sustained hull damage after collision with dock. Immediate dry docking required for inspection and repair.",
  "vessel_name": "MV Coastal Navigator",
  "action": "analyze"
}
```

**Expected Response:**
- Status: `pending`
- Options including dry dock allocation
- Communications drafted

---

### Scenario 4: Approve the Plan

First run a crisis analysis (Scenario 1-3), then:

**Request Body:**
```json
{
  "crisis_description": "MV Baltic Trader propeller shaft failure requiring immediate attention",
  "vessel_name": "MV Baltic Trader",
  "action": "approve"
}
```

**Expected Response:**
- Status: `approved`
- Actions Taken: Shows executed actions (emails sent, schedule updated, etc.)

---

### Scenario 5: Reject the Plan

**Request Body:**
```json
{
  "crisis_description": "MV Baltic Trader propeller shaft failure requiring immediate attention",
  "vessel_name": "MV Baltic Trader",
  "action": "reject"
}
```

**Expected Response:**
- Status: `rejected`
- Messages: "Plan rejected by human operator"

---

## Step-by-Step Postman Instructions

### Setup (One Time)

1. **Open Postman**
2. **Create New Request**
   - Click "New" → "HTTP Request"
   - Or click the "+" tab

3. **Configure Request**
   - Method: `POST`
   - URL: `https://l89algnkzd.execute-api.us-east-1.amazonaws.com/prod/crisis-agent`

4. **Add Headers**
   - Click "Headers" tab
   - Add: `Content-Type` = `application/json`
   - Add: `x-api-key` = `<YOUR_API_KEY>` (get from .env file)

5. **Add Body**
   - Click "Body" tab
   - Select "raw"
   - Select "JSON" from dropdown
   - Paste one of the scenario JSON examples

6. **Save Request**
   - Click "Save"
   - Name: "Crisis Agent - Propeller Failure"
   - Create Collection: "HelmStream API"

### Running Tests

1. **Test Analysis**
   - Use Scenario 1 body with `"action": "analyze"`
   - Click "Send"
   - Review response

2. **View Response**
   - Check "Pretty" view for formatted JSON
   - Look for:
     - `status`: "pending"
     - `options`: Array of 3 options
     - `recommended_option`: The AI's choice
     - `stakeholder_emails`: 3 drafted emails
     - `suggested_actions`: 6 planned actions

3. **Test Approval**
   - Change body to `"action": "approve"`
   - Click "Send"
   - Check `actions_taken` in response

---

## Response Structure

### Success Response (200)

```json
{
  "crisis": "MV Baltic Trader propeller shaft failure...",
  "vessel": "MV Baltic Trader",
  "status": "pending",
  "recommended_option": {
    "option_number": 1,
    "title": "Emergency Repair",
    "description": "Immediate dry dock for propeller replacement",
    "duration_days": 7,
    "risk_level": "medium",
    "pros": ["Fast turnaround", "Reliable solution"],
    "cons": ["High cost", "Dock availability"],
    "cost_analysis": {
      "total": 70000,
      "cost_per_day": 10000,
      "duration_days": 7
    }
  },
  "justification": "Emergency repair provides the best balance...",
  "options": [
    { "option_number": 1, "title": "Emergency Repair", ... },
    { "option_number": 2, "title": "Temporary Fix", ... },
    { "option_number": 3, "title": "Complete Overhaul", ... }
  ],
  "stakeholder_emails": [
    {
      "recipient_role": "Operations Manager",
      "email_content": "Subject: URGENT: Crisis Response...\n\nDear Operations Team..."
    },
    {
      "recipient_role": "Dock Scheduler",
      "email_content": "Subject: Emergency Dock Allocation..."
    },
    {
      "recipient_role": "Technical Lead",
      "email_content": "Subject: Emergency Repair Assessment..."
    }
  ],
  "suggested_actions": [
    {
      "action": "send_email",
      "description": "Send crisis response email to Operations Manager",
      "recipient": "Operations Manager"
    },
    {
      "action": "send_email",
      "description": "Send crisis response email to Dock Scheduler",
      "recipient": "Dock Scheduler"
    },
    {
      "action": "send_email",
      "description": "Send crisis response email to Technical Lead",
      "recipient": "Technical Lead"
    },
    {
      "action": "update_schedule",
      "description": "Allocate dock for MV Baltic Trader - Emergency Repair",
      "duration_days": 7
    },
    {
      "action": "log_decision",
      "description": "Log crisis resolution decision in system",
      "option_selected": 1
    },
    {
      "action": "notify_team",
      "description": "Alert shipyard team of emergency response plan",
      "priority": "high"
    }
  ],
  "actions_taken": [],
  "messages": [
    "Analysis complete. RAG context retrieved.",
    "Generated 3 options with cost analysis",
    "Recommended Option 1: Emergency Repair",
    "Drafted 3 stakeholder communications",
    "Prepared 6 actions for approval",
    "Agent workflow paused. Awaiting human approval."
  ],
  "dock_status": {
    "dock_1": {
      "status": "available",
      "current_vessel": null,
      "next_available": "now"
    },
    "dock_2": {
      "status": "available",
      "current_vessel": null,
      "next_available": "now"
    }
  }
}
```

### Error Response (403 - No API Key)

```json
{
  "message": "Forbidden"
}
```

**Fix:** Add `x-api-key` header

### Error Response (500 - Internal Error)

```json
{
  "error": "Error message here",
  "traceback": "..."
}
```

---

## Testing Checklist

### ✅ Pre-Test
- [ ] API key added to headers
- [ ] Content-Type set to application/json
- [ ] Body is valid JSON
- [ ] URL is correct

### ✅ Test Flow
1. [ ] Send "analyze" request → Status: pending
2. [ ] Review 3 options generated
3. [ ] Check recommended option
4. [ ] View 3 drafted emails
5. [ ] See 6 suggested actions
6. [ ] Send "approve" request → Status: approved
7. [ ] Check actions_taken is populated

### ✅ Expected Behavior
- [ ] Response time: 10-20 seconds
- [ ] Status code: 200
- [ ] Options: Always 3
- [ ] Emails: Always 3
- [ ] Suggested actions: Always 6
- [ ] Human-in-the-loop: Status pending until approved

---

## Postman Environment Setup (Optional)

For easier testing, create a Postman Environment:

1. **Click "Environments"** (left sidebar)
2. **Create New Environment**
   - Name: "HelmStream Production"
3. **Add Variables:**

| Variable | Initial Value | Current Value |
|----------|---------------|---------------|
| `base_url` | `https://l89algnkzd.execute-api.us-east-1.amazonaws.com/prod` | Same |
| `api_key` | `<YOUR_API_KEY>` | Same |

4. **Use in Request:**
   - URL: `{{base_url}}/crisis-agent`
   - Header: `x-api-key: {{api_key}}`

---

## Postman Collection JSON

Import this into Postman (File → Import → Paste JSON):

```json
{
  "info": {
    "name": "HelmStream Crisis Agent",
    "description": "Test the Crisis Response Agent",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Analyze Crisis - Propeller Failure",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          },
          {
            "key": "x-api-key",
            "value": "<YOUR_API_KEY>",
            "description": "Get from .env file"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"crisis_description\": \"MV Baltic Trader propeller shaft failure requiring immediate attention\",\n  \"vessel_name\": \"MV Baltic Trader\",\n  \"action\": \"analyze\"\n}"
        },
        "url": {
          "raw": "https://l89algnkzd.execute-api.us-east-1.amazonaws.com/prod/crisis-agent",
          "protocol": "https",
          "host": ["l89algnkzd", "execute-api", "us-east-1", "amazonaws", "com"],
          "path": ["prod", "crisis-agent"]
        }
      }
    },
    {
      "name": "Approve Crisis Plan",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          },
          {
            "key": "x-api-key",
            "value": "<YOUR_API_KEY>"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"crisis_description\": \"MV Baltic Trader propeller shaft failure requiring immediate attention\",\n  \"vessel_name\": \"MV Baltic Trader\",\n  \"action\": \"approve\"\n}"
        },
        "url": {
          "raw": "https://l89algnkzd.execute-api.us-east-1.amazonaws.com/prod/crisis-agent",
          "protocol": "https",
          "host": ["l89algnkzd", "execute-api", "us-east-1", "amazonaws", "com"],
          "path": ["prod", "crisis-agent"]
        }
      }
    },
    {
      "name": "Analyze Crisis - Engine Breakdown",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          },
          {
            "key": "x-api-key",
            "value": "<YOUR_API_KEY>"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"crisis_description\": \"MV Pacific Star main engine breakdown during port entry. Tugboat assistance required and emergency repair needed.\",\n  \"vessel_name\": \"MV Pacific Star\",\n  \"action\": \"analyze\"\n}"
        },
        "url": {
          "raw": "https://l89algnkzd.execute-api.us-east-1.amazonaws.com/prod/crisis-agent",
          "protocol": "https",
          "host": ["l89algnkzd", "execute-api", "us-east-1", "amazonaws", "com"],
          "path": ["prod", "crisis-agent"]
        }
      }
    }
  ]
}
```

---

## Troubleshooting

### "Forbidden" Error
**Cause:** Missing or invalid API key
**Fix:** Check `x-api-key` header is set correctly

### "Internal Server Error"
**Cause:** Invalid JSON or Lambda error
**Fix:** Validate JSON syntax, check CloudWatch logs

### Slow Response (>30 seconds)
**Normal:** Agent uses Claude 3 Sonnet which takes 10-20 seconds
**If timeout:** Check Lambda timeout setting (should be 60s)

### Empty `suggested_actions`
**Cause:** Old Lambda code
**Fix:** Redeploy with updated code (already done)

---

## Demo Tips for Hackathon

1. **Pre-load the request** in Postman before presenting
2. **Use Scenario 1** (Propeller Failure) - most impressive results
3. **Show the response in Pretty view** - easier to read
4. **Highlight key fields:**
   - `recommended_option.title`
   - `stakeholder_emails` (3 drafted)
   - `suggested_actions` (6 planned actions)
   - `status: "pending"` (human-in-the-loop)
5. **Then approve it** to show the execution flow

---

## Quick Test Command

Test in terminal first to verify:

```bash
curl -X POST https://l89algnkzd.execute-api.us-east-1.amazonaws.com/prod/crisis-agent \
  -H 'Content-Type: application/json' \
  -H 'x-api-key: <YOUR_API_KEY>' \
  -d '{
    "crisis_description": "MV Baltic Trader propeller shaft failure requiring immediate attention",
    "vessel_name": "MV Baltic Trader",
    "action": "analyze"
  }' | jq .
```

Then replicate the exact same request in Postman!

---

*Last Updated: 2025-11-07*
*For HelmStream AWS Bedrock Hackathon*
