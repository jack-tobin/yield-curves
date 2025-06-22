# Changelog

All notable changes to the Yield Curves Analysis Application will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Support for additional countries (US, UK, FR, IT)
- Advanced analytics (duration, convexity calculations)
- PDF report generation
- API documentation with OpenAPI/Swagger

## [0.1.0] - 2025-06-22

### 🎉 Initial Release

This is the first production release of the Yield Curves Analysis Application, located at https://yield-curves-app.onrender.com/

### Added

#### Core Features
- **User Authentication System**
  - User registration and login functionality
  - Personal analysis workspace per user

- **Analysis Management**
  - Create and manage named analysis projects
  - Delete analysis projects with confirmation
  - Analysis listing with creation/update timestamps

- **Bond Data Analysis**
  - Support for German government bonds (DE)
  - Bond scatter creation by country and date
  - Individual bond data display (ISIN, maturity, coupon, yield)

- **Yield Curve Calibration**
  - QuantLib integration for professional-grade calculations
  - Svensson model fitting for yield curve construction
  - Zero rate curve generation

- **Data Visualization**
  - Zero curve overlay functionality
  - Multi-curve comparison capabilities

#### Technical Infrastructure
- **Django 5.2+ Backend**
  - PostgreSQL database integration
  - Comprehensive data models for bonds and metrics
  - Error handling and validation

- **QuantLib Engine**
  - Support for fixed-rate and zero-coupon bonds

- **Database Schema**
  - Historical bond metrics

- **Deployment Ready**
  - Docker containerization
  - Render.com deployment configuration

#### API Endpoints
- `GET /analyses/` - List user analyses
- `POST /analyses/create/` - Create new analysis
- `DELETE /analyses/{id}/` - Delete analysis
- `POST /analyses/{id}/scatters/` - Add bond scatter
- `DELETE /analyses/{id}/scatters/{scatter_id}/` - Remove bond scatter
- `POST /analyses/{id}/selected-data/` - Get selected scatter data
- `GET /analyses/{id}/scatters/{scatter_id}/zero-curve/` - Generate zero curve
- `GET /bond-date-range/` - Get available data date range

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
- **Containerized Deployment**: Docker-based deployment with multi-stage builds
- **Cloud Database**: PostgreSQL on Render.com with Frankfurt region
- **Static File Handling**: WhiteNoise for production static file serving
- **Process Management**: Gunicorn WSGI server
- **Development Tools**: Comprehensive development environment with uv package manager

---
