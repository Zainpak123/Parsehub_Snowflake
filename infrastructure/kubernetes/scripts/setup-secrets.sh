#!/bin/bash
# Setup Kubernetes Secrets
# Usage: ./setup-secrets.sh <namespace>

set -e

NAMESPACE=${1:-parsehub}
ENVIRONMENT=${2:-local}

echo "=========================================="
echo "Creating Kubernetes Secrets"
echo "=========================================="
echo "Namespace: $NAMESPACE"
echo "Environment: $ENVIRONMENT"
echo ""

# Check if namespace exists
if ! kubectl get namespace "$NAMESPACE" > /dev/null 2>&1; then
    echo "Creating namespace: $NAMESPACE"
    kubectl create namespace "$NAMESPACE"
else
    echo "Namespace already exists: $NAMESPACE"
fi

echo ""
echo "=========================================="
echo "Snowflake Credentials"
echo "=========================================="

read -p "Enter Snowflake Account ID: " SNOWFLAKE_ACCOUNT
read -p "Enter Snowflake User: " SNOWFLAKE_USER
read -sp "Enter Snowflake Password: " SNOWFLAKE_PASSWORD
echo ""
read -p "Enter Snowflake Warehouse: " SNOWFLAKE_WAREHOUSE
read -p "Enter Snowflake Database: " SNOWFLAKE_DATABASE
read -p "Enter Snowflake Schema: " SNOWFLAKE_SCHEMA

# Create secret
kubectl create secret generic snowflake-credentials \
  --from-literal=account="$SNOWFLAKE_ACCOUNT" \
  --from-literal=user="$SNOWFLAKE_USER" \
  --from-literal=password="$SNOWFLAKE_PASSWORD" \
  --from-literal=warehouse="$SNOWFLAKE_WAREHOUSE" \
  --from-literal=database="$SNOWFLAKE_DATABASE" \
  --from-literal=schema="$SNOWFLAKE_SCHEMA" \
  -n "$NAMESPACE" \
  --dry-run=client \
  -o yaml | kubectl apply -f -

echo "✓ Snowflake credentials secret created"

echo ""
echo "=========================================="
echo "ParseHub API Key"
echo "=========================================="

read -sp "Enter ParseHub API Key: " PARSEHUB_API_KEY
echo ""

# Create secret
kubectl create secret generic parsehub-api-key \
  --from-literal=api-key="$PARSEHUB_API_KEY" \
  -n "$NAMESPACE" \
  --dry-run=client \
  -o yaml | kubectl apply -f -

echo "✓ ParseHub API key secret created"

echo ""
echo "=========================================="
echo "All secrets created successfully!"
echo "=========================================="
