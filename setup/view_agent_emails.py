#!/usr/bin/env python3
"""
View the full emails drafted by the Crisis Response Agent
"""

import json
import boto3

lambda_client = boto3.client('lambda', region_name='us-east-1')

print("🤖 Invoking Crisis Response Agent...")
print()

payload = {
    'crisis_description': 'MV Baltic Trader propeller shaft failure requiring immediate attention',
    'vessel_name': 'MV Baltic Trader',
    'action': 'analyze'
}

response = lambda_client.invoke(
    FunctionName='helmstream-crisis-agent',
    InvocationType='RequestResponse',
    Payload=json.dumps(payload)
)

result = json.loads(response['Payload'].read())

if result['statusCode'] == 200:
    body = json.loads(result['body'])

    print("=" * 80)
    print("CRISIS RESPONSE AGENT - DRAFTED EMAILS")
    print("=" * 80)
    print()

    # Show crisis overview
    print("📋 CRISIS SCENARIO:")
    print(f"   Vessel: {payload['vessel_name']}")
    print(f"   Description: {payload['crisis_description']}")
    print()

    # Show options generated
    options = body.get('options', [])
    print(f"💡 OPTIONS GENERATED: {len(options)}")
    for opt in options:
        print(f"   {opt['option_number']}. {opt['title']} - {opt['duration_days']} days, {opt['risk_level']} risk")
    print()

    # Show recommendation
    recommended = body.get('recommended_option', {})
    if recommended:
        print("🎯 RECOMMENDED OPTION:")
        print(f"   {recommended.get('title')} ({recommended.get('duration_days')} days)")
        print()

    # Show justification
    justification = body.get('justification', '')
    if justification:
        print("📊 JUSTIFICATION:")
        print(f"   {justification}")
        print()

    # Show drafted emails
    emails = body.get('stakeholder_emails', [])

    if emails:
        print("=" * 80)
        print(f"📧 DRAFTED EMAILS ({len(emails)} total)")
        print("=" * 80)
        print()

        for i, email in enumerate(emails, 1):
            print(f"{'─' * 80}")
            print(f"EMAIL {i} of {len(emails)}")
            print(f"{'─' * 80}")
            print(f"TO:       {email['recipient_role']}")
            print(f"SUBJECT:  Crisis Response - {payload['vessel_name']}")
            print(f"{'─' * 80}")
            print()
            print(email['email_content'])
            print()
            print(f"{'─' * 80}")
            print()
    else:
        print("⚠️  No emails were drafted")

    # Show agent status
    print("=" * 80)
    print("AGENT STATUS")
    print("=" * 80)
    print(f"Status: {body.get('status', 'unknown').upper()}")
    print()

    if body.get('status') == 'pending':
        print("⚠️  The agent is awaiting human approval before executing actions.")
        print()
        print("To approve and execute:")
        print("  - Change action='approve' in the API call")
        print()
        print("To reject:")
        print("  - Change action='reject' in the API call")

    print("=" * 80)

else:
    print(f"❌ Error: {result}")
