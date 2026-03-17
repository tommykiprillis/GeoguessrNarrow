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
        print("❌ Error: countries.json not found")
        return None

def save_features(features):
    """Save features to features.json"""
    with open("features.json", "w", encoding="utf-8") as f:
        json.dump(features, f, indent=4, ensure_ascii=False)
    print("✅ Saved updated features to features.json")

def save_countries(countries):
    """Save updated countries to countries.json"""
    with open("countries.json", "w", encoding="utf-8") as f:
        json.dump(countries, f, indent=4, ensure_ascii=False)
    print("✅ Saved updated countries to countries.json")

def display_categories(features):
    """Display existing categories and their features"""
    print("\n📂 Existing Categories:")
    print("-" * 40)
    
    if not features:
        print("  No categories found.")
        return []
    
    categories = []
    for i, (category, category_data) in enumerate(features.items(), 1):
        categories.append(category)
        print(f"\n  {i}. {category.title()}:")
        if category_data:
            for feature, feature_data in category_data.items():
                if feature_data.get("type") == "enum":
                    values = feature_data.get("values", [])
                    print(f"     • {feature} → {', '.join(values)}")
                else:
                    print(f"     • {feature} (type: {feature_data.get('type', 'unknown')})")
        else:
            print("     (empty category)")
    
    return categories

def select_category(features):
    """Let user select a category"""
    if not features:
        print("❌ No categories exist yet.")
        return None
    
    categories = list(features.keys())
    
    print("\n📋 Select a category:")
    for i, category in enumerate(categories, 1):
        num_features = len(features[category])
        print(f"  {i}. {category.replace('_', ' ').title()} ({num_features} features)")
    
    while True:
        try:
            choice = input(f"\nEnter choice (1-{len(categories)}): ").strip()
            
            if not choice:
                print("❌ Please enter a choice.")
                continue
            
            choice = int(choice)
            
            if 1 <= choice <= len(categories):
                selected_category = categories[choice - 1]
                display_name = selected_category.replace('_', ' ').title()
                print(f"✅ Selected category: '{display_name}'")
                return selected_category
            else:
                print(f"❌ Please enter a number between 1 and {len(categories)}")
        except ValueError:
            print("❌ Please enter a valid number.")

def select_feature(category, features):
    """Let user select a feature from a category"""
    if not features[category]:
        print(f"❌ Category '{category}' has no features.")
        return None
    
    feature_list = list(features[category].keys())
    
    print(f"\n📋 Features in '{category.replace('_', ' ').title()}':")
    for i, feature in enumerate(feature_list, 1):
        feature_data = features[category][feature]
        if feature_data.get("type") == "enum":
            values = feature_data.get("values", [])
            print(f"  {i}. {feature} ({len(values)} values)")
        else:
            print(f"  {i}. {feature}")
    
    while True:
        try:
            choice = input(f"\nEnter choice (1-{len(feature_list)}): ").strip()
            
            if not choice:
                print("❌ Please enter a choice.")
                continue
            
            choice = int(choice)
            
            if 1 <= choice <= len(feature_list):
                selected_feature = feature_list[choice - 1]
                print(f"✅ Selected feature: '{selected_feature}'")
                return selected_feature
            else:
                print(f"❌ Please enter a number between 1 and {len(feature_list)}")
        except ValueError:
            print("❌ Please enter a valid number.")

def show_feature_details(category, feature, features):
    """Show detailed information about a feature"""
    if category not in features or feature not in features[category]:
        print(f"❌ Feature '{feature}' not found in category '{category}'")
        return
    
    feature_data = features[category][feature]
    print(f"\n📊 Feature Details:")
    print("-" * 40)
    print(f"  Category: {category}")
    print(f"  Feature: {feature}")
    print(f"  Type: {feature_data.get('type', 'unknown')}")
    
    if feature_data.get("type") == "enum":
        values = feature_data.get("values", [])
        print(f"  Values: {', '.join(values)}")
        print(f"  Number of values: {len(values)}")

def delete_feature_from_countries(category, feature, countries):
    """Remove a feature from all countries"""
    countries_affected = 0
    
    for country_name, country_data in countries.items():
        if category in country_data and feature in country_data[category]:
            del country_data[category][feature]
            countries_affected += 1
            
            # Check if category is now empty
            if not country_data[category]:
                del country_data[category]
    
    return countries_affected

def delete_feature_and_category(category, feature, features, countries):
    """Delete a feature and its category if it's the only feature"""
    print(f"\n⚠️  WARNING: '{feature}' is the only feature in category '{category}'")
    print("   Deleting it will also delete the entire category from:")
    print("   - features.json")
    print("   - countries.json (all countries)")
    print("   - template.json (when regenerated)")
    
    confirm = input(f"\nDelete the entire '{category}' category? (y/N): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Deletion cancelled.")
        return False
    
    # Delete category from features
    del features[category]
    print(f"✅ Deleted category '{category}' from features.json")
    
    # Delete category from all countries
    countries_affected = 0
    for country_name, country_data in countries.items():
        if category in country_data:
            del country_data[category]
            countries_affected += 1
    
    print(f"✅ Deleted category from {countries_affected} countries")
    return True

def delete_single_feature(category, feature, features, countries):
    """Delete a single feature without deleting the category"""
    print(f"\n⚠️  WARNING: You are about to delete feature '{feature}'")
    print("   This will delete it from:")
    print("   - features.json")
    print("   - countries.json (all countries)")
    print("   - template.json (when regenerated)")
    
    confirm = input(f"\nDelete feature '{feature}'? (y/N): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Deletion cancelled.")
        return False
    
    # Delete feature from features
    del features[category][feature]
    print(f"✅ Deleted feature '{feature}' from features.json")
    
    # Delete feature from all countries
    countries_affected = delete_feature_from_countries(category, feature, countries)
    print(f"✅ Deleted feature from {countries_affected} countries")
    return True

def update_template():
    """Update template.json after deletion"""
    print("\n🔄 Updating template.json...")
    
    # Check if the template script exists
    if not os.path.exists("script_features_to_template.py"):
        print("⚠️  script_features_to_template.py not found.")
        print("   You'll need to run it manually to update template.json.")
        return False
    
    try:
        # Import and run the template script
        sys.path.insert(0, os.getcwd())
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "script_features_to_template", 
            "script_features_to_template.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if hasattr(module, 'main'):
            module.main()
            print("✅ Successfully updated template.json")
            return True
        else:
            print("❌ Could not find main function in script_features_to_template.py")
            return False
    except Exception as e:
        print(f"❌ Failed to update template.json: {e}")
        return False

def main():
    print("=" * 60)
    print("🗑️  DELETE FEATURE FROM GeoGuessr Narrower")
    print("=" * 60)
    
    # Load existing features
    features = load_features()
    if features is None:
        return
    
    # Load existing countries
    countries = load_countries()
    if countries is None:
        return
    
    # Display existing structure
    display_categories(features)
    
    # Select category
    category = select_category(features)
    if not category:
        return
    
    # Select feature
    feature = select_feature(category, features)
    if not feature:
        return
    
    # Show feature details
    show_feature_details(category, feature, features)
    
    # Check if this is the only feature in the category
    is_only_feature = len(features[category]) == 1
    
    # Delete the feature
    if is_only_feature:
        success = delete_feature_and_category(category, feature, features, countries)
    else:
        success = delete_single_feature(category, feature, features, countries)
    
    if not success:
        return
    
    # Save changes
    save_features(features)
    save_countries(countries)
    
    # Update template
    update_template()
    
    # Show summary
    print("\n" + "=" * 60)
    print("📊 DELETION SUMMARY")
    print("=" * 60)
    
    if is_only_feature:
        print(f"✅ Deleted entire category: '{category}'")
    else:
        print(f"✅ Deleted feature: '{feature}' from category: '{category}'")
    
    print(f"\n📈 Remaining structure:")
    display_categories(features)
    
    print("\n" + "=" * 60)
    print("✅ FEATURE DELETION COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    main()