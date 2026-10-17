# Platform security and observability runbook

## Istio

1. Sync the Argo CD applications in `platform/argocd/platform-apps.yaml` and wait for `istiod` and the ingress gateway to become ready.
2. Apply `kubectl apply -f platform/istio/namespace-and-security.yaml` and `kubectl apply -f platform/istio/gateway-and-routing.yaml`.
3. Restart workloads in the `default` namespace so they receive sidecars: `kubectl rollout restart deployment -n default`.
4. Verify `kubectl get peerauthentication,virtualservice,destinationrule,gateway -n default` and inspect proxy status with `istioctl proxy-status`.

STRICT mTLS blocks plaintext traffic between injected workloads. Any workload without an Istio sidecar in this namespace will fail to communicate until it is injected or an intentional, reviewed policy exception is designed. The HTTP Gateway is a learning setup; use TLS termination and a managed certificate for real external traffic.

## Prometheus / Grafana

The Argo CD app installs `kube-prometheus-stack` in `monitoring`. Check `kubectl -n monitoring get pods` and use port-forwarding for local Grafana access. Do not expose dashboards publicly. Application-level Prometheus metrics are not enabled in the starter APIs yet; see `platform/monitoring/README.md`.

## GitHub OIDC / WIF

The IAM Terraform module creates a workload identity pool/provider constrained to the exact GitHub repository claim. Configure repository Actions variables from Terraform outputs and ensure each workflow has `permissions: id-token: write`. The provider restricts the repository, but production pipelines should additionally constrain branch/environment claims and use protected GitHub environments. Never use long-lived service-account keys.
