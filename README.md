# Yield Curves App

A web application for analyzing government bond yield curves, built with Django and QuantLib.

The application is available at: **https://yield-curves-app.onrender.com/**

## Features

### Core Functionality
- **Bond Data Analysis**: Import and analyze government bond market data
- **Yield Curve Calibration**: Fit Nelson-Siegel-Svensson curves to bond yields
- **Multi-Country Support**: Currently supports German (DE) government bonds
- **Historical Data**: Compare yield curves across dates

## Data Sources

- **Bundsbank Government bond market data**

## Technology Stack

- **Backend**: Django 5.2+ (Python)
- **Database**: PostgreSQL
- **Curve Fitting Engine**: QuantLib
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: Docker, Render
- **Environment Management**: uv

### Supported Countries

- **DE**: Germany

## Known Issues

- Currently limited to German government bonds

## Future Enhancements

- [ ] Support for additional countries (US, UK, FR, IT)
- [ ] Advanced curve models (B-splines, kernel methods)
- [ ] API documentation with OpenAPI/Swagger
