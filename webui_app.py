from flask import Flask, request, render_template, jsonify
import google.generativeai as palm
import textwrap
import numpy as np
import pandas as pd
import os

# Create Flask app
app = Flask(__name__)

# Create directory for documents to be uploaded to our vector DB.
DOCUMENT_DIR = "./documents/"
RESPONSE_FILENAME = 'response.txt'

# Setup API_KEY via environment variable
API_KEY = os.getenv('API_KEY')
palm.configure(api_key=API_KEY)

# Grab model that will work for our use case
models = [m for m in palm.list_models() if 'embedText' in m.supported_generation_methods]

# No Models? No Bueno.
if not models:
    raise ValueError("No models found that support 'embedText' generation method.")
text_model = models[0]
print(text_model)

# The following section searches for documents in the document directory and loads them into our documents list..
documents = []
# create a for loop to iterate through each document in DOCUMENT_DIR
for filename in os.listdir(DOCUMENT_DIR):
    # if the document ends with .txt, open the document and read it
    if filename.endswith(".txt"):
        # read the document join the document directory and the filename, and read the file in utf-8 encoding
        with open(os.path.join(DOCUMENT_DIR, filename), 'r', encoding='utf-8') as file:
            # if the document is not empty, print the document name, length, and the document
            doc_text = file.read()
            if doc_text.strip(): 
                print(f"Loaded document '{filename}' with length {len(doc_text)}:\n{doc_text}\n")
                documents.append(doc_text)
            else:
                print(f"Skipped empty document '{filename}'")
# after the for loop, print the number of documents loaded from the directory to the console
print(f"Loaded {len(documents)} documents from directory: {DOCUMENT_DIR}")
# Gotta let em know if there's no documents in the directory!
if not documents:
    raise ValueError(f"No text files found in the document directory: {DOCUMENT_DIR}")

# df is a pandas dataframe that contains the text and embeddings for each document.
df = pd.DataFrame(documents)

# df.columns represents the column names of the dataframe. Here, we're renaming the column to 'Text'.
df.columns = ['Text']

# Next we generate embeddings for each document and add them to the dataframe.  
# We pass the text and the model to the generate_embeddings function provided by the palm library.
df['Embeddings'] = [palm.generate_embeddings(model=text_model, text=text)['embedding'] for text in df['Text']]
if df['Embeddings'].isnull().any():
    raise ValueError("Failed to generate embeddings for some texts.")

# We convert the embeddings to numpy arrays. This is necessary for the cosine similarity function to work.
df['Embeddings'] = df['Embeddings'].apply(np.array)


#Next we need to create the make_prompt function. This function will take the query and the best passage and return the prompt.
def make_prompt(query, relevant_passage):
    #we set escaped equal to the query with all single and double quotes removed.
    escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
    prompt = textwrap.dedent("""\
    You are an AI assistant with access to a wide range of documents. Your role is to help answer queries by providing detailed, accurate, and relevant information based on these documents. 
    For the following query: '{query}', you have identified the following passage as potentially relevant: '{relevant_passage}'. 
    Please provide a comprehensive response, making sure to include any necessary context or background information.
    """).format(query=query, relevant_passage=escaped)
    
    # Return the prompt.
    return prompt

# We are updating this function to test stacking embeddings into a matrix.
def find_best_passage(query, dataframe):
    # Generate embeddings for the query!
    query_embedding = palm.generate_embeddings(model=text_model, text=query)

    # Stack the embeddings into a matrix.
    embeddings_matrix = np.stack(dataframe['Embeddings'].to_numpy()) # This is a numpy array of shape (n, 512) where n is the number of documents.
    # This is a numpy array of shape (n, 1) where n is the number of documents. #This is used to calculate the cosine similarity between the query and each passage in the document.
    dot_products = np.matmul(embeddings_matrix, query_embedding['embedding']) 
    idx = np.argmax(dot_products)
    return dataframe.iloc[idx]['Text'] # return the passage with the highest cosine similarity to the query.


# now we need to summon a new api model to handle the generatingOfText.
text_models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
if not text_models:
    raise ValueError("No models found that support 'generateText' generation method.")
# We grab the first model in the list.
text_model2 = text_models[0]

# Now we need to create the app route for the home page.
@app.route('/', methods=['GET', 'POST'])
def index():
    loaded_files = os.listdir(DOCUMENT_DIR)
    if request.method == 'POST':
        query = request.form['topic']
        passage = find_best_passage(query, df)
        prompt = make_prompt(query, passage)
        temperature = 0.5
        section = palm.generate_text(
        prompt=prompt,
        model=text_model2,
        candidate_count=3,
        temperature=temperature,
        max_output_tokens=5000
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

@app.route('/generate-section', methods=['POST'])
def generate_section():
    topic = request.form['topic']
    passage = find_best_passage(topic, df)
    prompt = make_prompt(topic, passage)

    temperature = 0.5
    section = palm.generate_text(
        prompt=prompt,
        model=text_model2,
        candidate_count=3,
        temperature=temperature,
        max_output_tokens=5000
    )
    if not section.candidates:
        return jsonify({'error': 'No text was generated for this topic.'})

    section = section.candidates[0]['output']
    with open(RESPONSE_FILENAME, 'a', encoding='utf-8') as response_file:
        response_file.write(f"Document Genie Says: {section}\n")

    return jsonify({'section': section})

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

if __name__ == "__main__":
    app.run(debug=True)