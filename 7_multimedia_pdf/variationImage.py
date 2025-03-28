from openai import OpenAI
import os


# Get OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("Please set OPENAI_API_KEY in your .env file")
#define client
client= OpenAI(api_key=OPENAI_API_KEY)

# Define the prompt for the image generation

def image_url_response(path:str):
    response = client.images.create_variation(
        model="dall-e-2",
        #prompt=prompt,
        size="1024x1024",
        n=1,
        image=open(path,"rb")
    )
    return response.data[0].url

def main():
    """Example usage of the QueryExpander"""
    try:
        while True:
            query = input("\nEnter a path of image: ")
            if query.lower() == 'quit':
                print("Bye bye!")
                break
            
            url = image_url_response(query)
            print(url)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Please check your API key and try again.")

if __name__ == "__main__":
    main()