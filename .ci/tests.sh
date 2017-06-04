set -e
set -x

source .ci/env_variables.sh

args=()

if [ "$system_os" == "LINUX" ] ; then
  args+=('--doctest-modules')
fi

python -m pytest "${args[@]}"