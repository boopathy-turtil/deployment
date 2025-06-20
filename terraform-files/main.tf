
terraform {

  backend "s3" {
    bucket = "boopathy-devsecops-engineer"
    key    = "tf-infra/terraform.tfstate"
    region = "ap-south-1"
  }
}


provider "aws" {
  region = "ap-south-1"
}