import streamlit as st
import pandas as pd
from google.cloud import firestore
import pydeck as pdk
from datetime import datetime

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

# Fetch data from Firestore (assuming the collection is named 'emergencies')
emergencies_ref = db.collection('emergencies')
emergencies = emergencies_ref.stream()

# Create a list to hold emergency data and coordinates for the map
emergency_list = []
all_coordinates = []

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
    code = emergency_data.get('code', 'No code')  # Fetching 'code'
    urgency = emergency_data.get('urgency', 0)    # Fetching 'urgency'

    # Collect coordinates for map
    all_coordinates.append({
        'lat': lat,
        'lon': lon,
        'code': code,
        'urgency': urgency
    })

    # Store the emergency data in a list for later use
    emergency_list.append({
        'doc_id': doc_id,
        'lat': lat,
        'lon': lon,
        'images': [image1, image2, image3],
        'number': number,
        'description': description,
        'equipment': equipment,
        'condition': condition,
        'current_action': current_action,
        'people': people,
        'code': code,
        'urgency': urgency
    })

# Create a DataFrame with all the coordinates
df_all_coordinates = pd.DataFrame(all_coordinates)

# Create two columns for the layout
col1, col2 = st.columns([2, 3])  # Adjust ratio as needed (col1: 2, col2: 3 for more space on emergency list)

# Column 1: Master map
with col1:
    st.subheader("Master Map of Emergency Locations")
    
    initial_view_state = pdk.ViewState(
        latitude=df_all_coordinates['lat'].mean(),
        longitude=df_all_coordinates['lon'].mean(),
        zoom=10,
        pitch=0,
    )

    layer = pdk.Layer(
        'ScatterplotLayer',
        data=df_all_coordinates,
        get_position='[lon, lat]',
        get_color='[200, 30, 0, 160]',
        get_radius=200,
    )

    # Render the map with PyDeck
    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=initial_view_state,
    ))

# Column 2: Emergency Details
with col2:
    @st.dialog("Details:")
    def show_emergency_details(emergency):
        st.write(f"**Phone Number:** {emergency['number']}")
        st.write(f"**Description:** {emergency['description']}")
        st.write(f"**Equipment Needed:** {emergency['equipment']}")
        st.write(f"**Victim Condition:** {emergency['condition']}")
        st.write(f"**Current Action:** {emergency['current_action']}")
        st.write(f"**Number of People:** {emergency['people']}")
        notes = st.text_input(label="Notes: ", key=emergency['doc_id'])

        # Show images if they exist
        if emergency['images'][0]:
            st.image(emergency['images'][0])
        if emergency['images'][1]:
            st.image(emergency['images'][1])
        if emergency['images'][2]:
            st.image(emergency['images'][2])

        # Dispatch button
        if st.button('Responded'):
            # Create a report document in Firestore
            report_data = {
                'emergency_id': emergency['doc_id'],
                'number': emergency['number'],
                'description': emergency['description'],
                'notes': notes,
                'equipment': emergency['equipment'],
                'condition': emergency['condition'],
                'current_action': emergency['current_action'],
                'people': emergency['people'],
                'code': emergency['code'],
                'urgency': emergency['urgency'],
                'timestamp': datetime.now(),
            }
            db.collection('reports').add(report_data)
            
            # Delete the emergency document
            db.collection('emergencies').document(emergency['doc_id']).delete()
            
            # Show success message
            st.success(f'Report created and emergency {emergency["code"]} resolved!')
    st.subheader("Emergency List")

    # Display emergency 'code' and 'urgency' initially
    for idx, emergency in enumerate(emergency_list):
        # Create a clickable button for each emergency code and urgency
        if st.button(f"Code: {emergency['code']}, Urgency: {emergency['urgency']}", key=f"emergency_{idx}"):
            # Show the details in a dialog/modal
            show_emergency_details(emergency)