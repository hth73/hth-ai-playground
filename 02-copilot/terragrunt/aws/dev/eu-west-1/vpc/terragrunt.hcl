include "global" {
  path = "${get_repo_root()}/02-copilot/terragrunt/root.hcl"
}

include "root" {
  path   = find_in_parent_folders("root.hcl")
  expose = true
}

terraform {
  source = "../../../../../terraform/modules/aws/vpc"
}

inputs = {
  # -------------------------------------------------------------------
  # Environment
  # -------------------------------------------------------------------
  env_name = "dev"
  vpc_name = "dev"

  region = include.root.locals.region.region
  azs    = include.root.locals.region.azs

  # -------------------------------------------------------------------
  # Network
  # -------------------------------------------------------------------
  network_cidr = "172.16.16.0/20"

  vpn_cidr = [
    "172.16.192.0/26",
    "172.16.192.64/26",
    "172.16.192.128/26"
  ]

  private_cidr = [
    "172.16.22.0/23",
    "172.16.24.0/23",
    "172.16.26.0/23"
  ]

  public_cidr = [
    "172.16.16.0/23",
    "172.16.18.0/23",
    "172.16.20.0/23"
  ]

  # -------------------------------------------------------------------
  # AWS Service Endpoints
  # -------------------------------------------------------------------
  aws_service_endpoints = [
    "com.amazonaws.eu-west-1.s3",
    "com.amazonaws.eu-west-1.dynamodb"
  ]
}
