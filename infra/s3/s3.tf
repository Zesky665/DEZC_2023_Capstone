terraform {
  required_providers {

    aws = {
      source  = "hashicorp/aws"
      version = "4.0.0"
    }
  }

  required_version = "~> 1.3.7"
}

provider "aws" {
  region = var.aws_region
}

data "aws_availability_zones" "available" {
  state = "available"
}
resource "aws_s3_bucket" "bucket" {
  bucket        = "my-zoomcamp-capstone-bucket-zharec"
  force_destroy = true

  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}