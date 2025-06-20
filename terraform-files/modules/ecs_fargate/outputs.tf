output "alb_dns_name" {
  description = "The DNS name of the Application Load Balancer"
  value       = aws_lb.this.dns_name
}

output "ecs_service_name" {
  description = "The name of the ECS Service"
  value       = aws_ecs_service.this.name
}

output "ecs_cluster_name" {
  description = "The name of the ECS Cluster"
  value       = aws_ecs_cluster.this.name
}
