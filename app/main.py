import xmltodict
from pathlib import Path
import sys
from datetime import datetime

if len(sys.argv) != 2:
    print("give safeplus.xml file path as first argument of the script")
    sys.exit()

XML_FILE = sys.argv[1]
VIP_OUT = Path(XML_FILE).parent / "vipnotes"

with open(XML_FILE, "rb") as file:
    root = xmltodict.parse(file, dict_constructor=dict)

if "safeboxplus" in root:
    secret_data = root["safeboxplus"]

def tolist(leaf) -> list:
    if type(leaf) is list:
        return leaf
    else:
        a = []
        a.append(leaf)
        return a

def special_sym_replace(source: str) -> str:
    source = source.strip()
    source = source.replace("/", "x")
    source = source.replace("\\", "x")
    return source

def parse_safeplus_xml(folder: dict, basepath):
    if "folder" in folder:
        folders = folder["folder"]
        for fld in tolist(folders):
            folder_title = fld["@title"]
            folder_title = special_sym_replace(folder_title)
            folderdir = basepath / folder_title
            folderdir.mkdir(parents=True, exist_ok=True)

            parse_safeplus_xml(fld, folderdir)

    if "card" in folder:
        cards = folder["card"]
        for card in tolist(cards):
            card_title = str(card["@title"])
            card_title = special_sym_replace(card_title)
            notedir = basepath / card_title
            notedir.mkdir(parents=True, exist_ok=True)
            notetxt = notedir / (card_title + ".txt")
            notetxt.touch()

            card_text = ""
            card_desc = ""
            if "description" in card:
                card_desc = str(card["description"])
                card_desc = card_desc.strip()
                if card_desc != "None":
                    card_text += "Описание" + "\r\n"
                    card_text += card_desc + "\r\n"

            card_fields = card["field"]
            for field in tolist(card_fields):
                if "#text" in field:
                    field_txt = str(field["#text"])
                    card_text += str(field["@title"]).strip() + "\r\n"

                    if "@type" in field and field["@type"] == "datetime":
                        date = datetime.fromtimestamp(int(field_txt) / 1000)
                        field_txt = date.strftime("%Y-%m-%d")

                    card_text += field_txt + "\r\n"

            notetxt.write_text(card_text)
    return True

if parse_safeplus_xml(secret_data, VIP_OUT):
    print("check vipnotes directory near safeplus.xml")
