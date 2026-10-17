#!/bin/bash
# LLM page-image review of Markdown transcriptions.
# usage: [REVIEW_DIR=dir] [DATASHEETS="a b"] run_review.sh grok|agy
# Pages must first be rendered with render_pages.py into $REVIEW_DIR/pages.
# Output: $REVIEW_DIR/review/<model>/<name>_p<N>.out (raw), log in $REVIEW_DIR/review/<model>.log
export PATH=$HOME/.local/bin:$PATH
M=$1; R=${REVIEW_DIR:-$HOME/work/pdf2llm-run}; T=$(cd "$(dirname "$0")" && pwd)/review_prompt.tmpl
mkdir -p "$R/review/$M"
for d in ${DATASHEETS:-ina190 ltc3313 ltc3315a ltc3309a}; do
  for md in "$R"/pages/$d/p*.md; do
    p=$(basename "$md" .md); n=${p#p}; out=$R/review/$M/${d}_p$n.out
    [ -s "$out" ] && grep -q "discrepancies" "$out" && continue
    P=$(sed -e "s/{img}/$p.png/" -e "s/{top}/${p}_top.png/" -e "s/{bottom}/${p}_bottom.png/" -e "s/{md}/$p.md/" -e "s/{name}/$d/g" -e "s/{page}/$n/g" "$T")
    cd "$R/pages/$d" || exit 1
    start=$(date +%s)
    if [ "$M" = grok ]; then timeout 900 nice grok -p "$P" --cwd . --disable-web-search < /dev/null > "$out" 2>&1
    else timeout 900 nice agy -p "$P" --print-timeout 880s --model gemini-4-argon-high < /dev/null > "$out" 2>&1; fi
    echo "$d p$n rc=$? secs=$(( $(date +%s)-start ))" >> "$R/review/$M.log"
  done
done
echo DONE >> "$R/review/$M.log"
