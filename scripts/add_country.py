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

def prompt_for_feature_values(country_name, features, use_template=None):
    """Interactive prompt to set feature values for the new country"""
    print(f"\n🎯 Setting up features for {country_name}:")
    print("=" * 60)
    
    # If we have a template from a previous country, use it
    if use_template:
        country_data = use_template
        print("   Using feature template from previous country.")
    else:
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
            
            # Show current selections if using template
            if use_template:
                current_true = [k for k, v in country_data[category][feature].items() if v is True]
                if current_true:
                    print(f"    Current: {', '.join(current_true)}")
            
            while True:
                print(f"    Enter numbers (comma-separated) or type 'all', 'none', 'skip' or values:")
                for i, value in enumerate(values, 1):
                    current_marker = "✓ " if use_template and country_data[category][feature].get(value, False) else "  "
                    print(f"      {i}. {current_marker}{value}")
                
                user_input = input(f"    Your choice: ").strip().lower()
                
                if not user_input:
                    print("    ⚠️  No input. Setting all to False.")
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
                
                elif user_input == 'skip':
                    print("    ⏭️  Skipping - keeping current values.")
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
    
    print(f"\n📈 Total: {true_count}/{total_count} features set to True")
    return true_count, total_count

def process_single_country(country_name, features, countries, feature_template=None):
    """Process a single country addition"""
    # Check if country already exists
    if country_name in countries:
        print(f"\n⚠️  '{country_name}' already exists in countries.json.")
        overwrite = input("   Do you want to overwrite it? (y/n): ").strip().lower()
        if overwrite != 'y':
            print(f"   ⏭️  Skipping '{country_name}'")
            return countries, False
    
    print(f"\n📝 Processing '{country_name}'...")
    
    # Ask if user wants to set features
    if feature_template is not None:
        # We already have a template from a previous country
        set_features = 'y'
    else:
        print(f"\n🤔 Do you want to set feature values for {country_name} now?")
        print("   If you choose 'no', all features will be set to False.")
        
        while True:
            set_features = input("Set features now? (y/n): ").strip().lower()
            
            if set_features == 'y' or set_features == 'n':
                break
            else:
                print("❌ Please enter 'y' for yes or 'n' for no.")
    
    # Get country data
    if set_features == 'y':
        if feature_template is None:
            # First time setting features for this batch
            country_data = prompt_for_feature_values(country_name, features)
            feature_template = country_data  # Save as template for next countries
        else:
            # Use existing template
            print(f"   Using feature template from previous country.")
            country_data = prompt_for_feature_values(country_name, features, feature_template)
    else:
        # Create template with all False
        country_data = create_country_template(features)
        print(f"   Created '{country_name}' with all features set to False.")
    
    # Add the country to the countries dictionary
    countries[country_name] = country_data
    
    # Show summary for this country
    true_count, total_count = show_country_summary(country_name, country_data)
    
    return countries, feature_template, true_count, total_count

def main():
    print("=" * 60)
    print("🌍 ADD NEW COUNTRIES TO GeoGuessr Narrower")
    print("=" * 60)
    
    # Load features structure
    features = load_features()
    if not features:
        return
    
    # Load existing countries
    countries = load_countries()
    
    # Ask for country names
    print("\n📝 Enter the names of countries to add (separated by commas):")
    print("   Examples:")
    print("   - Single: 'United States'")
    print("   - Multiple: 'France, Germany, Italy, Spain'")
    print("   - Multiple with spaces: 'United Kingdom, United States, Japan'")
    
    while True:
        countries_input = input("Country names: ").strip()
        
        if not countries_input:
            print("❌ Country names cannot be empty. Please try again.")
            continue
        
        # Split by commas and clean up
        country_names = [name.strip() for name in countries_input.split(',')]
        country_names = [name for name in country_names if name]  # Remove empty strings
        
        if not country_names:
            print("❌ No valid country names found. Please try again.")
            continue
        
        # Check for duplicates in input
        unique_countries = []
        duplicates_in_input = []
        for name in country_names:
            if name not in unique_countries:
                unique_countries.append(name)
            else:
                duplicates_in_input.append(name)
        
        if duplicates_in_input:
            print(f"⚠️  Found duplicates in input: {', '.join(set(duplicates_in_input))}")
            print("   Keeping only unique names.")
        
        if len(unique_countries) == 1:
            print(f"\n✅ Adding 1 country: {unique_countries[0]}")
        else:
            print(f"\n✅ Adding {len(unique_countries)} countries: {', '.join(unique_countries)}")
        
        # Confirm
        confirm = input("\nProceed? (y/n): ").strip().lower()
        if confirm == 'y':
            break
        else:
            print("❌ Operation cancelled. Please enter country names again.")
    
    # Ask about batch feature setting
    print(f"\n⚡ BATCH SETTINGS for {len(unique_countries)} countries:")
    print("   1. Set features for EACH country individually")
    print("   2. Set features ONCE and apply to ALL countries")
    print("   3. Set ALL features to False for ALL countries (fastest)")
    
    while True:
        batch_mode = input("\nChoose mode (1/2/3): ").strip()
        
        if batch_mode in ["1", "2", "3"]:
            break
        else:
            print("❌ Please enter 1, 2, or 3.")
    
    # Process countries
    print(f"\n{'='*60}")
    print("🚀 PROCESSING COUNTRIES...")
    print(f"{'='*60}")
    
    added_count = 0
    skipped_count = 0
    feature_template = None
    
    # Track statistics
    total_true_features = 0
    total_all_features = 0
    
    if batch_mode == "2":
        # Set features once for the first country, then apply to others
        print("\n📋 You will set features for the FIRST country,")
        print("   then choose whether to use those features for the rest.")
        print("   For each subsequent country, you can:")
        print("   - Use the same features (press Enter at each feature)")
        print("   - Customize features (type 'skip' to keep template values)")
        print("   - Override individual features")
    
    for i, country_name in enumerate(unique_countries):
        print(f"\n{'='*60}")
        print(f"🇺🇳 COUNTRY {i+1}/{len(unique_countries)}: {country_name}")
        print(f"{'='*60}")
        
        if batch_mode == "3":
            # Fast mode - all features False
            if country_name in countries:
                print(f"⚠️  '{country_name}' already exists. Skipping to avoid overwrite.")
                skipped_count += 1
                continue
            
            countries[country_name] = create_country_template(features)
            print(f"✅ Added '{country_name}' with all features set to False.")
            added_count += 1
            
            # Count features for stats
            true_count, total_count = show_country_summary(country_name, countries[country_name])
            total_true_features += true_count
            total_all_features += total_count
            
        else:
            # Individual or template mode
            result = process_single_country(country_name, features, countries, feature_template)
            countries, new_template, true_count, total_count = result
            
            if new_template is not False:  # Country was added
                added_count += 1
                total_true_features += true_count
                total_all_features += total_count
                
                # Save template for batch mode 2
                if batch_mode == "2" and feature_template is None and new_template is not None:
                    feature_template = new_template
                    print(f"\n💾 Saved feature template from '{country_name}' for remaining countries.")
                    print("   For subsequent countries, you can type 'skip' to keep template values.")
            else:
                skipped_count += 1
    
    # Save all changes at once
    if added_count > 0:
        save_countries(countries)
    else:
        print("\n⚠️  No countries were added.")
        return
    
    # Final summary
    print(f"\n{'='*60}")
    print("📊 ADDITION SUMMARY")
    print(f"{'='*60}")
    
    print(f"\n✅ Successfully added {added_count} country(s):")
    if added_count <= 10:
        added_names = [name for name in unique_countries if name in countries and name not in set(unique_countries[:len(unique_countries)-added_count-skipped_count])]
        for name in added_names:
            print(f"   • {name}")
    else:
        print(f"   (First 10 shown)")
        for name in list(countries.keys())[-10:]:
            print(f"   • {name}")
    
    if skipped_count > 0:
        print(f"\n⏭️  Skipped {skipped_count} country(s) (already existed)")
    
    print(f"\n📈 Statistics:")
    print(f"   • Total countries in database: {len(countries)}")
    
    if added_count > 0:
        avg_true = total_true_features / added_count if added_count > 0 else 0
        avg_total = total_all_features / added_count if added_count > 0 else 0
        print(f"   • Average features per added country: {avg_true:.1f}/{avg_total:.0f} True")
        print(f"   • Total features set to True in new countries: {total_true_features}")
    
    print(f"\n{'='*60}")
    print(f"✅ BATCH ADDITION COMPLETE!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()