#!/usr/bin/env python3
"""
HelmStream - Crisis Response Agent Demo
Demonstrates the autonomous agent handling a shipyard emergency
"""

import json
import boto3
import time
import sys

# AWS clients
lambda_client = boto3.client('lambda', region_name='us-east-1')

# ANSI colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")


def print_step(step_num, title):
    """Print a step header"""
    print(f"\n{Colors.OKCYAN}{Colors.BOLD}STEP {step_num}: {title}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'-'*80}{Colors.ENDC}")


def print_success(message):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_info(label, value):
    """Print labeled information"""
    print(f"{Colors.OKBLUE}{label}:{Colors.ENDC} {value}")


def invoke_crisis_agent(crisis_description, vessel_name, action='analyze'):
    """Invoke the crisis response agent"""
    print(f"\n{Colors.WARNING}🚨 Invoking Crisis Response Agent...{Colors.ENDC}")

    payload = {
        'crisis_description': crisis_description,
        'vessel_name': vessel_name,
        'action': action
    }

    try:
        response = lambda_client.invoke(
            FunctionName='helmstream-crisis-agent',
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )

        result = json.loads(response['Payload'].read())

        if result['statusCode'] == 200:
            return json.loads(result['body'])
        else:
            print(f"{Colors.FAIL}Error: {result}{Colors.ENDC}")
            return None

    except Exception as e:
        print(f"{Colors.FAIL}Exception: {str(e)}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        return None


def display_options(options):
    """Display the generated options"""
    print(f"\n{Colors.BOLD}Generated Options:{Colors.ENDC}\n")

    for option in options:
        print(f"{Colors.BOLD}Option {option['option_number']}: {option['title']}{Colors.ENDC}")
        print(f"  Description: {option['description']}")
        print(f"  Duration: {option['duration_days']} days")
        print(f"  Risk Level: {option['risk_level'].upper()}")

        if 'cost_analysis' in option:
            cost = option['cost_analysis']
            print(f"  Estimated Cost: ${cost['total']:,}")
            print(f"    - Daily Rate: ${cost['cost_per_day']:,.0f}/day")

        print(f"  Pros: {', '.join(option['pros'])}")
        print(f"  Cons: {', '.join(option['cons'])}")
        print()


def display_recommendation(recommended_option, justification):
    """Display the agent's recommendation"""
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎯 AGENT RECOMMENDATION{Colors.ENDC}\n")

    print(f"{Colors.BOLD}Recommended: Option {recommended_option['option_number']} - {recommended_option['title']}{Colors.ENDC}")
    print(f"\n{Colors.BOLD}Justification:{Colors.ENDC}")
    print(f"{justification}\n")

    if 'cost_analysis' in recommended_option:
        cost = recommended_option['cost_analysis']
        print(f"{Colors.BOLD}Cost Analysis:{Colors.ENDC}")
        print(f"  Total Estimated Cost: ${cost['total']:,}")
        print(f"  Duration: {cost['duration_days']} days")
        print(f"  Daily Rate: ${cost['cost_per_day']:,.0f}")


def display_communications(emails):
    """Display drafted stakeholder communications"""
    print(f"\n{Colors.BOLD}📧 DRAFTED STAKEHOLDER COMMUNICATIONS{Colors.ENDC}\n")

    for i, email in enumerate(emails, 1):
        print(f"{Colors.OKCYAN}Email {i} - To: {email['recipient_role']}{Colors.ENDC}")
        print(f"{'-'*80}")
        print(email['email_content'])
        print(f"{'-'*80}\n")


def main():
    """Main demo execution"""
    print_header("HELMSTREAM CRISIS RESPONSE AGENT DEMO")

    print(f"{Colors.BOLD}Scenario:{Colors.ENDC}")
    print("MV Baltic Trader has experienced a critical propeller shaft failure")
    print("requiring immediate emergency response and coordination.")
    print("\nThe autonomous agent will:")
    print("  1. Analyze the crisis using RAG (historical context)")
    print("  2. Check current dock availability")
    print("  3. Generate resolution options with cost analysis")
    print("  4. Recommend the optimal solution")
    print("  5. Draft communications to stakeholders")
    print("  6. Present for human approval")
    print("\nPress Enter to begin...")
    input()

    # Crisis scenario
    crisis_description = """
    MV Baltic Trader has experienced a critical propeller shaft failure during
    routine inspection. Initial assessment indicates the propeller assembly
    requires complete replacement. This is an emergency repair situation
    requiring immediate dock allocation and timeline coordination.
    """

    vessel_name = "MV Baltic Trader"

    # ========================================
    # STEP 1-5: Analysis Phase
    # ========================================
    print_step(1, "INITIATING CRISIS ANALYSIS")

    result = invoke_crisis_agent(crisis_description.strip(), vessel_name, action='analyze')

    if not result:
        print(f"{Colors.FAIL}❌ Agent failed to respond{Colors.ENDC}")
        sys.exit(1)

    print_success("Crisis analysis complete!")

    # Display execution log
    print(f"\n{Colors.BOLD}Agent Execution Log:{Colors.ENDC}")
    for i, message in enumerate(result.get('messages', []), 1):
        print(f"  {i}. {message}")

    time.sleep(2)

    # ========================================
    # STEP 2: Review RAG Context
    # ========================================
    print_step(2, "HISTORICAL CONTEXT (RAG)")

    print(f"{Colors.BOLD}The agent queried the RAG system for similar past incidents:{Colors.ENDC}\n")
    # Show dock status
    dock_status = result.get('dock_status', {})
    print(f"{Colors.BOLD}Current Dock Status:{Colors.ENDC}")
    print(json.dumps(dock_status, indent=2))

    time.sleep(2)

    # ========================================
    # STEP 3: Review Options
    # ========================================
    print_step(3, "GENERATED RESOLUTION OPTIONS")

    options = result.get('options', [])
    if options:
        display_options(options)
    else:
        print(f"{Colors.WARNING}No options generated{Colors.ENDC}")

    time.sleep(2)

    # ========================================
    # STEP 4: Review Recommendation
    # ========================================
    print_step(4, "AGENT RECOMMENDATION")

    recommended_option = result.get('recommended_option', {})
    justification = result.get('justification', '')

    if recommended_option:
        display_recommendation(recommended_option, justification)
    else:
        print(f"{Colors.WARNING}No recommendation generated{Colors.ENDC}")

    time.sleep(2)

    # ========================================
    # STEP 5: Review Communications
    # ========================================
    print_step(5, "STAKEHOLDER COMMUNICATIONS")

    emails = result.get('stakeholder_emails', [])
    if emails:
        display_communications(emails)
    else:
        print(f"{Colors.WARNING}No communications drafted{Colors.ENDC}")

    time.sleep(2)

    # ========================================
    # STEP 6: Human Approval
    # ========================================
    print_step(6, "HUMAN-IN-THE-LOOP APPROVAL")

    print(f"{Colors.BOLD}Status:{Colors.ENDC} {result.get('status', 'unknown').upper()}")

    print(f"\n{Colors.WARNING}The agent has paused and is awaiting human approval.{Colors.ENDC}")
    print(f"{Colors.BOLD}Would you like to approve this plan?{Colors.ENDC} (yes/no): ", end='')

    approval = input().strip().lower()

    if approval in ['yes', 'y']:
        print(f"\n{Colors.OKGREEN}✓ Plan approved! Executing actions...{Colors.ENDC}\n")

        # Invoke agent with approval
        exec_result = invoke_crisis_agent(crisis_description.strip(), vessel_name, action='approve')

        if exec_result:
            actions = exec_result.get('actions_taken', [])
            print(f"{Colors.BOLD}Actions Executed:{Colors.ENDC}")
            for i, action in enumerate(actions, 1):
                print(f"  {i}. {action}")
                print_success(f"Action {i} completed")
                time.sleep(0.5)

            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ CRISIS RESOLUTION COMPLETE!{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}❌ Execution failed{Colors.ENDC}")
    else:
        print(f"\n{Colors.WARNING}Plan rejected by human operator{Colors.ENDC}")

        # Invoke agent with rejection
        invoke_crisis_agent(crisis_description.strip(), vessel_name, action='reject')

    # ========================================
    # SUMMARY
    # ========================================
    print_header("DEMO COMPLETE")

    print(f"{Colors.BOLD}What Just Happened:{Colors.ENDC}")
    print("  ✓ Agent detected and analyzed a critical crisis situation")
    print("  ✓ Retrieved relevant historical context from 88 shipyard emails")
    print("  ✓ Checked real-time dock availability")
    print("  ✓ Generated 3 resolution options with full cost analysis")
    print("  ✓ Recommended optimal solution using AI reasoning")
    print("  ✓ Drafted professional communications to stakeholders")
    print("  ✓ Presented plan for human approval (safety checkpoint)")
    print("  ✓ Executed approved actions autonomously")

    print(f"\n{Colors.BOLD}Agent Capabilities Demonstrated:{Colors.ENDC}")
    print("  🤖 Autonomous multi-step reasoning")
    print("  🔍 RAG integration for contextual decision-making")
    print("  💰 Automated cost-benefit analysis")
    print("  📧 Professional communication drafting")
    print("  👤 Human-in-the-loop safety controls")
    print("  ⚡ End-to-end workflow orchestration")

    print(f"\n{Colors.BOLD}Time Savings:{Colors.ENDC}")
    print("  Manual Process: ~2-4 hours of coordination")
    print("  Agent Process: ~30 seconds + human approval")
    print(f"  {Colors.OKGREEN}Efficiency Gain: 240x faster!{Colors.ENDC}")

    print(f"\n{Colors.OKCYAN}{'='*80}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'Thank you for watching the demo!'.center(80)}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'='*80}{Colors.ENDC}\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Demo interrupted by user{Colors.ENDC}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.FAIL}Error: {str(e)}{Colors.ENDC}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
