# Deployment bug drills (deliberately broken exercises)

The working application and Helm charts are kept separate from these exercises. Apply **one exercise at a time** in a disposable namespace/cluster, observe the failure, diagnose it, then revert the change. Never use these broken manifests for production.

## Drill 1 — Wrong container port
Symptom: Pod starts, but Service traffic fails or probes fail.
- In a temporary copy of a Helm values file, set the container port to `8001` while Uvicorn still listens on `8000`.
- Diagnose with `kubectl get pods`, `kubectl describe pod`, and `kubectl logs`.
- Fix: align containerPort, Service targetPort, and probe port with the app's actual port (`8000`).

## Drill 2 — Wrong health path
Symptom: Pod repeatedly restarts or remains unready.
- Change a temporary liveness/readiness probe from `/health` to `/healthz`.
- Diagnose with `kubectl describe pod` and Events.
- Fix: use `/health`, which both FastAPI apps implement, or implement the expected endpoint intentionally.

## Drill 3 — Image tag mismatch
Symptom: `ImagePullBackOff` or `ErrImagePull`.
- Set a temporary image tag to a nonexistent SHA.
- Diagnose with `kubectl describe pod`.
- Fix: verify Artifact Registry path and published SHA tag; update Helm values/GitOps commit to the existing immutable tag.

## Drill 4 — Missing Secret Manager permission
Symptom: a secret-reading init container or external secret integration returns permission denied.
- In a disposable test identity only, remove `roles/secretmanager.secretAccessor` on the single test secret.
- Diagnose the workload identity mapping and IAM policy.
- Fix: grant the minimum secret-level role to the exact runtime identity; do not switch to a project Owner role.

## Drill 5 — Wrong Kubernetes Service selector
Symptom: Service exists but has no endpoints.
- Change a temporary Service selector so it no longer matches the Deployment pod labels.
- Diagnose with `kubectl get endpoints` / `kubectl get endpointslices` and inspect labels.
- Fix: make Service selectors exactly match the Pod template labels.

## Drill 6 — Bad environment variable name
Symptom: application uses an unexpected default or fails to connect to a dependency.
- In a temporary values override, rename an expected variable (for example, `DATABASE_URL` to `DB_URL`) without changing the code.
- Diagnose with `kubectl describe pod` and application logs. Never print secret values.
- Fix: align the variable name in chart and application configuration.

## Drill 7 — SonarCloud quality gate
Symptom: validation is green but the Sonar job fails.
- Add a small, intentionally poor code pattern in a disposable branch and inspect the analysis result.
- Fix the finding rather than weakening or disabling the quality gate. Keep the regression test where applicable.

## Safe workflow

```bash
kubectl config current-context
kubectl create namespace bug-drills
# Use only temporary override files in this namespace.
kubectl -n bug-drills get pods,svc,endpoints
kubectl -n bug-drills describe pod POD_NAME
kubectl -n bug-drills logs POD_NAME
# Delete the exercise namespace when finished:
kubectl delete namespace bug-drills
```

Do not store real credentials in exercise YAML. The intentionally broken examples are described procedurally so the checked-in baseline remains deployable.
