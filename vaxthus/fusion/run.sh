#!/bin/bash
# run.sh skript.py [--ro] [--timeout N]   (Växthus: yakitori _n.py + _v.py + skript). Exit 1 om Fusion-skriptet kastar.
cd ~/code/buttercup/vaxthus/fusion
s=$1; shift
f=/Users/hiro/.hermes/cache/scratch/_vrun_$(basename $s)
cat ~/code/yamay_yakitori50/native/_n.py _v.py "$s" > $f
for i in 1 2 3 4 5 6; do
  out=$(~/.hermes/hermes-agent/venv/bin/python ~/code/yamay_yakitori50/native/run_long.py $f "$@" 2>&1)
  if echo "$out" | grep -q "ConnectError: All connection attempts failed"; then echo "(ConnectError, försök $i, väntar 20 s)" >&2; sleep 20; continue; fi
  echo "$out"
  echo "$out" | grep -q '"success": false\|Traceback\|Exception' && exit 1
  exit 0
done
echo "$out"; exit 1
