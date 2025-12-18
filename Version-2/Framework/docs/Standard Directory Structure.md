HSTL Photo Metadata System
Standard Directory Structure:

┌────────────────────────────────────────────────────────────────────────────────┐
│ C:\Data\HSTL_Batches\                                                          │
│ ├── {batch_name}\          # Assigned as batch is created                      │
│ │   ├── input\                                                                 │
│ │   │   ├── tiff\          # Place source TIFFs here                           │
│ │   │   └── spreadsheet\                                                       │
│ │   ├── output\                                                                │
│ │   │   ├── csv\                                                               │
│ │   │   ├── tiff_processed\                                                    │
│ │   │   ├── jpeg\                                                              │
│ │   │   ├── jpeg_resized\                                                      │
│ │   │   └── jpeg_watermarked\                                                  │
│ │   ├── logs\                                                                  │
│ │   ├── reports\                                                               │
│ │   └── config\                                                                │
│ │       └── project_config.yaml                                                │
└────────────────────────────────────────────────────────────────────────────────┘


