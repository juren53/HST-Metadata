# ✅ CORRECT PowerShell hashtable syntax
$row3_mapping = @{
    'Title' = 'Headline'
    'Accession Number' = 'ObjectName'
    'Restrictions' = 'CopyrightNotice'
    'Scopenote' = 'Caption-Abstract'
    'Related Collection' = 'Source'
    'Source Photographer' = 'By-line'
    'Institutional Creator' = 'By-lineTitle'
}

# Example of how to use it
Write-Host "Column Mappings:"
$row3_mapping.GetEnumerator() | ForEach-Object {
    Write-Host "  '$($_.Key)' -> '$($_.Value)'"
}

Write-Host "`nThis mapping is already implemented in your enhanced google-to-csv.py script!"
Write-Host "It automatically detects these column headers and maps them correctly."
