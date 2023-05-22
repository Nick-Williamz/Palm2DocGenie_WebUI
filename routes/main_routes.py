from flask import request, render_template, jsonify
import textwrap
import os
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as palm
from modules.forms import ChatForm

from modules import document_loader
from modules import embedding_generator
from modules import text_generator

DOCUMENT_DIR = "./documents/"
RESPONSE_FILENAME = 'conversation.txt'

# Load documents
documents = document_loader.load_documents()

# Configure palm and get text model
API_KEY = os.getenv('API_KEY')
embedding_generator.configure_palm(API_KEY)
text_model = embedding_generator.get_text_model()

# Generate embeddings DataFrame
df = embedding_generator.generate_embeddings_df(documents, text_model)

# Get text generation model
text_model2 = text_generator.get_text_generation_model()

# The existing find_best_passage, make_prompt, and other functions remain the same
def find_best_passage(query, dataframe):
    # Generate embeddings for the query!
    query_embedding = palm.generate_embeddings(model=text_model, text=query)

    # Stack the embeddings into a matrix.
    embeddings_matrix = np.stack(dataframe['Embeddings'].to_numpy())

    # Calculate the cosine similarity between the query and each passage in the document.
    cosine_similarities = cosine_similarity(embeddings_matrix, np.array(query_embedding['embedding']).reshape(1, -1))
    # Find the index of the passage with the highest cosine similarity to the query.
    idx = np.argmax(cosine_similarities)

    # Return the passage with the highest cosine similarity and its cosine similarity value.
    return dataframe.iloc[idx]['Text'], cosine_similarities[idx][0]

#Next we need to create the make_prompt function. This function will take the query and the best passage and return the prompt.
def make_prompt(query, relevant_passage):
    escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
    prompt = textwrap.dedent("""\
    AI assistant, answer the query: '{query}'. Use the following relevant passage: '{escaped}'.
    Provide a comprehensive response with necessary context or background information. Feel free to use your own knowledge to fill in any gaps or provide additional insights.
    """).format(query=query, escaped=escaped)

    return prompt


# create register route app function
def register_routes(app):
    # Now we need to create the app route for the home page.
    @app.route('/', methods=['GET', 'POST'])
    def index():
        loaded_files = os.listdir(DOCUMENT_DIR)
        if request.method == 'POST':
            query = request.form['topic']
            passage = find_best_passage(query, df)
            prompt = make_prompt(query, passage)
            temperature = 0.2
            section = palm.generate_text(
            prompt=prompt,
            model=text_model2,
            candidate_count=3,
            temperature=temperature,
            max_output_tokens=8000
        )

            if not section.candidates:
                return "No text was generated for this topic."

            section = section.candidates[0]['output']
            with open(RESPONSE_FILENAME, 'a') as response_file:
                response_file.write(f"Query: {query}\nResponse: {section}\n")

            return f"Response to '{query}' has been added to the response file."

        return render_template('index.html', loaded_files=loaded_files)  # assuming you have a template named index.html

    @app.route('/get-models', methods=['GET'])
    def get_models():
        embedding_model_name = text_model.name if text_model else None
        generation_model_name = text_model2.name if text_model2 else None        
        print(f"Embedding Model In Use: {embedding_model_name}")
        print(f"Text Generation Model In Use: {generation_model_name}")
        return jsonify({'embedding_model': embedding_model_name, 'generation_model': generation_model_name})
    
    @app.route('/chat', methods=['GET', 'POST'])
    def chat():
        form = ChatForm()
        if request.method == 'POST':
            user_message = request.form['message']
            response = palm.chat(messages=user_message)
            model_response = response.last
            return jsonify({'model_response': model_response})
        return render_template('chat.html', form=form)
    
    @app.route('/generate-section', methods=['POST'])
    def generate_section():
        topic = request.form['topic']
        passage, cosine_similarity = find_best_passage(topic, df)
        prompt = make_prompt(topic, passage)

        temperature = 0.3
        section = palm.generate_text(
            prompt=prompt,
            model=text_model2,
            candidate_count=3,
            temperature=temperature,
            max_output_tokens=8000
        )
        if not section.candidates:
            return jsonify({'error': 'No text was generated for this topic.'})

        section = section.candidates[0]['output']
        with open(RESPONSE_FILENAME, 'a', encoding='utf-8') as response_file:
                 response_file.write(f"User Query: {topic}\n")  # Write the user's query to the file
                 response_file.write(f"Document Genie Says:\n{section}\n")  # Write the generated 
        return jsonify({'section': section, 'cosine_similarity': cosine_similarity})


    @app.route('/clear-document', methods=['POST'])
    def clear_document():
        clear_output = request.form.get('clear_output')
        if clear_output == 'true':
            # Clear the output screen
            with open(RESPONSE_FILENAME, 'w') as response_file:
                response_file.write('')
        
        # Get the updated list of loaded files
        loaded_files = os.listdir(DOCUMENT_DIR)
        # Return a JSON response indicating the success of clearing the document
        return jsonify({'success': 'Document cleared', 'loaded_files': loaded_files})