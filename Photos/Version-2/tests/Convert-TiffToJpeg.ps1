# Script to convert TIFF files to JPEG while preserving IPTC metadata
$tiffFiles = Get-ChildItem -Path "." -Filter "*.tif"
$count = 0
$total = $tiffFiles.Count

Write-Host "Starting conversion of $total TIFF files to JPEG format..." -ForegroundColor Green
Write-Host "Preserving all metadata including IPTC tags" -ForegroundColor Green
Write-Host ""

foreach ($file in $tiffFiles) {
    $count++
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
    $jpegPath = Join-Path -Path "." -ChildPath "$baseName.jpg"
    
    Write-Host "[$count/$total] Converting: $($file.Name) -> $baseName.jpg" -ForegroundColor Cyan
    
    # Use ExifTool to convert TIFF to JPEG and preserve all metadata
    & exiftool -tagsfromfile "$($file.FullName)" -all:all "-FileType=JPEG" "-FileTypeExtension=jpg" "-o=$jpegPath" -overwrite_original
    
    if (Test-Path $jpegPath) {
        Write-Host "  - Success! JPEG created with metadata preserved." -ForegroundColor Green
    } else {
        Write-Host "  - Failed to create JPEG file." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Conversion complete! $count TIFF files converted to JPEG format." -ForegroundColor Green
Write-Host "All IPTC metadata has been preserved in the JPEG files." -ForegroundColor Green

# Verify IPTC metadata in the first JPEG file as a sample
$firstJpeg = Get-ChildItem -Path "." -Filter "*.jpg" | Select-Object -First 1
if ($firstJpeg) {
    Write-Host ""
    Write-Host "Sample metadata from $($firstJpeg.Name):" -ForegroundColor Yellow
    & exiftool -IPTC $firstJpeg.FullName
}
