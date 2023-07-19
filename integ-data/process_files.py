import json
import os
import glob

INTEG_TEST_DIR = "../aws-cdk/packages/@aws-cdk-testing/framework-integ/test"
MODULES_TO_IGNORE = {''}

# Loops through all modules in the @aws-cdk-testing to get the CFN template.json and cdk app code for 
# each integ test. Ignores a few modules with MODULES_TO_IGNORE 
def process_integ_tests():
    print("Processing integ tests ... ")

    jsonl_examples = []

    modules = [f.path for f in os.scandir(INTEG_TEST_DIR) if f.is_dir()]
    for module in modules: 
        print(str(module))                                                                                           
        cur_module_examples = process_module(module)
        jsonl_examples += cur_module_examples
    
    f = open("integ-data/integ-data.jsonl", "w")
    for ex in jsonl_examples:
        f.write(ex)
    f.close()

    print('Done. Number of examples added: ' + str(len(jsonl_examples)))
    return

# Processes the template.out and integ.ts files for a given module, e.g. aws-apigateway
def process_module(modulePath):
    module_test_dir = os.path.join(modulePath, 'test')
    example_cases = []
    for root, dirs, files in os.walk(module_test_dir):
        for file in files:
            module_tests_added = 0
            if file.endswith(".ts") and not file.__contains__('.d.ts') and not file.__contains__('.js'):

                individual_integ_test_name = file.split(".ts")[0]
                snapshot_folder_name = os.path.join(module_test_dir, individual_integ_test_name + ".js.snapshot")
                snapshot_test_json = process_integ_snapshot_directory(snapshot_folder_name)

                if snapshot_test_json:
                    cdk_code = process_integ_ts_file(os.path.join(modulePath, 'test', file))
                    str_to_write_to_file = f'{{ "prompt": "{ snapshot_test_json }", "completion": "{ cdk_code }"}}'
                    example_cases.append(str_to_write_to_file)

    return example_cases

# Returns the CDK code for an integ.ts file
def process_integ_ts_file(testFilePath):
    app_str = ""
    j = open(testFilePath, "r")
    app_str = j.read()
    app_str = app_str.replace('\\', '\\\\')
    app_str = app_str.replace('"', '\\"')
    app_str = app_str.replace('\n', '\\n')
    return app_str


# Copies the CFN code of the snapshot directory for an integ test
def process_integ_snapshot_directory(folder):

    for root, dirs, files in os.walk(folder):
        manifest_files = []
        for file in files:
            if file.endswith("template.json"):
                file_path = os.path.join(root, file)
                manifest_files.append(file_path)
        if len(manifest_files) == 1:
            f = open(manifest_files[0])
            template_data = json.load(f)
            f.close()

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

            # Return the modified JSON without new line characters
            return template_json
        else:
            print('Not doing this test. This many template.json files found: ' + str(len(manifest_files)))
            return
    print("No files found at path: " + folder)
    return

# Call the function
process_integ_tests()