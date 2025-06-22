# Yield Curves Analysis Application

A web application for analyzing government bond yields and curves. Built with Django and QuantLib, this application allows users to visualize bond data and calibrate yield curves.

## 🚀 Live Demo

The application is available at: **https://yield-curves-app.onrender.com/**

## 📋 Features

### Core Functionality
- **Bond Data Analysis**: Import and analyze government bond market data
- **Yield Curve Calibration**: Fit Nelson-Siegel and Svensson curves to bond prices
- **Multi-Country Support**: Currently supports German (DE) government bonds
- **Interactive Visualizations**: Plot yield curves and bond scatter data
- **Historical Analysis**: Compare yield curves across different dates
- **User Management**: Secure user authentication and personal analysis storage

## Data Sources

- **Bundsbank Government bond market data**

## 🛠️ Technology Stack

- **Backend**: Django 5.2+ (Python)
- **Database**: PostgreSQL
- **Curve Fitting Engine**: QuantLib
- **Data Processing**: Pandas, NumPy
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: Docker, Render.com
- **Environment Management**: uv

## 📊 How It Works

1. **Create Analysis**: Users create named analysis projects
2. **Add Bond Scatters**: Select country and date combinations for analysis
3. **View Bond Data**: Examine individual bond characteristics (ISIN, maturity, coupon, yield)
4. **Generate Curves**: Calibrate zero curves using Svensson fitting methods
5. **Compare Results**: Overlay multiple curves for comparative analysis

## 🏗️ Project Structure

```
yield-curves/
├── src/
│   ├── apps/
│   │   ├── accounts/         # User authentication
│   │   └── yield_curves/     # Core yield curve functionality
│   ├── curve_engine/         # QuantLib integration
│   ├── config/               # Django settings
│   ├── templates/            # HTML templates
│   └── static/               # CSS, JS, images
├── tests/                    # Test suite
├── scripts/                  # Utility scripts
└── Dockerfile                # Container configuration
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- uv (Python package manager)
- Docker (optional)
- PostgreSQL database

## 📈 Usage Guide

### Creating Your First Analysis

1. **Sign up** for an account or log in
2. **Create Analysis**: Click "New Analysis" and give it a descriptive name
3. **Add Bond Scatter**:
   - Select a country (e.g., "DE" for Germany)
   - Choose a date for which you want bond data
   - Click "Add Scatter"
4. **View Bond Data**: Click on your scatter to see individual bond details
5. **Generate Zero Curve**: Use the curve generation feature to fit a yield curve

### Supported Countries

Currently supported:
- **DE**: Germany (German government bonds - Bunds)

*Additional countries can be added by extending the calendar support in the curve engine.*

## 🐛 Known Issues

- Currently limited to German government bonds

## 🔮 Future Enhancements

- [ ] Support for additional countries (US, UK, FR, IT)
- [ ] Advanced curve models (B-splines, kernel methods)
- [ ] Advanced analytics (duration, convexity)
- [ ] Export functionality (PDF reports, Excel)
- [ ] API documentation with OpenAPI/Swagger
