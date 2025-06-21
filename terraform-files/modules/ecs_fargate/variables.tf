variable "service_name" {}
variable "image_url" {
  default = "375949729256.dkr.ecr.ap-south-1.amazonaws.com/dev-fast-api-repo:latest"
}
variable "cpu" {}
variable "memory" {}
variable "desired_count" {}
variable "vpc_id" {}
variable "subnet_ids" {
  type = list(string)
}
variable "container_port" {}
variable "aws_region" {
  type    = string
  default = "ap-south-1"  # or whatever region you're using
}