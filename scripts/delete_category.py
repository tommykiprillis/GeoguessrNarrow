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
        num_features = len(category_data)
        num_values = 0
        for feature_data in category_data.values():
            if feature_data.get("type") == "enum":
                num_values += len(feature_data.get("values", []))
        
        print(f"\n  {i}. {category.replace('_', ' ').title()}:")
        print(f"     Features: {num_features}")
        print(f"     Total values: {num_values}")
        if category_data:
            for feature, feature_data in category_data.items():
                if feature_data.get("type") == "enum":
                    values = feature_data.get("values", [])
                    print(f"     • {feature} → {', '.join(values)}")
    
    return categories

def select_category(features):
    """Let user select a category"""
    if not features:
        print("❌ No categories exist yet.")
        return None
    
    categories = list(features.keys())
    
    print("\n📋 Select a category to delete:")
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

def show_category_details(features, category_name):
    """Show detailed information about a category"""
    if category_name not in features:
        print(f"❌ Category '{category_name}' not found.")
        return
    
    category_data = features[category_name]
    print(f"\n📊 Category Details: '{category_name}'")
    print("=" * 60)
    
    print(f"Number of features: {len(category_data)}")
    
    total_values = 0
    for feature, feature_data in category_data.items():
        if feature_data.get("type") == "enum":
            values = feature_data.get("values", [])
            total_values += len(values)
            print(f"\n  {feature}:")
            print(f"    Type: {feature_data.get('type')}")
            print(f"    Values: {', '.join(values)}")
            print(f"    Count: {len(values)} values")
    
    print(f"\n📈 Total values in category: {total_values}")
    return len(category_data), total_values

def delete_category_from_features(features, category_name):
    """Delete a category from features"""
    if category_name not in features:
        return features, 0
    
    # Count what we're deleting
    num_features = len(features[category_name])
    num_values = 0
    for feature_data in features[category_name].values():
        if feature_data.get("type") == "enum":
            num_values += len(feature_data.get("values", []))
    
    # Delete the category
    del features[category_name]
    
    return features, num_features, num_values

def delete_category_from_countries(countries, category_name):
    """Delete a category from all countries"""
    countries_affected = 0
    
    for country_name, country_data in countries.items():
        if category_name in country_data:
            del country_data[category_name]
            countries_affected += 1
    
    return countries, countries_affected

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
    print("🗑️  DELETE CATEGORY FROM GeoGuessr Narrower")
    print("=" * 60)
    
    # Load existing features
    features = load_features()
    if features is None:
        return
    
    # Load existing countries
    countries = load_countries()
    if countries is None:
        return
    
    # Display existing categories
    display_categories(features)
    
    # Select category to delete
    category_name = select_category(features)
    if not category_name:
        return
    
    # Show category details
    num_features, num_values = show_category_details(features, category_name)
    
    # Calculate impact
    countries_count = len(countries)
    countries_with_category = sum(1 for country_data in countries.values() if category_name in country_data)
    
    # Show warning and get confirmation
    print(f"\n⚠️  🚨 EXTREME DANGER ZONE 🚨")
    print("=" * 60)
    print(f"\nYou are about to PERMANENTLY DELETE category '{category_name}'")
    print("\n📉 THIS WILL DELETE:")
    print(f"   • {num_features} features from features.json")
    print(f"   • {num_values} feature values")
    print(f"   • Category from {countries_with_category} out of {countries_count} countries")
    print(f"   • All related data from template.json")
    print("\n📌 THIS ACTION CANNOT BE UNDONE!")
    print("   There is no undo button. Once deleted, data is gone forever.")
    
    # First confirmation
    confirm1 = input(f"\nType 'DELETE' to proceed: ").strip()
    
    if confirm1 != 'DELETE':
        print("❌ Deletion cancelled (first confirmation failed).")
        return
    
    # Second confirmation
    print(f"\n⚠️  FINAL WARNING:")
    print(f"   You typed 'DELETE'. Are you ABSOLUTELY SURE?")
    print(f"   Category '{category_name}' and ALL its data will be PERMANENTLY LOST.")
    
    confirm2 = input(f"\nType 'YES-I-AM-SURE' to confirm deletion: ").strip()
    
    if confirm2 != 'YES-I-AM-SURE':
        print("❌ Deletion cancelled (second confirmation failed).")
        return
    
    # Perform deletion
    print(f"\n🔄 Deleting category '{category_name}'...")
    
    # Delete from features
    features, deleted_features, deleted_values = delete_category_from_features(features, category_name)
    print(f"✅ Deleted {deleted_features} features ({deleted_values} values) from features.json")
    
    # Delete from countries
    countries, affected_countries = delete_category_from_countries(countries, category_name)
    print(f"✅ Deleted category from {affected_countries} countries")
    
    # Save changes
    save_features(features)
    save_countries(countries)
    
    # Update template
    update_template()
    
    # Show final summary
    print("\n" + "=" * 60)
    print("📊 DELETION SUMMARY")
    print("=" * 60)
    
    print(f"\n✅ Successfully deleted category: '{category_name}'")
    print(f"📉 Deleted statistics:")
    print(f"   • Features removed: {deleted_features}")
    print(f"   • Values removed: {deleted_values}")
    print(f"   • Countries affected: {affected_countries}")
    
    # Show remaining categories
    if features:
        print(f"\n📁 Remaining categories: {len(features)}")
        for i, (category, category_data) in enumerate(features.items(), 1):
            print(f"  {i}. {category} ({len(category_data)} features)")
    else:
        print(f"\n⚠️  No categories remaining. The system is empty!")
    
    print("\n" + "=" * 60)
    print("✅ CATEGORY DELETION COMPLETE!")
    print("=" * 60)
    
    # Final warning about web interface
    print("\n💡 Remember to refresh your web browser to see the changes!")
    print("   The deleted category will no longer appear in the feature selection.")

if __name__ == "__main__":
    main()