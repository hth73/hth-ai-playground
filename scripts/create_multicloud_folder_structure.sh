#!/usr/bin/env bash

set -euo pipefail
trap SIGINT SIGTERM ERR EXIT

# ---------------------------------------------------------------------------
# Script       : Creating Multi-Cloud Terraform/Terragrunt structure
# Author       : Helmut Thurnhofer
# Website      : https://github.com/hth73/hth-ai-playground
# Version      : 1.0
# Last changes : 21.09.2026 
# ---------------------------------------------------------------------------

BASE_DIR="../02-copilot"
mkdir -p "${BASE_DIR}"

echo "Creating Multi-Cloud Terraform/Terragrunt structure..."
echo "Base directory: ${BASE_DIR}"
echo

# =============================================================================
# AWS
# =============================================================================
echo "Creating AWS structure..."

mkdir -p \
    "${BASE_DIR}/terragrunt/aws/infra/eu-west-1/vpc" \
    "${BASE_DIR}/terragrunt/aws/infra/eu-west-1/tgw" \
    "${BASE_DIR}/terragrunt/aws/infra/eu-west-1/dns-resolver" \
    "${BASE_DIR}/terragrunt/aws/infra/eu-west-1/git" \
    \
    "${BASE_DIR}/terragrunt/aws/dev/eu-west-1/vpc" \
    "${BASE_DIR}/terragrunt/aws/dev/eu-west-1/eks" \
    "${BASE_DIR}/terragrunt/aws/dev/eu-west-1/iam" \
    \
    "${BASE_DIR}/terragrunt/aws/tst/eu-west-1/vpc" \
    "${BASE_DIR}/terragrunt/aws/tst/eu-west-1/eks" \
    "${BASE_DIR}/terragrunt/aws/tst/eu-west-1/iam" \
    \
    "${BASE_DIR}/terragrunt/aws/pro/eu-west-1/vpc" \
    "${BASE_DIR}/terragrunt/aws/pro/eu-west-1/eks" \
    "${BASE_DIR}/terragrunt/aws/pro/eu-west-1/iam"

# =============================================================================
# Azure
# =============================================================================
echo "Creating Azure structure..."

mkdir -p \
    "${BASE_DIR}/terragrunt/azure/infra/westeurope/vnet" \
    "${BASE_DIR}/terragrunt/azure/infra/westeurope/dns" \
    "${BASE_DIR}/terragrunt/azure/infra/westeurope/private-dns" \
    \
    "${BASE_DIR}/terragrunt/azure/dev/westeurope/vnet" \
    "${BASE_DIR}/terragrunt/azure/dev/westeurope/aks" \
    "${BASE_DIR}/terragrunt/azure/dev/westeurope/identity" \
    \
    "${BASE_DIR}/terragrunt/azure/tst/westeurope/vnet" \
    "${BASE_DIR}/terragrunt/azure/tst/westeurope/aks" \
    "${BASE_DIR}/terragrunt/azure/tst/westeurope/identity" \
    \
    "${BASE_DIR}/terragrunt/azure/pro/westeurope/vnet" \
    "${BASE_DIR}/terragrunt/azure/pro/westeurope/aks" \
    "${BASE_DIR}/terragrunt/azure/pro/westeurope/identity"

# =============================================================================
# GCP
# =============================================================================
echo "Creating GCP structure..."

mkdir -p \
    "${BASE_DIR}/terragrunt/gcp/infra/europe-west3/network" \
    "${BASE_DIR}/terragrunt/gcp/infra/europe-west3/dns" \
    \
    "${BASE_DIR}/terragrunt/gcp/dev/europe-west3/network" \
    "${BASE_DIR}/terragrunt/gcp/dev/europe-west3/gke" \
    "${BASE_DIR}/terragrunt/gcp/dev/europe-west3/iam" \
    \
    "${BASE_DIR}/terragrunt/gcp/tst/europe-west3/network" \
    "${BASE_DIR}/terragrunt/gcp/tst/europe-west3/gke" \
    "${BASE_DIR}/terragrunt/gcp/tst/europe-west3/iam" \
    \
    "${BASE_DIR}/terragrunt/gcp/pro/europe-west3/network" \
    "${BASE_DIR}/terragrunt/gcp/pro/europe-west3/gke" \
    "${BASE_DIR}/terragrunt/gcp/pro/europe-west3/iam"

# =============================================================================
# Terraform Modules
# =============================================================================
echo "Creating Terraform modules..."

mkdir -p \
    "${BASE_DIR}/terraform/modules/aws/vpc" \
    "${BASE_DIR}/terraform/modules/aws/tgw" \
    "${BASE_DIR}/terraform/modules/aws/dns-resolver" \
    "${BASE_DIR}/terraform/modules/aws/git" \
    "${BASE_DIR}/terraform/modules/aws/eks" \
    "${BASE_DIR}/terraform/modules/aws/iam" \
    \
    "${BASE_DIR}/terraform/modules/azure/vnet" \
    "${BASE_DIR}/terraform/modules/azure/dns" \
    "${BASE_DIR}/terraform/modules/azure/private-dns" \
    "${BASE_DIR}/terraform/modules/azure/aks" \
    "${BASE_DIR}/terraform/modules/azure/identity" \
    \
    "${BASE_DIR}/terraform/modules/gcp/network" \
    "${BASE_DIR}/terraform/modules/gcp/dns" \
    "${BASE_DIR}/terraform/modules/gcp/gke" \
    "${BASE_DIR}/terraform/modules/gcp/iam"

# =============================================================================
# Root files
# =============================================================================
echo "Creating root files..."

touch \
    "${BASE_DIR}/terragrunt/common.hcl" \
    "${BASE_DIR}/terragrunt/root.hcl" \
    "${BASE_DIR}/terragrunt/versions.hcl" \
    "${BASE_DIR}/README.md"

# =============================================================================
# Git: keep empty directories
# =============================================================================
find "${BASE_DIR}" \
    -type d \
    -empty \
    -exec touch "{}/.gitkeep" \;
