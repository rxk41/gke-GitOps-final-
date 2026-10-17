# Setup notes

## Google Cloud prerequisites

Enable billing and set a project:
```bash
gcloud config set project YOUR_PROJECT_ID
gcloud services enable \
  compute.googleapis.com \
  container.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  cloudresourcemanager.googleapis.com \
  artifactregistry.googleapis.com \
  sqladmin.googleapis.com \
  servicenetworking.googleapis.com \
  secretmanager.googleapis.com
```

The Terraform API module also enables APIs, but the initial identity needs permission to enable them. Bootstrap privileges are intentionally separate from the least-privilege runtime identities.

## Terraform

Copy `terraform.tfvars.example` to `terraform.tfvars`. Use a zone, not a region, for `zone`. The example uses `asia-south1-a`; change it if needed.

For a first lab, Terraform state may be local. Before team use, configure a protected GCS backend bucket with object versioning and restricted access. Do not commit state or credentials.

Review the plan for:
- Zonal GKE cluster in the exact selected zone
- Three nodes, `e2-standard-4`, 25 GB `pd-balanced` boot disk
- Expected VPC ranges and external load-balancer resources

## GitHub Actions authentication

Use Workload Identity Federation, not a long-lived service-account JSON key. Create a workload identity pool/provider, restrict the provider condition to your GitHub repository and intended branch, and grant the federated principal Artifact Registry Writer on the target repository. Set GitHub repository variables:
- `GCP_PROJECT_ID`
- `GCP_REGION`
- `GAR_REPOSITORY`
- `WIF_PROVIDER`
- `WIF_SERVICE_ACCOUNT`

The workflow included here publishes images. The initial Terraform provisioning should be run manually until you have deliberately designed and reviewed a separate infrastructure workflow.

## Kubernetes platform

Install Argo CD using the official instructions: https://argo-cd.readthedocs.io/en/stable/getting_started/

Then edit `platform/argocd/root-app.yaml` to point to your repository URL and branch. The root Application installs the platform and workloads from this repo.

Platform charts use upstream Helm repositories:
- Istio: https://istio-release.storage.googleapis.com/charts
- Prometheus Community: https://prometheus-community.github.io/helm-charts

The sample values are deliberately modest. Check compatibility of chart versions with each other and your GKE/Kubernetes version before deployment. Pin versions in `platform/argocd/platform-apps.yaml` rather than tracking floating chart versions.

## Load balancer and TLS

The frontend chart uses a `LoadBalancer` Service for the simplest IP-only lab. This is straightforward but creates a cloud load balancer and is not the same as an Istio ingress gateway. For a more realistic Istio ingress exercise, change the exposure design to an Istio Gateway and the appropriate GKE load-balancer integration.

Use HTTP only with non-sensitive sample data. A Google-managed certificate for a standard external HTTPS load balancer generally needs a domain name that resolves to its IP. No DNS name is required for the initial HTTP lab.
