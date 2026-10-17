# GitOps troubleshooting exercises

Make a separate branch for each exercise and change one thing at a time.

| Exercise | Break it intentionally | Investigate |
|---|---|---|
| CI build | Wrong Docker build context | GitHub Actions build logs |
| Python deps | Remove a required dependency | pip/build logs and import errors |
| Image pull | Set a non-existent image tag | `kubectl describe pod -n apps` |
| Registry auth | Remove image push permission in a test setup | `docker push` and IAM policy |
| Helm values | Misspell `replicaCount` or image key | `helm lint` and `helm template` |
| Argo source | Wrong chart path in Application | `argocd app get APP` |
| Sync drift | Manually edit a test Deployment | Argo CD diff and self-heal |
| Service routing | Mismatch selector and pod labels | `kubectl get endpoints -n apps` |
| Probe failure | Point readiness probe at invalid path | `kubectl describe pod -n apps` |
| Istio routing | Wrong host/destination in VirtualService | `istioctl analyze -n apps` |
| Metrics | Remove a scrape annotation/config | Prometheus Targets page |

Useful commands:
```bash
kubectl get pods -A
kubectl get events -A --sort-by=.lastTimestamp
kubectl describe pod POD -n apps
kubectl logs POD -n apps --all-containers
helm lint helm/product-api
helm template product-api helm/product-api -f helm/product-api/values-dev.yaml
argocd app list
argocd app get product-api
argocd app diff product-api
istioctl analyze -n apps
kubectl get svc,endpoints -n apps
kubectl top nodes
kubectl top pods -A
```

For every lab, record: symptom, diagnostic command/output, root cause, fix, and prevention. Do not intentionally break Terraform state or shared infrastructure for these exercises.
