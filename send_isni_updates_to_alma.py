import os
import pymarc
import requests
import xml.etree.ElementTree as ET
from io import StringIO

# Counters
total = 0
progress = 0
existing_isni = 0
no_new_LOD = 0

# Variables
apiKey = os.environ.get("ALMA_API_PROD")
headers = {"Accept": "application/xml", "Content-Type": "application/xml"}

# Error log file
error_log_file = 'isni2alma_errors.txt'

tree = ET.parse("results\isni_wiki\isni_wiki_v4_qa_checked.xml")
root = tree.getroot()
total = len(root)

for child in root:
    if child.tag == "record":
        mmsID = child.find("controlfield[@tag='001']").text.strip()
        LODs = child.findall("datafield[@tag='100']/subfield[@code='1']")
        if child.find("datafield[@tag='100']/subfield[@code='z']") is not None:
            qa = child.find("datafield[@tag='100']/subfield[@code='z']").text.strip()
        else:
            qa = ""
        isni = ""
        wiki = ""
        for each in LODs:
            if "isni" in each.text.strip():
                isni = each.text.strip()
            if "wiki" in each.text.strip():
                wiki = each.text.strip()
        # Skip if nothing new to add
        if isni == "" and qa == "":
            progress += 1
            no_new_LOD +=1
            continue
        # Get Alma record from API
        url = f"https://api-eu.hosted.exlibrisgroup.com/almaws/v1/bibs/{mmsID}?apikey={apiKey}"
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            with open(error_log_file, 'a') as error_file:
                error_file.write(f"{mmsID} - no bibrec\n")
            # Skip the record if the error message indicates an invalid MMS ID
            if "Invalid MMS ID" in r.text:
                progress += 1
                continue
        if r.status_code == 200:
            # Parse XML to pymarc
            xml_content = r.content.decode("utf-8")
            xml_file_like = StringIO(xml_content)
            records = pymarc.parse_xml_to_array(xml_file_like)

            # Add in linked open data fields
            for record in records:
                field100 = record.get("100")
                if field100 is not None:  # Check if field100 exists
                    field100_1 = field100.get_subfields("1")
                    field100_z = field100.get_subfields("z")
                    if not any("isni" in subfield for subfield in field100_1):
                        if isni != "":
                            field100.add_subfield("1", isni)
                        if qa != "":
                            field100.add_subfield("z", qa)
                    else:
                        existing_isni +=1
                        if len(field100_z) == 0:
                            field100.add_subfield("z", "ISNIQAPASS_HUMAN")
                    if not any("wiki" in subfield for subfield in field100_1):
                        if wiki != "":
                            field100.add_subfield("1", wiki)

                    # Convert back to XML
                    xml = pymarc.record_to_xml(record)
                    # Add bib wrapper
                    xml_element = ET.fromstring(xml)
                    bib_element = ET.Element("bib")
                    bib_element.append(xml_element)
                    xml_with_bib = ET.tostring(bib_element, encoding="utf-8")
                    # Send to Alma
                    r = requests.put(url, data=xml_with_bib, headers=headers)
                    if r.status_code != 200:
                        print(r.text)
                else:
                    # Log the MMS ID to the error log file if field100 is None
                    with open(error_log_file, 'a') as error_file:
                        error_file.write(f"{mmsID} - no 100 field\n")
            progress += 1  # Incrementing here only once per record
    print(f"\rProgress: {progress}/{total} records, {existing_isni} recs with existing ISNI, {no_new_LOD} recs with no new LOD elements", end="")
total_skipped = existing_isni + no_new_LOD
updated_record_count = progress - total_skipped
print(f"\n{updated_record_count} records updated with LOD")

'''
import os
import pymarc
import requests
import xml.etree.ElementTree as ET
from io import StringIO

#counters
total = 0
progress = 0


# variables
apiKey = os.environ.get("ALMA_API_SANDBOX")
headers = {"Accept": "application/xml", "Content-Type": "application/xml"}


tree = ET.parse("results\isni_wiki\isni_wiki_v4_qa_checked.xml")
root = tree.getroot()
total = len(root)

for child in root:
    if child.tag == "record":
        mmsID = child.find("controlfield[@tag='001']").text.strip()
        LODs = child.findall("datafield[@tag='100']/subfield[@code='1']")
        if child.find("datafield[@tag='100']/subfield[@code='z']") is not None:
            qa = child.find("datafield[@tag='100']/subfield[@code='z']").text.strip()
        else:
            qa = ""
        isni = ""
        wiki = ""
        for each in LODs:
            if "isni" in each.text.strip():
                isni = each.text.strip()
            if "wiki" in each.text.strip():
                wiki = each.text.strip()
        # skip if nothing new to add
        if isni == "" and qa == "":
            progress += 1
            continue
        # get alma rec from api
        url = f"https://api-eu.hosted.exlibrisgroup.com/almaws/v1/bibs/{mmsID}?apikey={apiKey}"
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            print(f"Error for MMS ID {mmsID}: {r.text}")
            # Skip the record if the error message indicates an invalid MMS ID
            if "Invalid MMS ID" in r.text:
                continue
        if r.status_code == 200:
            # parse xml to pymarc
            xml_content = r.content.decode("utf-8")
            xml_file_like = StringIO(xml_content)
            records = pymarc.parse_xml_to_array(xml_file_like)
            # Process the records as needed
            progress += 1

            # add in linked open data fields
            for record in records:
                field100 = record.get("100")
                field100_1 = field100.get_subfields("1")
                field100_z = field100.get_subfields("z")
                if not any("isni" in subfield for subfield in field100_1):
                    if isni != "":
                        field100.add_subfield("1", isni)
                    if qa != "":
                        field100.add_subfield("z", qa)
                else:
                    if len(field100_z) == 0:
                        field100.add_subfield("z", "ISNIQAPASS_HUMAN")
                if not any("wiki" in subfield for subfield in field100_1):
                    if wiki != "":
                        field100.add_subfield("1", wiki)

                # convert back to xml
                xml = pymarc.record_to_xml(record)
                # add bib wrapper
                xml_element = ET.fromstring(xml)
                bib_element = ET.Element("bib")
                bib_element.append(xml_element)
                xml_with_bib = ET.tostring(bib_element, encoding="utf-8")
                # send to alma
                r = requests.put(url, data=xml_with_bib, headers=headers)
                progress += 1
                if r.status_code != 200:
                    print(r.text)
    print(f"\rProgress: {progress}/{total} records" , end="")
 
'''
