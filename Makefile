.PHONY: fmt validate plan lint-helm

fmt:
	terraform -chdir=infra/terraform/envs/dev fmt -recursive

validate:
	terraform -chdir=infra/terraform/envs/dev init -backend=false
	terraform -chdir=infra/terraform/envs/dev validate

lint-helm:
	helm lint helm/frontend
	helm lint helm/product-api
	helm lint helm/order-api

plan:
	terraform -chdir=infra/terraform/envs/dev init
	terraform -chdir=infra/terraform/envs/dev plan
