from key import key
import os
import streamlit as st
from langchain import PromptTemplate, LLMChain
from langchain import HuggingFaceHub

os.environ["HUGGINGFACEHUB_API_TOKEN"]=key

#LLM: llm using hagging face hub repository
repo_id="mistralai/Mistral-7B-Instruct-v0.2"
llm=HuggingFaceHub(repo_id=repo_id, model_kwargs={"temperature": 0.3, "max_new_tokens": 200})

#Template:
template="""

Question: {question}\n\n """

prompt=PromptTemplate(template=template, input_variables=["question"])
llm_chain=LLMChain(prompt=prompt, llm=llm)


#create streamlit:
def main():


    st.title("HPI-SecEng")
    #get user input:
    question=st.text_input("Enter your question")

    #generate the response:
    if st.button("Get answer"):
        with st.spinner("Generating answer..."):
            response= llm_chain.run(question)
        # formatted_response = format_response(response)
        st.success(response)



if __name__=="__main__":
    main()

