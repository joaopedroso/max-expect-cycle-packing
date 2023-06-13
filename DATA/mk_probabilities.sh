DATA=.	# directory where instances are located

echo "producing probabilities for small instances"
for size in 10 20 30 40 50 60 70 80 90 100; do
    echo -e "\t$size..."
    for rnd in `seq -f "%02g" 1 50`; do 
        file=small/"$size"_"$rnd".input.gz; 
        python kep_io.py $file $rnd
    done; 
done
echo "done"

echo "producing probabilities for big instances"
for size in 70 100 200 300 400 500 600 700 800 900 1000; do 
    echo -e "\t$size..."
    for rnd in `seq -f "%02g" 1 10`; do 
        file=big/"$size"_"$rnd".input.gz; 
        python kep_io.py $file $rnd
    done; 
done
echo "done"
