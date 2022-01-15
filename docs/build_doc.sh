#!/bin/bash

APP_SCHEMA=app_schema.json

gen_doc ()
{
  local kind=$1
  local dir=$2
  local config=$3

  [[ ! -z "$dir" ]] || exit 2
  rm -rf "$dir" && mkdir -p  "$dir"

  generate-schema-doc \
    --config-file "$config" \
    "$APP_SCHEMA" \
    "$dir"/"main.$kind"
}


main ()
{
  albero schema > "$APP_SCHEMA"
  for i in html md; do
    gen_doc "$i" "docs_$i" "doc_config_${i}.yaml"
  done
}

main


