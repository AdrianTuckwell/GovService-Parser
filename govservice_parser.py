import json
import csv
import xml.etree.ElementTree as ET

def load_integrations(integration_file):
    integrations = {}
    try:
        with open(integration_file, mode='r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                integration_id = row.get('Integration ID')
                integration_name = row.get('Integration Name')
                if integration_id and integration_name:
                    integrations[integration_id] = integration_name
    except Exception as e:
        raise RuntimeError(f"Failed to load integrations from CSV: {str(e)}")
    return integrations

def extract_process_stages(json_data):
    try:
        if "processName" in json_data:
            process_name = json_data["processName"]
            stages_dict = json_data.get("stages", {})
            stages = []
            for stage_id, stage_info in stages_dict.items():
                stage_name = stage_info.get("name", "Unnamed Stage")
                stages.append((stage_name, stage_info))
            return process_name, stages
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred during extraction of stages: {str(e)}")

def extract_process_integrations(process_name, stages, integration_mapping):
    try:
        processes = []
        for stage_name, stage_info in stages:
            integrations = stage_info.get("props", {}).get("integrations", [])
            integration_details = []
            for integration in integrations:
                integration_id = integration.get("id", "Unknown ID")
                integration_name = integration_mapping.get(integration_id, integration_id)
                integration_details.append(integration_name)
            processes.append((stage_name, integration_details))
        return process_name, processes
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred during extraction: {str(e)}")

def generate_xml(data):
    process_name, stages = data

    process_elem = ET.Element("Process")
    process_elem.text = process_name

    stages_elem = ET.SubElement(process_elem, "Stages")

    for stage_name, integration_details in stages:
        stage_elem = ET.SubElement(stages_elem, "Stage")
        stage_elem.text = stage_name

        integrations_elem = ET.SubElement(stage_elem, "Integrations")

        for integration_name in integration_details:
            integration_elem = ET.SubElement(integrations_elem, "Integration")
            integration_elem.text = integration_name

    tree = ET.ElementTree(process_elem)
    return tree

def write_xml(tree, output_file):
    try:
        tree.write(output_file, encoding="utf-8", xml_declaration=True, method="xml")
        print(f"XML successfully written to {output_file}")
    except Exception as e:
        raise RuntimeError(f"Failed to write XML to {output_file}: {str(e)}")

def main(input_file, integration_file, output_file):
    try:
        with open(input_file, 'r') as f:
            json_data = json.load(f)

        process_name, stages = extract_process_stages(json_data)
        integration_mapping = load_integrations(integration_file)
        processes = extract_process_integrations(process_name, stages, integration_mapping)

        xml_tree = generate_xml(processes)

        write_xml(xml_tree, output_file)

    except FileNotFoundError as fnf_error:
        print(f"Error: {fnf_error}")
    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON from '{input_file}'.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    input_file = "input.json"             # Replace with your input JSON file path
    integration_file = "integrations.csv" # Replace with your integrations CSV file path
    output_file = "output.xml"            # Replace with your desired output XML file path
    main(input_file, integration_file, output_file)
