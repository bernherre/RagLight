from openai import OpenAI
import os
from PIL import Image
import io


# Get OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("Please set OPENAI_API_KEY in your .env file")
#define client
client= OpenAI(api_key=OPENAI_API_KEY)

# Define the prompt for the image generation
# Define the prompt for the image generation
def image_format(path: str, mode: str):
    # Open the image
    byteImg = Image.open(path)
    
    # Convert the image to the specified mode
    if mode in ["RGBA", "LA", "L"]:
        byteImg = byteImg.convert(mode)
    else:
        raise ValueError("Unsupported mode. Use 'RGBA', 'LA', or 'L'.")

    # Save the image to a BytesIO object
    byteImgIO = io.BytesIO()
    byteImg.save(byteImgIO, "PNG")
    byteImgIO.seek(0)
    byteImg = byteImgIO.read()

    # Return the BytesIO object
    dataBytesIO = io.BytesIO(byteImg)
    Image.open(dataBytesIO)
    return dataBytesIO

def image_url_response(question:str, path:str):
    prompt_template = "Edit this image : {} "
    prompt = prompt_template.format(question)
    response = client.images.edit(
        model="dall-e-2",
        prompt=prompt,
        image=image_format(path, "RGBA"),
        size="1024x1024",
        n=1,
    )
    return response.data[0].url

def main():
    """Example usage of the QueryExpander"""
    try:
        while True:
            query = input("\nEnter what you want to modify: ")
            path = input("\nEnter your image path: ")
            if (query.lower() == 'quit') | (path.lower() == 'quit') :
                print("Bye bye!")
                break
            
            url = image_url_response(query, path)
            print(url)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Please check your API key and try again.")

if __name__ == "__main__":
    main()