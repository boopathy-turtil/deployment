
terraform {

  backend "s3" {
    bucket = "cms-app-terraform-be1"
    key    = "tf-infra/terraform.tfstate"
    region = "ap-south-1"
  }
}


provider "aws" {
  region = "ap-south-1"
}