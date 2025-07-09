variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "c5.4xlarge"
}

variable "ssh_key_path" {
  default = ".ssh/workshop_key.pub"
}

variable "repo_url" {
  description = "Repo for cloning"
  type        = string
}

variable "domain" {
  description = "Domain (without protocol)"
  type        = string
  default     = "docker-workshop.com"
}

variable "cloudflare_api_token" {
  description = "Cloudflare API token"
  type        = string
  sensitive   = true
}

variable "cloudflare_zone_id" {
  description = "Cloudflare zone ID"
  type        = string
}
