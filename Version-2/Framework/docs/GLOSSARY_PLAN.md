# HSTL Photo Framework Glossary Development Plan

## Overview

This document outlines the plan for creating a comprehensive glossary for the HSTL Photo Framework project. The glossary will serve as a reference for both technical users and non-technical staff working with the framework.

## 1. Glossary Scope & Structure

### Primary Categories

1. **Core Concepts** - Framework architecture and fundamental principles
2. **Processing Pipeline** - 8-step workflow terminology  
3. **Data & File Types** - Input/output formats and metadata structures
4. **Technical Components** - Classes, modules, and system elements
5. **User Interface** - GUI and CLI terminology
6. **Configuration & Management** - Settings and batch management terms

### Target Audience

- **Technical Users**: Developers, system administrators
- **Non-Technical Users**: Archivists, photo collection managers
- **New Users**: People learning the framework for the first time

## 2. Key Terms Identified

### Core Concepts
- **Batch** - A single photo collection processing job with dedicated directories
- **Pipeline** - Sequential execution of 8 processing steps
- **ProcessingContext** - Shared data bus between pipeline steps
- **Framework** - Umbrella application managing the complete HSTL workflow

### Processing Steps (1-8)
1. **Google Spreadsheet Preparation** - Collaborative metadata setup
2. **CSV Conversion** - Google Worksheet to CSV conversion via `g2c.py`
3. **Unicode Filtering** - Text encoding cleanup and validation
4. **TIFF Conversion** - 16-bit to 8-bit image format conversion
5. **Metadata Embedding** - IPTC metadata injection into TIFF files
6. **JPEG Conversion** - TIFF to JPEG format conversion
7. **JPEG Resizing** - 800x800 pixel constraint application
8. **Watermarking** - Copyright watermark application to restricted images

### Data Structures
- **BatchRegistry** - Central inventory of all processing batches
- **ConfigManager** - YAML configuration file handler
- **StepProcessor** - Abstract base class for processing steps
- **PathManager** - Directory path management utility
- **ValidationResult** - Input/output validation data structure

### File Types
- **TIFF** - High-quality archival image format
- **JPEG** - Web-friendly compressed image format
- **CSV** - Metadata storage format from Google Sheets
- **YAML** - Configuration file format

### Metadata Fields (IPTC)
- **Accession Number** - Unique image identifier (`ObjectName`)
- **Headline** - Image title from spreadsheet
- **Caption-Abstract** - Image description (`Scopenote`)
- **By-line** - Photographer name
- **CopyrightNotice** - Usage restrictions
- **DateCreated** - Image creation date

## 3. Glossary Organization Structure

```
docs/GLOSSARY.md
├── 1. Core Framework Concepts
├── 2. Processing Pipeline Terminology  
├── 3. Data & File Formats
├── 4. Technical Architecture
├── 5. User Interface Terms
├── 6. Configuration & Management
├── 7. Acronyms & Abbreviations
└── 8. Cross-Reference Index
```

## 4. Implementation Strategy

### Phase 1: Core Terms Extraction
- [ ] Scan all `.py` files for class names, methods, and key variables
- [ ] Extract terminology from existing documentation
- [ ] Identify IPTC metadata field mappings from DATA_DICTIONARY.md

### Phase 2: Definition Development
- [ ] Write clear, concise definitions for each term
- [ ] Include context of usage within the framework
- [ ] Add code examples where helpful
- [ ] Cross-reference related terms

### Phase 3: Integration & Maintenance
- [ ] Link glossary from main README.md
- [ ] Add glossary references in relevant documentation
- [ ] Establish update process for new terms

## 5. Recommended Format

Each glossary entry should include:

```markdown
### **Term**

**Definition:** Clear, concise explanation of what the term means.

**Context:** How and where it's used in the framework.

**Related Terms:** Term1, Term2, Term3

**Example:** 
```python
# Code snippet or usage scenario
```
```

## 6. Priority Terms for Initial Release

### Essential (High Priority)
- Batch, Pipeline, ProcessingContext, StepProcessor, ConfigManager, PathManager
- TIFF, JPEG, CSV, YAML
- Framework, Configuration, Validation

### Important (Medium Priority)
- ValidationResult, BatchRegistry, Accession Number, Headline, CopyrightNotice
- Watermarking, Unicode Filtering, Metadata Embedding
- GUI, CLI, Step1-Step8

### Reference (Low Priority)
- Individual IPTC field names, GUI component names
- Specific CLI command terms, Error messages
- Version-specific terminology

## 7. Maintenance Process

### Adding New Terms
1. Identify new terminology during development
2. Determine appropriate category and priority
3. Write definition following established format
4. Add cross-references to related terms
5. Update cross-reference index

### Review Schedule
- **Monthly**: Check for new terms in code changes
- **Quarterly**: Review and refine existing definitions
- **Annually**: Complete glossary audit and reorganization

## 8. Success Metrics

- **Completeness**: All framework concepts documented
- **Clarity**: Non-technical users can understand technical terms
- **Accessibility**: Easy to navigate and find specific terms
- **Accuracy**: Definitions reflect current framework behavior
- **Maintainability**: Clear process for updates and additions

## 9. Integration Points

### Documentation Links
- README.md → Glossary
- USER_GUIDE.md → Relevant glossary sections
- DATA_DICTIONARY.md → Glossary cross-references
- API documentation → Glossary term links

### Code Integration
- Docstring references to glossary terms
- Comment explanations linking to glossary
- Error messages using glossary terminology

---

*This plan serves as the roadmap for creating a comprehensive, user-friendly glossary that supports all users of the HSTL Photo Framework.*