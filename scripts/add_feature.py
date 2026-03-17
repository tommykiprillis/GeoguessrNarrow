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

def save_features(features):
    """Save features to features.json"""
    with open("features.json", "w", encoding="utf-8") as f:
        json.dump(features, f, indent=4, ensure_ascii=False)
    print("✅ Saved updated features to features.json")

def display_categories(features):
    """Display existing categories and their features"""
    print("\n📂 Existing Categories:")
    print("-" * 40)
    
    if not features:
        print("  No categories found.")
        return
    
    for i, (category, category_data) in enumerate(features.items(), 1):
        print(f"\n  {i}. {category.title()}:")
        if category_data:
            for feature, feature_data in category_data.items():
                if feature_data.get("type") == "enum":
                    values = feature_data.get("values", [])
                    print(f"     • {feature} → {', '.join(values)}")
                else:
                    print(f"     • {feature} (type: {feature_data.get('type', 'unknown')})")

def add_new_category(features):
    """Add a new category to features"""
    print("\n📝 Creating a new category:")
    
    while True:
        category_name = input("Enter new category name (snake_case recommended, e.g., 'environment', 'architecture'): ").strip().lower()
        
        if not category_name:
            print("❌ Category name cannot be empty.")
            continue
        
        # Check if category already exists
        if category_name in features:
            print(f"❌ Category '{category_name}' already exists. Please choose a different name.")
            continue
        
        # Validate name (only letters, numbers, and underscores)
        if not all(c.isalnum() or c == '_' for c in category_name):
            print("❌ Category name can only contain letters, numbers, and underscores.")
            continue
        
        # Confirm
        display_name = category_name.replace('_', ' ').title()
        confirm = input(f"✅ Create category '{display_name}'? (y/n): ").strip().lower()
        
        if confirm == 'y':
            features[category_name] = {}
            print(f"✅ Created new category: '{display_name}'")
            return category_name
        else:
            print("❌ Category creation cancelled.")
            return None

def select_category(features):
    """Let user select an existing category"""
    if not features:
        print("❌ No categories exist yet.")
        return None
    
    categories = list(features.keys())
    
    print("\n📋 Select an existing category:")
    for i, category in enumerate(categories, 1):
        print(f"  {i}. {category.replace('_', ' ').title()}")
    print(f"  {len(categories) + 1}. Create a new category")
    
    while True:
        try:
            choice = input(f"\nEnter choice (1-{len(categories) + 1}): ").strip()
            
            if not choice:
                print("❌ Please enter a choice.")
                continue
            
            choice = int(choice)
            
            if 1 <= choice <= len(categories):
                selected_category = categories[choice - 1]
                display_name = selected_category.replace('_', ' ').title()
                print(f"✅ Selected category: '{display_name}'")
                return selected_category
            elif choice == len(categories) + 1:
                return None  # Signal to create new category
            else:
                print(f"❌ Please enter a number between 1 and {len(categories) + 1}")
        except ValueError:
            print("❌ Please enter a valid number.")

def add_feature_to_category(features, category):
    """Add a new feature to a specific category"""
    print(f"\n🎯 Adding feature to '{category.replace('_', ' ').title()}':")
    
    # Show existing features in this category
    if features[category]:
        print("\nExisting features in this category:")
        for feature in features[category].keys():
            print(f"  • {feature}")
    
    # Get feature name
    while True:
        feature_name = input("\nEnter new feature name (snake_case, e.g., 'landscape', 'roof_type'): ").strip().lower()
        
        if not feature_name:
            print("❌ Feature name cannot be empty.")
            continue
        
        # Check if feature already exists in this category
        if feature_name in features[category]:
            print(f"❌ Feature '{feature_name}' already exists in this category.")
            overwrite = input("   Do you want to overwrite it? (y/n): ").strip().lower()
            if overwrite != 'y':
                continue
            else:
                print(f"⚠️  Overwriting existing feature '{feature_name}'")
                break
        
        # Validate name
        if not all(c.isalnum() or c == '_' for c in feature_name):
            print("❌ Feature name can only contain letters, numbers, and underscores.")
            continue
        
        # Confirm
        display_name = feature_name.replace('_', ' ').title()
        confirm = input(f"✅ Create feature '{display_name}'? (y/n): ").strip().lower()
        
        if confirm == 'y':
            break
        else:
            print("❌ Feature creation cancelled.")
            return None
    
    # Get feature type (currently only supports enum)
    print(f"\n📝 Setting up feature type for '{feature_name}':")
    print("  Currently supported types:")
    print("  1. enum - Multiple choice options")
    print("  2. boolean - True/False (coming soon)")
    print("  3. text - Free text input (coming soon)")
    
    feature_type = "enum"  # Currently only enum is supported
    print(f"\n✅ Defaulting to 'enum' type for now.")
    
    # Get enum values
    print(f"\n🎨 Setting up values for '{feature_name}':")
    print("  Enter values one at a time.")
    print("  Press Enter on an empty line when done.")
    
    enum_values = []
    while True:
        value = input(f"  Value {len(enum_values) + 1}: ").strip()
        
        if not value:
            if len(enum_values) == 0:
                print("  ❌ You must enter at least one value.")
                continue
            else:
                break
        
        if value in enum_values:
            print(f"  ⚠️  Value '{value}' already added. Skipping.")
            continue
        
        enum_values.append(value)
        print(f"  ✅ Added '{value}'")
    
    # Show summary
    print(f"\n📊 Summary for '{feature_name}':")
    print(f"  Type: {feature_type}")
    print(f"  Values: {', '.join(enum_values)}")
    print(f"  Total values: {len(enum_values)}")
    
    confirm = input("\n✅ Create this feature? (y/n): ").strip().lower()
    
    if confirm == 'y':
        # Create the feature structure
        features[category][feature_name] = {
            "type": feature_type,
            "values": enum_values
        }
        
        print(f"\n🎉 Successfully created feature '{feature_name}'!")
        return feature_name
    else:
        print("❌ Feature creation cancelled.")
        return None

def add_multiple_features(features, category):
    """Allow user to add multiple features to a category"""
    features_added = []
    
    while True:
        feature_name = add_feature_to_category(features, category)
        
        if feature_name:
            features_added.append(feature_name)
        
        # Ask if user wants to add another feature
        if len(features_added) > 0:
            add_another = input(f"\n➕ Add another feature to '{category.replace('_', ' ').title()}'? (y/n): ").strip().lower()
            if add_another != 'y':
                break
        else:
            break
    
    return features_added

def update_template_and_countries():
    """Run the existing template script to update template.json and countries.json"""
    print("\n[UPDATING] Updating template.json and countries.json...")
    
    # Check if the template script exists
    if not os.path.exists("script_features_to_template.py"):
        print("[WARNING] script_features_to_template.py not found.")
        print("   You'll need to run it manually to update template.json and countries.json.")
        return
    
    # Import and run directly instead of using subprocess
    try:
        # Import the function directly
        sys.path.insert(0, os.getcwd())  # Add current directory to Python path
        
        # Dynamically import the module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "script_features_to_template", 
            "script_features_to_template.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Call the main function
        if hasattr(module, 'main'):
            module.main()
        elif hasattr(module, 'generate_template'):
            module.generate_template("features.json", "template.json", "countries.json")
        else:
            print("[ERROR] Could not find main or generate_template function in script_features_to_template.py")
            
        print("[OK] Successfully updated template.json and countries.json")
        
    except Exception as e:
        print(f"[ERROR] Failed to update template.json and countries.json: {e}")
        print("   Please run 'python script_features_to_template.py' manually.")

def show_feature_summary(features, new_category=None, new_features=None):
    """Show a summary of the updated features"""
    print("\n" + "=" * 60)
    print("📊 FEATURES SUMMARY")
    print("=" * 60)
    
    total_features = 0
    total_values = 0
    
    for category, category_data in features.items():
        category_features = len(category_data)
        total_features += category_features
        
        print(f"\n{category.replace('_', ' ').title()}:")
        print(f"  Features: {category_features}")
        
        for feature, feature_data in category_data.items():
            if feature_data.get("type") == "enum":
                values = feature_data.get("values", [])
                total_values += len(values)
                indicator = "🆕 " if (category == new_category and feature in new_features) else "  "
                print(f"  {indicator}{feature}: {', '.join(values)}")
    
    print(f"\n📈 Total: {len(features)} categories, {total_features} features, {total_values} values")

def main():
    print("=" * 60)
    print("➕ ADD NEW FEATURE TO GeoGuessr Narrower")
    print("=" * 60)
    
    # Load existing features
    features = load_features()
    if features is None:
        return
    
    # Display existing structure
    display_categories(features)
    
    # Decide where to add the new feature
    print("\n🎯 Where would you like to add the new feature?")
    print("   1. Add to an existing category")
    print("   2. Create a new category")
    
    while True:
        choice = input("\nEnter choice (1 or 2): ").strip()
        
        if choice == "1":
            # Select existing category
            selected_category = select_category(features)
            if selected_category is None:
                # User wants to create new category instead
                selected_category = add_new_category(features)
                if not selected_category:
                    return
            break
        elif choice == "2":
            # Create new category
            selected_category = add_new_category(features)
            if not selected_category:
                return
            break
        else:
            print("❌ Please enter 1 or 2.")
    
    if not selected_category:
        print("❌ No category selected. Exiting.")
        return
    
    # Add feature(s) to the selected category
    print(f"\n{'='*60}")
    print(f"Adding feature(s) to '{selected_category.replace('_', ' ').title()}'")
    print(f"{'='*60}")
    
    added_features = add_multiple_features(features, selected_category)
    
    if not added_features:
        print("❌ No features were added.")
        return
    
    # Save the updated features
    save_features(features)
    
    # Show summary
    show_feature_summary(features, selected_category, added_features)
    
    # Ask about updating template and countries
    print("\n" + "=" * 60)
    print("🔄 UPDATE TEMPLATE AND COUNTRIES")
    print("=" * 60)
    
    print("\nDo you want to update template.json and countries.json with the new features?")
    print("  This will:")
    print("  1. Update template.json with the new feature structure")
    print("  2. Add the new features to all existing countries (set to False by default)")
    
    update = input("\nUpdate template and countries? (y/n): ").strip().lower()
    
    if update == 'y':
        update_template_and_countries()
    else:
        print("\n⚠️  Remember to run 'python script_features_to_template.py' later")
        print("   to update template.json and countries.json with the new features.")
    
    print("\n" + "=" * 60)
    print("✅ FEATURE ADDITION COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    main()