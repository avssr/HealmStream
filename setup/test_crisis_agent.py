#!/usr/bin/env python3
import json
import boto3

lambda_client = boto3.client('lambda', region_name='us-east-1')

print("🚨 Testing Crisis Response Agent...")
print()

payload = {
    'crisis_description': 'Baltic Trader propeller shaft failure requiring immediate attention',
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
    print('✅ Crisis Agent Response:')
    print(f'   Status: {body.get("status", "unknown")}')
    print(f'   Options Generated: {len(body.get("options", []))}')

    recommended = body.get('recommended_option', {})
    print(f'   Recommendation: {recommended.get("title", "N/A")}')
    print(f'   Emails Drafted: {len(body.get("stakeholder_emails", []))}')
    print(f'   Messages: {len(body.get("messages", []))}')
    print()

    print('Agent execution log:')
    for i, msg in enumerate(body.get('messages', [])[:5], 1):
        print(f'  {i}. {msg}')

    if recommended:
        print()
        print(f'Recommended Option: {recommended.get("title")}')
        print(f'Duration: {recommended.get("duration_days")} days')
        print(f'Risk: {recommended.get("risk_level")}')
else:
    print(f'❌ Error: {result}')
