output "frontend_url" {
  description = "Public URL of the deployed frontend"
  value       = data.google_cloud_run_v2_service.frontend.uri
}

output "service_name" {
  description = "Cloud Run service name"
  value       = google_cloud_run_v2_service.frontend.name
}

output "deployed_image" {
  description = "Docker image deployed"
  value       = var.docker_image
}
