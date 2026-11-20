#!/bin/bash
# Render every quest task through the real components. See tools/practice/render_quest.jsx.
# Usage: bash tools/practice/render_quest.sh
set -e
cd "$(dirname "$0")/../.."
ROOT=$PWD
mkdir -p tmp

sed -e "s#COMPDIR#$ROOT/site/src/components/konkursy#g" \
    -e "s#DATADIR#$ROOT/pub/konkursy/angielski/data#g" \
    tools/practice/render_quest.jsx > tmp/_rq_gen.jsx

(cd site && node_modules/.bin/esbuild "$ROOT/tmp/_rq_gen.jsx" \
    --bundle --loader:.jsx=jsx --jsx=automatic --format=cjs --platform=node \
    --external:react --external:react-dom --external:react/jsx-runtime \
    --outfile="$ROOT/tmp/_rq.cjs" --log-level=error)

NODE_PATH=$ROOT/site/node_modules node tmp/_rq.cjs
