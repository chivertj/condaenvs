basefilename=$1
for file in ${basefilename}*
do
    echo "UPDATING:"$file
    conda env update --file ${file} --prune
done

