from openai import OpenAI
import os


# Get OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("Please set OPENAI_API_KEY in your .env file")
#define client
client= OpenAI(api_key=OPENAI_API_KEY)

# Define the prompt for the image generation

def image_url_response(question:str):
    prompt_template = "Create an image of: {} the most realistic as posible and friendly with neutral characteristics."
    prompt = prompt_template.format(question)
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    return response.data[0].url

def main():
    """Example usage of the QueryExpander"""
    try:
        while True:
            query = input("\nEnter your image description: ")
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