# SmartCompress FS

### Adaptive File System with Automatic Compression

SmartCompress FS is a Python-based intelligent file-system utility designed to optimize disk usage by automatically identifying and compressing suitable files when available storage falls below a defined threshold.

The system prioritizes files based on factors such as file size and last-access time, performs lossless compression using Gzip/Zlib, and maintains metadata required for reliable restoration.

It combines real-time disk monitoring, automated compression, metadata management, logging, and a graphical interface into a single file-management workflow.

---

## Features

- **Real-time disk monitoring**
  - Continuously monitors available disk space.
  - Triggers compression when storage falls below a configurable threshold.

- **Intelligent file prioritization**
  - Evaluates files using size and last-access time.
  - Prioritizes larger and less-recently-accessed files for compression.

- **Lossless compression**
  - Supports Gzip and Zlib compression.
  - Preserves file contents for reliable decompression.

- **Metadata preservation**
  - Stores information such as original file paths and file types.
  - Uses JSON-based mappings to support safe restoration.

- **Automatic compression**
  - Reduces the need for manual disk cleanup.
  - Designed with low-storage and resource-constrained environments in mind.

- **Graphical User Interface**
  - Tkinter-based interface for interacting with compression and decompression operations.
  - Displays system operations through a user-friendly interface.

- **Logging**
  - Records compression and decompression operations.
  - Provides traceability for system actions.

- **Compressed-file marking**
  - Identifies files that have already been compressed to prevent unnecessary repeated operations.

---

## System Architecture

```text
                    ┌─────────────────────┐
                    │       Start         │
                    └──────────┬──────────┘
                               │
                               ▼
                  ┌─────────────────────────┐
                  │ Initialize Parameters   │
                  │ • Disk threshold        │
                  │ • File-system paths     │
                  │ • Compression settings  │
                  └────────────┬────────────┘
                               │
                               ▼
                  ┌─────────────────────────┐
                  │ Monitor Disk Space      │
                  │ Continuously             │
                  └────────────┬────────────┘
                               │
                               ▼
                       ┌───────────────┐
                       │ Below         │
                       │ Threshold?    │
                       └───────┬───────┘
                           No  │  Yes
                               │
                    ┌──────────┘
                    │
                    ▼
              Continue Monitoring

                               Yes
                                │
                                ▼
                  ┌─────────────────────────┐
                  │ Scan File System        │
                  │ for Candidate Files     │
                  └────────────┬────────────┘
                               │
                               ▼
                  ┌─────────────────────────┐
                  │ Evaluate Files          │
                  │ • File size             │
                  │ • Last-access time      │
                  └────────────┬────────────┘
                               │
                               ▼
                  ┌─────────────────────────┐
                  │ Update Disk Usage       │
                  │ Metrics                 │
                  └────────────┬────────────┘
                               │
                               ▼
                  ┌─────────────────────────┐
                  │ Compress Selected Files│
                  │ & Store Metadata        │
                  └────────────┬────────────┘
                               │
                               ▼
                     Continue Monitoring
