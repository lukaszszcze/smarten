#!/bin/bash
# Score every quest exercise with its own answer key and with a blank attempt.
# Usage: bash tools/practice/val_quest_perfect.sh
set -e
cd "$(dirname "$0")/../.."
ROOT=$PWD
mkdir -p tmp

sed -e "s#SCORINGSRC#$ROOT/site/src/lib/scoring.js#g" \
    -e "s#DATADIR#$ROOT/pub/konkursy/angielski/data#g" \
    tools/practice/val_quest_perfect.jsx > tmp/_vqp_gen.jsx

(cd site && node_modules/.bin/esbuild "$ROOT/tmp/_vqp_gen.jsx" \
    --bundle --loader:.jsx=jsx --jsx=automatic --format=cjs --platform=node \
    --external:react --external:react-dom --external:react/jsx-runtime \
    --outfile="$ROOT/tmp/_vqp.cjs" --log-level=error)

NODE_PATH=$ROOT/site/node_modules node tmp/_vqp.cjs
