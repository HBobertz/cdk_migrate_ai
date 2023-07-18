import json
import os
import sys
import glob

def process_template():
    file_path = sys.argv[1]
    app_path = sys.argv[2]
    # Define the directory path

    template_json = ""
    # Check if a file was found
    if file_path:
        # Read the JSON file
        with open(file_path, 'r') as file:
            template_data = json.load(file)

        # Check if 'resources' key exists in the template
        if 'resources' in template_data:
            resources = template_data['resources']

            # Delete 'CDKMetadata' key if exists under 'resources'
            if 'CDKMetadata' in resources:
                del resources['CDKMetadata']

        # Check if 'conditions' key exists in the template
        if 'conditions' in template_data:
            conditions = template_data['conditions']

            # Delete 'CDKMetadataAvailable' key if exists under 'conditions'
            if 'CDKMetadataAvailable' in conditions:
                del conditions['CDKMetadataAvailable']

        # Replace double quotes with \"
        template_json = json.dumps(template_data)
        template_json = template_json.replace('"', '\\"')

        # Replace new line characters with \\n
        template_json = template_json.replace('\n', '\\n')

        # Print the modified JSON without new line characters
    else:
        print("No template.json file found in the directory.")
    app_str = ""
    if app_path:
        j = open(app_path, "r")
        app_str = j.read()
        app_str = app_str.replace('\\', '\\\\')
        app_str = app_str.replace('"', '\\"')
        app_str = app_str.replace('\n', '\\n')
    f = open(file_path, "w")
    f.write(f'{{ "prompt": "{template_json}", "completion": "{app_str}"}}')

# Call the function
process_template()
