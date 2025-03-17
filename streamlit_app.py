import os
import sys
import pysqlite3  # Ensure pysqlite3-binary is installed

# Replace the built-in sqlite3 module with pysqlite3
sys.modules['sqlite3'] = pysqlite3

import sqlite3  # This now refers to pysqlite3
import streamlit as st
from openai import OpenAI

# Set API keys via user input
gpt_api_key = st.text_input("Enter your OpenAI API key", type="password")
serper_api_key = st.text_input("Enter your Serper API key", type="password")

# IMPORTANT: Set the environment variable for OPENAI_API_KEY before any dependent libraries are loaded
if gpt_api_key:
    os.environ["OPENAI_API_KEY"] = gpt_api_key
    client = OpenAI(api_key=gpt_api_key)
    model="gpt-3.5-turbo",
    messages= {"role": "system", "content": "You are a helpful assistant"}
if serper_api_key:
    os.environ["SERPER_API_KEY"] = serper_api_key

from crewai import Crew, Process, Agent, Task
from crewai_tools import SerperDevTool, WebsiteSearchTool
from typing import Any, Dict

#Streamlit UI
st.title("Your New Favourite Psychic")
st.write("The Future is Closer Than You Think")

# User-provided inputs
st.title("💬 Chat with our psychic")
date_of_birth = st.text_input("When were you born? (enter your birthday in this format: 15 May 1990)")
time_of_birth = st.text_input("What time were you born? (enter your time of birth in this format: 14:30")
city_of_birth = st.text_input("Where where you born? (enter the closest city to your birth place: such as Seattle or New York")
research_question = st.text_input("What question do you have for the spirits?")

# Construct research topic
topic = (f"Person born on {date_of_birth} at {time_of_birth} in {city_of_birth}. "
         f"{research_question}")
print(f"DEBUG: Query being used for search: {topic}")

# Define Agents
researcher = Agent(
    name="Researcher",
    role="Astrology Researcher",
    goal="Gather reliable information on a topic and provide advice",
    backstory="An experienced astrologist and psychologist skilled in extracting key insights from online sources",
    tools=[WebsiteSearchTool(), SerperDevTool()],
    verbose=True
)

writer = Agent(
    name="Writer",
    role="Writer",
    goal="Accurately summarize detailed research about psychology and astrology to give personalized advice",
    backstory="An experienced psychic skilled in turning astrology and psychology research into thorough advice",
    tools=[WebsiteSearchTool(), SerperDevTool()],
    verbose=True
)


psychic = Agent(
    name="Psychic",
    role='Mystic Advisor',
    goal="Provide highly-specific observations and personalized advice with eccentric flair",
    temperature=1.3,  # High temperature for creativity
    backstory="You are a mystical fortune teller who gives wildly creative, dramatic, and humorous astrology readings. Be as theatrical and ridiculous as possible!",
    llm='gpt-3.5-turbo',
    tools=[WebsiteSearchTool(), SerperDevTool()],
    verbose=True
) 

# Define Tasks
research_task = Task(
    description=f"Use astrology-related sources to research: {topic}. Focus only on astrological insights and ignore unrelated topics.",
    expected_output=f"Summarise astrological predictions relevant to: {topic}. Ignore any unrelated content.",
    agent=researcher
)

write_task = Task(
    description=f"Write advice based on the research findings for: {topic}.",
    expected_output=f"Outline detailed notes.",
    agent=writer,
    context=[research_task]
)

summary_task = Task(
    description=f"Write advice in a fortune telling style based on the research findings for: {topic}.",
    expected_output=f"Answer the users question in a whimsical fortune",
    agent=psychic,
    context=[research_task]
)

# Assemble Crew
crew = Crew(
    agents=[researcher, writer, psychic],
    tasks=[research_task, write_task, summary_task],
    process=Process.sequential,
    verbose=True,
    manager_llm="gpt-3.5-turbo",
        manager_callbacks=["Crew Manager"]
    )
final = crew.kickoff()

# Execute Research
with st.spinner("Consulting the spirits..."):
    result = crew.kickoff()

#optional debug
#print(f"DEBUG: Query being used for search: {topic}")

if "messages" not in st.session_state:
    st.session_state.messages = []

st.session_state.messages.append({"role": "assistant", "content": result})
st.chat_message("assistant").write(result)