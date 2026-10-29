#!/usr/bin/env bash
set -euo pipefail

DOCS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$DOCS_DIR/.." && pwd)"
export PYTHONPATH="$ROOT_DIR/src:${PYTHONPATH:-}"

rm -rf "$DOCS_DIR/_build"
for lang in en ja; do
  rm -rf "$DOCS_DIR/$lang/api"
  mkdir -p "$DOCS_DIR/$lang/api"
  sphinx-apidoc --force --module-first -o "$DOCS_DIR/$lang/api" "$ROOT_DIR/src/device_proxy"
  sphinx-build -b html -D language="$lang" -c "$DOCS_DIR" "$DOCS_DIR/$lang" "$DOCS_DIR/_build/html/$lang"
done

# docs/index.md を Pages ルートの index.html としてビルドする。
# 各言語の HTML は個別に生成したものを優先する。
sphinx-build -b html -D language=en -c "$DOCS_DIR" "$DOCS_DIR" "$DOCS_DIR/_build/root"
cp "$DOCS_DIR/_build/root/index.html" "$DOCS_DIR/_build/html/index.html"
cp -R "$DOCS_DIR/_build/root/_static" "$DOCS_DIR/_build/html/"
cp -R "$DOCS_DIR/_build/root/_images" "$DOCS_DIR/_build/html/" 2>/dev/null || true
touch "$DOCS_DIR/_build/html/.nojekyll"
