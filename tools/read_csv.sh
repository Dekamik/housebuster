#!/bin/bash
set -xeuo pipefail
IFS=$'\n\t'

FILE="${1}"
DIR="$(dirname -- "$(readlink -f "${BASH_SOURCE}")")"

trap 'python "${DIR}/delim.py" "${FILE}" \; ,' EXIT
python "${DIR}/delim.py" "${FILE}" , \;
cat "${FILE}" | sed -e 's/;;/; ;/g' | column -s\; -t | less -#5 -N -S
