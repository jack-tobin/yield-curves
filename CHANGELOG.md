# Changelog

All notable changes to the Yield Curves Analysis Application will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-06-22

- **User Authentication**

- **Analysis CRUD**

- **Bond Yield Scatter CRUD**
  - Support for German government bonds (DE)

- **Yield Curve Calibration**
  - QuantLib integration
  - Currently support Nelson Siegel Svensson model

### Technical Specifications

#### Dependencies
- Python 3.10+ runtime
- Django 5.2+ web framework
- QuantLib 1.38+ quant library
- PostgreSQL 16 database
- NumPy and Pandas for data processing

#### Data Sources
- Bundsbank Government bond market data

#### Supported Markets
- Germany (DE) - German government bonds (Bunds)

### Infrastructure
- **Containerized Deployment**: Docker deployment with multi-stage build
- **Cloud**: Deployed web service and PostgreSQL database using Render cloud
- **Static File**: WhiteNoise for production static file serving
- **Development Tools**: Comprehensive development environment with uv package manager

---
