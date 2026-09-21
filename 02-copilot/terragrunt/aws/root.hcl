locals {
  versions = read_terragrunt_config(
    "${get_repo_root()}/02-copilot/terragrunt/versions.hcl"
  )

  account = read_terragrunt_config(
    find_in_parent_folders("account.hcl")
  ).inputs

  region = read_terragrunt_config(
    find_in_parent_folders("region.hcl")
  ).inputs
}

terraform_version_constraint  = local.versions.terraform_version_constraint
terragrunt_version_constraint = local.versions.terragrunt_version_constraint
prevent_destroy                = get_env("TG_PREVENT_DESTROY", true)

remote_state {
  backend = "s3"
  config = {
    region         = local.region.state_bucket_region
    bucket         = local.region.state_bucket
    key            = "${path_relative_to_include()}/terraform.tfstate"
    encrypt        = true
    use_lockfile   = true
  }
}

generate "provider" {
  path      = "generated_provider.tf"
  if_exists = "overwrite"
  contents  = <<EOF
provider "aws" {
  region              = "${local.region.region}"
  allowed_account_ids = [
    "${local.account.account_id}"
  ]
}
EOF
}
