import json
from typing import Dict, List

def load_countries(path: str) -> Dict:
    """Load country data from JSON file"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def narrow_countries(
    countries: Dict,
    selected_features: Dict[str, str]
) -> List[Dict]:
    """
    Returns countries sorted by match score
    Works with the new nested categories structure
    """
    results = []
    
    for country_name, country_data in countries.items():
        matched = 0
        total = len(selected_features)
        
        for feature_path, selected_value in selected_features.items():
            # Split the feature path by dot to get category and feature
            parts = feature_path.split('.')
            if len(parts) != 2:
                continue  # Skip invalid paths
            
            category, feature = parts
            
            # Navigate through the nested structure
            if category in country_data and feature in country_data[category]:
                feature_data = country_data[category][feature]
                # Check if the selected value exists and is True
                if selected_value in feature_data and feature_data[selected_value]:
                    matched += 1
        
        if matched > 0 and total > 0:
            score = matched / total
            results.append({
                "name": country_name,
                "matched": matched,
                "total": total,
                "score": score
            })
    
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


if __name__ == "__main__":
    # Test the functionality with the exact features from the problem
    countries = load_countries("countries.json")
    
    print("=" * 60)
    print("🧪 TESTING EXACT SCENARIO FROM THE PROBLEM")
    print("=" * 60)
    
    # Exact selected features from the problem
    selected_features = {
        "road.driving_side": "right",
        "road.inner_road_line_colour": "white",
        "road.outer_road_line_colour": "white",
        "google_camera.generation": "gen3"
    }
    
    print(f"\nSelected features:")
    for k, v in selected_features.items():
        print(f"  - {k}: {v}")
    
    matches = narrow_countries(countries, selected_features)
    
    print(f"\nResults:")
    for m in matches:
        print(f"  {m['name']}: {m['matched']}/{m['total']} ({m['score']:.0%})")
    
    print("\n" + "=" * 60)
    print("🔍 VERIFYING EACH FEATURE FOR EACH COUNTRY")
    print("=" * 60)
    
    for country_name, country_data in countries.items():
        print(f"\n{country_name}:")
        for feature_path, selected_value in selected_features.items():
            parts = feature_path.split('.')
            if len(parts) == 2:
                category, feature = parts
                if category in country_data and feature in country_data[category]:
                    feature_data = country_data[category][feature]
                    if selected_value in feature_data:
                        value = feature_data[selected_value]
                        status = "✅" if value else "❌"
                        print(f"  {status} {category}.{feature}.{selected_value}: {value}")
                    else:
                        print(f"  ❌ {category}.{feature}.{selected_value}: Value not found")
                else:
                    print(f"  ❌ {category}.{feature}: Category or feature not found")
    
    print("\n" + "=" * 60)
    print("EXPECTED RESULTS:")
    print("- United States: 3/4 (75%)")
    print("- Serbia: 4/4 (100%)")
    print("=" * 60)