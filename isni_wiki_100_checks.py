import xml.etree.ElementTree as ET

# Parse the XML file
tree = ET.parse('C:/Users/ssa041rs/Desktop/202412_alma_xml/20241216_py_nbs_data_scripts/results/isni_wiki/isni_wiki_v4_qa_checked.xml')
root = tree.getroot()

# Open a TSV file to write the output with UTF-8 encoding
with open('isni_wiki_v4_100_checks.tsv', 'w', encoding='utf-8') as tsv_file:
    # Write the header
    tsv_file.write("Author\tAuthority\tISNI\tQA_Status\n")
    
    # Iterate through each record in the XML
    for record in root.findall('record'):
        # Initialize variables to store subfield values
        author = ""
        authority = ""
        isni_url = ""
        qa_status = ""
        
        # Find the datafield with tag 100
        datafield_100 = record.find("datafield[@tag='100']")
        if datafield_100 is not None:
            # Find subfield a
            subfield_a = datafield_100.find("subfield[@code='a']")
            if subfield_a is not None:
                author = subfield_a.text.strip()
            
            # Find subfield 9
            subfield_9 = datafield_100.find("subfield[@code='9']")
            if subfield_9 is not None:
                authority = subfield_9.text.strip()
            
            # Find subfield 1 that contains ISNI URL
            subfields_1 = datafield_100.findall("subfield[@code='1']")
            for subfield_1 in subfields_1:
                if "isni.org" in subfield_1.text:
                    isni_url = subfield_1.text.strip()

            # Find subfield z that contains qa status
            subfields_z = datafield_100.findall("subfield[@code='z']")
            for subfield_z in subfields_z:
                if "ISNIQAPASS" or "ISNIQAFAIL" in subfield_z.text:
                    qa_status = subfield_z.text.strip()
                    break
        
        # Write the values to the TSV file
        tsv_file.write(f"{author}\t{authority}\t{isni_url}\t{qa_status}\n")

print("TSV file has been created successfully.")