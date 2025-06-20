provider "aws" {
  
}
variable "region" {
  default = "ap-south-1"
}

variable "ecr_repository_name" {
  default = "my-ecr-repo"
}

variable "service_name" {
  default = "my-fargate-service"
}

variable "vpc_id" {
  default = "vpc-0d3f7fc807218d15b"
}

variable "subnet_ids" {
  default = [
  "subnet-00fe2bd0c30a0efd5",
  "subnet-0adcb03cea7476613"
]
}

module "ecs_fargate" {
  source         = "./modules/ecs_fargate"
  service_name   = var.service_name
  image_url      = "033464272864.dkr.ecr.ap-south-1.amazonaws.com/dev-fast-api-repo:latest"

  cpu            = 1024
  memory         = 3072
  desired_count  = 1
  vpc_id         = var.vpc_id
  subnet_ids     = var.subnet_ids
  container_port = 80
}

output "ecs_cluster_name" {
  description = "The name of the ECS Cluster"
  value       = module.ecs_fargate.ecs_cluster_name
}

output "ecs_service_name" {
  description = "The name of the ECS Service"
  value       = module.ecs_fargate.ecs_service_name
}

output "alb_dns_name" {
  description = "The DNS name of the Application Load Balancer"
  value       = module.ecs_fargate.alb_dns_name
}
