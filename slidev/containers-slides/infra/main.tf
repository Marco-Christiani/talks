terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.4.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

# Elastic IP for stable address
resource "aws_eip" "workshop" {
  domain = "vpc"
  tags = {
    Name = "docker-workshop-eip"
  }
}

# Security group
resource "aws_security_group" "workshop" {
  name_prefix = "docker-workshop-"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Get an AMI
# data "aws_ami" "ubuntu" {
#   most_recent = true
#   owners      = ["099720109477"] # Canonical

#   filter {
#     name = "name"
#     # values = ["ubuntu/images/hvm-ssd/ubuntu-22.04-amd64-server-*"]
#     values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-*-amd64-server-*"]
#   }

#   filter {
#     name   = "virtualization-type"
#     values = ["hvm"]
#   }

#   # filter {
#   #   name   = "architecture"
#   #   values = ["x86_64"]
#   # }
# }
data "aws_ssm_parameter" "ubuntu_jammy" {
  # name = "/aws/service/canonical/ubuntu/server/22.04/stable/current/amd64/hvm/ebs-ssd/ami-id"
  name = "/aws/service/canonical/ubuntu/server/jammy/stable/current/amd64/hvm/ebs-gp2/ami-id"
}

resource "aws_key_pair" "workshop" {
  key_name   = "workshop-key"
  public_key = file("${path.module}/${var.ssh_key_path}")
}

# EC2 instance
resource "aws_instance" "workshop" {
  # ami           = data.aws_ami.ubuntu.id
  ami           = data.aws_ssm_parameter.ubuntu_jammy.value
  instance_type = var.instance_type
  key_name = aws_key_pair.workshop.key_name

  vpc_security_group_ids = [aws_security_group.workshop.id]

  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    repo_url = var.repo_url
    domain   = var.domain
  }))

  tags = {
    Name = "docker-workshop"
  }

  # EBS Volume
  root_block_device {
    volume_size = 30
    volume_type = "gp3"
  }

}

# Associate Elastic IP
resource "aws_eip_association" "workshop" {
  instance_id   = aws_instance.workshop.id
  allocation_id = aws_eip.workshop.id
}

# Cloudflare DNS records
# If i ever host the slides on the ec2 instance create a root record
# resource "cloudflare_record" "workshop_main" {
#   zone_id = var.cloudflare_zone_id
#   name    = var.domain
#   type    = "A"
#   value   = aws_eip.workshop.public_ip
#   proxied = true
# }

# Separate subdomain for direct ws access
resource "cloudflare_record" "workshop_api" {
  zone_id = var.cloudflare_zone_id
  name    = "api.${var.domain}"
  type    = "A"
  value   = aws_eip.workshop.public_ip
  proxied = true
}

# Page rules to disable caching
resource "cloudflare_page_rule" "no_cache_slides" {
  zone_id = var.cloudflare_zone_id
  # protocol is required https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs/resources/page_rule
  target   = "https://${var.domain}/*"
  priority = 1
  # required https://registry.terraform.io/providers/cloudflare/cloudflare/4.3.0/docs/resources/page_rule
  status = "active"

  actions {
    cache_level       = "bypass"
    browser_cache_ttl = 120 # min val
  }
}

resource "cloudflare_page_rule" "no_cache_api" {
  zone_id  = var.cloudflare_zone_id
  target   = "https://api.${var.domain}/*"
  priority = 2
  status   = "active"

  actions {
    cache_level       = "bypass"
    browser_cache_ttl = 120 # min val
  }
}


# Zone settings for aggressive no-cache
# API key doesnt have this perm i dont think and not sure i need this anyways
# resource "cloudflare_zone_settings_override" "workshop" {
#   zone_id = var.cloudflare_zone_id
#
#   settings {
#     browser_cache_ttl = 0
#     cache_level       = "simplified" # aggressive/basic/simplified
#     development_mode  = "on"
#   }
# }
