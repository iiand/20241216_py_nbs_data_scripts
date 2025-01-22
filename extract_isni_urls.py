import xml.etree.ElementTree as ET

# Path to the XML file
xml_file_path = 'C:/Users/ssa041rs/Desktop/202412_alma_xml/20241216_py_nbs_data_scripts/results/isni_wiki/updated_isni_wiki_v2_20241220_nbs_id_scot_author_matched_bibrecs.xml'

# Path to the output text file
output_file_path = 'C:/Users/ssa041rs/Desktop/202412_alma_xml/20241216_py_nbs_data_scripts/results/isni_wiki/updated_isni_wiki_v2_20241220_nbs_id_scot_author_matched_bibrecs.txt'

# Parse the XML file
tree = ET.parse(xml_file_path)
root = tree.getroot()

# Open the output text file in write mode
with open(output_file_path, 'w') as output_file:
    # Iterate over each 100 subfield 1 element in the XML
    for elem in root.findall(".//subfield[@code='1']"):
        # Write the text content of the element to the output file
        output_file.write(elem.text + '\n')

print(f"Strings from each 100 subfield 1 element have been written to {output_file_path}.")