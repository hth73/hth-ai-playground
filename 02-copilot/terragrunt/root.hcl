locals {
  versions = read_terragrunt_config(
    "${get_repo_root()}/02-copilot/terragrunt/versions.hcl"
  )
}

terraform_version_constraint = local.versions.terraform_version_constraint
terragrunt_version_constraint = local.versions.terragrunt_version_constraint

prevent_destroy = get_env("TG_PREVENT_DESTROY", true)
