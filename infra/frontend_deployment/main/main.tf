locals {
  # Create a unique resource name per deployment environment
  resource_name = "${var.app_name}-${var.environment}"

  # Create labels for billing organization
  labels = {
    application = var.app_name
    environment = var.environment
    component   = "frontend"
  }
}

resource "google_cloud_run_v2_service" "frontend" {
  name                = local.resource_name
  location            = var.region
  deletion_protection = false
  launch_stage        = "GA"
  ingress             = "INGRESS_TRAFFIC_ALL"
  labels              = local.labels

  template {
    timeout               = "300s"
    execution_environment = "EXECUTION_ENVIRONMENT_GEN2"

    containers {
      image = var.docker_image

      ports {
        name           = "http1"
        container_port = 3000
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        cpu_idle = true
      }

      startup_probe {
        failure_threshold     = 3
        initial_delay_seconds = 0
        timeout_seconds       = 10
        period_seconds        = 10
        http_get {
          path = "/"
          port = 3000
        }
      }

      env {
        name  = "NEXT_PUBLIC_API_URL"
        value = var.backend_url
      }

      env {
        name  = "NODE_ENV"
        value = "production"
      }
    }

    scaling {
      max_instance_count = 10
    }
  }
}

# Allow unauthenticated access (public frontend)
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  name     = google_cloud_run_v2_service.frontend.name
  location = google_cloud_run_v2_service.frontend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Read Cloud Run service state after resource modification
data "google_cloud_run_v2_service" "frontend" {
  name       = google_cloud_run_v2_service.frontend.name
  location   = var.region
  depends_on = [google_cloud_run_v2_service.frontend]
}
