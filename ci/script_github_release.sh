is_a_release="${IS_A_RELEASE:-false}"
prod_release="${PROD_RELEASE:-false}"
github_token="${GITHUB_TOKEN:-}"

# Functions
function fn_die() {
  echo -e "$1" >&2
  exit "${2:-1}"
}

# checking if GITHUB_TOKEN is set
echo "=== Checking if GITHUB_TOKEN is set ==="
if [ -z "${github_token:-}" ]; then
  fn_die "GITHUB_TOKEN variable is not set. Exiting ..."
fi

# If a production release build Generate GitHub Release
if [ "${is_a_release}" = "true" ] && [ "${prod_release}" = "true" ]; then
  # Release notes to Github
  echo "" && echo "=== Generating GitHub Release ${TRAVIS_TAG} for ${TRAVIS_REPO_SLUG} ===" && echo ""
  curl -X POST -H "Accept: application/vnd.github+json" -H "Authorization: token ${github_token}" https://api.github.com/repos/"${TRAVIS_REPO_SLUG}"/releases -d "{\"tag_name\":\"${TRAVIS_TAG}\",\"generate_release_notes\":true}"
else
  echo "" && echo "=== The build is NOT a production release. Github Release won't be generated ===" && echo ""
fi