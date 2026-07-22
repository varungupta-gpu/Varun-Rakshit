#!/bin/bash

# Build and Deploy Script for YOLO Segment Processor Cloud Run Jobs
# Usage: ./build_deploy_v2.sh [OPTIONS]

set -e  # Exit on any error

# ── Supported Jobs ────────────────────────────────────────────────
JOB_DEV="analysis-processor-dev"
JOB_PROD="analysis-processor"

# ── Defaults ─────────────────────────────────────────────────────
DEFAULT_TAG=""
TAG=""
ENVIRONMENT=""
DEPLOYMENT_NAME="$JOB_DEV"   # Default: deploy to dev job

DEPLOY_MODE=false
ROLLBACK_MODE=false
VERIFY_MODE=false
VERBOSE=false
DRY_RUN=false
SKIP_CONFIRM=false
NO_CACHE=false

# ── Colors ───────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# ── Helpers ──────────────────────────────────────────────────────
print_status()  { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error()   { echo -e "${RED}[ERROR]${NC} $1"; }
print_action()  { echo -e "${BLUE}${BOLD}$1${NC}"; }
print_command() { if [ "$VERBOSE" = true ]; then echo -e "${YELLOW}[CMD]${NC} $1"; fi; }

# ── Help ─────────────────────────────────────────────────────────
show_help() {
    cat << EOF
Build and Deploy Script for Analysis Processor Cloud Run Jobs

Usage: $0 [OPTIONS]

Modes (exactly one required):
    --deploy              Build, push, and deploy job
    --rollback            Rollback job to a specific image tag
    --verify              Verify current job state

Options:
    --job JOB             Job to target (default: $JOB_DEV)
                            $JOB_DEV   (default)
                            $JOB_PROD
    --env ENVIRONMENT     Environment (dev, prod) [default: dev]
    --tag TAG             Custom image tag (required for rollback, optional for deploy)
    --verbose             Enable verbose output
    --dry-run             Show configuration without executing
    --yes                 Skip confirmation prompt
    --no-cache            Build Docker image without layer cache
    --help                Show this help message

Examples:
    # Deploy to dev job (default)
    $0 --deploy

    # Deploy to dev job explicitly
    $0 --deploy --job $JOB_DEV

    # Deploy to prod job
    $0 --deploy --job $JOB_PROD

    # Rollback dev job to a previous tag
    $0 --rollback --job $JOB_DEV --tag dev-20260101-120000

    # Verify current state of prod job
    $0 --verify --job $JOB_PROD

    # Deploy without confirmation prompt (CI/CD)
    $0 --deploy --job $JOB_DEV --yes

Environment Configuration:
    dev   →  video-backend-dev  (default)
    prod  →  video-backend-prod
EOF
}

# ── Environment Setup ─────────────────────────────────────────────
configure_environment() {
    if [ -z "$ENVIRONMENT" ]; then
        ENVIRONMENT="dev"
    fi

    case "$ENVIRONMENT" in
        "dev")
            PROJECT="video-backend-dev"
            REGION="asia-south1"
            REPO="backend-repo"
            ;;
        "prod")
            PROJECT="video-backend-prod"
            REGION="asia-south1"
            REPO="backend-repo"
            ;;
        *)
            print_error "Unsupported environment: $ENVIRONMENT (use dev or prod)"
            exit 1
            ;;
    esac

    DEFAULT_TAG="${ENVIRONMENT}-$(date +%Y%m%d-%H%M%S)"
}

# ── Deployment Config ─────────────────────────────────────────────
configure_deployment() {
    case "$DEPLOYMENT_NAME" in
        "$JOB_DEV")
            IMAGE_NAME="$JOB_DEV"
            DOCKERFILE="Dockerfile"
            BUILD_DIR="."
            PLATFORM="linux/amd64"
            ;;
        "$JOB_PROD")
            IMAGE_NAME="$JOB_PROD"
            DOCKERFILE="Dockerfile"
            BUILD_DIR="."
            PLATFORM="linux/amd64"
            ;;
        *)
            print_error "Unsupported job: $DEPLOYMENT_NAME"
            print_error "Supported jobs: $JOB_DEV, $JOB_PROD"
            exit 1
            ;;
    esac

    # Each job has its own image path in Artifact Registry
    REGISTRY_TARGET="${REGION}-docker.pkg.dev/${PROJECT}/${REPO}/${IMAGE_NAME}"
}

# ── Prerequisites ─────────────────────────────────────────────────
check_prerequisites() {
    print_status "Checking prerequisites..."

    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running or not accessible"
        exit 1
    fi

    if [ ! -d "$BUILD_DIR" ]; then
        print_error "Build directory not found: $BUILD_DIR"
        exit 1
    fi

    if [ ! -f "$BUILD_DIR/$DOCKERFILE" ]; then
        print_error "Dockerfile not found: $BUILD_DIR/$DOCKERFILE"
        exit 1
    fi

    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed"
        exit 1
    fi

    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "Not authenticated with gcloud. Run 'gcloud auth login' first"
        exit 1
    fi

    if ! gcloud projects describe "$PROJECT" > /dev/null 2>&1; then
        print_error "Project '$PROJECT' not found or not accessible"
        exit 1
    fi

    print_success "All prerequisites met"
}

# ── Build & Push ──────────────────────────────────────────────────
build_local_image() {
    local tag=$1
    print_status "Building ${IMAGE_NAME}:${tag} for ${PLATFORM}..."

    local cache_flag=""
    if [ "$NO_CACHE" = true ]; then cache_flag="--no-cache"; fi

    DOCKER_BUILD_CMD="cd $BUILD_DIR && docker build --platform $PLATFORM $cache_flag -t ${IMAGE_NAME}:${tag} -f ${DOCKERFILE} ."
    print_command "$DOCKER_BUILD_CMD"

    if ! eval "$DOCKER_BUILD_CMD"; then
        print_error "Docker build failed"
        exit 1
    fi

    docker tag ${IMAGE_NAME}:${tag} ${IMAGE_NAME}:latest
    print_success "Local image built and tagged"
}

push_to_registry() {
    local tag=$1
    print_status "Pushing to Artifact Registry..."

    docker tag ${IMAGE_NAME}:${tag} ${REGISTRY_TARGET}:${tag}
    docker tag ${IMAGE_NAME}:${tag} ${REGISTRY_TARGET}:latest

    print_status "Pushing tag: ${tag}"
    docker push ${REGISTRY_TARGET}:${tag}

    print_status "Pushing latest"
    docker push ${REGISTRY_TARGET}:latest

    print_success "Image pushed to registry"
}

# ── Deploy ────────────────────────────────────────────────────────
deploy_job() {
    local tag=$1
    print_status "Updating Cloud Run Job: ${DEPLOYMENT_NAME}..."

    DEPLOY_CMD="gcloud run jobs update ${DEPLOYMENT_NAME} --region=${REGION} --project=${PROJECT} --image=${REGISTRY_TARGET}:${tag}"

    if [ "$VERBOSE" = true ]; then
        DEPLOY_CMD="$DEPLOY_CMD --verbosity=debug"
    else
        DEPLOY_CMD="$DEPLOY_CMD --quiet"
    fi

    print_command "$DEPLOY_CMD"

    if eval "$DEPLOY_CMD"; then
        print_success "Job deployed successfully"
    else
        print_error "Deployment failed. The job may not exist yet — create it first in the GCP console or with gcloud."
        exit 1
    fi
}

# ── Confirm ───────────────────────────────────────────────────────
confirm_operation() {
    local operation_type="$1"
    local tag="$2"

    if [ "$SKIP_CONFIRM" = true ]; then
        print_status "Skipping confirmation (--yes flag set)"
        return
    fi

    echo ""
    if [ "$DEPLOYMENT_NAME" = "$JOB_PROD" ]; then
        print_warning "⚠️  You are targeting the PRODUCTION job: ${DEPLOYMENT_NAME}"
    fi
    print_warning "About to ${operation_type} ${DEPLOYMENT_NAME} with tag ${tag} in ${PROJECT}"
    echo ""

    while true; do
        read -p "Do you want to proceed? (y/n): " -n 1 -r
        echo
        case $REPLY in
            [Yy]*) print_success "Proceeding..."; break ;;
            [Nn]*) print_status "Operation cancelled"; exit 0 ;;
            *) print_error "Please answer y or n" ;;
        esac
    done
}

# ── Verify ────────────────────────────────────────────────────────
verify_job() {
    local expected_tag="$1"

    if ! gcloud beta run jobs describe "$DEPLOYMENT_NAME" --region="$REGION" --project="$PROJECT" > /dev/null 2>&1; then
        print_error "Job does not exist: $DEPLOYMENT_NAME"
        return 1
    fi

    local deployed_image=$(gcloud beta run jobs describe "$DEPLOYMENT_NAME" --region="$REGION" --project="$PROJECT" --format="get(template.spec.containers[0].image)" 2>/dev/null)

    if [ -z "$deployed_image" ]; then
        print_warning "Could not retrieve job image information"
        return 0
    fi

    print_status "Deployed image: $deployed_image"

    local deployed_tag=$(echo "$deployed_image" | sed 's/.*://')
    print_status "Deployed tag: $deployed_tag"

    if [ -n "$expected_tag" ]; then
        if [ "$deployed_tag" = "$expected_tag" ]; then
            print_success "Tag verification: $deployed_tag matches expected $expected_tag"
        else
            print_warning "Tag verification: deployed $deployed_tag does not match expected $expected_tag"
        fi
    else
        print_status "No expected tag provided — showing current deployment state"
    fi

    # Environment variables
    print_status "Environment variables:"
    local env_vars=$(gcloud beta run jobs describe "$DEPLOYMENT_NAME" --region="$REGION" --project="$PROJECT" --format="get(template.spec.containers[0].env)" 2>/dev/null)
    if [ -n "$env_vars" ] && [ "$env_vars" != "[]" ]; then
        echo "$env_vars" | python3 -m json.tool 2>/dev/null || echo "        $env_vars"
    else
        print_status "  No environment variables configured"
    fi

    # Resource configuration
    print_status "Resource configuration:"
    local job_cpu=$(gcloud beta run jobs describe "$DEPLOYMENT_NAME" --region="$REGION" --project="$PROJECT" --format="get(template.spec.containers[0].resources.limits.cpu)" 2>/dev/null)
    local job_memory=$(gcloud beta run jobs describe "$DEPLOYMENT_NAME" --region="$REGION" --project="$PROJECT" --format="get(template.spec.containers[0].resources.limits.memory)" 2>/dev/null)
    local job_timeout=$(gcloud beta run jobs describe "$DEPLOYMENT_NAME" --region="$REGION" --project="$PROJECT" --format="get(template.spec.timeoutSeconds)" 2>/dev/null)
    [ -n "$job_cpu" ]     && echo "        CPU: $job_cpu"
    [ -n "$job_memory" ]  && echo "        Memory: $job_memory"
    [ -n "$job_timeout" ] && echo "        Timeout: ${job_timeout}s ($((job_timeout / 3600))h)"

    # Job status
    local job_status=$(gcloud beta run jobs describe "$DEPLOYMENT_NAME" --region="$REGION" --project="$PROJECT" --format="get(status.conditions[0].status,status.conditions[0].type)" 2>/dev/null)
    if echo "$job_status" | grep -q "True.*Ready"; then
        print_success "Job status: Ready"
    else
        print_warning "Job status: Not ready or still configuring"
    fi

    print_success "Verification completed"
}

# ── Modes ─────────────────────────────────────────────────────────
deploy_mode() {
    configure_environment
    configure_deployment

    if [ -z "$TAG" ]; then TAG="$DEFAULT_TAG"; fi

    print_action "DEPLOY: ${DEPLOYMENT_NAME} → ${PROJECT} (tag: ${TAG})"
    print_status "  Environment:     $ENVIRONMENT"
    print_status "  Project:         $PROJECT"
    print_status "  Job:             $DEPLOYMENT_NAME"
    print_status "  Tag:             $TAG"
    print_status "  Registry Target: $REGISTRY_TARGET"
    print_status "  Dockerfile:      $DOCKERFILE"
    print_status "  Cache:           $([ "$NO_CACHE" = true ] && echo "disabled (--no-cache)" || echo "enabled")"

    check_prerequisites

    if [ "$DRY_RUN" = true ]; then return; fi

    confirm_operation "deploy" "$TAG"
    build_local_image "$TAG"
    push_to_registry "$TAG"
    deploy_job "$TAG"
    verify_job "$TAG"
}

rollback_mode() {
    configure_environment
    configure_deployment

    print_action "ROLLBACK: ${DEPLOYMENT_NAME} → ${PROJECT} (tag: ${TAG})"
    print_status "  Environment:     $ENVIRONMENT"
    print_status "  Project:         $PROJECT"
    print_status "  Job:             $DEPLOYMENT_NAME"
    print_status "  Tag:             $TAG"
    print_status "  Registry Target: $REGISTRY_TARGET"

    check_prerequisites

    if [ "$DRY_RUN" = true ]; then return; fi

    confirm_operation "rollback" "$TAG"
    deploy_job "$TAG"
    verify_job "$TAG"
}

verify_mode() {
    configure_environment
    configure_deployment

    if [ -n "$TAG" ]; then
        print_action "VERIFY: ${DEPLOYMENT_NAME} in ${PROJECT} (expected tag: ${TAG})"
    else
        print_action "VERIFY: ${DEPLOYMENT_NAME} in ${PROJECT} (current state)"
    fi
    print_status "  Environment:     $ENVIRONMENT"
    print_status "  Project:         $PROJECT"
    print_status "  Job:             $DEPLOYMENT_NAME"
    print_status "  Registry Target: $REGISTRY_TARGET"

    check_prerequisites

    if [ "$DRY_RUN" = true ]; then return; fi

    verify_job "$TAG"
}

# ── Arg Parsing ───────────────────────────────────────────────────
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --deploy)   DEPLOY_MODE=true;   shift ;;
            --rollback) ROLLBACK_MODE=true; shift ;;
            --verify)   VERIFY_MODE=true;   shift ;;
            --job)
                if [[ -n "$2" && "$2" != --* ]]; then
                    DEPLOYMENT_NAME="$2"; shift 2
                else
                    print_error "--job requires a value"; exit 1
                fi
                ;;
            --env)
                if [[ -n "$2" && "$2" != --* ]]; then
                    ENVIRONMENT="$2"; shift 2
                else
                    print_error "--env requires a value"; exit 1
                fi
                ;;
            --tag)
                if [[ -n "$2" && "$2" != --* ]]; then
                    TAG="$2"; shift 2
                else
                    print_error "--tag requires a value"; exit 1
                fi
                ;;
            --verbose)   VERBOSE=true;      shift ;;
            --dry-run)   DRY_RUN=true;      shift ;;
            --yes)       SKIP_CONFIRM=true; shift ;;
            --no-cache)  NO_CACHE=true;     shift ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    if [ "$DEPLOY_MODE" = false ] && [ "$ROLLBACK_MODE" = false ] && [ "$VERIFY_MODE" = false ]; then
        print_error "Exactly one of --deploy, --rollback, or --verify must be specified"
        exit 1
    fi

    if [ "$DEPLOYMENT_NAME" != "$JOB_DEV" ] && [ "$DEPLOYMENT_NAME" != "$JOB_PROD" ]; then
        print_error "Unsupported job: $DEPLOYMENT_NAME"
        print_error "Supported jobs: $JOB_DEV, $JOB_PROD"
        exit 1
    fi

    if [ "$ROLLBACK_MODE" = true ] && [ -z "$TAG" ]; then
        print_error "--tag is required for rollback"
        exit 1
    fi
}

# ── Cleanup trap ──────────────────────────────────────────────────
cleanup() {
    if [ $? -ne 0 ]; then
        print_error "Script failed."
    fi
}
trap cleanup EXIT

# ── Entry Point ───────────────────────────────────────────────────
for arg in "$@"; do
    if [ "$arg" = "--help" ]; then show_help; exit 0; fi
done

parse_arguments "$@"

if [ "$DRY_RUN" = true ]; then
    print_warning "DRY RUN MODE — no operations will be performed"
fi

if   [ "$DEPLOY_MODE"   = true ]; then deploy_mode
elif [ "$ROLLBACK_MODE" = true ]; then rollback_mode
elif [ "$VERIFY_MODE"   = true ]; then verify_mode
fi

print_success "Script completed successfully!"
