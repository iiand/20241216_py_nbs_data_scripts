import xml.etree.ElementTree as ET
import os

def parse_xml(file_path):
    try:
        tree = ET.parse(file_path)
        return tree
    except ET.ParseError as e:
        print(f"ParseError: Error parsing {file_path}: {e}")
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {file_path} not found: {e}")
    except Exception as e:
        print(f"Unexpected error parsing {file_path}: {e}")
    return None

def extract_discrepancies(file_path):
    tree = parse_xml(file_path)
    if tree is None:
        return None
    root = tree.getroot()
    discrepancies = {}
    for discrepancy in root.findall('.//discrepancy'):
        controlfield = discrepancy.find('.//controlfield').text.strip()
        subfield_1 = discrepancy.find('.//subfield_1').text.strip()
        discrepancies[controlfield] = subfield_1
    return discrepancies

def update_xml_with_discrepancies(source_file, discrepancies, output_file):
    tree = parse_xml(source_file)
    if tree is None:
        return
    root = tree.getroot()
    
    for record in root.findall('.//record'):
        controlfield = record.find('.//controlfield[@tag="001"]').text.strip()
        if controlfield in discrepancies:
            datafield_100 = record.find('.//datafield[@tag="100"]')
            if datafield_100 is not None:
                subfield_1_element = ET.SubElement(datafield_100, 'subfield', code='1')
                subfield_1_element.text = discrepancies[controlfield]
    
    tree.write(output_file)
    print(f"Updated XML has been saved to '{output_file}'.")

def main():
    discrepancies_file = 'isni_wiki_discrepancies.xml'
    source_file = 'C:/Users/ssa041rs/Desktop/202412_alma_xml/20241216_py_nbs_data_scripts/results/isni_wiki/isni_wiki_v2_20241220_nbs_id_scot_author_matched_bibrecs.xml'
    output_file = 'C:/Users/ssa041rs/Desktop/202412_alma_xml/20241216_py_nbs_data_scripts/results/isni_wiki/updated_isni_wiki_20241220_nbs_id_scot_author_matched_bibrecs.xml'

    discrepancies = extract_discrepancies(discrepancies_file)
    if discrepancies is None:
        print("Failed to extract discrepancies.")
        return

    update_xml_with_discrepancies(source_file, discrepancies, output_file)

if __name__ == "__main__":
    main()