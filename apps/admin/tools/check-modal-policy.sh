#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(dirname "$0")/..
PATTERNS="<nz-modal|\[nzVisible\]|\[\(nzVisible\)\]|isModalOpen|showModal"

echo "Checking modal policy patterns in apps/admin/src..."
if git --no-pager grep -nE -- "${PATTERNS}" -- apps/admin/src; then
  echo "Forbidden modal patterns found. Failing check."
  exit 1
fi

echo "No forbidden modal patterns found."
exit 0
