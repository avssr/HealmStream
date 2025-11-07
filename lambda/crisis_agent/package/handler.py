#!/usr/bin/env python3
"""
HelmStream - Crisis Response Agent
LangGraph-powered autonomous agent for handling shipyard emergencies
"""

import json
import boto3
import os
from datetime import datetime
from typing import TypedDict, Annotated, Sequence
from decimal import Decimal

# AWS clients
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
lambda_client = boto3.client('lambda', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

# Environment variables
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'helmstream-emails')
RAG_ENGINE_FUNCTION = os.environ.get('RAG_ENGINE_FUNCTION', 'helmstream-rag-engine-emails')
BEDROCK_CLAUDE_MODEL_ID = os.environ.get('BEDROCK_CLAUDE_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')

# Agent state definition
class AgentState(TypedDict):
    """State that the agent maintains throughout execution"""
    crisis_description: str
    vessel_name: str
    detected_at: str

    # Analysis results
    rag_context: str
    dock_status: dict
    options: list

    # Recommendations
    recommended_option: dict
    justification: str

    # Communications
    stakeholder_emails: list

    # Execution
    actions_taken: list
    approval_status: str

    # Messages/logs
    messages: list


# ============================================
# AGENT TOOLS
# ============================================

def tool_query_rag(query: str) -> str:
    """Query the RAG system for relevant historical context"""
    print(f"🔍 Tool: Querying RAG for: {query}")

    try:
        response = lambda_client.invoke(
            FunctionName=RAG_ENGINE_FUNCTION,
            InvocationType='RequestResponse',
            Payload=json.dumps({
                'message': query,
                'top_k': 3
            })
        )

        result = json.loads(response['Payload'].read())
        if result['statusCode'] == 200:
            body = json.loads(result['body'])

            # Format context from sources
            context = f"RAG Answer: {body['answer']}\n\nSources:\n"
            for i, source in enumerate(body.get('sources', [])[:3], 1):
                context += f"{i}. [{source.get('sender_role')}] {source.get('sender')}\n"
                context += f"   Subject: {source.get('subject')}\n"
                context += f"   Vessel: {source.get('vessel_involved')}\n\n"

            return context
        else:
            return f"Error querying RAG: {result.get('body', 'Unknown error')}"
    except Exception as e:
        return f"Error querying RAG: {str(e)}"


def tool_check_dock_status() -> dict:
    """Check current dock availability and scheduled allocations"""
    print("🏗️ Tool: Checking dock status")

    # Query DynamoDB for recent dock-related emails
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)

    try:
        # Get recent operational emails about docks
        response = table.scan(
            FilterExpression='event_category = :cat',
            ExpressionAttributeValues={':cat': 'operational'},
            Limit=10
        )

        # Analyze emails to determine dock status
        dock_info = {
            'dock_1': {'status': 'available', 'current_vessel': None, 'next_available': 'now'},
            'dock_2': {'status': 'available', 'current_vessel': None, 'next_available': 'now'},
            'analysis': 'Based on recent communications'
        }

        # Parse emails for dock mentions
        for item in response.get('Items', []):
            subject = item.get('subject', '').lower()
            body = item.get('body', '').lower()

            if 'dock 1' in subject or 'dock 1' in body:
                if 'allocated' in body or 'occupied' in body:
                    dock_info['dock_1']['status'] = 'occupied'
                    dock_info['dock_1']['current_vessel'] = item.get('vessel_involved', 'Unknown')

            if 'dock 2' in subject or 'dock 2' in body:
                if 'unavailable' in body or 'failure' in body:
                    dock_info['dock_2']['status'] = 'unavailable'
                elif 'allocated' in body or 'occupied' in body:
                    dock_info['dock_2']['status'] = 'occupied'
                    dock_info['dock_2']['current_vessel'] = item.get('vessel_involved', 'Unknown')

        return dock_info

    except Exception as e:
        return {'error': str(e), 'dock_1': {'status': 'unknown'}, 'dock_2': {'status': 'unknown'}}


def tool_calculate_option_costs(option_description: str, duration_days: int) -> dict:
    """Calculate estimated costs for a proposed option"""
    print(f"💰 Tool: Calculating costs for: {option_description}")

    # Simplified cost model
    costs = {
        'dock_rental': duration_days * 5000,  # $5K/day
        'labor': duration_days * 3000,  # $3K/day
        'equipment': duration_days * 2000,  # $2K/day
    }

    # Add premium for external services
    if 'external' in option_description.lower():
        costs['external_premium'] = duration_days * 10000

    # Add demurrage risk
    if duration_days > 10:
        costs['demurrage_risk'] = (duration_days - 10) * 8000

    total = sum(costs.values())

    return {
        'breakdown': costs,
        'total': total,
        'duration_days': duration_days,
        'cost_per_day': total / duration_days if duration_days > 0 else 0
    }


def tool_draft_stakeholder_email(recipient_role: str, situation: str, recommendation: str) -> str:
    """Draft email to stakeholder about the crisis"""
    print(f"📧 Tool: Drafting email to {recipient_role}")

    templates = {
        'Operations Manager': f"""Subject: URGENT: Crisis Response - {situation}

Dear Operations Team,

SITUATION:
{situation}

RECOMMENDED ACTION:
{recommendation}

This recommendation is based on analysis of historical similar incidents, current dock availability, and cost-benefit analysis.

Please review and approve to proceed.

Best regards,
HelmStream Crisis Response Agent""",

        'Dock Scheduler': f"""Subject: Emergency Dock Allocation - {situation}

Hi,

We have an emergency situation requiring immediate dock allocation:

{situation}

Recommended schedule adjustment:
{recommendation}

Please confirm availability and any conflicts.

Thanks,
HelmStream Agent""",

        'Technical Lead': f"""Subject: Emergency Repair Assessment - {situation}

Hello,

Crisis situation detected:
{situation}

Proposed technical approach:
{recommendation}

Please assess feasibility and provide technical input.

Regards,
HelmStream Agent"""
    }

    return templates.get(recipient_role, f"Subject: Crisis Update\n\n{situation}\n\nRecommendation: {recommendation}")


# ============================================
# LANGGRAPH AGENT WORKFLOW
# ============================================

def analyze_crisis(state: AgentState) -> AgentState:
    """Step 1: Analyze the crisis using RAG and current system state"""
    print("\n" + "="*60)
    print("STEP 1: ANALYZING CRISIS")
    print("="*60)

    crisis = state['crisis_description']
    vessel = state['vessel_name']

    # Query RAG for similar past incidents
    rag_query = f"What happened with {vessel}? Any similar emergencies or propeller issues in the past?"
    rag_context = tool_query_rag(rag_query)

    # Check current dock status
    dock_status = tool_check_dock_status()

    state['rag_context'] = rag_context
    state['dock_status'] = dock_status
    state['messages'].append(f"Analysis complete. RAG context retrieved. Dock status: {json.dumps(dock_status, indent=2)}")

    return state


def generate_options(state: AgentState) -> AgentState:
    """Step 2: Generate possible resolution options"""
    print("\n" + "="*60)
    print("STEP 2: GENERATING OPTIONS")
    print("="*60)

    crisis = state['crisis_description']
    dock_status = state['dock_status']

    # Use Claude to generate options based on context
    prompt = f"""You are a shipyard crisis management expert. Analyze this situation and provide 3 concrete options.

CRISIS: {crisis}

DOCK STATUS:
- Dock 1: {dock_status.get('dock_1', {}).get('status', 'unknown')}
- Dock 2: {dock_status.get('dock_2', {}).get('status', 'unknown')}

HISTORICAL CONTEXT:
{state['rag_context']}

Provide 3 options as a JSON array with this structure:
[
  {{
    "option_number": 1,
    "title": "Short title",
    "description": "Detailed description",
    "duration_days": estimated_days,
    "risk_level": "low/medium/high",
    "pros": ["pro1", "pro2"],
    "cons": ["con1", "con2"]
  }}
]

Return ONLY the JSON array, no other text."""

    try:
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}]
        }

        response = bedrock_runtime.invoke_model(
            modelId=BEDROCK_CLAUDE_MODEL_ID,
            body=json.dumps(request_body)
        )

        result = json.loads(response['body'].read())
        options_text = result['content'][0]['text']

        # Extract JSON from response
        import re
        json_match = re.search(r'\[.*\]', options_text, re.DOTALL)
        if json_match:
            options = json.loads(json_match.group(0))
        else:
            # Fallback options
            options = [
                {
                    "option_number": 1,
                    "title": "Extend current dock stay",
                    "description": "Keep vessel in Dock 1, extend allocation",
                    "duration_days": 20,
                    "risk_level": "low",
                    "pros": ["Controlled environment", "No vessel movement"],
                    "cons": ["Blocks dock for other vessels"]
                },
                {
                    "option_number": 2,
                    "title": "External heavy lift at anchorage",
                    "description": "Use external contractor for repairs",
                    "duration_days": 15,
                    "risk_level": "high",
                    "pros": ["Frees up dock"],
                    "cons": ["Weather dependent", "Higher risk"]
                },
                {
                    "option_number": 3,
                    "title": "Refer to external shipyard",
                    "description": "Transfer to another facility",
                    "duration_days": 25,
                    "risk_level": "medium",
                    "pros": ["Not our problem"],
                    "cons": ["Logistical nightmare", "Customer dissatisfaction"]
                }
            ]

        # Calculate costs for each option
        for option in options:
            option['cost_analysis'] = tool_calculate_option_costs(
                option['description'],
                option['duration_days']
            )

        state['options'] = options
        state['messages'].append(f"Generated {len(options)} options with cost analysis")

    except Exception as e:
        print(f"Error generating options: {str(e)}")
        state['messages'].append(f"Error generating options: {str(e)}")
        state['options'] = []

    return state


def recommend_solution(state: AgentState) -> AgentState:
    """Step 3: Recommend the best option with justification"""
    print("\n" + "="*60)
    print("STEP 3: RECOMMENDING SOLUTION")
    print("="*60)

    options = state['options']

    if not options:
        state['messages'].append("No options available for recommendation")
        return state

    # Use Claude to analyze and recommend
    prompt = f"""You are a shipyard operations expert. Review these options and recommend the best one.

OPTIONS:
{json.dumps(options, indent=2)}

CRISIS CONTEXT: {state['crisis_description']}

Provide your recommendation as JSON:
{{
  "recommended_option_number": 1,
  "justification": "Detailed explanation of why this is the best choice",
  "key_factors": ["factor1", "factor2", "factor3"]
}}

Return ONLY the JSON, no other text."""

    try:
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}]
        }

        response = bedrock_runtime.invoke_model(
            modelId=BEDROCK_CLAUDE_MODEL_ID,
            body=json.dumps(request_body)
        )

        result = json.loads(response['body'].read())
        recommendation_text = result['content'][0]['text']

        # Extract JSON
        import re
        json_match = re.search(r'\{.*\}', recommendation_text, re.DOTALL)
        if json_match:
            recommendation = json.loads(json_match.group(0))

            # Find the recommended option
            recommended_num = recommendation['recommended_option_number']
            recommended_option = next((opt for opt in options if opt['option_number'] == recommended_num), options[0])

            state['recommended_option'] = recommended_option
            state['justification'] = recommendation['justification']
            state['messages'].append(f"Recommended Option {recommended_num}: {recommended_option['title']}")

    except Exception as e:
        print(f"Error in recommendation: {str(e)}")
        # Default to lowest risk option
        state['recommended_option'] = min(options, key=lambda x: {'low': 1, 'medium': 2, 'high': 3}.get(x['risk_level'], 2))
        state['justification'] = "Selected lowest risk option as default"
        state['messages'].append(f"Default recommendation: {state['recommended_option']['title']}")

    return state


def draft_communications(state: AgentState) -> AgentState:
    """Step 4: Draft emails to stakeholders"""
    print("\n" + "="*60)
    print("STEP 4: DRAFTING COMMUNICATIONS")
    print("="*60)

    recommended = state['recommended_option']
    crisis = state['crisis_description']

    # Draft emails to key stakeholders
    stakeholders = [
        'Operations Manager',
        'Dock Scheduler',
        'Technical Lead'
    ]

    emails = []
    for stakeholder in stakeholders:
        email = tool_draft_stakeholder_email(
            stakeholder,
            crisis,
            f"{recommended['title']}: {recommended['description']}\n\nJustification: {state['justification']}"
        )
        emails.append({
            'recipient_role': stakeholder,
            'email_content': email
        })

    state['stakeholder_emails'] = emails
    state['messages'].append(f"Drafted {len(emails)} stakeholder communications")

    return state


def await_approval(state: AgentState) -> AgentState:
    """Step 5: Wait for human approval (checkpoint)"""
    print("\n" + "="*60)
    print("STEP 5: AWAITING HUMAN APPROVAL")
    print("="*60)

    state['approval_status'] = 'pending'
    state['messages'].append("Agent workflow paused. Awaiting human approval to proceed.")

    return state


def execute_approved_actions(state: AgentState) -> AgentState:
    """Step 6: Execute the approved plan"""
    print("\n" + "="*60)
    print("STEP 6: EXECUTING APPROVED ACTIONS")
    print("="*60)

    if state.get('approval_status') != 'approved':
        state['messages'].append("Cannot execute - approval not granted")
        return state

    actions = []

    # Simulate sending emails
    for email in state['stakeholder_emails']:
        actions.append(f"Sent email to {email['recipient_role']}")

    # Simulate updating schedule
    actions.append(f"Updated schedule: {state['recommended_option']['title']}")

    # Log decision
    actions.append(f"Logged crisis resolution in system")

    state['actions_taken'] = actions
    state['messages'].append(f"Executed {len(actions)} actions successfully")

    return state


# ============================================
# LAMBDA HANDLER
# ============================================

def lambda_handler(event, context):
    """
    Crisis Response Agent Lambda Handler

    Event format:
    {
      "crisis_description": "Baltic Trader propeller shaft failure requiring immediate attention",
      "vessel_name": "MV Baltic Trader",
      "action": "analyze" | "approve" | "reject"
    }
    """
    print("🚨 Crisis Response Agent activated")
    print(f"Event: {json.dumps(event, indent=2)}")

    try:
        # Initialize or load state
        crisis_description = event.get('crisis_description', 'Unknown crisis')
        vessel_name = event.get('vessel_name', 'Unknown vessel')
        action = event.get('action', 'analyze')

        # Initialize state
        state = AgentState(
            crisis_description=crisis_description,
            vessel_name=vessel_name,
            detected_at=datetime.utcnow().isoformat(),
            rag_context='',
            dock_status={},
            options=[],
            recommended_option={},
            justification='',
            stakeholder_emails=[],
            actions_taken=[],
            approval_status='pending',
            messages=[]
        )

        # Execute workflow based on action
        if action == 'analyze':
            # Full analysis workflow
            state = analyze_crisis(state)
            state = generate_options(state)
            state = recommend_solution(state)
            state = draft_communications(state)
            state = await_approval(state)

        elif action == 'approve':
            # Load previous state (simplified - in production, load from DynamoDB)
            # For demo, we'll just mark as approved
            state['approval_status'] = 'approved'
            state = execute_approved_actions(state)

        elif action == 'reject':
            state['approval_status'] = 'rejected'
            state['messages'].append("Plan rejected by human operator")

        # Return complete state
        return {
            'statusCode': 200,
            'body': json.dumps({
                'crisis': crisis_description,
                'vessel': vessel_name,
                'status': state['approval_status'],
                'recommended_option': state.get('recommended_option', {}),
                'justification': state.get('justification', ''),
                'options': state.get('options', []),
                'stakeholder_emails': state.get('stakeholder_emails', []),
                'actions_taken': state.get('actions_taken', []),
                'messages': state['messages'],
                'dock_status': state.get('dock_status', {})
            }, default=str)
        }

    except Exception as e:
        print(f"Error in crisis agent: {str(e)}")
        import traceback
        traceback.print_exc()

        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'traceback': traceback.format_exc()
            })
        }
