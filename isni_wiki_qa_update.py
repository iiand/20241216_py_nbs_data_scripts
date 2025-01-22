import xml.etree.ElementTree as ET

# Function to check the conditions and add subfield z
def check_and_add_subfield_z(record):
    datafield_100 = record.find("datafield[@tag='100']")
    if datafield_100 is not None:
        subfield_1_isni = any(subfield.text and 'isni.org' in subfield.text for subfield in datafield_100.findall("subfield[@code='1']"))
        subfield_1_wikidata = any(subfield.text and 'wikidata.org' in subfield.text for subfield in datafield_100.findall("subfield[@code='1']"))
        subfield_9_present = datafield_100.find("subfield[@code='9']") is not None

        if subfield_1_isni and subfield_1_wikidata and subfield_9_present:
            subfield_z = ET.SubElement(datafield_100, "subfield", code="z")
            subfield_z.text = "ISNIQAPASS"

# Parse the input XML file
tree = ET.parse('C:/Users/ssa041rs/Desktop/202412_alma_xml/20241216_py_nbs_data_scripts/results/isni_wiki/isni_wiki_v4_20241220_nbs_id_scot_author_matched_bibrecs.xml')
root = tree.getroot()

# Iterate over each record and apply the check
for record in root.findall('record'):
    check_and_add_subfield_z(record)

# Write the modified XML to a new file
tree.write('C:/Users/ssa041rs/Desktop/202412_alma_xml/20241216_py_nbs_data_scripts/results/isni_wiki/isni_wiki_v4_qa_checked.xml')

print("The XML file has been processed and saved as 'isni_wiki_v4_qa_checked.xml'.")