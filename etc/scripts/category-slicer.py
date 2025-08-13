#!/usr/bin/env python3

# category slicer - create structured output sliced by the 'category' field of licenses

import json
import os
import glob
from collections import defaultdict

def main():
    # Initialize the result dictionary with categories as keys
    categories = defaultdict(list)
    
    # Get all JSON files in the docs directory
    json_files = glob.glob('../docs/*.json')
    
    print(f"Processing {len(json_files)} JSON files...")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                license_data = json.load(f)
            
            # Skip if the data is not a dictionary (might be a list or other type)
            if not isinstance(license_data, dict):
                print(f"Skipping {json_file}: not a dictionary object")
                continue
            
            # Extract the required fields
            category = license_data.get('category', 'Unknown')
            spdx_license_key = license_data.get('spdx_license_key', license_data.get('key'))
            short_name = license_data.get('short_name', '')
            name = license_data.get('name', '')
            
            # Create the license entry
            license_entry = {
                'spdx_license_key': spdx_license_key,
                'short_name': short_name,
                'name': name
            }
            
            # Add to the appropriate category
            categories[category].append(license_entry)
            
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error processing {json_file}: {e}")
            continue
    
    # Convert defaultdict to regular dict and sort entries within each category
    result = {}
    for category, licenses in categories.items():
        # Sort licenses by short_name for consistent output
        result[category] = sorted(licenses, key=lambda x: x['short_name'].lower())
    
    # Write the unified JSON file
    output_file = 'licenses_by_category.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    # Write the markdown file
    markdown_file = 'licenses_by_category.md'
    with open(markdown_file, 'w', encoding='utf-8') as f:
        f.write("# Licenses by Category\n\n")
        
        for category, licenses in sorted(result.items()):
            f.write(f"## {category}\n\n")
            
            for license_entry in licenses:
                name = license_entry['name']
                spdx_key = license_entry['spdx_license_key']
                
                f.write(f"- {name}, {spdx_key}\n")
            
            f.write("\n")
    
    print(f"Created unified JSON file: {output_file}")
    print(f"Created markdown file: {markdown_file}")
    print(f"Found {len(result)} categories:")
    for category, licenses in sorted(result.items()):
        print(f"  {category}: {len(licenses)} licenses")

if __name__ == '__main__':
    main()

