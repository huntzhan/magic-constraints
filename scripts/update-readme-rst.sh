#!/usr/bin/env bash
PROJECT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

README_MD="$PROJECT_DIR/README.md"
README_RST="$PROJECT_DIR/README.rst"

pandoc -f markdown_github -t rst -o "$README_RST" "$README_MD"
