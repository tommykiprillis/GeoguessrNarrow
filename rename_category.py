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
        print(f"\n  {i}. {category.replace('_', ' ').title()}:")
        print(f"     Features: {num_features}")
        if category_data:
            for feature, feature_data in category_data.items():
                if feature_data.get("type") == "enum":
                    values = feature_data.get("values", [])
                    print(f"     • {feature} ({len(values)} values)")
    
    return categories

def select_category(features):
    """Let user select a category"""
    if not features:
        print("❌ No categories exist yet.")
        return None
    
    categories = list(features.keys())
    
    print("\n📋 Select a category to rename:")
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

def get_new_category_name(features, old_name):
    """Get a new name for the category"""
    while True:
        new_name = input(f"\nEnter new name for '{old_name}' (snake_case recommended): ").strip().lower()
        
        if not new_name:
            print("❌ Category name cannot be empty.")
            continue
        
        if new_name == old_name:
            print("❌ New name is the same as current name.")
            continue
        
        # Check if new name already exists
        if new_name in features:
            print(f"❌ Category '{new_name}' already exists.")
            continue
        
        # Validate name (only letters, numbers, and underscores)
        if not all(c.isalnum() or c == '_' for c in new_name):
            print("❌ Category name can only contain letters, numbers, and underscores.")
            continue
        
        # Show preview
        print(f"\n📋 Preview of changes:")
        print(f"  Old name: {old_name}")
        print(f"  New name: {new_name}")
        print(f"  Features: {len(features[old_name])} features will be moved")
        
        confirm = input(f"\n✅ Rename category '{old_name}' to '{new_name}'? (y/N): ").strip().lower()
        
        if confirm == 'y':
            return new_name
        else:
            print("❌ Rename cancelled.")
            return None

def rename_category_in_features(features, old_name, new_name):
    """Rename a category in the features structure"""
    # Create new category with the old data
    features[new_name] = features[old_name]
    # Delete old category
    del features[old_name]
    
    print(f"✅ Renamed category in features.json")
    return features

def rename_category_in_countries(countries, old_name, new_name):
    """Rename a category in all countries"""
    countries_updated = 0
    
    for country_name, country_data in countries.items():
        if old_name in country_data:
            # Move category data to new name
            country_data[new_name] = country_data[old_name]
            # Delete old category
            del country_data[old_name]
            countries_updated += 1
    
    print(f"✅ Renamed category in {countries_updated} countries")
    return countries

def update_template():
    """Update template.json after renaming"""
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
    print("🏷️  RENAME CATEGORY IN GeoGuessr Narrower")
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
    
    # Select category to rename
    old_category_name = select_category(features)
    if not old_category_name:
        return
    
    # Get new category name
    new_category_name = get_new_category_name(features, old_category_name)
    if not new_category_name:
        return
    
    # Confirm one more time with full impact
    print(f"\n⚠️  FINAL CONFIRMATION:")
    print(f"   You are about to rename category '{old_category_name}' to '{new_category_name}'")
    print(f"   This will affect:")
    print(f"   - features.json: Category renamed")
    print(f"   - countries.json: {len(countries)} countries updated")
    print(f"   - template.json: Will be regenerated")
    print(f"   - Web interface: Category will appear with new name")
    
    confirm = input(f"\n🚨 PROCEED WITH RENAME? (type 'YES' to confirm): ").strip()
    
    if confirm != 'YES':
        print("❌ Rename cancelled.")
        return
    
    # Perform the rename
    print(f"\n🔄 Renaming category...")
    
    # Rename in features
    features = rename_category_in_features(features, old_category_name, new_category_name)
    
    # Rename in countries
    countries = rename_category_in_countries(countries, old_category_name, new_category_name)
    
    # Save changes
    save_features(features)
    save_countries(countries)
    
    # Update template
    update_template()
    
    # Show summary
    print("\n" + "=" * 60)
    print("📊 RENAME SUMMARY")
    print("=" * 60)
    
    print(f"\n✅ Successfully renamed:")
    print(f"   '{old_category_name}' → '{new_category_name}'")
    
    # Show updated category structure
    if new_category_name in features:
        num_features = len(features[new_category_name])
        print(f"\n📁 New category '{new_category_name}':")
        print(f"   Features: {num_features}")
        
        for feature, feature_data in features[new_category_name].items():
            if feature_data.get("type") == "enum":
                values = feature_data.get("values", [])
                print(f"   • {feature}: {len(values)} values")
    
    print("\n" + "=" * 60)
    print("✅ CATEGORY RENAME COMPLETE!")
    print("=" * 60)
    
    # Reminder about web interface
    print("\n💡 Remember to refresh your web browser to see the updated category name!")

if __name__ == "__main__":
    main()