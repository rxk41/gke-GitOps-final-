# Platform configuration guide

## Istio
Istio resources live in `platform/istio/`, split into namespace, gateway, virtual service, destination rules, and authentication policy. Review the namespace/service names before applying. `PeerAuthentication` STRICT requires sidecar injection for all workloads in `apps`.

## Helm ConfigMaps and Secrets
Each application chart supports a ConfigMap through `configMap.create`, `configMap.name`, and `configMap.data`. For credentials, create a Kubernetes Secret through your approved secret workflow (prefer External Secrets/Secret Manager integration) and set `secret.existingSecret` to its name. The chart references the existing Secret but does not store secret values in Git or Helm values. Do not put plaintext passwords or tokens in `values.yaml`.

## Prometheus
The lab uses a small `kube-prometheus-stack` deployment. Prometheus scrapes cluster components; the Python apps need `/metrics` instrumentation before app-level scraping is configured.
