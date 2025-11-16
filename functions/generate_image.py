import os
from pathlib import Path
from google import genai
from google.genai import types


def generate_image(working_directory, file_path, content):
    """
    Generate an image using Google's Gemini model 'gemini-2.5-flash-image'.
    
    Args:
        working_directory: The working directory path
        file_path: The path where to save the generated image (relative to working_directory)
        content: The prompt/description for the image to generate
    
    Returns:
        str: Success message or error message
    """
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return "Error: GEMINI_API_KEY environment variable not set"
        
        client = genai.Client(api_key=api_key)
        
        # Create the full path for saving the image
        full_path = Path(working_directory) / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate the image using gemini-2.5-flash-image model
        result_image = client.models.generate_content(
            model='gemini-2.5-flash-image',
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part(text=content)]
                )
            ]
        )
        
        # Process the response and save the image
        image_saved = False
        for candidate in result_image.candidates:
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    if part.text is not None:
                        print(f"Model response: {part.text}")
                    elif part.inline_data is not None:
                        # Save the image
                        image = part.as_image()
                        image.save(str(full_path))
                        image_saved = True
                        return f"Image successfully generated and saved to {file_path}"
        
        if not image_saved:
            return "Error: No image data found in the response"
            
    except Exception as e:
        return f"Error generating image: {e}"

schema_generate_image = types.FunctionDeclaration(
    name="generate_image",
    description="Generate image, constrained to the file path in the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The image to generate or regenerate image to, relative to the working directory. Must be provided.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The image to write or overwrite into a file. Must be provided.",
            ),
        },
    ),
)
