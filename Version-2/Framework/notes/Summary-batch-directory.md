## Batch Data Directory Summary

I would like to develop a Batch Data Directory Summary feature that provides the user a snap shot of the existing files associated with the 'current batch'.    This feature would be called from the Tools pull down menu and would be called 'Batch Data Summary'.

Below is the Data Directory Tree structure:



[BatchName]/

├── input/

│   ├── tiff/              ← Selected TIFF images placed here

│   └── spreadsheet/       ← Selected Excel file placed here

├── output/

│   ├── csv/               → Exported CSV (Step 2)

│   ├── tiff_processed/    → Processed TIFFs (Step 4)

│   ├── jpeg/              → JPEG conversions (Step 6)

│   ├── jpeg_resized/      → Resized JPEGs (Step 7)

│   └── jpeg_watermarked/  → Watermarked JPEGs (Step 8)

├── reports/               → Validation and processing reports

├── logs/                  → Processing logs

└── config/



The Data Directory table provides an overview of the input files and output files generated during the batch processing workflow, including file counts and sizes.

|                  | Number of Files | Size   |
| ---------------- | --------------- | ------ |
| **Input**        |                 |        |
| SpreadSheet      | 1               | 34 KB  |
| TIFFs            | 55              | 2.6 GB |
|                  |                 |        |
| **Output**       |                 |        |
| Export CSV       | 3               | 23 KB  |
| Processed TIFFs  | 53              | 2.6 GB |
| JPEG Converted   | 53              | 24 5MB |
| JPEG Resized     | 53              | 245 MB |
| JPEG WaterMarked | 53              | 245 MB |
|                  |                 |        |
| Reports          | 5               | 58 KB  |
| Logs             | 3               | 67 KB  |
| Config           | 1               | 5 KB   |
|                  |                 |        |
| **Total**        |                 | 2.9 GB |
