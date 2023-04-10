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

resource "aws_iam_role" "redshift_copy_unload" {
  name = "redshift_copy_unload"

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "redshift.amazonaws.com"
        }
      }
    ]
  })

  inline_policy {
    name = "amazon_s3_read_only_access"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action = [
            "s3:Get*",
            "s3:List*",
            "s3-object-lambda:Get*",
            "s3-object-lambda:List*"
          ]
          Effect   = "Allow"
          Resource = "*"
        }
      ]
    })
  }

  tags = {
    tag-key = "tag-value"
  }
}

resource "aws_redshift_cluster" "zoomcamp-capstone-dwh" {
  cluster_identifier = "zoomcamp-capstone-dwh"
  database_name      = "capstone_db"
  master_username    = "zhare_c"
  master_password    = var.redshift_password
  node_type          = "dc2.large"
  cluster_type       = "single-node"
  iam_roles          = [aws_iam_role.redshift_copy_unload.arn]

  // default values
  port                  = 5439
  allow_version_upgrade = true
  number_of_nodes       = 1
  publicly_accessible   = true
  skip_final_snapshot   = true // default is false, prevents destroy action


  tags = {
    Name        = "Redshift Serverless Capstone"
    Environment = "Dev"
  }
}