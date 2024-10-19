import streamlit as st
import pandas as pd
from google.cloud import firestore

st.set_page_config(page_title="First Responder Landing Page", page_icon="https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/850170/capsule_616x353.jpg?t=1710854690", layout="wide")

hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

# Authenticate to Firestore with the JSON account key.
db = firestore.Client.from_service_account_json("firestore-key.json")

st.header('ProjectName First Responder Dashboard')
st.write("")
st.write("")
st.write("")

# Fetch data from Firestore (assuming the collection is named 'emergencies')
emergencies_ref = db.collection('emergencies')
emergencies = emergencies_ref.stream()

# Create a list to hold emergency data
emergency_list = []

for emergency in emergencies:
    emergency_data = emergency.to_dict()
    doc_id = emergency.id

    # Extracting fields from the Firestore document
    lat = emergency_data.get('lat', 0.0)
    lon = emergency_data.get('lon', 0.0)
    image1 = emergency_data.get('pic1', '')
    image2 = emergency_data.get('pic2', '')
    image3 = emergency_data.get('pic3', '')
    condition = emergency_data.get('condition', 'Unknown')
    current_action = emergency_data.get('current', 'N/A')
    description = emergency_data.get('description', 'No description')
    equipment = emergency_data.get('equipment', 'Unknown')
    number = emergency_data.get('number', 'N/A')
    people = emergency_data.get('people', 0)

    # Create map data for current emergency location
    data = {
        'lat': [lat],
        'lon': [lon],
    }
    df = pd.DataFrame(data)

    # Store the emergency data in a list for later use
    emergency_list.append({
        'doc_id': doc_id,
        'images': [image1, image2, image3],
        'number': number,
        'description': description,
        'equipment': equipment,
        'condition': condition,
        'current_action': current_action,
        'people': people,
        'map_data': df,
    })

# Display three emergencies per row with dividers
for i in range(0, len(emergency_list), 3):
    # Create a new container for each row of emergencies
    cols = st.columns(3)

    for j, emergency in enumerate(emergency_list[i:i+3]):
        with cols[j % 3]:  # Ensure we don't exceed the number of columns
            # Create map for the emergency
            st.map(emergency['map_data'])

            st.image(emergency['images'][0])
            st.image(emergency['images'][1])
            st.image(emergency['images'][2])
            st.write(f"**Phone Number:** {emergency['number']}")
            st.write(f"**Description:** {emergency['description']}")
            st.write(f"**Equipment Needed:** {emergency['equipment']}")
            st.write(f"**Victim Condition:** {emergency['condition']}")
            st.write(f"**Current Action:** {emergency['current_action']}")
            st.write(f"**Number of People:** {emergency['people']}")

            # Dispatch button
            if st.button('Dispatch', key=emergency['doc_id']):
                st.success('Sent to first responders!', icon="✅")

    # Divider between rows of emergencies
    st.markdown("---")