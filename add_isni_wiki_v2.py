import xml.etree.ElementTree as ET
import requests
import re
import os
from tqdm import tqdm

# ISNI account credentials
username=os.environ.get('isni_username')
password=os.environ.get('isni_password')

def query_isni_database(name, date, username, password):
    try:
        # Construct the ISNI query URL
        base_url = f"https://isni-m.oclc.org/sru/username={username}/password={password}/DB=1.3/"
        query = f"?query=pica.nw+%3D+{name.replace(' ', '+')}+and+pica.dti+%3D+{date}&version=1.1&operation=searchRetrieve&recordSchema=isni-e"
        url = base_url + query
        response = requests.get(url)
        
        if response.status_code == 200:
            if response.text.strip():  # Check if the response is not empty
                results = ET.fromstring(response.content)
                
                # Find the <srw:record> with the highest count of <source> elements
                best_record = None
                max_sources = 0
                
                for record in results.findall('.//srw:record', namespaces={'srw': 'http://www.loc.gov/zing/srw/'}):
                    sources_count = len(record.findall('.//source'))
                    if sources_count > max_sources:
                        max_sources = sources_count
                        best_record = record
                
                if best_record is not None:
                    isni_uri = best_record.find('.//isniURI').text
                    
                    # Use regex to find the WKP source and subsourceIdentifier starting with Q
                    pattern = re.compile(r'<source>WKP<\/source>\s*\n*<subsourceIdentifier>(Q\d+)<\/subsourceIdentifier>')
                    match = pattern.search(ET.tostring(best_record, encoding='unicode'))
                    
                    if match:
                        subsource_id = match.group(1)
                        wikidata_url = f"https://www.wikidata.org/wiki/{subsource_id}"
                        return isni_uri, wikidata_url
            else:
                print("ISNI query returned an empty response.")
        else:
            print(f"Error: Received status code {response.status_code} from ISNI query.")
    except Exception as e:
        print(f"Exception occurred while querying ISNI: {e}")
    return None, None

def query_isni_by_url(isni_url):
    try:
        # Construct the ISNI query URL using the ISNI URL
        url = isni_url.replace("https://isni.org/isni/", "https://isni-m.oclc.org/sru/?query=pica.isn%3D")
        response = requests.get(url)
        
        if response.status_code == 200:
            if response.text.strip():  # Check if the response is not empty
                results = response.content.decode('utf-8')
                
                # Use regex to find the WKP source and subsourceIdentifier starting with Q
                pattern = re.compile(r'<source>WKP<\/source>\s*\n*<subsourceIdentifier>(Q\d+)<\/subsourceIdentifier>')
                match = pattern.search(results)
                
                if match:
                    subsource_id = match.group(1)
                    wikidata_url = f"https://www.wikidata.org/wiki/{subsource_id}"
                    return wikidata_url
        else:
            print(f"Error: Received status code {response.status_code}")
    except Exception as e:
        print(f"Exception occurred: {e}")
    return None

# Load XML data from file
with open('20241220_nbs_id_scot_author_matched_bibrecs.xml', 'r', encoding='utf-8') as file:
    xml_data = file.read()

# Parse the XML data
root = ET.fromstring(xml_data)

# Iterate over each record in the collection with a progress bar
for record in tqdm(root.findall('record'), desc="Processing records"):
    datafields = record.findall('datafield[@tag="100"]')
    
    # Check if the record already contains an ISNI URL and Wikidata URL in subfield '1'
    has_isni_subfield = False
    has_wikidata_subfield = False
    isni_url_present = None
    
    for datafield in datafields:
        for subfield in datafield.findall('subfield'):
            if subfield.get('code') == '1':
                if "isni.org" in subfield.text:
                    has_isni_subfield = True
                    isni_url_present = subfield.text.strip()
                elif "wikidata.org" in subfield.text:
                    has_wikidata_subfield = True
    
    # Skip the record if it has both an existing ISNI URL and Wikidata URL
    if has_isni_subfield and has_wikidata_subfield:
        continue
    
    if has_isni_subfield and isni_url_present:
        # Extract the values from subfields 'a' and 'd'
        name = None
        date = None
        
        for datafield in datafields:
            for subfield in datafield.findall('subfield'):
                if subfield.get('code') == 'a':
                    name = subfield.text.strip()
                elif subfield.get('code') == 'd':
                    date = re.sub(r'[^0-9-]', '', subfield.text.strip())  # Remove punctuation from the end of the string
        
        # Query the ISNI database using the extracted values (name and date)
        _, wikidata_url = query_isni_database(name, date, username, password)
        
        if wikidata_url:
            print(f"Adding Wikidata URL: {wikidata_url}")
            # Add the Wikidata URL to the corresponding 100 field in a new subfield '1'
            new_subfield = ET.Element('subfield', {'code': '1'})
            new_subfield.text = wikidata_url
            datafields[0].append(new_subfield)
    
    elif not has_isni_subfield or (has_isni_subfield and not has_wikidata_subfield):
        # Extract the values from subfields 'a' and 'd'
        name = None
        date = None
        
        for datafield in datafields:
            for subfield in datafield.findall('subfield'):
                if subfield.get('code') == 'a':
                    name = subfield.text.strip()
                elif subfield.get('code') == 'd':
                    date = re.sub(r'[^0-9-]', '', subfield.text.strip())  # Remove punctuation from the end of the string
        
        # Query the ISNI database using the extracted values (name and date)
        isni_url, wikidata_url = query_isni_database(name, date, username, password)
        
        if isni_url and not has_isni_subfield:
            print(f"Adding ISNI URL: {isni_url}")
            # Add the ISNI URL to the corresponding 100 field in a new subfield '1'
            new_subfield = ET.Element('subfield', {'code': '1'})
            new_subfield.text = isni_url
            datafields[0].append(new_subfield)
        
        if wikidata_url:
            print(f"Adding Wikidata URL: {wikidata_url}")
            # Add the Wikidata URL to the corresponding 100 field in a new subfield '1'
            new_subfield = ET.Element('subfield', {'code': '1'})
            new_subfield.text = wikidata_url
            datafields[0].append(new_subfield)

# Write the modified XML data to a new file
tree = ET.ElementTree(root)
tree.write('C:/Users/ssa041rs/Desktop/202412_alma_xml/20241216_py_nbs_data_scripts/results/isni_wiki_isni_wiki_v2_20241220_nbs_id_scot_author_matched_bibrecs.xml')

print("The updated records have been written to 'isni_wiki_isni_wiki_v2_20241220_nbs_id_scot_author_matched_bibrecs.xml'.")

