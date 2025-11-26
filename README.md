# Purpose of this repository

A linked data event stream (LDES) is a collection of members described using the Resource Description Framework (RDF). The specification explains how a client can reproduce the history of an event stream and how it can then remain synchronised when new members are published.

## Before running the container

- Place your input files in a folder named `your_input_folder` in the current directory.
- (Optional) Place your templates in a folder named `your_input_folder_with_templates` in the current directory.
   if you don't provide this folder, the container will use the default templates.
- $pwd is the current directory where you have the input folder.

### To build the docker image:

```bash
docker build -t ror-records-ldes-builder .
```

### To run:

```bash
docker run --rm -v "$(pwd)/your_input_folder:/workspace" -v "$(pwd)/your_input_folder_with_templates:/src/templates" ror-records-ldes-builder
```

for windows users
```bash
docker run --rm -v /$(pwd)/your_input_folder:/workspace -v /$(pwd)/your_input_folder_with_templates:/src/templates ror-records-ldes-builder
```
```mermaid
flowchart TD

    A[Start] --> B[Loop over given folder]
    B --> C{Child folders match semver regex?}
    C -->|No| B
    C -->|Yes| D[Collect versioned folders]

    %% Latest must be checked BEFORE LDES
    D --> E{Latest folder exists?}
    E -->|No| F[Create latest folder]
    E -->|Yes| G[Continue]
    F --> G

    %% LDES folder check after latest
    G --> H{LDES folder exists?}
    H -->|No| I[Create LDES folder]
    H -->|Yes| J[Check existing LDES fragments]
    I --> K[Proceed]
    J --> K[Proceed]

    %% Step 2
    K --> L[Loop over versioned folders]

    L --> M[Find all JSON files in folder]

    %% Step 3
    M --> N[Extract version from JSON file]

    %% Step 4
    N --> O[Generate TTL file using Subyt]

    %% Step 5
    O --> P[Generate JSON-LD using RDFLib from TTL]

    %% Step 7 (workspace/latest symlink creation)
    P --> Q[Create relative symlink: ln -s ../version/x latest/x]

    %% Step 8
    Q --> R[Loop over versioned folders again]
    R --> S[Load all JSON-LD files for tfolder version into memory]

    S --> T[Use Subyt with ldes_fragment template]
    T --> U[Write version.ttl fragment into LDES folder]

    U --> V[End]
```
