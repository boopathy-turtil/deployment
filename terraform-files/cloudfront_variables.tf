variable "cloudfront_distribution_name" {
  type = map(string)
  default = {
    "dev"  = "dev-cloudfront"
    "test" = "test-cloudfront"
    "prod" = "prod-cloudfront"
  }
}

variable "cloudfront_domain_name" {
  type = map(string)
  default = {
    "dev"  = "devapi.cms.turtil.co"
    "test" = "testapi.cms.turtil.co"
    "prod" = "api.cms.turtil.co" # e.g., "app.example.com"
  }
}

variable "cloudfront_route53_zone_id" {
  type = map(string)
  default = {
    "dev"  = "Z0964890C8UWZEUGAVHY"
    "test" = "Z0964890C8UWZEUGAVHY"
    "prod" = "Z0964890C8UWZEUGAVHY" # e.g., "Z1234567890"
  }
}

variable "cloudfront_acm_certificate_arn" {
  type = map(string)
  default = {
    "dev"  = "arn:aws:acm:us-east-1:033464272864:certificate/83a60ab3-b5e4-4195-aba0-e7791868f47e"
    "test" = null
    "prod" = null
  }
}