#!/bin/bash

# HelmStream - Add API Key Authentication to API Gateway
# Phase 4: Secure API endpoints with API keys

set -e  # Exit on error

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../.env"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Configuration file not found: $CONFIG_FILE"
    exit 1
fi

source "$CONFIG_FILE"

echo "============================================"
echo "HelmStream - Add API Authentication"
echo "============================================"
echo "Region: $AWS_REGION"
echo "API ID: $API_GATEWAY_ID"
echo ""

# Step 1: Create API Key
echo "🔑 Step 1: Creating API key..."
API_KEY_NAME="helmstream-api-key"

# Check if API key already exists
EXISTING_KEY_ID=$(aws apigateway get-api-keys \
    --region "$AWS_REGION" \
    --query "items[?name=='$API_KEY_NAME'].id" \
    --output text)

if [ -n "$EXISTING_KEY_ID" ]; then
    echo "⚠️  API key already exists: $EXISTING_KEY_ID"
    API_KEY_ID="$EXISTING_KEY_ID"

    # Get the key value
    API_KEY_VALUE=$(aws apigateway get-api-key \
        --api-key "$API_KEY_ID" \
        --include-value \
        --region "$AWS_REGION" \
        --query 'value' \
        --output text)
else
    # Create new API key
    API_KEY_RESPONSE=$(aws apigateway create-api-key \
        --name "$API_KEY_NAME" \
        --description "API key for HelmStream" \
        --enabled \
        --region "$AWS_REGION")

    API_KEY_ID=$(echo "$API_KEY_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
    API_KEY_VALUE=$(echo "$API_KEY_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['value'])")

    echo "✓ Created API key: $API_KEY_ID"
fi

echo ""

# Step 2: Create Usage Plan
echo "📊 Step 2: Creating usage plan..."
USAGE_PLAN_NAME="helmstream-usage-plan"

# Check if usage plan exists
EXISTING_PLAN_ID=$(aws apigateway get-usage-plans \
    --region "$AWS_REGION" \
    --query "items[?name=='$USAGE_PLAN_NAME'].id" \
    --output text)

if [ -n "$EXISTING_PLAN_ID" ]; then
    echo "⚠️  Usage plan already exists: $EXISTING_PLAN_ID"
    USAGE_PLAN_ID="$EXISTING_PLAN_ID"
else
    USAGE_PLAN_ID=$(aws apigateway create-usage-plan \
        --name "$USAGE_PLAN_NAME" \
        --description "Usage plan for HelmStream API" \
        --throttle burstLimit=100,rateLimit=50 \
        --quota limit=10000,period=MONTH \
        --api-stages apiId="$API_GATEWAY_ID",stage=prod \
        --region "$AWS_REGION" \
        --query 'id' \
        --output text)

    echo "✓ Created usage plan: $USAGE_PLAN_ID"
fi

echo ""

# Step 3: Associate API key with usage plan
echo "🔗 Step 3: Associating API key with usage plan..."

aws apigateway create-usage-plan-key \
    --usage-plan-id "$USAGE_PLAN_ID" \
    --key-id "$API_KEY_ID" \
    --key-type API_KEY \
    --region "$AWS_REGION" 2>/dev/null || echo "  (key may already be associated)"

echo "✓ API key associated with usage plan"
echo ""

# Step 4: Update methods to require API key
echo "🔐 Step 4: Requiring API key for endpoints..."

# Get resource IDs
QUERY_RESOURCE_ID=$(aws apigateway get-resources \
    --rest-api-id "$API_GATEWAY_ID" \
    --region "$AWS_REGION" \
    --query 'items[?pathPart==`query`].id' \
    --output text)

EMAIL_RESOURCE_ID=$(aws apigateway get-resources \
    --rest-api-id "$API_GATEWAY_ID" \
    --region "$AWS_REGION" \
    --query 'items[?pathPart==`process-email`].id' \
    --output text)

# Update /query POST method
aws apigateway update-method \
    --rest-api-id "$API_GATEWAY_ID" \
    --resource-id "$QUERY_RESOURCE_ID" \
    --http-method POST \
    --patch-operations op=replace,path=/apiKeyRequired,value=true \
    --region "$AWS_REGION" > /dev/null

echo "✓ /query endpoint now requires API key"

# Update /process-email POST method
aws apigateway update-method \
    --rest-api-id "$API_GATEWAY_ID" \
    --resource-id "$EMAIL_RESOURCE_ID" \
    --http-method POST \
    --patch-operations op=replace,path=/apiKeyRequired,value=true \
    --region "$AWS_REGION" > /dev/null

echo "✓ /process-email endpoint now requires API key"
echo ""

# Step 5: Redeploy API
echo "🚀 Step 5: Redeploying API..."

DEPLOYMENT_ID=$(aws apigateway create-deployment \
    --rest-api-id "$API_GATEWAY_ID" \
    --stage-name prod \
    --description "Added API key authentication" \
    --region "$AWS_REGION" \
    --query 'id' \
    --output text)

echo "✓ API redeployed: $DEPLOYMENT_ID"
echo ""

# Save API key to config
echo "" >> "$CONFIG_FILE"
echo "# API Authentication" >> "$CONFIG_FILE"
echo "API_KEY_ID=$API_KEY_ID" >> "$CONFIG_FILE"
echo "API_KEY_VALUE=$API_KEY_VALUE" >> "$CONFIG_FILE"
echo "USAGE_PLAN_ID=$USAGE_PLAN_ID" >> "$CONFIG_FILE"

# Summary
echo "============================================"
echo "✅ API Authentication Enabled!"
echo "============================================"
echo ""
echo "🔑 Your API Key:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$API_KEY_VALUE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  SAVE THIS KEY - You won't be able to see it again!"
echo ""
echo "============================================"
echo "📋 Usage Limits:"
echo "============================================"
echo "  • Rate: 50 requests/second"
echo "  • Burst: 100 requests"
echo "  • Monthly quota: 10,000 requests"
echo ""
echo "============================================"
echo "🧪 Test with cURL:"
echo "============================================"
echo ""
echo "Query endpoint (with API key):"
echo "curl -X POST $API_GATEWAY_URL/query \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -H 'x-api-key: $API_KEY_VALUE' \\"
echo "  -d '{\"message\":\"What is the status of MV Pacific Star?\",\"top_k\":5}'"
echo ""
echo "============================================"
echo "🔧 Postman Setup:"
echo "============================================"
echo "1. Open your request in Postman"
echo "2. Go to 'Headers' tab"
echo "3. Add new header:"
echo "   Key: x-api-key"
echo "   Value: $API_KEY_VALUE"
echo "4. Send request"
echo ""
echo "============================================"
echo "✅ Configuration updated: $CONFIG_FILE"
echo "============================================"
