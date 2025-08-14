#!/usr/bin/env bash
# Deploy to Azure Container Apps using Azure CLI
# Prereqs: az CLI logged in, subscription selected.
# Variables to set:
#   RESOURCE_GROUP, LOCATION, ACR_NAME, ACA_ENV, APP_NAME, IMAGE
set -euo pipefail

: "${RESOURCE_GROUP:?Need RESOURCE_GROUP}"
: "${LOCATION:?Need LOCATION}"
: "${ACR_NAME:?Need ACR_NAME}"
: "${ACA_ENV:?Need ACA_ENV}"
: "${APP_NAME:?Need APP_NAME}"
: "${IMAGE:?Need IMAGE}"

echo "Creating resource group: $RESOURCE_GROUP in $LOCATION"
az group create -n "$RESOURCE_GROUP" -l "$LOCATION"

echo "Creating Azure Container Registry: $ACR_NAME"
az acr create -n "$ACR_NAME" -g "$RESOURCE_GROUP" --sku Basic --admin-enabled true || true

echo "Building & pushing image to ACR: $IMAGE"
az acr build --registry "$ACR_NAME" --image "$IMAGE" .

ACR_LOGIN_SERVER=$(az acr show -n "$ACR_NAME" --query loginServer -o tsv)

echo "Creating Container Apps environment: $ACA_ENV"
az containerapp env create -g "$RESOURCE_GROUP" -n "$ACA_ENV" -l "$LOCATION" || true

echo "Deploying Container App: $APP_NAME"
az containerapp create \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --environment "$ACA_ENV" \
  --image "$ACR_LOGIN_SERVER/$IMAGE" \
  --ingress external \
  --target-port 8000 \
  --cpu 0.5 --memory 1.0Gi \
  --env-vars DATABASE_URL="sqlite:///./app.db" LOG_LEVEL="INFO"

echo "Deployment complete."
az containerapp show -g "$RESOURCE_GROUP" -n "$APP_NAME" --query properties.configuration.ingress.fqdn -o tsv
