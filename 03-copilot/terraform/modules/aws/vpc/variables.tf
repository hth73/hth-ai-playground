variable "env_name" {
  description = "Environment name for the VPC."
  type        = string
}

variable "vpc_name" {
  description = "Name of the VPC."
  type        = string
}

variable "region" {
  description = "AWS region for the VPC."
  type        = string
}

variable "azs" {
  description = "Availability zones used by the VPC."
  type        = list(string)
}

variable "network_cidr" {
  description = "CIDR block for the VPC."
  type        = string
}

variable "vpn_cidr" {
  description = "CIDR ranges for VPN subnets."
  type        = list(string)
}

variable "private_cidr" {
  description = "CIDR ranges for private subnets."
  type        = list(string)
}

variable "public_cidr" {
  description = "CIDR ranges for public subnets."
  type        = list(string)
}

variable "aws_service_endpoints" {
  description = "AWS service endpoints to expose or configure."
  type        = list(string)
}
