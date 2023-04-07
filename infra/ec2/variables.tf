variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "eu-central-1"
}

variable "instance_type" {
  description = "ec2 type"
  type        = string
  default     = "a1.medium"
}

variable "vpc_cidr_block" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "my_ip_address" {
  description = "Your IP address"
  type        = string
  sensitive   = true
}

variable "capstone_subnet_count" {
  description = "Number of subnets"
  type        = number
  default = 1
}

variable "public_subnet_cidr_blocks" {
  description = "Availability CIDR blocks for public subnets"
  type        = string
  default = "10.0.1.0/24"
}

variable "capstone_subnet_cidr_blocks" {
  description = "Availability CIDR blocks for public subnets"
  type        = string
  default = "10.0.5.0/24"
}

variable "capstone_instance_type" {
  description = "capstone instance type"
  type        = string
  default     = "t2.micro"
}

