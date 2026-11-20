#!/bin/bash
# Print what a student sees for the named OJAJ practice exercises.
# Usage: bash tools/ojaj/peek_ojaj.sh ojaj_e1gl_list ojaj_e2gl_dinozaury
set -e
cd "$(dirname "$0")/../.."
ROOT=$PWD
mkdir -p tmp

sed -e "s#COMPDIR#$ROOT/site/src/components/konkursy#g" \
    -e "s#DATADIR#$ROOT/pub/konkursy/angielski/data#g" \
    tools/ojaj/peek_ojaj.jsx > tmp/_pk_gen.jsx

(cd site && node_modules/.bin/esbuild "$ROOT/tmp/_pk_gen.jsx" \
    --bundle --loader:.jsx=jsx --jsx=automatic --format=cjs --platform=node \
    --external:react --external:react-dom --external:react/jsx-runtime \
    --outfile="$ROOT/tmp/_pk.cjs" --log-level=error)

NODE_PATH=$ROOT/site/node_modules node tmp/_pk.cjs "$@"
