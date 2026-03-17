from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, List
import json
import os
from pathlib import Path

app = FastAPI()

# Get the directory where this script is located
BASE_DIR = Path(__file__).parent.parent

# Allow local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class NarrowRequest(BaseModel):
    selected_features: Dict[str, str]


def load_countries():
    """Load country data from JSON file"""
    file_path = BASE_DIR / "data" / "countries.json"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.post("/narrow")
def narrow(req: NarrowRequest):
    # Load fresh data on each request
    countries = load_countries()
    results = []
    
    print(f"\n📡 Received request with {len(req.selected_features)} features:")
    for key, value in req.selected_features.items():
        print(f"   - {key}: {value}")
    
    for country_name, country_data in countries.items():
        matched = 0
        total = len(req.selected_features)
        
        print(f"\n🔍 Checking {country_name}:")
        
        for feature_path, selected_value in req.selected_features.items():
            # Split the feature path by dot to get category and feature
            parts = feature_path.split('.')
            if len(parts) != 2:
                print(f"   ⚠️ Invalid feature path: {feature_path}")
                continue
            
            category, feature = parts
            
            # Navigate through the nested structure
            if category in country_data and feature in country_data[category]:
                feature_data = country_data[category][feature]
                # Check if the selected value exists and is True
                if selected_value in feature_data:
                    is_true = feature_data[selected_value]
                    print(f"   - {category}.{feature}.{selected_value}: {is_true}")
                    if is_true:
                        matched += 1
                        print(f"     ✅ Match!")
                    else:
                        print(f"     ❌ No match (False)")
                else:
                    print(f"   - {category}.{feature}.{selected_value}: ❌ Value not found in feature data")
            else:
                print(f"   - {category}.{feature}: ❌ Category or feature not found")
        
        print(f"   📊 Total matched: {matched}/{total}")
        
        if matched > 0 and total > 0:
            score = matched / total
            results.append({
                "name": country_name,
                "matched": matched,
                "total": total,
                "score": score
            })
    
    # Sort by score
    results.sort(key=lambda x: x["score"], reverse=True)
    
    print(f"\n📤 Returning {len(results)} results:")
    for r in results:
        print(f"   - {r['name']}: {r['matched']}/{r['total']} ({r['score']:.0%})")
    
    return results


@app.get("/")
def read_root():
    file_path = BASE_DIR / "src" / "index.html"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(file_path)


@app.get("/features.json")
def get_features():
    # Check if file exists
    file_path = BASE_DIR / "data" / "features.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="features.json not found")
    
    # Read and return the file content
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Return as JSON response
    return JSONResponse(content=json.loads(content))


@app.get("/styles.css")
def get_css():
    file_path = BASE_DIR / "src" / "styles.css"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="styles.css not found")
    return FileResponse(file_path, media_type="text/css")


@app.get("/script.js")
def get_js():
    file_path = BASE_DIR / "src" / "script.js"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="script.js not found")
    return FileResponse(file_path, media_type="application/javascript")


# Test endpoint to see if server is working
@app.get("/test")
def test():
    return {
        "status": "ok",
        "files": {
            "features.json": (BASE_DIR / "data" / "features.json").exists(),
            "countries.json": (BASE_DIR / "data" / "countries.json").exists(),
            "styles.css": (BASE_DIR / "src" / "styles.css").exists(),
            "script.js": (BASE_DIR / "src" / "script.js").exists(),
            "index.html": (BASE_DIR / "src" / "index.html").exists()
        },
        "base_directory": str(BASE_DIR),
        "working_directory": os.getcwd()
    }


# Country data inspection endpoint
@app.get("/debug/countries")
def debug_countries():
    try:
        countries = load_countries()
        return {
            "status": "ok",
            "countries": list(countries.keys()),
            "sample_data": {
                "United States": countries.get("United States", {}),
                "Serbia": countries.get("Serbia", {})
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}