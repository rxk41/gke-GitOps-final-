variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  default = "asia-south1"
}

variable "zone" {
  type    = string
  default = "asia-south1-a"
}

variable "github_repository" {
  type        = string
  description = "Exact OWNER/REPOSITORY for GitHub OIDC Workload Identity Federation."
}

variable "sonar_secret_id" {
  type    = string
  default = "sonarcloud-token"
}