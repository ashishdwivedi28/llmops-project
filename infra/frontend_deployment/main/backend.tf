terraform {
  required_version = ">= 1.0"

  backend "gcs" {
    # bucket = var.terraform_state_bucket  # Set via -backend-config in workflow
    prefix = "frontend"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.region
}
