import os
import zipfile
import base64
import xml.etree.ElementTree as ET
import fnmatch

class FileUtils:
    def __init__(self, base_path):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def create_xml(self, xml_content, file_name):
        try:
            path_full = os.path.join(self.base_path, file_name)
            if os.path.exists(path_full):
                os.remove(path_full)
            
            with open(path_full, "w", encoding="utf-8") as f:
                f.write(xml_content)
            return path_full
        except Exception as e:
            print(f"❌ Error creating XML file: {e}")
            return None

    def create_zip(self, xml_content, xml_file_name, zip_file_name):
        try:
            xml_path = self.create_xml(xml_content, xml_file_name)
            if not xml_path:
                return None

            zip_path = os.path.join(self.base_path, zip_file_name)
            if os.path.exists(zip_path):
                os.remove(zip_path)

            with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(xml_path, arcname=xml_file_name)

            if os.path.exists(zip_path):
                with open(zip_path, "rb") as zip_file:
                    zip_content = zip_file.read()
                    zip_base64 = base64.b64encode(zip_content).decode('utf-8')
                
                return {
                    "message": "ZIP created successfully",
                    "path": zip_path,
                    "size": os.path.getsize(zip_path),
                    "content_base64": zip_base64
                }
            else:
                print("❌ ZIP file was not created")
                return None
        except Exception as e:
            print(f"❌ Error creating ZIP file: {e}")
            return None
    def get_files_content(self, zip_file_name):
        try:
            matched=[
                f for f in os.listdir(self.base_path)
                if zip_file_name in f
            ]
            return matched
            
        except Exception as e:
            print(f"❌ Error getting file content: {e}")
            return []
    def get_file_base64(self, filename:str)-> str:
        try:
            pathfull = os.path.join(self.base_path, filename)
            with open(pathfull, "rb") as f:
                file_content = f.read()
                file_base64 = base64.b64encode(file_content).decode('utf-8')
                return file_base64  
        except Exception as e:
            print(f"❌ Error getting file content: {e}")
            return {"error": str(e)}
    
    def get_file_content(self, pathfull:str)-> str:
        with open(pathfull, "r") as f:
            file_content = f.read()
            return file_content
    