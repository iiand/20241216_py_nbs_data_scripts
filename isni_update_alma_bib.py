import os
import pymarc
import requests
import xml.etree.ElementTree as ET
from io import StringIO

#environmental variables
apiKey = os.environ.get("ALMA_API_SANDBOX")
headers = {"Accept" : "application/xml"}

tree = ET.parse("C:/Users/ssa041rs/Desktop/202412_alma_xml/20241216_py_nbs_data_scripts/results/isni_wiki/isni_wiki_v4_qa_test_alma_update.xml")
root = tree.getroot()

for child in root:
        if child.tag == "record":
                for subchild in child:
                        if subchild in child:
                                if subchild.tag == "controlfield":
                                        if subchild.attrib["tag"] == "001":
                                                mms_id = subchild.text.strip()
                                                
                                                #get alma rec from api
                                                url = f"https://api-eu.hosted.exlibrisgroup.com/almaws/v1/bibs/{mms_id}?apikey={apiKey}"
                                                r = requests.get(url, headers=headers)
                                                if r.status_code == 200:
                                                       xml_content = r.content.decode("utf-8")
                                                       xml_file_like = StringIO(xml_content)
                                                       records = pymarc.parse_xml_to_array(xml_file_like)

                                                       isni = "shnisni"
                                                       
                                                       for record in records:
                                                        linky_isni = (record.get("100").get("1"))
                                                        
                                                        if linky_isni is None:
                                                               record["100"]["1"] = linky_isni

                                                               