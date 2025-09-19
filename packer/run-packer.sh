#!/usr/bin/env bash
set -euo pipefail

# Usage: ./run-packer.sh <playbook-path-relative-to-src> [--become] [--limit <pattern>] [--extra "-e foo=bar"]

PLAYBOOK=${1:?"Usage: $0 <playbook-path-relative-to-src> [--become] [--extra \"-e foo=bar\"]"}
BECOME=false
EXTRA_ARGS=()
LIMIT=""
BASE_IMAGE=${BASE_IMAGE:-ubuntu:22.04}
shift || true

while [[ $# -gt 0 ]]; do
  case "$1" in
    --become)
      BECOME=true
      shift
      ;;
    --limit)
      LIMIT="$2"
      shift 2
      ;;
    --extra)
      EXTRA_ARGS+=("$2")
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
SRC_DIR="$REPO_ROOT/src"
[[ -d "$SRC_DIR" ]] || { echo "src/ not found at $SRC_DIR"; exit 1; }
[[ -f "$SRC_DIR/$PLAYBOOK" ]] || { echo "Playbook not found: $SRC_DIR/$PLAYBOOK"; exit 1; }

IMAGE_TAG=ansible-packer:local
if ! docker image inspect "$IMAGE_TAG" >/dev/null 2>&1; then
  echo "Building $IMAGE_TAG..."
  docker build -t "$IMAGE_TAG" -f "$REPO_ROOT/packer/Dockerfile" "$REPO_ROOT/packer"
fi

ARGS=( build -var "playbook_file=$PLAYBOOK" -var "base_image=$BASE_IMAGE" )
$BECOME && ARGS+=( -var 'become=true' )
# Always include --limit if provided
if [[ -n "$LIMIT" ]]; then
  EXTRA_ARGS+=("--limit" "$LIMIT")
fi

if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
  # Build a JSON array for ansible_extra_args, preserving spaces inside each arg
  json='['
  for i in "${!EXTRA_ARGS[@]}"; do
    a=${EXTRA_ARGS[$i]}
    # escape quotes
    a=${a//"/\\"}
    if [[ $i -gt 0 ]]; then json+=','; fi
    json+="\"$a\""
  done
  json+=']'
  ARGS+=( -var "ansible_extra_args=$json" )
fi

docker run --rm -it \
  -v "$REPO_ROOT:/workspace" \
  -v "$REPO_ROOT/.packer.d:/root/.packer.d" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -w /workspace/packer \
  -e PACKER_LOG=1 \
  "$IMAGE_TAG" init template.pkr.hcl

exec docker run --rm -it \
  -v "$REPO_ROOT:/workspace" \
  -v "$REPO_ROOT/.packer.d:/root/.packer.d" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -w /workspace/packer \
  -e PACKER_LOG=1 \
  "$IMAGE_TAG" "${ARGS[@]}" template.pkr.hcl
