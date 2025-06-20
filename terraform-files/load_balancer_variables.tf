variable "alb_name" {
  type = map(string)
  default = {
    "dev"  = "dev-alb"
    "test" = "test-alb"
    "prod" = "prod-alb"
  }
}

variable "alb_target_group_port" {
  type = map(number)
  default = {
    "dev"  = 80
    "test" = 80
    "prod" = 80
  }
}

variable "alb_health_check_path" {
  type = map(string)
  default = {
    "dev"  = "/health"
    "test" = "/health"
    "prod" = "/health"
  }
}