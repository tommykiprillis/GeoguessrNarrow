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
        return None
    
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
    
    return feature_data

def update_feature_name(category, old_name, new_name, features, countries):
    """Update the name of a feature"""
    if new_name in features[category]:
        print(f"❌ Feature '{new_name}' already exists in category '{category}'")
        return False
    
    # Update in features.json
    features[category][new_name] = features[category][old_name]
    del features[category][old_name]
    
    # Update in all countries
    countries_updated = 0
    for country_name, country_data in countries.items():
        if category in country_data and old_name in country_data[category]:
            country_data[category][new_name] = country_data[category][old_name]
            del country_data[category][old_name]
            countries_updated += 1
    
    print(f"✅ Renamed feature '{old_name}' to '{new_name}'")
    print(f"✅ Updated {countries_updated} countries")
    return True

def update_feature_values(category, feature, features, countries):
    """Update the values of an enum feature"""
    feature_data = features[category][feature]
    
    if feature_data.get("type") != "enum":
        print(f"❌ Feature '{feature}' is not an enum type")
        return False
    
    current_values = feature_data.get("values", [])
    print(f"\n🔄 Current values: {', '.join(current_values)}")
    
    print("\nWhat would you like to do?")
    print("  1. Add new values")
    print("  2. Remove values")
    print("  3. Rename a value")
    print("  4. Replace all values")
    
    while True:
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            return add_feature_values(category, feature, features, countries, current_values)
        elif choice == "2":
            return remove_feature_values(category, feature, features, countries, current_values)
        elif choice == "3":
            return rename_feature_value(category, feature, features, countries, current_values)
        elif choice == "4":
            return replace_all_values(category, feature, features, countries, current_values)
        else:
            print("❌ Please enter a number between 1 and 4.")

def add_feature_values(category, feature, features, countries, current_values):
    """Add new values to an enum feature"""
    print(f"\n➕ Adding new values to '{feature}':")
    print(f"  Current values: {', '.join(current_values)}")
    print("\n  Enter new values one at a time.")
    print("  Press Enter on an empty line when done.")
    
    new_values = []
    while True:
        value = input(f"  New value {len(new_values) + 1}: ").strip()
        
        if not value:
            if len(new_values) == 0:
                print("  ⚠️  No new values added.")
                return False
            else:
                break
        
        if value in current_values or value in new_values:
            print(f"  ⚠️  Value '{value}' already exists. Skipping.")
            continue
        
        new_values.append(value)
        print(f"  ✅ Added '{value}'")
    
    # Add new values to features
    features[category][feature]["values"].extend(new_values)
    
    # Add new values to all countries (set to False by default)
    countries_updated = 0
    for country_name, country_data in countries.items():
        if category in country_data and feature in country_data[category]:
            for value in new_values:
                country_data[category][feature][value] = False
            countries_updated += 1
    
    print(f"\n✅ Added {len(new_values)} new values to '{feature}'")
    print(f"✅ Updated {countries_updated} countries")
    return True

def remove_feature_values(category, feature, features, countries, current_values):
    """Remove values from an enum feature"""
    print(f"\n➖ Removing values from '{feature}':")
    print(f"  Current values: {', '.join(current_values)}")
    print("\n  Enter values to remove (comma-separated):")
    for i, value in enumerate(current_values, 1):
        print(f"    {i}. {value}")
    
    while True:
        user_input = input("\n  Values to remove: ").strip()
        
        if not user_input:
            print("  ⚠️  No values removed.")
            return False
        
        # Parse input
        values_to_remove = []
        parts = [p.strip() for p in user_input.split(',')]
        
        for part in parts:
            if part.isdigit():
                idx = int(part)
                if 1 <= idx <= len(current_values):
                    values_to_remove.append(current_values[idx-1])
            elif part in current_values:
                values_to_remove.append(part)
        
        if values_to_remove:
            break
        else:
            print("  ❌ No valid values selected. Please try again.")
    
    # Confirm removal
    print(f"\n⚠️  You are about to remove: {', '.join(values_to_remove)}")
    print("   These values will be removed from:")
    print("   - features.json")
    print("   - all countries in countries.json")
    
    confirm = input("\n  Confirm removal? (y/N): ").strip().lower()
    
    if confirm != 'y':
        print("  ❌ Removal cancelled.")
        return False
    
    # Remove values from features
    new_values = [v for v in current_values if v not in values_to_remove]
    features[category][feature]["values"] = new_values
    
    # Remove values from all countries
    countries_updated = 0
    for country_name, country_data in countries.items():
        if category in country_data and feature in country_data[category]:
            for value in values_to_remove:
                if value in country_data[category][feature]:
                    del country_data[category][feature][value]
            countries_updated += 1
    
    print(f"\n✅ Removed {len(values_to_remove)} values from '{feature}'")
    print(f"✅ Updated {countries_updated} countries")
    return True

def rename_feature_value(category, feature, features, countries, current_values):
    """Rename a value in an enum feature"""
    print(f"\n✏️  Renaming a value in '{feature}':")
    print(f"  Current values: {', '.join(current_values)}")
    
    # Select value to rename
    print("\n  Select value to rename:")
    for i, value in enumerate(current_values, 1):
        print(f"    {i}. {value}")
    
    while True:
        try:
            choice = input(f"\n  Enter number (1-{len(current_values)}): ").strip()
            
            if not choice:
                print("  ❌ Renaming cancelled.")
                return False
            
            choice = int(choice)
            
            if 1 <= choice <= len(current_values):
                old_value = current_values[choice - 1]
                break
            else:
                print(f"  ❌ Please enter a number between 1 and {len(current_values)}")
        except ValueError:
            print("  ❌ Please enter a valid number.")
    
    # Get new value name
    while True:
        new_value = input(f"\n  New name for '{old_value}': ").strip()
        
        if not new_value:
            print("  ❌ Renaming cancelled.")
            return False
        
        if new_value == old_value:
            print("  ⚠️  New name is the same as old name.")
            continue
        
        if new_value in current_values:
            print(f"  ❌ Value '{new_value}' already exists.")
            continue
        
        break
    
    # Confirm rename
    print(f"\n⚠️  You are about to rename '{old_value}' to '{new_value}'")
    print("   This will update:")
    print("   - features.json")
    print("   - all countries in countries.json")
    
    confirm = input("\n  Confirm rename? (y/N): ").strip().lower()
    
    if confirm != 'y':
        print("  ❌ Renaming cancelled.")
        return False
    
    # Update features
    idx = current_values.index(old_value)
    features[category][feature]["values"][idx] = new_value
    
    # Update all countries
    countries_updated = 0
    for country_name, country_data in countries.items():
        if category in country_data and feature in country_data[category]:
            if old_value in country_data[category][feature]:
                # Preserve the boolean value
                value = country_data[category][feature][old_value]
                country_data[category][feature][new_value] = value
                del country_data[category][feature][old_value]
                countries_updated += 1
    
    print(f"\n✅ Renamed '{old_value}' to '{new_value}'")
    print(f"✅ Updated {countries_updated} countries")
    return True

def replace_all_values(category, feature, features, countries, current_values):
    """Replace all values in an enum feature"""
    print(f"\n🔄 Replacing all values in '{feature}':")
    print(f"  Current values: {', '.join(current_values)}")
    print("\n  ⚠️  WARNING: This will remove all current values and add new ones.")
    print("  Existing country data for this feature will be LOST!")
    
    confirm = input("\n  Are you sure? (y/N): ").strip().lower()
    
    if confirm != 'y':
        print("  ❌ Replacement cancelled.")
        return False
    
    # Get new values
    print(f"\n  Enter new values one at a time.")
    print("  Press Enter on an empty line when done.")
    
    new_values = []
    while True:
        value = input(f"  Value {len(new_values) + 1}: ").strip()
        
        if not value:
            if len(new_values) == 0:
                print("  ⚠️  No values entered. Keeping current values.")
                return False
            else:
                break
        
        if value in new_values:
            print(f"  ⚠️  Value '{value}' already added. Skipping.")
            continue
        
        new_values.append(value)
        print(f"  ✅ Added '{value}'")
    
    # Update features
    features[category][feature]["values"] = new_values
    
    # Update all countries (set all to False)
    countries_updated = 0
    for country_name, country_data in countries.items():
        if category in country_data and feature in country_data[category]:
            country_data[category][feature] = {value: False for value in new_values}
            countries_updated += 1
    
    print(f"\n✅ Replaced all values in '{feature}'")
    print(f"✅ Updated {countries_updated} countries")
    return True

def update_template():
    """Update template.json after updates"""
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
    print("✏️  UPDATE FEATURE IN GeoGuessr Narrower")
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
    feature_data = show_feature_details(category, feature, features)
    if not feature_data:
        return
    
    # Ask what to update
    print(f"\n🤔 What would you like to update about '{feature}'?")
    print("   1. Rename the feature")
    print("   2. Update the feature's values")
    
    while True:
        choice = input("\nEnter choice (1-2): ").strip()
        
        if choice == "1":
            # Rename feature
            new_name = input(f"\nEnter new name for '{feature}': ").strip().lower()
            
            if not new_name:
                print("❌ Feature name cannot be empty.")
                return
            
            if new_name == feature:
                print("❌ New name is the same as current name.")
                return
            
            if update_feature_name(category, feature, new_name, features, countries):
                # Update was successful, update the feature variable
                feature = new_name
            break
        
        elif choice == "2":
            # Update feature values
            if feature_data.get("type") == "enum":
                update_feature_values(category, feature, features, countries)
            else:
                print(f"❌ Feature '{feature}' is not an enum type.")
                print("   Only enum features can have their values updated.")
            break
        
        else:
            print("❌ Please enter 1 or 2.")
    
    # Save changes
    save_features(features)
    save_countries(countries)
    
    # Update template
    update_template()
    
    # Show summary
    print("\n" + "=" * 60)
    print("📊 UPDATE SUMMARY")
    print("=" * 60)
    
    # Show updated feature details
    show_feature_details(category, feature, features)
    
    print("\n" + "=" * 60)
    print("✅ FEATURE UPDATE COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    main()