from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import os

def create_client(client_class, endpoint, key, credential_class=None):
    """Create an Azure client with the given credentials."""
    if credential_class:
        return client_class(endpoint=endpoint, credentials=credential_class(key))
    return client_class(endpoint=endpoint, credential=AzureKeyCredential(key))

def analyze_document(client, file_path, model="prebuilt-document"):
    """Analyze a document using Azure Form Recognizer."""
    with open(file_path, "rb") as document:
        result = client.begin_analyze_document(model, document).result()

    print("=== Extracted Data ===")
    for kv_pair in result.key_value_pairs:
        if kv_pair.key and kv_pair.value:
            print(f"{kv_pair.key.content}: {kv_pair.value.content}")

    return result

def analyze_image(client, file_path, features=None):
    """Analyze an image using Azure Computer Vision."""
    if features is None:
        features = ["ImageType", "Objects", "Description"]
        
    with open(file_path, "rb") as image:
        result = client.analyze_image_in_stream(image, visual_features=features)

    print("\n=== Visual Analysis ===")
    print(f"Image Type: {'Clip Art' if result.image_type.clip_art_type else 'Photo'}")
    if result.description.captions:
        print(f"Description: {result.description.captions[0].text}")

    return result

def process_file(file_path, form_client=None, vision_client=None):
    """Process a file with the appropriate client based on extension."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
        
    ext = os.path.splitext(file_path)[1].lower()

    if ext in ['.pdf', '.jpg', '.jpeg', '.png', '.tiff'] and form_client:
        return analyze_document(form_client, file_path)
    elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif'] and vision_client:
        return analyze_image(vision_client, file_path)
    else:
        print(f"Unsupported file type: {ext}")
        return None

def main():
# API Configuration
    config = {
        "form_recognizer": {
            "endpoint": "https://<your-form-recognizer-endpoint>.cognitiveservices.azure.com/",
            "key": "<your-form-recognizer-key>"
        },
        "computer_vision": {
            "endpoint": "https://<your-computer-vision-endpoint>.cognitiveservices.azure.com/",
            "key": "<your-computer-vision-key>"
        }
    }

    # Initialize clients
    form_client = create_client(
        DocumentAnalysisClient, 
        config["form_recognizer"]["endpoint"], 
        config["form_recognizer"]["key"]
    )

    vision_client = create_client(
        ComputerVisionClient, 
        config["computer_vision"]["endpoint"], 
        config["computer_vision"]["key"],
        CognitiveServicesCredentials
    )

    # Process files
    files = {
        "document": "bob_documento.pdf",
        "image": "bob_imagem.png"
    }

    for file_path in files.values():
        process_file(file_path, form_client, vision_client)

if __name__ == "__main__":
    main()