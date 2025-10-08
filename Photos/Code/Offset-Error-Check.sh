for dir in */; do
    echo "Processing directory: $dir"
    num_files=$(ls "$dir"/*.jpg 2>/dev/null | wc -l)
    echo "Number of JPEG files: $num_files"
    cd "$dir"
    exiftool -validate -warning -error -a *.jpg | grep "Bad offset for IFD0 StripByteCounts" | wc -l
    cd ..
done

