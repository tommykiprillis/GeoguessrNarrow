# GeoGuessr Narrower

A web-based tool for narrowing down possible GeoGuessr countries based on visible features.

---

## Overview

**GeoGuessr Narrower** helps players identify potential countries by selecting observable features from Street View imagery. The application provides real-time matching against a database of country characteristics.

---

## Project Structure

### Core Files

- **app.py** — FastAPI backend server  
- **index.html** — Web interface  
- **script.js** — Frontend logic  
- **styles.css** — Styling with light/dark themes  

### Data Files

- **features.json** — Feature definitions (categories, features, values)  
- **countries.json** — Country-specific feature assignments  
- **template.json** — Empty template for new countries  

### Management Scripts

- **add_country.py** — Interactive script to add new countries  
- **add_feature.py** — Interactive script to add new features  
- **script_features_to_template.py** — Updates template and country files  
- **narrower.py** — Command-line testing tool  

---

## Features

- **Interactive Feature Selection** — Click-based interface to select observed features  
- **Real-time Matching** — Instant country matching with percentage scores  
- **Feature Management** — Extensible system for adding new countries and features  
- **Dark/Light Mode** — Theme toggle with persistent preference  
- **Visual Feedback** — Color-coded results based on match scores  

---

## Extensions

 - Using `add_feature.py` to add new categories and features
 - Using `add_country.py` to add the remaining countries
 - Running `script_feature_to_template.py` to assign new features to existing countries
 - Reloading FastAPI to apply changes

