import pandas as pd
import plotly.express as px
import streamlit as st
import reverse_geocode

from dotenv import load_dotenv
import os
import requests


def request_interpretation(text):
  # Load the environment variables from the .env file
  load_dotenv()

  # Now you can access the environment variables using os.environ
  api_key = os.environ.get('OPEN_AI_API_KEY')

  from openai import OpenAI
  client = OpenAI()

  completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system", "content": "You are a helpful assistant that is helping parse coordinates and returning results in CSV: [DATE_RECIEVED,START_DATE,END_DATE,STATUS,LOCATION]."},
      {"role": "user", "content": text}
    ]
  )

  # print(completion.choices[0].message)
  return completion.choices[0].message.content


def get_port_data():
  # Load the JSON file into a DataFrame
  file_path = 'ports.json'  # Update this to your file path
  with open(file_path, 'r') as file:
      data = pd.read_json(file)

  # Transpose the DataFrame to get each port as a row and their attributes as columns
  df_transposed = data.transpose()

  # Handle potential inconsistencies in 'coordinates' data.
  # Extract and split coordinates only if they are in list format, else fill with NaN
  df_transposed['lat'] = df_transposed['coordinates'].apply(lambda x: x[1] if isinstance(x, list) else pd.NA)
  df_transposed['lon'] = df_transposed['coordinates'].apply(lambda x: x[0] if isinstance(x, list) else pd.NA)

  # Drop the original 'coordinates' column as it's no longer needed
  df_transposed_cleaned = df_transposed.drop(columns=['coordinates'])

  # Display the first few rows of the cleaned DataFrame
  print(df_transposed_cleaned.head())
  return df_transposed_cleaned

def port_map(st):
  df = get_port_data()

  st.title('Sea Ports Location Dashboard')

  # Plot using Plotly Express
  fig = px.scatter_geo(df,
                      lat='lat',
                      lon='lon',
                      hover_name='name',  # Shows port name when hovering over points
                      projection='natural earth')  # You can change the projection type

  st.plotly_chart(fig, use_container_width=True)


def get_country_from_coords(lat, lon):
    coordinates = [(lat, lon)]
    result = reverse_geocode.search(coordinates)
    # result is a list of dictionaries, get the 'country' from the first item
    return result[0]['country']

def load_data():
  # Load the CSV file into a DataFrame
  file_path = 'data/test.csv'  # Update this to your file path
  df = pd.read_csv(file_path)

  # Display the first few rows of the DataFrame
  print(df.head())
  # Apply the function to each row in the DataFrame
  df['country'] = df.apply(lambda row: get_country_from_coords(row['lat'], row['lon']), axis=1)
  return df

df = load_data()
print(df.head())


# Streamlit layout
st.set_page_config(layout="wide")
st.title("Ship Tracking Dashboard")

# Initialize session state for selected ship
if 'selected_ship' not in st.session_state:
    st.session_state.selected_ship = None

# Column layout
ship_names_col, map_col, sked_col = st.columns([1, 2, 2])

with ship_names_col:
    st.subheader("Ships")
    # Generate a button for each unique ship name
    ship_names = df['shipname'].unique()
    for name in ship_names:
        if st.button(name, key=name):  # Ensure each button has a unique key
            st.session_state.selected_ship = name
st.subheader("AI Intrepretation")
# Filter data for selected ship if any
if st.session_state.selected_ship:
    filtered_df = df[df['shipname'] == st.session_state.selected_ship]

    # Middle column for map
    with map_col:
        st.subheader(f"Route of {st.session_state.selected_ship}")
        st.map(filtered_df)

    # Right column for schedule data
    with sked_col:
        # Use a container for the schedule to potentially include scrolling
        sked_container = st.container()
        sked_container.subheader(f" Combined Schedule messages of {st.session_state.selected_ship} ")
        text = ""
        for index, row in filtered_df.iterrows():
            text += f"Date: {row['date']} - Sked: {row['sked']}\n"
        sked_container.text(text)
        interp = ""

    gpt_col, df_col = st.columns([2, 2])
    with gpt_col:
      with st.spinner('Wait for it...'):
        interp = request_interpretation(text="what is the schedule of the ship? return in CSV format with headers, please parse the date ranges [DATE_RECEIVED,START_DATE,END_DATE,STATUS]: "+text)
    
      st.text(interp)
  
    with df_col:

      from io import StringIO

      df = pd.read_csv(StringIO(interp))
      import plotly.express as px
      st.dataframe(df)
      # Create the Plotly Gantt chart
      fig = px.timeline(df, x_start="START_DATE", x_end="END_DATE", color="STATUS", title="Operations Gantt Chart",
                        labels={"Task": "Status"}, color_discrete_map={"UNDERWAY": "blue", "In transit": "orange", "PORT": "green"})
      fig.update_yaxes(categoryorder="total ascending")
      fig.update_layout(xaxis_title="Date", yaxis_title="Status", xaxis=dict(tickformat="%Y-%m-%d"))

      # Streamlit app
      st.title('Gantt Chart Visualization')
      st.plotly_chart(fig, use_container_width=True)

else:
    st.write("Please select a ship to display its information.")



