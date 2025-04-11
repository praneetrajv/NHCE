# Import the required library
from google import genai

# Initialize the client
client = genai.Client(api_key="AIzaSyBUOaiuWHurJgxrrQh7qMNYrHLMuuTKUOU")

# Define a function for generating content
def generate_content(input_text):
    
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents= "summeriz the data and remove uneccesary information in a paragraph without extra enojis or bulleting points\n\n" + input_text
    )
    return response.text


    