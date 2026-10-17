# Prometheus and Grafana (minimal lab setup)

Argo CD installs `kube-prometheus-stack` using `platform/argocd/platform-apps.yaml`. This enables Prometheus, Grafana, node-exporter, and kube-state-metrics with one Prometheus replica, 24-hour retention, a 5 GB retention cap, and modest resource requests/limits. Alertmanager is disabled to keep the lab small.

```bash
kubectl -n monitoring get pods
kubectl -n monitoring get prometheus,servicemonitor
kubectl -n monitoring port-forward svc/kube-prometheus-stack-grafana 3000:80
```

Open `http://localhost:3000`. Do not expose Grafana publicly; use port-forwarding for the lab. Do not commit Grafana passwords or tokens.

The sample FastAPI apps currently expose `/health`, not Prometheus `/metrics`. Cluster-level dashboards work immediately; app-specific metrics need `prometheus-fastapi-instrumentator` plus a `ServiceMonitor`. Add that only when app metrics are required.
