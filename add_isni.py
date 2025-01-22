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
        print(f"ISNI query URL: {url}")  # Log the query URL
        response = requests.get(url)
        
        if response.status_code == 200:
            if response.text.strip():  # Check if the response is not empty
                results = ET.fromstring(response.content)
                print(f"ISNI query results for {name} {date}: {ET.tostring(results, encoding='unicode')}")  # Log the results
                
                # Write the ISNI query response to an XML file
                with open('isni_query_response.xml', 'wb') as f:
                    f.write(response.content)
                
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
                    return isni_uri
            else:
                print("ISNI query returned an empty response.")
        else:
            print(f"Error: Received status code {response.status_code} from ISNI query.")
    except Exception as e:
        print(f"Exception occurred while querying ISNI: {e}")
    return None

# Load XML data from file
with open('isni_test.xml', 'r', encoding='utf-8') as file:
    xml_data = file.read()

# Parse the XML data
root = ET.fromstring(xml_data)

# Iterate over each record in the collection with a progress bar
for record in tqdm(root.findall('record'), desc="Processing records"):
    datafields = record.findall('datafield[@tag="100"]')
    
    # Check if the record already contains an ISNI URL in subfield '1'
    has_isni = any(subfield.get('code') == '1' for datafield in datafields for subfield in datafield.findall('subfield'))
    
    if not has_isni:
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
        isni_url = query_isni_database(name, date, username, password)
        
        if isni_url:
            # Add the ISNI URL to the corresponding 100 field in a new subfield '1'
            new_subfield = ET.Element('subfield', {'code': '1'})
            new_subfield.text = isni_url
            datafields[0].append(new_subfield)
            
# Write the modified XML data to a new file
tree = ET.ElementTree(root)
tree.write('isni_v1.xml')

print("The updated records have been written to 'isni_added.xml'.")