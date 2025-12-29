import json
import os
import sys

def generate_template(features_path: str, template_path: str, countries_path: str = "countries.json"):
    """
    Convert features.json to template.json format and update countries.json
    """
    # Load features
    with open(features_path, 'r', encoding='utf-8') as f:
        features = json.load(f)
    
    # Generate template
    template = {"COUNTRY_NAME": {}}
    
    for category, category_data in features.items():
        template["COUNTRY_NAME"][category] = {}
        
        for feature, feature_data in category_data.items():
            if feature_data.get("type") == "enum":
                # Create object with all enum values set to false
                template["COUNTRY_NAME"][category][feature] = {
                    value: False for value in feature_data["values"]
                }
            else:
                # Handle other types if needed in the future
                template["COUNTRY_NAME"][category][feature] = {}
    
    # Save template
    with open(template_path, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Template generated successfully at {template_path}")
    
    # Now update countries.json if it exists
    try:
        with open(countries_path, 'r', encoding='utf-8') as f:
            countries = json.load(f)
    except FileNotFoundError:
        print(f"[WARNING] {countries_path} not found. Skipping country updates.")
        return
    
    # First, add the structure with all false values
    updated_countries, new_features_by_country = add_feature_structure(countries, features)
    
    # Then prompt user to set values for new features
    if new_features_by_country:
        print(f"\n[NEW FEATURES] New features detected! Let's set them up:")
        updated_countries = prompt_for_new_features(updated_countries, features, new_features_by_country)
    else:
        print(f"\n[OK] No new features to add. All features already exist in {countries_path}")
    
    # Save updated countries
    with open(countries_path, 'w', encoding='utf-8') as f:
        json.dump(updated_countries, f, indent=4, ensure_ascii=False)
    
    print(f"[OK] {countries_path} updated successfully")


def add_feature_structure(countries: dict, features: dict):
    """
    Add missing feature structure to countries and track what's new
    Returns: (updated_countries, new_features_by_country)
    """
    updated = {}
    new_features_by_country = {}
    
    for country_name, country_data in countries.items():
        updated[country_name] = country_data.copy()
        new_features_by_country[country_name] = []
        
        # Add missing categories and features
        for category, category_data in features.items():
            # Ensure category exists in country
            if category not in updated[country_name]:
                updated[country_name][category] = {}
            
            # Add missing features in this category
            for feature, feature_data in category_data.items():
                if feature_data.get("type") == "enum":
                    # Check if feature exists
                    feature_exists = feature in updated[country_name][category]
                    
                    if not feature_exists:
                        # Create new feature with all values set to False
                        updated[country_name][category][feature] = {
                            value: False for value in feature_data["values"]
                        }
                        new_features_by_country[country_name].append((category, feature))
                    else:
                        # Feature exists, check for missing enum values
                        existing_feature = updated[country_name][category][feature]
                        for value in feature_data["values"]:
                            if value not in existing_feature:
                                existing_feature[value] = False
                                # Track that we added a new enum value
                                new_features_by_country[country_name].append((category, feature))
    
    return updated, new_features_by_country


def prompt_for_new_features(countries: dict, features: dict, new_features_by_country: dict) -> dict:
    """
    Interactive prompt to set values for new features
    """
    updated_countries = countries.copy()
    
    # Group features by category
    features_by_category = {}
    for category, category_data in features.items():
        for feature, feature_data in category_data.items():
            if feature_data.get("type") == "enum":
                if category not in features_by_category:
                    features_by_category[category] = {}
                features_by_category[category][feature] = feature_data["values"]
    
    # Get list of all countries
    country_names = list(countries.keys())
    
    print("\n" + "="*60)
    print("QUICK SETUP: New Features Configuration")
    print("="*60)
    
    # Process each country
    for country_name in country_names:
        if not new_features_by_country.get(country_name):
            continue
        
        print(f"\n[CONFIGURING] {country_name}:")
        print("-" * 40)
        
        # Group new features by category
        features_by_cat = {}
        for category, feature in new_features_by_country[country_name]:
            if category not in features_by_cat:
                features_by_cat[category] = []
            features_by_cat[category].append(feature)
        
        # Process each category
        for category, feature_list in features_by_cat.items():
            print(f"\n  [CATEGORY] {category.title()}:")
            
            for feature in feature_list:
                values = features_by_category[category][feature]
                print(f"\n    [FEATURE] {feature.replace('_', ' ').title()}:")
                print(f"      Options: {', '.join(values)}")
                
                # Ask user which values are true
                while True:
                    print(f"      Enter numbers (comma-separated) or type 'all', 'none', or values:")
                    for i, value in enumerate(values, 1):
                        print(f"        {i}. {value}")
                    
                    user_input = input(f"      Your choice: ").strip().lower()
                    
                    if not user_input:
                        print("      [INFO] No input. Setting all to False.")
                        # Set all to False
                        for value in values:
                            updated_countries[country_name][category][feature][value] = False
                        break
                    
                    elif user_input == 'none':
                        print("      [OK] Setting all to False.")
                        for value in values:
                            updated_countries[country_name][category][feature][value] = False
                        break
                    
                    elif user_input == 'all':
                        print("      [OK] Setting all to True.")
                        for value in values:
                            updated_countries[country_name][category][feature][value] = True
                        break
                    
                    else:
                        # Try to parse as numbers
                        if ',' in user_input:
                            parts = [p.strip() for p in user_input.split(',')]
                            try:
                                # Try to parse as numbers
                                selected_indices = [int(p) for p in parts if p.isdigit()]
                                selected_values = []
                                
                                for idx in selected_indices:
                                    if 1 <= idx <= len(values):
                                        selected_values.append(values[idx-1])
                                
                                if selected_indices and not selected_values:
                                    print("      [ERROR] Invalid numbers. Please try again.")
                                    continue
                                
                                if selected_indices:
                                    # User entered numbers
                                    print(f"      [OK] Setting {', '.join(selected_values)} to True.")
                                    for value in values:
                                        updated_countries[country_name][category][feature][value] = (value in selected_values)
                                    break
                                else:
                                    # User might have entered values directly
                                    selected_values = []
                                    for part in parts:
                                        if part in values:
                                            selected_values.append(part)
                                    
                                    if selected_values:
                                        print(f"      [OK] Setting {', '.join(selected_values)} to True.")
                                        for value in values:
                                            updated_countries[country_name][category][feature][value] = (value in selected_values)
                                        break
                                    else:
                                        print("      [ERROR] Invalid input. Please enter numbers or valid values.")
                                        continue
                            except ValueError:
                                # Not numbers, try as values
                                selected_values = []
                                for part in parts:
                                    if part in values:
                                        selected_values.append(part)
                                
                                if selected_values:
                                    print(f"      [OK] Setting {', '.join(selected_values)} to True.")
                                    for value in values:
                                        updated_countries[country_name][category][feature][value] = (value in selected_values)
                                    break
                                else:
                                    print("      [ERROR] Invalid input. Please try again.")
                                    continue
                        else:
                            # Single value
                            if user_input.isdigit():
                                idx = int(user_input)
                                if 1 <= idx <= len(values):
                                    selected_value = values[idx-1]
                                    print(f"      [OK] Setting {selected_value} to True.")
                                    for value in values:
                                        updated_countries[country_name][category][feature][value] = (value == selected_value)
                                    break
                                else:
                                    print("      [ERROR] Invalid number. Please try again.")
                                    continue
                            elif user_input in values:
                                print(f"      [OK] Setting {user_input} to True.")
                                for value in values:
                                    updated_countries[country_name][category][feature][value] = (value == user_input)
                                break
                            else:
                                print("      [ERROR] Invalid input. Please try again.")
                                continue
    
    print("\n" + "="*60)
    print("[OK] Configuration Complete!")
    print("="*60)
    
    return updated_countries


def show_summary(countries: dict, features: dict):
    """
    Show a summary of what was configured
    """
    print("\n[SUMMARY] Configuration Summary:")
    print("="*60)
    
    for country_name, country_data in countries.items():
        print(f"\n{country_name}:")
        for category, category_data in country_data.items():
            print(f"  {category.title()}:")
            for feature, feature_data in category_data.items():
                if isinstance(feature_data, dict):
                    true_values = [k for k, v in feature_data.items() if v is True]
                    if true_values:
                        print(f"    * {feature}: {', '.join(true_values)}")
                    else:
                        print(f"    * {feature}: None")


def main():
    # Default file paths
    features_path = "features.json"
    template_path = "template.json"
    countries_path = "countries.json"
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        features_path = sys.argv[1]
    if len(sys.argv) > 2:
        template_path = sys.argv[2]
    if len(sys.argv) > 3:
        countries_path = sys.argv[3]
    
    # Check if features.json exists
    if not os.path.exists(features_path):
        print(f"[ERROR] {features_path} not found")
        return
    
    # Generate template and update countries
    generate_template(features_path, template_path, countries_path)
    
    # Show summary
    try:
        with open(countries_path, 'r', encoding='utf-8') as f:
            countries = json.load(f)
        with open(features_path, 'r', encoding='utf-8') as f:
            features = json.load(f)
        show_summary(countries, features)
    except Exception as e:
        print(f"[WARNING] Could not show summary: {e}")


if __name__ == "__main__":
    main()