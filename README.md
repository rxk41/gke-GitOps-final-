# GKE GitOps Lab

A starter learning repository for a zonal GKE Standard cluster, Terraform modules, in-cluster PostgreSQL StatefulSet, GitHub Actions, Helm, Argo CD, Istio, Prometheus, and three sample services.

## Target environment

- One **zonal** GKE Standard cluster (example zone: `asia-south1-a`)
- 3 nodes, `e2-standard-4`, **25 GB boot disk per node**
- React frontend, FastAPI Product API, FastAPI Order API, PostgreSQL 16 StatefulSet
- 2 replicas for each application
- PostgreSQL runs in-cluster as a GitOps-managed StatefulSet on a dedicated tainted node pool
- Argo CD, Istio, Prometheus as GitOps-managed platform components
- External IP load balancer for the frontend; no custom DNS required for the HTTP lab
- GitHub Actions for tests, image builds, and registry publishing

> This is a learning starter, not a production-certified deployment. Review every Terraform plan and set billing alerts before provisioning. GKE nodes, persistent disks, external IPs/load balancers, and networking can incur charges. The dedicated PostgreSQL node pool adds node costs.

## Repository layout

- `infra/terraform`: modular cloud infrastructure and `dev` environment
- `apps`: frontend and two FastAPI APIs
- `helm`: application Helm charts
- `platform`: Argo CD Applications, Istio routing/security policies, and Prometheus/Grafana monitoring
- `.github/workflows`: validation and image publishing workflows
- `docs`: setup and troubleshooting exercises


## Terraform module structure

Every reusable module under `infra/terraform/modules/*` has the requested three-file layout: `variable.tf`, `main.tf`, and `output.tf`. The IAM module includes GitHub Actions OIDC federation using Google Cloud Workload Identity Federation (WIF), a repository-restricted provider condition, a dedicated CI service account, Artifact Registry write permission, and narrowly scoped Secret Manager access. It also creates a GKE workload service account and bindings for the `default/product-api` and `default/order-api` Kubernetes service accounts.

Set `github_repository` to the exact `OWNER/REPOSITORY` value. Before applying, create the `sonarcloud-token` Secret Manager secret. Database secret access is intentionally not configured in this baseline; add it later when you integrate a database. GitHub repository variables used by the workflows are `GCP_PROJECT_ID`, `GCP_WORKLOAD_IDENTITY_PROVIDER` (use the Terraform output `github_wif_provider_resource_name`), and `GCP_GITHUB_ACTIONS_SERVICE_ACCOUNT` (use the Terraform output `github_actions_service_account_email`). Do not create a service-account JSON key. GitHub Actions workflows must request `id-token: write` and authenticate through the WIF provider.

## PostgreSQL architecture

This repository uses only in-cluster PostgreSQL and does not provision a managed database service. PostgreSQL 16 runs in-cluster using the `helm/postgres` chart, a StatefulSet, a persistent volume claim, and an internal-only `ClusterIP` Service. The Terraform GKE module creates a dedicated PostgreSQL node pool labelled `workload=postgres` and tainted `dedicated=postgres:NoSchedule`; the PostgreSQL chart uses the matching node selector and toleration. The other workloads do not tolerate that taint and therefore remain on the general node pool.

The database is a single-replica learning setup. Its PodDisruptionBudget requests one available pod, which can block voluntary node drains while PostgreSQL is the only replica. A PDB does not protect against node failure, disk loss, accidental deletion, or data corruption. Back up data before changes and do not treat this as production HA.

The Product API and Order API still use in-memory data; they are not connected to PostgreSQL by this repository change. Database application code, drivers, connection settings, migrations, and queries must be implemented separately.

## Istio and monitoring platform

`platform/argocd/platform-apps.yaml` installs Istio base/istiod and `kube-prometheus-stack` (Prometheus + Grafana). The `istio-config-app.yaml` Argo CD Application syncs `platform/istio` after the Istio charts are installed; if installing manually, apply `platform/istio/namespace-and-security.yaml` and `platform/istio/gateway-and-routing.yaml` only after Istio CRDs are ready. They enable sidecar injection for the `default` namespace, enforce namespace-wide STRICT mTLS, create an ingress Gateway and VirtualService routes for the frontend and APIs, and apply an ISTIO_MUTUAL DestinationRule. The Kubernetes Services themselves are supplied by the application Helm charts. The sample apps expose `/health` but not `/metrics`; see `platform/monitoring/README.md` before adding ServiceMonitors for application metrics.

## Prerequisites

Install `gcloud`, Terraform, Docker, kubectl, Helm, and (optionally) `istioctl`. Authenticate locally with `gcloud auth login` and configure a billing-enabled Google Cloud project.

## Quick start

1. Copy `infra/terraform/envs/dev/terraform.tfvars.example` to `terraform.tfvars` and set `project_id`, zone, and GitHub identity values.
2. Configure the required APIs and IAM with an appropriately privileged bootstrap identity.
3. From `infra/terraform/envs/dev`, run:
   ```bash
   terraform init
   terraform fmt -recursive
   terraform validate
   terraform plan
   ```
4. Review the plan carefully before `terraform apply`.
5. Build and test applications locally first:
   ```bash
   docker build -t product-api:local apps/product-api
   docker build -t order-api:local apps/order-api
   docker build -t frontend:local apps/frontend
   ```
6. Install Argo CD using the official installation instructions linked in `docs/setup.md`, then apply the root Application in `platform/argocd/root-app.yaml` after updating repository URL and target revision.
7. Configure GitHub Actions Workload Identity Federation and repository secrets/variables as documented in `docs/setup.md`.

## Important implementation notes

- The GKE cluster is zonal: set `zone` to a zone such as `asia-south1-a`, not a region.
- The separately managed node pool is configured for exactly 3 nodes with `e2-standard-4` and 25 GB boot disks.
- HTTP to the frontend is for a disposable lab only. Do not send credentials or sensitive data over HTTP. Google-managed certificates for common external HTTPS load-balancer setups generally require a DNS name that resolves to the load balancer.
- PostgreSQL is a separate in-cluster StatefulSet and is not yet used by the sample APIs.
- Terraform creates cloud infrastructure; Argo CD manages Kubernetes platform and app resources. Avoid using `kubectl apply` as your normal app deployment path.
- Secret Manager secret values are intentionally not stored in this repository.

## Cleanup

From `infra/terraform/envs/dev`, inspect resources and run `terraform destroy` when finished. Confirm the external load balancer, both GKE node pools, persistent disks, and any separately created resources managed by Terraform are removed. Export PostgreSQL data before deleting its PVC or cluster.

## Security and troubleshooting additions

- `.github/workflows/validate.yaml` runs FastAPI tests, Ruff, and Helm lint.
- `.github/workflows/sonarcloud.yaml` runs SonarCloud SAST with a quality gate; the token is retrieved at runtime from Secret Manager using a dedicated WIF identity.
- `sonar-project.properties` defines the project scan scope. Replace the placeholder project key and organization before running scans.
- `docs/security-and-sonarcloud.md` explains secret names, IAM, WIF setup, and the finding-remediation loop.
- `docs/deployment-bug-drills.md` contains intentional deployment failure exercises. They are separate from the working baseline.
- Product and Order APIs include request validation, 404 handling, list filtering/order lookup examples, tests, and non-root container users.

Important: these APIs still use sample/in-memory data. They are suitable for learning, not production persistence. Do not handle real payment information.

## In-cluster PostgreSQL (StatefulSet)

The GitOps workload Applications include a separate PostgreSQL 16 StatefulSet in `helm/postgres`. It uses a 5 GiB PersistentVolumeClaim, an internal-only `ClusterIP` Service named `postgres`, and Kubernetes Secret `postgres-credentials`. It does not expose port 5432 publicly. The dedicated node pool uses a taint and the PostgreSQL pod has the matching toleration and node selector.

Before Argo CD syncs the PostgreSQL Application, create the credentials Secret in the `apps` namespace (do not commit the real password to Git):

```bash
kubectl create namespace apps --dry-run=client -o yaml | kubectl apply -f -
kubectl create secret generic postgres-credentials -n apps \
  --from-literal=username=appuser \
  --from-literal=password='REPLACE_WITH_A_STRONG_PASSWORD'
```

Replace the example password with your own strong password. If the Secret already exists, update it using your normal secret-management process rather than rerunning the create command. Argo CD will then deploy PostgreSQL from `platform/argocd/workload-apps.yaml` after you replace the repository URL placeholder with your GitHub repository.

From pods in the `apps` namespace, the database hostname is `postgres` and the port is `5432`; the initial database is `ecommerce`. **The sample Product API and Order API still use in-memory data and are not connected to PostgreSQL by this change.** Application code, dependencies, and database migrations must be updated separately before they persist or read data from PostgreSQL.

This is a single-replica learning setup, not a production database. A StatefulSet/PVC helps data survive pod replacement, but it is not a backup or high-availability strategy. GKE persistent disks and the GKE cluster can incur charges; delete the lab resources when finished, and understand that deleting a PVC can delete its stored data depending on the storage reclaim policy.
