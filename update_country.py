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

def save_countries(countries):
    """Save updated countries to countries.json"""
    with open("countries.json", "w", encoding="utf-8") as f:
        json.dump(countries, f, indent=4, ensure_ascii=False)
    print(f"✅ Saved {len(countries)} countries to countries.json")

def select_feature_for_batch(features):
    """Let user select a single feature to update across all countries"""
    print("\n📋 Select a feature to batch update:")
    
    # Create a flat list of all features with their categories
    all_features = []
    for category, category_data in features.items():
        for feature, feature_data in category_data.items():
            if feature_data.get("type") == "enum":
                all_features.append({
                    'category': category,
                    'feature': feature,
                    'values': feature_data.get("values", [])
                })
    
    # Display all features
    for i, feat in enumerate(all_features, 1):
        category_name = feat['category'].replace('_', ' ').title()
        feature_name = feat['feature'].replace('_', ' ').title()
        values = feat['values']
        print(f"  {i:2}. {category_name} → {feature_name} ({len(values)} values)")
    
    while True:
        choice = input(f"\nSelect feature (1-{len(all_features)}): ").strip()
        
        if not choice:
            print("❌ Please enter a choice.")
            continue
        
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(all_features):
                selected = all_features[idx - 1]
                print(f"\n✅ Selected feature: {selected['category']}.{selected['feature']}")
                print(f"   Possible values: {', '.join(selected['values'])}")
                return selected
            else:
                print(f"❌ Please enter a number between 1 and {len(all_features)}")
        else:
            # Try to match by category.feature format
            parts = choice.split('.')
            if len(parts) == 2:
                category, feature = parts
                for feat in all_features:
                    if feat['category'] == category and feat['feature'] == feature:
                        print(f"\n✅ Selected feature: {feat['category']}.{feat['feature']}")
                        print(f"   Possible values: {', '.join(feat['values'])}")
                        return feat
            print("❌ Feature not found. Please select from the list.")

def batch_update_single_feature(features, countries, selected_feature):
    """Update a single feature across multiple countries"""
    category = selected_feature['category']
    feature = selected_feature['feature']
    possible_values = selected_feature['values']
    
    print(f"\n🎯 Batch updating: {category}.{feature}")
    print(f"   Possible values: {', '.join(possible_values)}")
    print("=" * 60)
    print("\n💡 Instructions:")
    print("   • Enter comma-separated numbers or values (e.g., '1,3' or 'left,yellow')")
    print("   • Type 'all' to set ALL values to True")
    print("   • Type 'none' to set ALL values to False")
    print("   • Press Enter (empty) to QUIT batch update")
    print("=" * 60)
    
    country_list = sorted(countries.keys())
    total_countries = len(country_list)
    
    updated_count = 0
    skipped_count = 0
    
    for i, country_name in enumerate(country_list, 1):
        print(f"\n{'='*60}")
        print(f"🇺🇳 Country {i}/{total_countries}: {country_name}")
        print(f"{'='*60}")
        
        # Ensure the feature structure exists in this country
        if category not in countries[country_name]:
            countries[country_name][category] = {}
        if feature not in countries[country_name][category]:
            # Initialize with all False
            countries[country_name][category][feature] = {value: False for value in possible_values}
        
        # Get current true values for this feature
        current_true = []
        for value in possible_values:
            if value in countries[country_name][category][feature] and countries[country_name][category][feature][value]:
                current_true.append(value)
        
        # Display current state
        print(f"\n📊 Current {feature.replace('_', ' ').title()} for {country_name}:")
        if current_true:
            print(f"   ✅ Set to True: {', '.join(current_true)}")
        else:
            print(f"   ❌ All values are False")
        
        print(f"\n🔧 Options for {feature.replace('_', ' ').title()}:")
        for j, value in enumerate(possible_values, 1):
            current_marker = "✓ " if value in current_true else "  "
            print(f"   {j}. {current_marker}{value}")
        
        # Get user input
        while True:
            user_input = input(f"\n   Enter values for {country_name} (or press Enter to quit): ").strip().lower()
            
            if not user_input:
                # Empty input means quit
                print(f"\n⏹️  Quitting batch update after {updated_count} countries updated.")
                return countries, updated_count, skipped_count, True
            
            elif user_input == 'none':
                print(f"   ✅ Setting all values to False for {country_name}")
                for value in possible_values:
                    countries[country_name][category][feature][value] = False
                updated_count += 1
                break
            
            elif user_input == 'all':
                print(f"   ✅ Setting all values to True for {country_name}")
                for value in possible_values:
                    countries[country_name][category][feature][value] = True
                updated_count += 1
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
                            if 1 <= idx <= len(possible_values):
                                selected_values.append(possible_values[idx-1])
                        elif part in possible_values:
                            selected_values.append(part)
                else:
                    # Single value
                    if user_input.isdigit():
                        idx = int(user_input)
                        if 1 <= idx <= len(possible_values):
                            selected_values = [possible_values[idx-1]]
                    elif user_input in possible_values:
                        selected_values = [user_input]
                
                if selected_values:
                    print(f"   ✅ Setting {', '.join(selected_values)} to True for {country_name}")
                    for value in possible_values:
                        countries[country_name][category][feature][value] = (value in selected_values)
                    updated_count += 1
                    break
                else:
                    print(f"   ❌ Invalid input. Please enter numbers (1-{len(possible_values)}), values, 'all', or 'none'")
    
    return countries, updated_count, skipped_count, False

def show_country_summary(country_name, country_data):
    """Show a summary of the country's current features"""
    print(f"\n📊 Current features for {country_name}:")
    print("=" * 60)
    
    true_count = 0
    total_count = 0
    
    for category, category_data in country_data.items():
        print(f"\n{category.title()}:")
        for feature, feature_data in category_data.items():
            if isinstance(feature_data, dict):
                true_values = [k for k, v in feature_data.items() if v is True]
                total_count += len(feature_data)
                true_count += len(true_values)
                
                if true_values:
                    print(f"  • {feature.replace('_', ' ').title()}: {', '.join(true_values)}")
                else:
                    print(f"  • {feature.replace('_', ' ').title()}: None (all False)")
    
    print(f"\n📈 Summary: {true_count}/{total_count} features set to True")
    return true_count, total_count

def update_feature_values(country_name, country_data, features):
    """Interactive prompt to update feature values for a country"""
    print(f"\n🎯 Updating features for {country_name}:")
    print("=" * 60)
    
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
        # Ensure category exists in country data
        if category not in country_data:
            country_data[category] = {}
        
        print(f"\n📁 {category.title()}:")
        print("-" * 40)
        
        for feature, values in category_features.items():
            # Ensure feature exists in country data
            if feature not in country_data[category]:
                country_data[category][feature] = {value: False for value in values}
            
            # Get current true values for this feature
            current_true = []
            for value in values:
                if value in country_data[category][feature] and country_data[category][feature][value]:
                    current_true.append(value)
            
            print(f"\n  🔧 {feature.replace('_', ' ').title()}:")
            print(f"    Current: {', '.join(current_true) if current_true else 'None (all False)'}")
            print(f"    Options: {', '.join(values)}")
            
            while True:
                print(f"    Enter numbers (comma-separated) or type 'all', 'none', or values:")
                for i, value in enumerate(values, 1):
                    current_marker = "✓ " if value in current_true else "  "
                    print(f"      {i}. {current_marker}{value}")
                
                user_input = input(f"    Your choice (press Enter to keep current): ").strip().lower()
                
                if not user_input:
                    print("    ⚠️  Keeping current values.")
                    break
                
                elif user_input == 'none':
                    print("    ✅ Setting all to False.")
                    for value in values:
                        country_data[category][feature][value] = False
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

def update_specific_features(country_name, country_data, features):
    """Update only specific features instead of going through all"""
    print(f"\n🎯 Update specific features for {country_name}:")
    print("=" * 60)
    
    # Create a flat list of all features
    all_features = []
    for category, category_data in features.items():
        for feature, feature_data in category_data.items():
            if feature_data.get("type") == "enum":
                all_features.append((category, feature, feature_data["values"]))
    
    print("\n📋 Available features to update:")
    for i, (category, feature, values) in enumerate(all_features, 1):
        # Get current true values
        current_true = []
        if category in country_data and feature in country_data[category]:
            for value in values:
                if value in country_data[category][feature] and country_data[category][feature][value]:
                    current_true.append(value)
        
        print(f"  {i:2}. {category}.{feature}: {', '.join(current_true) if current_true else 'None'}")
    
    print("\nEnter the numbers of features you want to update (comma-separated)")
    print("Or press Enter to update all features")
    
    while True:
        user_input = input("\nFeature numbers to update: ").strip()
        
        if not user_input:
            # Update all features
            return update_feature_values(country_name, country_data, features)
        
        # Parse selected features
        selected_indices = []
        try:
            parts = [p.strip() for p in user_input.split(',')]
            for part in parts:
                if part.isdigit():
                    idx = int(part)
                    if 1 <= idx <= len(all_features):
                        selected_indices.append(idx - 1)
                    else:
                        print(f"❌ Number {idx} is out of range (1-{len(all_features)})")
                        break
            else:
                # All indices were valid
                break
        except ValueError:
            print("❌ Invalid input. Please enter numbers separated by commas.")
    
    # Update only selected features
    for idx in selected_indices:
        category, feature, values = all_features[idx]
        
        # Ensure category and feature exist in country data
        if category not in country_data:
            country_data[category] = {}
        if feature not in country_data[category]:
            country_data[category][feature] = {value: False for value in values}
        
        # Get current true values
        current_true = []
        for value in values:
            if value in country_data[category][feature] and country_data[category][feature][value]:
                current_true.append(value)
        
        print(f"\n  🔧 {category}.{feature}:")
        print(f"    Current: {', '.join(current_true) if current_true else 'None (all False)'}")
        print(f"    Options: {', '.join(values)}")
        
        while True:
            print(f"    Enter numbers (comma-separated) or type 'all', 'none', or values:")
            for i, value in enumerate(values, 1):
                current_marker = "✓ " if value in current_true else "  "
                print(f"      {i}. {current_marker}{value}")
            
            user_input = input(f"    Your choice (press Enter to keep current): ").strip().lower()
            
            if not user_input:
                print("    ⚠️  Keeping current values.")
                break
            
            elif user_input == 'none':
                print("    ✅ Setting all to False.")
                for value in values:
                    country_data[category][feature][value] = False
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

def select_country(countries):
    """Let user select a country to update"""
    if not countries:
        print("❌ No countries found in countries.json")
        return None
    
    country_list = sorted(countries.keys())
    
    print("\n📋 Select a country to update:")
    for i, country in enumerate(country_list, 1):
        # Count true features for this country
        true_count = 0
        total_count = 0
        country_data = countries[country]
        for category, category_data in country_data.items():
            for feature, feature_data in category_data.items():
                if isinstance(feature_data, dict):
                    for value in feature_data.values():
                        total_count += 1
                        if value:
                            true_count += 1
        
        print(f"  {i:2}. {country} ({true_count}/{total_count} features)")
    
    while True:
        user_input = input(f"\nEnter choice (1-{len(country_list)}): ").strip()
        
        if not user_input:
            print("❌ Please enter a choice.")
            continue
        
        if user_input.isdigit():
            idx = int(user_input)
            if 1 <= idx <= len(country_list):
                selected_country = country_list[idx - 1]
                print(f"✅ Selected country: '{selected_country}'")
                return selected_country
            else:
                print(f"❌ Please enter a number between 1 and {len(country_list)}")
        else:
            # Check if it's a valid country name
            if user_input in countries:
                print(f"✅ Selected country: '{user_input}'")
                return user_input
            else:
                print(f"❌ Country '{user_input}' not found.")
                print("   Please enter an exact match or use the number from the list.")

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

def main():
    print("=" * 60)
    print("✏️  UPDATE COUNTRY IN GeoGuessr Narrower")
    print("=" * 60)
    
    # Load features structure
    features = load_features()
    if not features:
        return
    
    # Load existing countries
    countries = load_countries()
    if not countries:
        return
    
    print(f"\n📊 Database has {len(countries)} countries")
    
    # Ask what to update
    print(f"\n🤔 What would you like to update?")
    print("   1. Update a single country")
    print("   2. Update a single feature across ALL countries (batch mode)")
    
    while True:
        choice = input("\nEnter choice (1-2): ").strip()
        
        if choice == "1":
            # Single country update
            country_name = select_country(countries)
            if not country_name:
                return
            
            # Show current summary
            true_before, total_before = show_country_summary(country_name, countries[country_name])
            
            # Ask how to update
            print(f"\n🤔 How do you want to update '{country_name}'?")
            print("   1. Update all features (go through every category)")
            print("   2. Update specific features only")
            print("   3. Reset all features to False")
            
            while True:
                choice = input("\nEnter choice (1-3): ").strip()
                
                if choice == "1":
                    # Update all features
                    updated_data = update_feature_values(country_name, countries[country_name], features)
                    countries[country_name] = updated_data
                    break
                elif choice == "2":
                    # Update specific features
                    updated_data = update_specific_features(country_name, countries[country_name], features)
                    countries[country_name] = updated_data
                    break
                elif choice == "3":
                    # Reset all to False
                    confirm = input(f"\n⚠️  Reset ALL features for '{country_name}' to False? (y/N): ").strip().lower()
                    if confirm == 'y':
                        countries[country_name] = create_country_template(features)
                        print(f"✅ Reset all features for '{country_name}' to False")
                    else:
                        print("❌ Reset cancelled.")
                        return
                    break
                else:
                    print("❌ Please enter 1, 2, or 3.")
            
            # Save the updated countries
            save_countries(countries)
            
            # Show updated summary
            true_after, total_after = show_country_summary(country_name, countries[country_name])
            
            print("\n" + "=" * 60)
            print(f"✅ Successfully updated '{country_name}'!")
            print("=" * 60)
            
            # Show before/after comparison
            print(f"\n📈 Comparison:")
            print(f"   Before: {true_before}/{total_before} features True")
            print(f"   After:  {true_after}/{total_after} features True")
            
            if true_before != true_after:
                change = true_after - true_before
                if change > 0:
                    print(f"   ⬆️  Added {change} True features")
                else:
                    print(f"   ⬇️  Removed {-change} True features")
            
            break
        
        elif choice == "2":
            # Batch update single feature across all countries
            # First select which feature to update
            selected_feature = select_feature_for_batch(features)
            if not selected_feature:
                return
            
            # Run the batch update
            countries, updated_count, skipped_count, quit_early = batch_update_single_feature(features, countries, selected_feature)
            
            if updated_count > 0:
                # Save changes
                save_countries(countries)
            
            # Show summary
            print("\n" + "=" * 60)
            print("📊 BATCH UPDATE SUMMARY")
            print("=" * 60)
            
            if updated_count > 0:
                feature_name = f"{selected_feature['category']}.{selected_feature['feature']}"
                print(f"\n✅ Updated {updated_count} country(s) for feature: {feature_name}")
                
                if quit_early:
                    print("⏹️  Stopped early (user quit)")
                
                print(f"\n📈 Total countries in database: {len(countries)}")
                print(f"💾 Changes have been saved to countries.json")
            else:
                print("\n⚠️  No countries were updated.")
            
            print("\n" + "=" * 60)
            print("✅ BATCH UPDATE COMPLETE!")
            print("=" * 60)
            break
        
        else:
            print("❌ Please enter 1 or 2.")

if __name__ == "__main__":
    main()