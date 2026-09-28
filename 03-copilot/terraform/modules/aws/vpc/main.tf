terraform {
  required_version = ">= 1.16.3, < 1.17.0"

  backend "s3" {}

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0, < 6.0"
    }
  }
}

resource "aws_vpc" "main" {
  cidr_block           = var.network_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name        = var.vpc_name
    Environment = var.env_name
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "${var.vpc_name}-igw"
    Environment = var.env_name
  }
}

resource "aws_subnet" "public" {
  count                   = length(var.public_cidr)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_cidr[count.index]
  availability_zone       = var.azs[count.index % length(var.azs)]
  map_public_ip_on_launch = true

  tags = {
    Name        = "${var.vpc_name}-public-${count.index + 1}"
    Environment = var.env_name
    Type        = "public"
  }
}

resource "aws_subnet" "private" {
  count             = length(var.private_cidr)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_cidr[count.index]
  availability_zone = var.azs[count.index % length(var.azs)]

  tags = {
    Name        = "${var.vpc_name}-private-${count.index + 1}"
    Environment = var.env_name
    Type        = "private"
  }
}

resource "aws_subnet" "vpn" {
  count             = length(var.vpn_cidr)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.vpn_cidr[count.index]
  availability_zone = var.azs[count.index % length(var.azs)]

  tags = {
    Name        = "${var.vpc_name}-vpn-${count.index + 1}"
    Environment = var.env_name
    Type        = "vpn"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name        = "${var.vpc_name}-public"
    Environment = var.env_name
  }
}

resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "${var.vpc_name}-private"
    Environment = var.env_name
  }
}

resource "aws_route_table_association" "private" {
  count          = length(aws_subnet.private)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

resource "aws_vpc_endpoint" "s3" {
  count             = contains(var.aws_service_endpoints, "com.amazonaws.${var.region}.s3") ? 1 : 0
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.private.id]

  tags = {
    Name        = "${var.vpc_name}-s3-endpoint"
    Environment = var.env_name
  }
}

resource "aws_vpc_endpoint" "dynamodb" {
  count             = contains(var.aws_service_endpoints, "com.amazonaws.${var.region}.dynamodb") ? 1 : 0
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.region}.dynamodb"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.private.id]

  tags = {
    Name        = "${var.vpc_name}-dynamodb-endpoint"
    Environment = var.env_name
  }
}
