#!/bin/bash
set -euo pipefail

base_docker_image_name="${BASE_DOCKER_IMAGE_NAME:-python}"
base_docker_image_tag="${BASE_DOCKER_IMAGE_TAG:-3.8-buster}"
docker_image_build_name="${DOCKER_IMAGE_BUILD_NAME:-nh-explorer-polling}"
docker_hub_org="${DOCKER_HUB_ORG:-horizenlabs}"

docker_writer_password="${DOCKER_WRITER_PASSWORD_POLLING:-}"
docker_writer_username="${DOCKER_WRITER_USERNAME:-}"

is_a_release="${IS_A_RELEASE:-false}"
prod_release="${PROD_RELEASE:-false}"
dev_release="${DEV_RELEASE:-false}"

workdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." &> /dev/null && pwd )"

echo "=== Workdir: ${workdir} ==="
command -v docker &> /dev/null

# Functions
function fn_die() {
  echo -e "$1" >&2
  exit "${2:-1}"
}

echo "=== Checking if DOCKER_WRITER_PASSWORD_POLLING is set ==="
if [ -z "${docker_writer_password:-}" ]; then
  fn_die "DOCKER_WRITER_PASSWORD_POLLING variable is not set. Exiting ..."
fi

echo "=== Checking if DOCKER_WRITER_USERNAME is set ==="
if [ -z "${docker_writer_username:-}" ]; then
  fn_die "DOCKER_WRITER_USERNAME variable is not set. Exiting ..."
fi

docker_tag=""
if [ "${is_a_release}" = "true" ]; then
  docker_tag="${TRAVIS_TAG}"
fi

# Building and publishing docker image
if [ -n "${docker_tag:-}" ]; then
  echo "" && echo "=== Building Docker image for api ===" && echo ""

  docker build -f "ci/Dockerfile_polling" \
  --build-arg ARG_FROM_IMAGE="${base_docker_image_name}" \
  --build-arg ARG_FROM_IMAGE_TAG="${base_docker_image_tag}" \
  -t "${docker_image_build_name}:${docker_tag}" .

  # Publishing to DockerHub
  echo "" && echo "=== Publishing Docker image on Docker Hub ===" && echo ""
  echo "${docker_writer_password}" | docker login -u "${docker_writer_username}" --password-stdin

  # Docker image(s) tags for PROD vs DEV release
  if [ "${prod_release}" = "true" ]; then
    publish_tags=("${docker_tag}" "latest")
  elif [ "${dev_release}" = "true" ]; then
    publish_tags=("${docker_tag}")
  fi

  for publish_tag in "${publish_tags[@]}"; do
    echo "" && echo "Publishing docker image: ${docker_image_build_name}:${publish_tag}"
    docker tag "${docker_image_build_name}:${docker_tag}" "index.docker.io/${docker_hub_org}/${docker_image_build_name}:${publish_tag}"
    docker push "index.docker.io/${docker_hub_org}/${docker_image_build_name}:${publish_tag}"
  done
else
  echo "" && echo "=== The build did NOT satisfy RELEASE build requirements. Docker image(s) was(were) NOT created/published ===" && echo ""
fi


######
# The END
######
echo "" && echo "=== Done ===" && echo ""

exit 0