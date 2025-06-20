variable "ecr_repository_name" {
  type = map(string)
  default = {
    "dev"  = "dev-fast-api-repo"
    "test" = "test-fast-api-repo"
    "prod" = "prod-fast-api-repo"
  }
}


variable "ecr_env_tags" {
  type = map(string)
  default = {
    "dev"  = "dev"
    "test" = "test"
    "prod" = "prod"
  }
  
}
