variable "redshift_password" {
  description = "Redshift password"
  type        = string
  sensitive   = true
}
variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "eu-central-1"
}