from google import genai
from google.genai import types

def create_prompt(chunks: list[str], question: str) -> str:
    """
    Returns the prompt template with relevant chunks and question attached
    """
    context = "\n\n".join(chunks)

    prompt= f"Answer using ONLY this context: {context}\n\nQuestion: {question}"

    return prompt

def generate_answer(prompt: str, client: genai.Client, model_name: str) -> str:
    """
    Generates an answer using the Google GenAI SDK models endpoint.
    """
    interaction = client.interactions.create(
        model=model_name,
        system_instruction="You are a helpful assistant and designed specifically to answer customer questions ONLY according to provided contexts.",
        input=prompt
    )

    return interaction.output_text
