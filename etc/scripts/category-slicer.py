#!/usr/bin/env python3

# category slicer - create structured output sliced by the 'category' field of licenses

import json
import os
import glob
import argparse
from collections import defaultdict

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Create structured output sliced by license category')
    parser.add_argument('--exclude-licenserefs', '-x', action='store_true',
                        help='Exclude licenses with LicenseRef-scancode- keys')
    parser.add_argument('--output-prefix', '-o', default='licenses_by_category',
                        help='Base name for output files (default: licenses_by_category)')
    args = parser.parse_args()
    
    # Initialize the result dictionary with categories as keys
    categories = defaultdict(list)

    # set up a dict with the metacategories we want to use
    metacategories = {
        'Safe for most uses': ['Permissive', 'Public Domain'],
        'Usually requires review': ['Free Restricted', 'Copyleft Limited', 'Source-available'],
        'High-risk for businesses': ['Commercial', 'Copyleft'],
        'Other': ['CLA', 'Patent License', 'Unstated License']
    }

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

            # Only exclude LicenseRef-scancode keys if --exclude-licenserefs flag is passed
            if args.exclude_licenserefs and spdx_license_key.startswith('LicenseRef-scancode-'):
                continue
            
            # Skip entries which have an is_deprecated field set to True
            if license_data.get('is_deprecated', False):
                continue

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
    output_file = f'{args.output_prefix}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    # Write the markdown file
    markdown_file = f'{args.output_prefix}.md'
    with open(markdown_file, 'w', encoding='utf-8') as f:
        f.write("# Licenses by Category\n\n")
        # insert metacategories as header 1
        for metacategory, subcategories in metacategories.items():
            f.write(f"## {metacategory}\n\n")
            for subcategory in subcategories:
                f.write(f"### {subcategory}\n\n")
                for category, licenses in sorted(result.items()):
                    if category == subcategory:
                        for license_entry in licenses:
                            f.write(f"- {license_entry['name']}, `{license_entry['spdx_license_key']}`\n")
                f.write("\n")
   
    print(f"Created unified JSON file: {output_file}")
    print(f"Created markdown file: {markdown_file}")
    print(f"Found {len(result)} categories:")
    for category, licenses in sorted(result.items()):
        print(f"  {category}: {len(licenses)} licenses")

if __name__ == '__main__':
    main()

