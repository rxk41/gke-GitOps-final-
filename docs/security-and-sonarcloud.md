# Security, secrets, SonarCloud SAST, and remediation

## Secret inventory (no values belong in Git)

| Purpose | Secret | Store in Secret Manager? | Consumer / use |
|---|---|---|---|
| SonarCloud analysis | `sonarcloud-token` | Yes | GitHub Actions authenticates to SonarCloud for analysis |

Do not commit token/password values, `.env` files, service-account JSON keys, Terraform state, or secret outputs. `.gitignore` should keep `terraform.tfvars`, `*.tfstate*`, `.env*`, and credential files out of Git.

## Create the SonarCloud secret

1. Create a SonarCloud project and organization; update `sonar-project.properties` with their exact identifiers.
2. Create a SonarCloud user/project token with only the access required for analysis.
3. Store it interactively in Secret Manager. Avoid putting the value in shell history:
   ```bash
   gcloud secrets create sonarcloud-token --replication-policy=automatic
   read -rsp "SonarCloud token: " SONAR_TOKEN; echo
   printf %s "$SONAR_TOKEN" | gcloud secrets versions add sonarcloud-token --data-file=-
   unset SONAR_TOKEN
   ```
   If the secret already exists, skip the `secrets create` command.
4. Create a dedicated GitHub Actions service account and grant it `roles/secretmanager.secretAccessor` **on this secret only**. Configure a Workload Identity Federation provider whose attribute condition restricts access to the exact repository and intended branch. Allow that provider to impersonate the service account.
5. Set repository variables `GCP_PROJECT_ID`, `GCP_WORKLOAD_IDENTITY_PROVIDER`, and `GCP_GITHUB_ACTIONS_SERVICE_ACCOUNT`.
6. Ensure the service account has no Artifact Registry write or project-admin roles unless that workflow genuinely needs them. The Sonar-only account should only read the Sonar secret.
7. Run `.github/workflows/sonarcloud.yaml`. Fork pull requests intentionally skip this privileged job.

Do not reuse the image-publishing identity for SAST if you can avoid it. A separate identity reduces the blast radius. Secret Manager values are fetched only at runtime and are masked in workflow logs; masking is not a substitute for avoiding echoing secrets.

## Remediation loop

1. Open the SonarCloud project and inspect Bugs, Vulnerabilities, Security Hotspots, and Code Smells.
2. For each issue, identify the source line and understand the data flow before editing.
3. Fix the root cause, add a regression test, and run locally:
   ```bash
   cd apps/product-api
   pip install -r requirements-dev.txt
   ruff check app tests
   python -m pytest -q tests
   ```
   Repeat for `apps/order-api`.
4. Push a branch and open a pull request. CI tests and the SonarCloud quality gate must pass before merge.
5. Re-scan after fixes. Record any accepted risk with a reason and owner; do not silence findings just to get a green build.

## Important limits of this starter

- Sample product data and order storage are in memory, not durable. Order data resets on restart and is not shared across replicas.
- No real payment card details should be handled by this lab.
- The health endpoint is a liveness check, not a database readiness check.
- SonarCloud is static analysis, not a full dynamic security test or a guarantee that the application is secure.
- Review third-party action versions and pin to full commit SHAs for hardened/production workflows.
