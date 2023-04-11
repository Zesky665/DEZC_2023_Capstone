// General Setup
terraform {
  cloud {
    organization = "ZhareC"

    workspaces {
      name = "capstone-workspace"
    }
  }
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.33.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_availability_zones" "available" {
  state = "available"
}
// General Setup

// S3 Bucket Definition
resource "aws_s3_bucket" "bucket" {
  bucket        = "my-zoomcamp-capstone-bucket-zharec"
  force_destroy = true

  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}
// S3 Bucket Definition

// EC2 Definition

data "aws_ami" "ubuntu" {

  most_recent = "true"

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"]
}


resource "aws_vpc" "capstone_vpc" {

  cidr_block = var.vpc_cidr_block

  enable_dns_hostnames = true


  tags = {
    Name = "capstone_vpc"
  }
}

resource "aws_internet_gateway" "capstone_igw" {
  vpc_id = aws_vpc.capstone_vpc.id

  tags = {
    Name = "capstone_igw"
  }
}

resource "aws_subnet" "capstone_public_subnet" {

  vpc_id = aws_vpc.capstone_vpc.id

  cidr_block = var.capstone_subnet_cidr_blocks

  availability_zone = data.aws_availability_zones.available.names[0]

  tags = {
    Name = "capstone_public_subnet"
  }
}

resource "aws_route_table" "capstone_public_rt" {
  vpc_id = aws_vpc.capstone_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.capstone_igw.id
  }
}

resource "aws_route_table_association" "capstone_public" {

  route_table_id = aws_route_table.capstone_public_rt.id

  subnet_id = aws_subnet.capstone_public_subnet.id
}

resource "aws_security_group" "capstone_web_sg" {
  name        = "capstone_web_sg"
  description = "Security group for capstone web servers"
  vpc_id      = aws_vpc.capstone_vpc.id

  ingress {
    description = "Allow all traffic through HTTP"
    from_port   = "80"
    to_port     = "80"
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow SSH from my computer"
    from_port   = "22"
    to_port     = "22"
    protocol    = "tcp"
    cidr_blocks = ["${var.my_ip_address}/32"]
  }

  ingress {
    description = "Allow access to capstone from anywhere"
    from_port   = "3000"
    to_port     = "3000"
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "capstone_web_sg"
  }
}

resource "aws_key_pair" "capstone_kp" {
  key_name = "capstone_kp"

  public_key = file("capstone_kp.pub")
}

resource "aws_secretsmanager_secret" "prefect_env" {
  name                           = "prefect_env"
  recovery_window_in_days        = 0
  force_overwrite_replica_secret = true
}

resource "aws_secretsmanager_secret_version" "prefect_env_version" {
  secret_id     = aws_secretsmanager_secret.prefect_env.id
  secret_string = var.prefect_env
}

resource "aws_instance" "capstone_web" {
  ami = data.aws_ami.ubuntu.id

  instance_type = var.capstone_instance_type

  subnet_id = aws_subnet.capstone_public_subnet.id

  key_name = aws_key_pair.capstone_kp.key_name

  vpc_security_group_ids = [aws_security_group.capstone_web_sg.id]

  user_data = <<EOF
#!/bin/bash
echo "Installing docker.io"
sudo apt update
sudo apt install -y docker.io
echo "Downloading the docker image"
sudo docker pull metabase/metabase:latest
sudo git clone https://github.com/Zesky665/DEZC_2023_Capstone.git
cd DEZC_2023_Capstone
sudo snap install aws-cli --classic
touch .prefect_env
echo "%{ var.prefect_env }" >> .prefect_env
EOF

  tags = {
    Name = "capstone_web"
  }
}

resource "aws_eip" "capstone_web_eip" {

  instance = aws_instance.capstone_web.id

  vpc = true

  tags = {
    Name = "capstone_web_eip"
  }
}

resource "aws_iam_role" "ec2_role" {
  name = "ec2_role"

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

  inline_policy {
    name = "ssm-allow-read-prefect_env"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action = [
            "kms:Decrypt",
            "secretsmanager:GetSecretValue",
            "ssm:GetParameters"
          ]
          Effect = "Allow"
          Resource = [
            aws_secretsmanager_secret.prefect_env.arn
          ]
        }
      ]
    })
  }

  tags = {
    tag-key = "tag-value"
  }
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "ec2_profile"
  role = aws_iam_role.ec2_role.name

  lifecycle {
    create_before_destroy = true
  }
}
// EC2 Definition

// Redshift Definition
resource "aws_iam_role" "redshift_copy_unload" {
  name = "redshift_copy_unload"

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
// Redshift Definition

// ECS Definition

resource "aws_iam_role" "prefect_agent_task_role" {
  name  = "prefect-agent-task-role-capstone"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      },
    ]
  })

  inline_policy {
    name = "prefect-agent-allow-ecs-task-capstone"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action = [
            "ec2:DescribeSubnets",
            "ec2:DescribeVpcs",
            "ecr:BatchCheckLayerAvailability",
            "ecr:BatchGetImage",
            "ecr:GetAuthorizationToken",
            "ecr:GetDownloadUrlForLayer",
            "ecs:DeregisterTaskDefinition",
            "ecs:DescribeTasks",
            "ecs:RegisterTaskDefinition",
            "ecs:RunTask",
            "iam:PassRole",
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:GetLogEvents",
            "logs:PutLogEvents"
          ]
          Effect   = "Allow"
          Resource = "*"
        }
      ]
    })
  }
}

resource "aws_iam_role" "prefect_agent_execution_role" {
  name = "prefect-agent-execution-role-capstone"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      },
    ]
  })
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"]
}
// ECS Definition
