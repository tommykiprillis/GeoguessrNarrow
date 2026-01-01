import json
import os
import sys

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

def delete_country(country_name, countries):
    """Delete a country from the database"""
    if country_name not in countries:
        print(f"❌ Country '{country_name}' not found in countries.json")
        return False
    
    # Confirm deletion
    print(f"\n⚠️  WARNING: You are about to delete '{country_name}'")
    print(f"   This action cannot be undone!")
    
    confirm = input(f"\nAre you sure you want to delete '{country_name}'? (y/N): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Deletion cancelled.")
        return False
    
    # Delete the country
    del countries[country_name]
    print(f"✅ Deleted '{country_name}' from countries.json")
    
    # Show summary
    print(f"\n📊 Remaining countries: {len(countries)}")
    if countries:
        print("   Countries:", ", ".join(sorted(countries.keys())[:10]), end="")
        if len(countries) > 10:
            print(f" and {len(countries) - 10} more...")
        else:
            print()
    
    return True

def main():
    print("=" * 60)
    print("🗑️  DELETE COUNTRY FROM GeoGuessr Narrower")
    print("=" * 60)
    
    # Load existing countries
    countries = load_countries()
    if countries is None:
        return
    
    if not countries:
        print("❌ No countries found in countries.json")
        return
    
    # Show existing countries
    print("\n📋 Existing Countries:")
    print("-" * 40)
    
    country_list = sorted(countries.keys())
    for i, country in enumerate(country_list, 1):
        print(f"  {i:2}. {country}")
    
    print(f"\nTotal: {len(countries)} countries")
    
    # Ask for country to delete
    print("\n📝 Enter the name or number of the country to delete:")
    print("   (You can type the full name or the number from the list)")
    
    while True:
        user_input = input("Country: ").strip()
        
        if not user_input:
            print("❌ Please enter a country name or number.")
            continue
        
        # Try to parse as number
        if user_input.isdigit():
            idx = int(user_input)
            if 1 <= idx <= len(country_list):
                country_name = country_list[idx - 1]
                break
            else:
                print(f"❌ Please enter a number between 1 and {len(country_list)}")
                continue
        
        # Check if it's a valid country name
        if user_input in countries:
            country_name = user_input
            break
        else:
            print(f"❌ Country '{user_input}' not found.")
            print("   Please enter an exact match or use the number from the list.")
    
    # Delete the country
    if delete_country(country_name, countries):
        # Save changes
        save_countries(countries)
        
        print("\n" + "=" * 60)
        print(f"✅ Successfully deleted '{country_name}'!")
        print("=" * 60)

if __name__ == "__main__":
    main()