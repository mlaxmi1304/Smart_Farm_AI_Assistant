from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv

import os
load_dotenv()

# Initialize LLM
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    
)

# Prompt template (VERY IMPORTANT)
prompt = ChatPromptTemplate.from_template("""
You are an expert agricultural advisor.

Disease: {disease_name}

Return response STRICTLY in this format:

Explanation:
- ...

Causes:
- ...

Treatment:
- ...

Prevention:
- ...

Keep it short and clear. Use bullet points.Return response in HTML format using <h4>, <ul>, <li> tags.
                                          
""")

# For tesiting this file:
# python plant_doctor.py

# chain = prompt | llm
# response = chain.invoke({"disease_name" : "Tomato_Blight"})
# print(response)

def get_plant_advice(disease_name):
    chain = prompt | llm
    response = chain.invoke({"disease_name": disease_name})
    return response.content