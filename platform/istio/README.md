# Istio platform resources

Resources are intentionally separated for learning and troubleshooting:

- `00-namespace.yaml`: `apps` namespace with sidecar injection enabled.
- `01-gateway.yaml`: ingress Gateway.
- `02-virtualservice.yaml`: path-based routing to the Helm Services.
- `03-destinationrule.yaml`: per-service `ISTIO_MUTUAL` upstream TLS.
- `04-authentication.yaml`: namespace-wide `PeerAuthentication` in `STRICT` mode.

Install Istio control plane and ingress gateway before applying these resources. Ensure the ingress gateway Service is exposed using your chosen GKE LoadBalancer/ingress approach. The routes assume Helm release/service names `frontend`, `product-api`, and `order-api` in namespace `apps`; API rewrites should match the FastAPI route prefixes. Strict mTLS will fail for workloads without injected Istio proxies, so verify injection and restart existing pods after enabling it.

```bash
kubectl apply -f platform/istio/00-namespace.yaml
kubectl apply -f platform/istio/01-gateway.yaml
kubectl apply -f platform/istio/02-virtualservice.yaml
kubectl apply -f platform/istio/03-destinationrule.yaml
kubectl apply -f platform/istio/04-authentication.yaml
kubectl -n apps get gateway,virtualservice,destinationrule,peerauthentication
kubectl -n apps get pods
```
