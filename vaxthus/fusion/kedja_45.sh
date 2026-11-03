cd ~/code/buttercup/vaxthus/fusion
./run.sh v04_syll_nock.py --timeout 1500 > v04.log 2>&1 || { echo "v04 FEL"; exit 1; }
sleep 30
./run.sh v05_beslag.py --timeout 1500 > v05.log 2>&1 || { echo "v05 FEL"; exit 1; }
echo "KLAR"
