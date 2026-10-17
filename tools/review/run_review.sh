#!/bin/bash
# LLM page-image review of Markdown transcriptions.
# usage: [REVIEW_DIR=dir] [DATASHEETS="a b"] [TEMPLATE=file] run_review.sh grok|agy|codex
# Models are pinned to the most capable ones (override with AGY_MODEL, CODEX_MODEL,
# CODEX_EFFORT, GROK_MODEL).
# Pages must first be rendered with render_pages.py into $REVIEW_DIR/pages.
# Output: $REVIEW_DIR/review/<model>/<name>_p<N>.out (raw), log in $REVIEW_DIR/review/<model>.log
export PATH=$HOME/.local/bin:$PATH
M=$1; R=${REVIEW_DIR:-$HOME/work/pdf2llm-run}; T=${TEMPLATE:-$(cd "$(dirname "$0")" && pwd)/review_prompt.tmpl}
AGY_MODEL=${AGY_MODEL:-gemini-4-argon-high}; CODEX_MODEL=${CODEX_MODEL:-gpt-6.1-sol}
CODEX_EFFORT=${CODEX_EFFORT:-xhigh}; GROK_MODEL=${GROK_MODEL:-grok-4.7}
mkdir -p "$R/review/$M"
for d in ${DATASHEETS:-ina190 ltc3313 ltc3315a ltc3309a}; do
  for md in "$R"/pages/$d/p*.md; do
    p=$(basename "$md" .md); n=${p#p}; out=$R/review/$M/${d}_p$n.out
    [ -s "$out" ] && grep -q "discrepancies" "$out" && continue
    P=$(sed -e "s/{img}/$p.png/" -e "s/{top}/${p}_top.png/" -e "s/{bottom}/${p}_bottom.png/" -e "s/{md}/$p.md/" -e "s/{name}/$d/g" -e "s/{page}/$n/g" "$T")
    cd "$R/pages/$d" || exit 1
    start=$(date +%s)
    if [ "$M" = grok ]; then timeout 900 nice grok -m "$GROK_MODEL" -p "$P" --cwd . --disable-web-search < /dev/null > "$out" 2>&1
    elif [ "$M" = codex ]; then timeout 900 nice codex exec -m "$CODEX_MODEL" -c model_reasoning_effort="$CODEX_EFFORT" --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox \
         -C . "$P

The Markdown file $p.md is reproduced here (no tool access needed):
$(cat "$p.md")" -i "$p.png" "${p}_top.png" "${p}_bottom.png" < /dev/null > "$out" 2>&1
    else timeout 900 nice agy -p "$P" --print-timeout 880s --model "$AGY_MODEL" < /dev/null > "$out" 2>&1; fi
    echo "$d p$n rc=$? secs=$(( $(date +%s)-start ))" >> "$R/review/$M.log"
  done
done
echo DONE >> "$R/review/$M.log"
