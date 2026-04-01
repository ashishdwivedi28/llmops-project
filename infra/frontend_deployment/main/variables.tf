variable "project" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region for Cloud Run service"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Deployment environment (dev, stage, prod)"
  type        = string
  default     = "dev"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "llmops-frontend"
}

variable "docker_image" {
  description = "Docker image URI for the frontend"
  type        = string
}

variable "backend_url" {
  description = "Backend API URL (Cloud Run service URL)"
  type        = string
}

variable "terraform_state_bucket" {
  description = "GCS bucket for Terraform state"
  type        = string
}
