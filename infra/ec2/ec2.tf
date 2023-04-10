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
  vpc_id = aws_vpc.capstone_vpc.id

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

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "ec2_profile"
  role = aws_iam_role.ec2_role.name

  lifecycle {
    create_before_destroy = true
  }
}
