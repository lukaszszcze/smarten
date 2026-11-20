#!/bin/bash
# Render every OJAJ task through the real components. See tools/ojaj/render_ojaj.jsx.
# Usage: bash tools/ojaj/render_ojaj.sh
set -e
cd "$(dirname "$0")/../.."
ROOT=$PWD
mkdir -p tmp

sed -e "s#COMPDIR#$ROOT/site/src/components/konkursy#g" \
    -e "s#DATADIR#$ROOT/pub/konkursy/angielski/data#g" \
    tools/ojaj/render_ojaj.jsx > tmp/_ro_gen.jsx

(cd site && node_modules/.bin/esbuild "$ROOT/tmp/_ro_gen.jsx" \
    --bundle --loader:.jsx=jsx --jsx=automatic --format=cjs --platform=node \
    --external:react --external:react-dom --external:react/jsx-runtime \
    --outfile="$ROOT/tmp/_ro.cjs" --log-level=error)

NODE_PATH=$ROOT/site/node_modules node tmp/_ro.cjs
