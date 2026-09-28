locals {
  account_name                    = "${basename(get_terragrunt_dir())}"
  account_id                      = "123456789123"
  default_dns_suffix              = "domain.de"
  subdomain_for_internal_services = "infra"
}

inputs = {
  account_id                            = local.account_id
  account_name                          = local.account_name
  default_dns_suffix                    = local.default_dns_suffix
  subdomain_for_internal_services       = local.subdomain_for_internal_services
  default_hosted_zone                   = "${local.account_name}.${local.default_dns_suffix}"
  default_hosted_zone_internal_services = "${local.account_name}.${local.subdomain_for_internal_services}.${local.default_dns_suffix}"
}
