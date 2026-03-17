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
    """Let user select a single feature to update across countries"""
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

def select_countries_for_batch(countries, feature_info):
    """Let user select which countries to update"""
    category = feature_info['category']
    feature = feature_info['feature']
    
    print(f"\n🎯 Selecting countries to update for {category}.{feature}")
    print("=" * 60)
    
    country_list = sorted(countries.keys())
    
    # Show all countries with their current value for this feature
    print("\n📋 Countries (with current value for this feature):")
    print("-" * 60)
    
    country_info = {}
    for i, country_name in enumerate(country_list, 1):
        # Get current true values for this feature
        current_true = []
        if (category in countries[country_name] and 
            feature in countries[country_name][category]):
            for value in feature_info['values']:
                if (value in countries[country_name][category][feature] and 
                    countries[country_name][category][feature][value]):
                    current_true.append(value)
        
        current_display = ', '.join(current_true) if current_true else 'None'
        print(f"  {i:3}. {country_name:30} → {current_display}")
        country_info[country_name] = {'index': i, 'current': current_true}
    
    print(f"\n💡 Options for selecting countries:")
    print("   • Enter 'all' to update ALL countries")
    print("   • Enter numbers (comma-separated, e.g., '1,3,5')")
    print("   • Enter country names (comma-separated, e.g., 'United States,Canada,Mexico')")
    print("   • Mix numbers and names (e.g., '1,United States,3')")
    
    while True:
        selection = input(f"\nEnter countries to update: ").strip()
        
        if not selection:
            print("❌ Please enter a selection.")
            continue
        
        if selection.lower() == 'all':
            print(f"✅ Selected ALL {len(country_list)} countries")
            return country_list, country_info
        
        # Parse the selection
        selected_countries = []
        parts = [p.strip() for p in selection.split(',')]
        
        for part in parts:
            if not part:
                continue
                
            if part.isdigit():
                # It's a number
                idx = int(part)
                if 1 <= idx <= len(country_list):
                    selected_countries.append(country_list[idx - 1])
                else:
                    print(f"⚠️  Warning: Number {idx} is out of range (1-{len(country_list)})")
            else:
                # It's a country name
                if part in countries:
                    selected_countries.append(part)
                else:
                    # Try case-insensitive match
                    found = False
                    for country in country_list:
                        if country.lower() == part.lower():
                            selected_countries.append(country)
                            found = True
                            break
                    if not found:
                        print(f"⚠️  Warning: Country '{part}' not found")
        
        # Remove duplicates
        selected_countries = list(dict.fromkeys(selected_countries))
        
        if selected_countries:
            print(f"\n✅ Selected {len(selected_countries)} country(s):")
            for i, country in enumerate(selected_countries, 1):
                print(f"   {i:2}. {country}")
            
            confirm = input(f"\nConfirm selection? (y/n): ").strip().lower()
            if confirm == 'y':
                return selected_countries, country_info
            else:
                print("❌ Selection cancelled. Please select again.")
                continue
        else:
            print("❌ No valid countries selected. Please try again.")

def batch_update_single_feature_all_at_once(features, countries, selected_feature, selected_countries, country_info):
    """Update a single feature for ALL selected countries at once"""
    category = selected_feature['category']
    feature = selected_feature['feature']
    possible_values = selected_feature['values']
    
    print(f"\n🎯 BATCH UPDATE ALL AT ONCE: {category}.{feature}")
    print("=" * 60)
    
    # Show summary of selected countries
    print(f"\n📊 Selected {len(selected_countries)} country(s):")
    for i, country_name in enumerate(selected_countries[:10], 1):  # Show first 10
        current_true = country_info[country_name]['current'] if country_name in country_info else []
        current_display = ', '.join(current_true) if current_true else 'None'
        print(f"   {i:2}. {country_name}: {current_display}")
    
    if len(selected_countries) > 10:
        print(f"   ... and {len(selected_countries) - 10} more")
    
    print(f"\n🔧 Options for {feature.replace('_', ' ').title()}:")
    for j, value in enumerate(possible_values, 1):
        print(f"   {j}. {value}")
    
    print(f"\n💡 Instructions:")
    print("   • Enter comma-separated numbers or values (e.g., '1,3' or 'left,yellow')")
    print("   • Type 'all' to set ALL values to True for ALL selected countries")
    print("   • Type 'none' to set ALL values to False for ALL selected countries")
    print("   • Type 'cancel' to cancel the batch update")
    print("=" * 60)
    
    # Get the values to set
    while True:
        user_input = input(f"\nEnter values to set for ALL {len(selected_countries)} countries: ").strip().lower()
        
        if not user_input:
            print("❌ Please enter a value.")
            continue
        
        if user_input == 'cancel':
            print("❌ Batch update cancelled.")
            return countries, 0, False
        
        elif user_input == 'none':
            # Set all values to False for all selected countries
            values_to_set = []
            action = "set ALL values to False"
            break
        
        elif user_input == 'all':
            # Set all values to True for all selected countries
            values_to_set = possible_values
            action = "set ALL values to True"
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
                values_to_set = selected_values
                action = f"set {', '.join(selected_values)} to True"
                break
            else:
                print(f"❌ Invalid input. Please enter numbers (1-{len(possible_values)}), values, 'all', 'none', or 'cancel'")
    
    # Show what will happen
    print(f"\n⚠️  You are about to:")
    print(f"   • Feature: {category}.{feature}")
    print(f"   • Action: {action}")
    print(f"   • Countries affected: {len(selected_countries)}")
    print(f"   • This will overwrite existing values for this feature!")
    
    # Show preview of changes for first 5 countries
    print(f"\n📋 Preview (first 5 countries):")
    for country_name in selected_countries[:5]:
        current_true = country_info[country_name]['current'] if country_name in country_info else []
        current_display = ', '.join(current_true) if current_true else 'None'
        
        if user_input == 'none':
            new_display = 'None'
        elif user_input == 'all':
            new_display = ', '.join(possible_values)
        else:
            new_display = ', '.join(values_to_set)
        
        print(f"   • {country_name}: {current_display} → {new_display}")
    
    if len(selected_countries) > 5:
        print(f"   ... and {len(selected_countries) - 5} more")
    
    # Final confirmation
    confirm = input(f"\n🚨 CONFIRM: Apply these changes to ALL {len(selected_countries)} countries? (y/N): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Batch update cancelled.")
        return countries, 0, False
    
    # Apply changes to all selected countries
    print(f"\n🔄 Applying changes to {len(selected_countries)} countries...")
    
    for country_name in selected_countries:
        # Ensure the feature structure exists in this country
        if category not in countries[country_name]:
            countries[country_name][category] = {}
        if feature not in countries[country_name][category]:
            # Initialize with all False
            countries[country_name][category][feature] = {value: False for value in possible_values}
        
        # Apply the values
        if user_input == 'none':
            # Set all to False
            for value in possible_values:
                countries[country_name][category][feature][value] = False
        elif user_input == 'all':
            # Set all to True
            for value in possible_values:
                countries[country_name][category][feature][value] = True
        else:
            # Set specific values
            for value in possible_values:
                countries[country_name][category][feature][value] = (value in values_to_set)
    
    print(f"✅ Successfully updated {len(selected_countries)} countries")
    return countries, len(selected_countries), False

def batch_update_single_feature_one_by_one(features, countries, selected_feature, selected_countries, country_info):
    """Update a single feature across selected countries one by one"""
    category = selected_feature['category']
    feature = selected_feature['feature']
    possible_values = selected_feature['values']
    
    print(f"\n🎯 Batch updating: {category}.{feature}")
    print(f"   Selected countries: {len(selected_countries)}")
    print(f"   Possible values: {', '.join(possible_values)}")
    print("=" * 60)
    print("\n💡 Instructions:")
    print("   • Enter comma-separated numbers or values (e.g., '1,3' or 'left,yellow')")
    print("   • Type 'all' to set ALL values to True")
    print("   • Type 'none' to set ALL values to False")
    print("   • Press Enter (empty) to SKIP current country")
    print("   • Type 'quit' to STOP batch update entirely")
    print("=" * 60)
    
    total_countries = len(selected_countries)
    updated_count = 0
    skipped_count = 0
    
    for i, country_name in enumerate(selected_countries, 1):
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
            user_input = input(f"\n   Enter values for {country_name}: ").strip().lower()
            
            if not user_input:
                # Empty input means skip this country
                print(f"   ⏭️  Skipping {country_name}")
                skipped_count += 1
                break
            
            if user_input == 'quit':
                print(f"\n⏹️  Stopping batch update after {updated_count} countries updated.")
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
                    print(f"   ❌ Invalid input. Please enter numbers (1-{len(possible_values)}), values, 'all', 'none', or 'quit'")
    
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
    print("   2. Update a single feature across specific countries (batch mode)")
    
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
            # Batch update single feature across specific countries
            # First select which feature to update
            selected_feature = select_feature_for_batch(features)
            if not selected_feature:
                return
            
            # Then select which countries to update
            selected_countries, country_info = select_countries_for_batch(countries, selected_feature)
            if not selected_countries:
                return
            
            # Ask which batch mode to use
            print(f"\n⚡ BATCH UPDATE MODE for {len(selected_countries)} countries:")
            print("   1. Update ALL AT ONCE (same values for all countries)")
            print("   2. Update ONE BY ONE (different values for each country)")
            
            while True:
                batch_mode = input("\nChoose batch mode (1/2): ").strip()
                
                if batch_mode == "1":
                    # Update all at once
                    countries, updated_count, quit_early = batch_update_single_feature_all_at_once(
                        features, countries, selected_feature, selected_countries, country_info
                    )
                    skipped_count = 0  # No skipping in all-at-once mode
                    break
                elif batch_mode == "2":
                    # Update one by one
                    countries, updated_count, skipped_count, quit_early = batch_update_single_feature_one_by_one(
                        features, countries, selected_feature, selected_countries, country_info
                    )
                    break
                else:
                    print("❌ Please enter 1 or 2.")
            
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
                
                if batch_mode == "2" and skipped_count > 0:
                    print(f"⏭️  Skipped {skipped_count} country(s)")
                
                if quit_early and batch_mode == "2":
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