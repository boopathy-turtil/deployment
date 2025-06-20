variable "region" {
  default = "ap-south-1"
}



variable "service_name" {
  default = "my-fargate-service"
}

variable "vpc_id" {
  default = "vpc-00565e5084c673e95"
}

variable "subnet_ids" {
  default = [
  "subnet-00063f27ce0fa0a82",
  "subnet-0ef43db73d55d5756"
]
}

module "ecs_fargate" {
  source         = "./modules/ecs_fargate"
  service_name   = var.service_name
  image_url      = "375949729256.dkr.ecr.ap-south-1.amazonaws.com/dev-fast-api-repo"

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
