import google.generativeai as palm

def get_text_generation_model():
    text_models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
    if not text_models:
        raise ValueError("No models found that support 'generateText' generation method.")
    return text_models[0]

def generate_text(prompt, text_model, temperature=0.5, candidate_count=3, max_output_tokens=5000):
    section = palm.generate_text(
        prompt=prompt,
        model=text_model,
        candidate_count=candidate_count,
        temperature=temperature,
        max_output_tokens=max_output_tokens
    )
    return section