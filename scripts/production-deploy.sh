#!/bin/bash
set -euo pipefail

# OnlyVips Production Deployment Script v2.0
# Enhanced with security checks and validation

# Color definitions
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
ENVIRONMENT="production"
CLUSTER_NAME=${CLUSTER_NAME:-"onlyvips-prod"}
NAMESPACE=${NAMESPACE:-"production"}
RELEASE_NAME=${RELEASE_NAME:-"onlyvips"}
SLACK_WEBHOOK=${SLACK_WEBHOOK:-""}

# Functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    send_slack_notification "❌ Deployment failed: $1"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

send_slack_notification() {
    if [[ -n "$SLACK_WEBHOOK" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"$1\"}" \
            "$SLACK_WEBHOOK" 2>/dev/null || true
    fi
}

# Pre-deployment checks
pre_deployment_checks() {
    log "Running pre-deployment checks..."
    
    # Check kubectl connection
    if ! kubectl cluster-info &>/dev/null; then
        error "Cannot connect to Kubernetes cluster"
    fi
    
    # Check namespace
    if ! kubectl get namespace "$NAMESPACE" &>/dev/null; then
        log "Creating namespace $NAMESPACE..."
        kubectl create namespace "$NAMESPACE"
    fi
    
    # Verify secrets exist
    local required_secrets=("backend-secret" "flirtbot-secret" "ton-wallet-secret")
    for secret in "${required_secrets[@]}"; do
        if ! kubectl get secret "$secret" -n "$NAMESPACE" &>/dev/null; then
            error "Required secret '$secret' not found in namespace $NAMESPACE"
        fi
    done
    
    # Check Helm
    if ! command -v helm &>/dev/null; then
        error "Helm is not installed"
    fi
    
    # Security checks
    log "Running security checks..."
    
    # Check for default secrets
    if kubectl get secret backend-secret -n "$NAMESPACE" -o jsonpath='{.data.SECRET_KEY}' | base64 -d | grep -q "gizli-anahtar-burada-saklanir"; then
        error "Default SECRET_KEY detected! Please update with secure value."
    fi
    
    # Check Redis password
    if ! kubectl get secret backend-secret -n "$NAMESPACE" -o jsonpath='{.data.REDIS_PASSWORD}' | base64 -d | grep -q "."; then
        warning "Redis password not set. Consider setting for production."
    fi
    
    # Check Sentry DSN
    if ! kubectl get secret backend-secret -n "$NAMESPACE" -o jsonpath='{.data.SENTRY_DSN}' | base64 -d | grep -q "."; then
        warning "Sentry DSN not configured. Error tracking will be disabled."
    fi
    
    # Run security scan on images
    log "Running container security scan..."
    if command -v trivy &>/dev/null; then
        trivy image --severity HIGH,CRITICAL "${BACKEND_IMAGE:-ghcr.io/onlyvips/backend-api:latest}" || warning "Security vulnerabilities found in backend image"
        trivy image --severity HIGH,CRITICAL "${FLIRTBOT_IMAGE:-ghcr.io/onlyvips/flirt-bot:latest}" || warning "Security vulnerabilities found in flirtbot image"
    else
        warning "Trivy not installed, skipping container security scan"
    fi
    
    success "Pre-deployment checks passed"
}

# Backup current deployment
backup_current_deployment() {
    log "Backing up current deployment..."
    
    local backup_dir="backups/$(date +'%Y%m%d_%H%M%S')"
    mkdir -p "$backup_dir"
    
    # Export current Helm values
    helm get values "$RELEASE_NAME" -n "$NAMESPACE" > "$backup_dir/values.yaml" 2>/dev/null || true
    
    # Export current manifests
    kubectl get all -n "$NAMESPACE" -o yaml > "$backup_dir/resources.yaml" 2>/dev/null || true
    
    success "Backup created in $backup_dir"
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    # Create migration job
    kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration-$(date +%s)
  namespace: $NAMESPACE
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: migration
        image: ${BACKEND_IMAGE:-ghcr.io/onlyvips/backend-api:latest}
        command: ["python", "manage.py", "migrate"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: backend-secret
              key: database-url
EOF
    
    # Wait for migration to complete
    kubectl wait --for=condition=complete --timeout=300s \
        job/db-migration-$(date +%s) -n "$NAMESPACE" || error "Migration failed"
    
    success "Database migrations completed"
}

# Deploy with canary strategy
deploy_canary() {
    log "Starting canary deployment..."
    
    # Deploy canary version (10% traffic)
    helm upgrade "$RELEASE_NAME" ./charts/onlyvips-chart \
        --install \
        --namespace "$NAMESPACE" \
        --values ./charts/onlyvips-chart/values-production.yaml \
        --set global.canary.enabled=true \
        --set global.canary.weight=10 \
        --wait \
        --timeout 10m || error "Canary deployment failed"
    
    log "Canary deployed with 10% traffic. Monitoring for 5 minutes..."
    
    # Monitor canary
    local canary_healthy=true
    for i in {1..5}; do
        sleep 60
        log "Canary health check $i/5..."
        
        # Check pod status
        if ! kubectl get pods -n "$NAMESPACE" -l version=canary | grep -q "Running"; then
            canary_healthy=false
            break
        fi
        
        # Check error rate (example with Prometheus)
        # error_rate=$(kubectl exec -n monitoring prometheus-0 -- \
        #     promtool query instant 'rate(http_requests_total{status=~"5.."}[5m])' | \
        #     awk '{print $2}')
        # if (( $(echo "$error_rate > 0.05" | bc -l) )); then
        #     canary_healthy=false
        #     break
        # fi
    done
    
    if [[ "$canary_healthy" == "true" ]]; then
        success "Canary deployment healthy"
        return 0
    else
        error "Canary deployment unhealthy, rolling back..."
        return 1
    fi
}

# Full deployment
deploy_full() {
    log "Proceeding with full deployment..."
    
    helm upgrade "$RELEASE_NAME" ./charts/onlyvips-chart \
        --namespace "$NAMESPACE" \
        --values ./charts/onlyvips-chart/values-production.yaml \
        --set global.canary.enabled=false \
        --wait \
        --timeout 10m || error "Full deployment failed"
    
    success "Full deployment completed"
}

# Post-deployment validation
post_deployment_validation() {
    log "Running post-deployment validation..."
    
    # Check all pods are running
    local not_running=$(kubectl get pods -n "$NAMESPACE" \
        --field-selector=status.phase!=Running \
        --no-headers | wc -l)
    
    if [[ "$not_running" -gt 0 ]]; then
        warning "$not_running pods are not in Running state"
    fi
    
    # Run smoke tests
    log "Running smoke tests..."
    ./scripts/smoke-test.sh || warning "Some smoke tests failed"
    
    # Check endpoints
    local endpoints=("https://api.onlyvips.com/health" 
                    "https://app.onlyvips.com" 
                    "https://panel.onlyvips.com")
    
    for endpoint in "${endpoints[@]}"; do
        if curl -s -o /dev/null -w "%{http_code}" "$endpoint" | grep -q "200"; then
            success "Endpoint $endpoint is healthy"
        else
            warning "Endpoint $endpoint returned non-200 status"
        fi
    done
}

# Main deployment flow
main() {
    log "Starting OnlyVips production deployment..."
    send_slack_notification "🚀 Starting production deployment..."
    
    # Step 1: Pre-deployment checks
    pre_deployment_checks
    
    # Step 2: Backup current deployment
    backup_current_deployment
    
    # Step 3: Run migrations
    run_migrations
    
    # Step 4: Deploy canary
    if deploy_canary; then
        # Step 5: Full deployment
        deploy_full
        
        # Step 6: Post-deployment validation
        post_deployment_validation
        
        send_slack_notification "✅ Production deployment completed successfully!"
        success "Deployment completed successfully!"
    else
        # Rollback
        log "Rolling back deployment..."
        helm rollback "$RELEASE_NAME" -n "$NAMESPACE"
        send_slack_notification "⚠️ Deployment rolled back due to canary failure"
        error "Deployment failed and rolled back"
    fi
}

# Run main function
main "$@" 