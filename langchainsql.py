#install mysql.connector-python
from key import key
import os
import streamlit as st
# from langchain import PromptTemplate, LLMChain
# from langchain import HuggingFaceHub
from langchain_community.llms import AlephAlpha
from langchain_core.prompts import PromptTemplate
from aleph_alpha_client import Client, CompletionRequest, Prompt
from sql import run_query
import pandas as pd
#########################################################################################
token = key
host = "https://alephalpha..../"
client = Client(token=token, host=host, total_retries=1)


####################################################################################

from aleph_alpha_client import Client, CompletionRequest, Prompt

from langchain_core.prompts import PromptTemplate
# answer shoule be only sql command, no extra information
template = """Generate a precise SQL command based on the given question. Do not include any additional text or queries. 
Do not include conditions or details not explicitly mentioned in the question. Attention to Uper/down cases.
from is departure and to is destination.
End your response immediately after the SQL command. 
Database name: flight
Columns: destination, departure, flight_date
Q: how many flights are there heading to Berlin on september?
A: SELECT COUNT(*) FROM flight WHERE destination="Berlin" AND MONTH(flight_date) = 9;

Q: are there flights to new york or london departing from paris on January first?
A: SELECT * FROM flight WHERE departure="Paris" AND (destination = "New York" OR destination = "London") AND flight_date ="2024-01-01";

Q: flights departures from berlin
A: SELECT * FROM flight WHERE departure = "Berlin";

Q: How many flights are from Berlin next month?
A: SELECT COUNT(*) FROM flight WHERE departure="Berlin" AND MONTH(flight_date) = MONTH(CURRENT_DATE + INTERVAL 1 MONTH);

Q: How many flights depart from Paris tomorrow?
A: SELECT COUNT(*) FROM flight WHERE departure="Paris" AND flight_date = CURRENT_DATE + INTERVAL 1 DAY;

Q: are there any flights depart from Paris in next two days?
A: SELECT * FROM flight WHERE departure = "Paris" AND flight_date BETWEEN NOW() AND NOW() + INTERVAL 2 DAY;

Q: Flights departing from New York on January 1st, 2025?
A: SELECT * FROM flight WHERE departure="New York" AND flight_date="2025-01-01";

Q: Insert flight from Berlin heading to Tehran on 2024 05 24
A: INSERT INTO flight (departure, destination, flight_date) VALUES ('Paris', 'Tehran', '2024-05-24');

Q: Can you delete information about flights from NEW york?
A: DELETE FROM flight WHERE departure="New York";

Q: Can you delete the flight heading to NEW york?
A: DELETE FROM flight WHERE destination="New York";

Q: What are the columns in the database?
A: SHOW COLUMNS FROM flight;

Q: show table
A: Show Tables;

{question}
A."""

prompt = PromptTemplate.from_template(template)

template2 = """
Given the following response, extract and return only the SQL command. in the following examples pay attention how Q: changed to the correct A:.
correct sql command ends with ;
please Do not include any additional text and Ignore any other text, Direct SQL Command:
Q: ~~~DELETE FROM flight WHERE departure="Istanbul";
A: 'DELETE FROM flight WHERE departure="Istanbul";'

Q: "Select * from flight"
A: Select * from flight;

Q: "Select * from flight;\n\nNote: The"
A: Select * from flight;

Q: "```\nSelect * from flight;\n```"
A: Select * from flight;

Q: A.\n Q. ~~~INSERT INTO flight (departure, destination, flight_date) VALUES ('Istanbul', 'Shiraz', '2024-11-16'); 
A: INSERT INTO flight (departure, destination, flight_date) VALUES ('Istanbul', 'Shiraz', '2024-11-16');

Q: show database;
A: Show Databases;

Q: {response1}
A:"""


prompt2 = PromptTemplate.from_template(template2)
# client = Client(token=token, host=host, total_retries=1)
llm = AlephAlpha(
    client=client,
    temperature=0,
    model="luminous-extended-control",
    maximum_tokens=50,
    aleph_alpha_api_key=token,
    host="https://alephalpha.gpu.tir.budru.de/",
)

llm_chain1 = prompt | llm
llm_chain2 = prompt2 | llm

##############



#################


#create streamlit:
def main():



    st.title("HPI-SecEng")
    #get user input:
    question=st.text_input("Enter your question")
##################################
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/HPI_logo.svg/1200px-HPI_logo.svg.png", width=150)
###################################
    #generate the response:
    if st.button("Get answer"):
        with st.spinner("Generating answer..."):
            response1= llm_chain1.invoke({"question": question})
            # st.success(response1)
            st.text(repr(response1))
            response=llm_chain2.invoke({"response1": response1})
            response=response.lstrip("-\/'~````\n~\n```")
            response=response.strip()
            st.success("Query results:")
            st.text(repr(response))
            # st.success(response)
            
        with st.spinner("Running SQL command..."):
            result = run_query(response) 
            # st.success(result)
            if result and len(result) > 1 and isinstance(result, list) and len(result[0])>1:#select
                df1 = pd.DataFrame(result, columns=['ID', 'Departure', 'Destination', 'Flight Date'])
                st.table(df1)
            elif result and len(result) > 0 and isinstance(result, int) or isinstance(result, str) or isinstance(result, list) :#Update, delete, count...
                st.success(f"result {result} ")
            else:
                data = {'ID': ["---"], 'Departure': ["---"], 'Destination': ["---"], 'Flight Date': ["---"]}
                df2=pd.DataFrame(data)
                st.table(df2)

        # formatted_response = format_response(response)
        # st.success(result)



        # st.success(result)



if __name__=="__main__":
    main()


##########################################################################
##########################################################################
##########################################################################
##########################################################################
##########################################################################SQL
import mysql.connector

def run_query(query):
    try:
        conn = mysql.connector.connect(
            host="172...",
            user="user",
            password="...",
            database="flights",
            port=3306
        )
        print("Successfully connected to the database.")
        cursor = conn.cursor(buffered=True)
        cursor.execute(query)
        conn.commit()
        if query.strip().upper().startswith("SELECT") : #Select
            records = cursor.fetchall()
            return records
        # elif query.strip().upper().startswith("DELETE"):
        #     cursor.execute("SELECT * FROM flight")
        #     all_records = cursor.fetchall()
        #     return all_records
        elif query.strip().upper().startswith("SHOW") :
            records = cursor.fetchall()
            return records
        #query.strip().upper().startswith("INSERT") or query.strip().upper().startswith("UPDATE") 
        else:
            cursor.execute("SELECT * FROM flight")
            all_records = cursor.fetchall()
            return all_records

    except mysql.connector.Error as e:
        return f"Database error: {e}"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()





##############################################################################################
 
