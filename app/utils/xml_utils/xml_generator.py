import xml.etree.ElementTree as ET
from .xml_templates import INVOICE_TEMPLATE,CREDIT_NOTE_TEMPLATE,DEBIT_NOTE_TEMPLATE

class XMLGenerator:
    def __init__(self, data):
        self.data = data

    def generate_invoice(self):
        root = ET.fromstring(INVOICE_TEMPLATE)

        # Find and replace placeholders
        for elem in root.iter():
            if elem.text and elem.text.startswith('@'):
                placeholder = elem.text[1:]
                if placeholder in self.data:
                    elem.text = str(self.data[placeholder])

        return ET.tostring(root, encoding='unicode')

    def generate_credit_note(self):
        root = ET.fromstring(CREDIT_NOTE_TEMPLATE)

        # Find and replace placeholders
        for elem in root.iter():
            if elem.text and elem.text.startswith('@'):
                placeholder = elem.text[1:]
                if placeholder in self.data:
                    elem.text = str(self.data[placeholder])

        return ET.tostring(root, encoding='unicode')

    def generate_debit_note(self):
        root = ET.fromstring(DEBIT_NOTE_TEMPLATE)

        # Find and replace placeholders
        for elem in root.iter():
            if elem.text and elem.text.startswith('@'):
                placeholder = elem.text[1:]
                if placeholder in self.data:
                    elem.text = str(self.data[placeholder])

        return ET.tostring(root, encoding='unicode')
