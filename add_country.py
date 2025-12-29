import json
import os
import sys

def load_features():
    """Load features from features.json"""
    try:
        with open("features.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: features.json not found")
        return None

def load_countries():
    """Load existing countries from countries.json"""
    try:
        with open("countries.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️  countries.json not found. Creating new file.")
        return {}

def create_country_template(features):
    """Create a country template with all features set to False"""
    country_template = {}
    
    for category, category_data in features.items():
        country_template[category] = {}
        
        for feature, feature_data in category_data.items():
            if feature_data.get("type") == "enum":
                # Create object with all enum values set to false
                country_template[category][feature] = {
                    value: False for value in feature_data["values"]
                }
            else:
                # Handle other types if needed in the future
                country_template[category][feature] = {}
    
    return country_template

def prompt_for_feature_values(country_name, features):
    """Interactive prompt to set feature values for the new country"""
    print(f"\n🎯 Setting up features for {country_name}:")
    print("=" * 60)
    
    country_data = create_country_template(features)
    
    # Group features by category for easier navigation
    features_by_category = {}
    for category, category_data in features.items():
        for feature, feature_data in category_data.items():
            if feature_data.get("type") == "enum":
                if category not in features_by_category:
                    features_by_category[category] = {}
                features_by_category[category][feature] = feature_data["values"]
    
    # Process each category
    for category, category_features in features_by_category.items():
        print(f"\n📁 {category.title()}:")
        print("-" * 40)
        
        for feature, values in category_features.items():
            print(f"\n  🔧 {feature.replace('_', ' ').title()}:")
            print(f"    Options: {', '.join(values)}")
            
            while True:
                print(f"    Enter numbers (comma-separated) or type 'all', 'none', or values:")
                for i, value in enumerate(values, 1):
                    print(f"      {i}. {value}")
                
                user_input = input(f"    Your choice: ").strip().lower()
                
                if not user_input:
                    print("    ⚠️  No input. Setting all to False.")
                    break
                
                elif user_input == 'none':
                    print("    ✅ Setting all to False.")
                    break
                
                elif user_input == 'all':
                    print("    ✅ Setting all to True.")
                    for value in values:
                        country_data[category][feature][value] = True
                    break
                
                else:
                    # Process the input
                    selected_values = []
                    
                    # Split by comma if multiple values
                    if ',' in user_input:
                        parts = [p.strip() for p in user_input.split(',')]
                        for part in parts:
                            if part.isdigit():
                                idx = int(part)
                                if 1 <= idx <= len(values):
                                    selected_values.append(values[idx-1])
                            elif part in values:
                                selected_values.append(part)
                    else:
                        # Single value
                        if user_input.isdigit():
                            idx = int(user_input)
                            if 1 <= idx <= len(values):
                                selected_values = [values[idx-1]]
                        elif user_input in values:
                            selected_values = [user_input]
                    
                    if selected_values:
                        print(f"    ✅ Setting {', '.join(selected_values)} to True.")
                        for value in values:
                            country_data[category][feature][value] = (value in selected_values)
                        break
                    else:
                        print("    ⚠️  Invalid input. Please try again.")
    
    return country_data

def save_countries(countries):
    """Save updated countries to countries.json"""
    with open("countries.json", "w", encoding="utf-8") as f:
        json.dump(countries, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Saved {len(countries)} countries to countries.json")

def show_country_summary(country_name, country_data):
    """Show a summary of the country's features"""
    print(f"\n📊 Summary for {country_name}:")
    print("=" * 60)
    
    for category, category_data in country_data.items():
        print(f"\n{category.title()}:")
        for feature, feature_data in category_data.items():
            if isinstance(feature_data, dict):
                true_values = [k for k, v in feature_data.items() if v is True]
                if true_values:
                    print(f"  • {feature.replace('_', ' ').title()}: {', '.join(true_values)}")
                else:
                    print(f"  • {feature.replace('_', ' ').title()}: None (all False)")

def main():
    print("=" * 60)
    print("🌍 ADD NEW COUNTRY TO GeoGuessr Narrower")
    print("=" * 60)
    
    # Load features structure
    features = load_features()
    if not features:
        return
    
    # Load existing countries
    countries = load_countries()
    
    # Ask for country name
    print("\n📝 Enter the name of the country to add:")
    print("   (Use the official English name, e.g., 'United States', 'Japan', 'United Kingdom')")
    
    while True:
        country_name = input("Country name: ").strip()
        
        if not country_name:
            print("❌ Country name cannot be empty. Please try again.")
            continue
        
        # Check if country already exists
        if country_name in countries:
            print(f"\n⚠️  '{country_name}' already exists in countries.json.")
            overwrite = input("   Do you want to overwrite it? (y/n): ").strip().lower()
            if overwrite != 'y':
                print("❌ Operation cancelled.")
                return
            else:
                print(f"✅ Will overwrite existing entry for '{country_name}'")
                break
        else:
            break
    
    # Ask if user wants to set features now or leave all as False
    print(f"\n🤔 Do you want to set feature values for {country_name} now?")
    print("   If you choose 'no', all features will be set to False.")
    
    while True:
        set_features = input("Set features now? (y/n): ").strip().lower()
        
        if set_features == 'y':
            # Interactive feature setup
            country_data = prompt_for_feature_values(country_name, features)
            break
        elif set_features == 'n':
            # Create template with all False
            country_data = create_country_template(features)
            print(f"\n✅ Created '{country_name}' with all features set to False.")
            break
        else:
            print("❌ Please enter 'y' for yes or 'n' for no.")
    
    # Add the country to the countries dictionary
    countries[country_name] = country_data
    
    # Save the updated countries
    save_countries(countries)
    
    # Show summary
    show_country_summary(country_name, country_data)
    
    print("\n" + "=" * 60)
    print(f"✅ Successfully added '{country_name}' to countries.json!")
    print("=" * 60)
    
    # Optional: Show quick stats
    print(f"\n📈 Quick Stats:")
    print(f"   • Total countries: {len(countries)}")
    
    # Count true features for the new country
    true_count = 0
    total_count = 0
    for category, category_data in country_data.items():
        for feature, feature_data in category_data.items():
            if isinstance(feature_data, dict):
                for value in feature_data.values():
                    total_count += 1
                    if value:
                        true_count += 1
    
    print(f"   • {country_name} has {true_count}/{total_count} features set to True")

if __name__ == "__main__":
    main()