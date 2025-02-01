import streamlit as st
from trip_planner_app import graph
from langchain_core.messages import AIMessage, HumanMessage
from datetime import datetime, timedelta
import json
from fpdf import FPDF
import base64
import tempfile
import os

# Constants
title = "AI Trip Planner Pro"
icon = "✈️"

# Theme customization
st.set_page_config(page_title=title, page_icon=icon, layout="wide")

# Custom CSS for better styling
st.markdown("""
    <style>
        .stButton>button {
            width: 100%;
        }
        .card {
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
            background-color: #f8f9fa;
        }
        .reset-button {
            background-color: #dc3545;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.3rem;
            border: none;
            cursor: pointer;
        }
        .download-button {
            background-color: #28a745;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.3rem;
            border: none;
            cursor: pointer;
        }
    </style>
""", unsafe_allow_html=True)

class TripPlanPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_font("Arial", "B", 24)
        self.cell(0, 20, "Trip Plan", ln=True, align="C")
        
    def add_section(self, title, content):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, title, ln=True)
        self.set_font("Arial", "", 12)
        self.multi_cell(0, 10, content)
        self.ln(10)

def create_pdf(trip_data):
    pdf = TripPlanPDF()
    
    # Add form data
    pdf.add_section("Trip Details", (
        f"Destination: {trip_data['form_data']['destination']}\n"
        f"Dates: {trip_data['form_data']['start_date']} to {trip_data['form_data']['end_date']}\n"
        f"Budget: ${trip_data['form_data']['budget']}\n"
        f"Accommodation: {trip_data['form_data']['accommodation_type']}\n"
        f"Activities: {trip_data['form_data']['activities']}\n"
        f"Special Requirements: {trip_data['form_data']['special_requirements']}"
    ))
    
    # Add plan sections
    pdf.add_section("Requirements Analysis", trip_data['plan']['requirements'])
    pdf.add_section("Destination Research", trip_data['plan']['destination'])
    pdf.add_section("Itinerary", trip_data['plan']['itinerary'])
    pdf.add_section("Budget Breakdown", trip_data['plan']['budget'])
    pdf.add_section("Accommodation Options", trip_data['plan']['accommodation'])
    pdf.add_section("Safety Information", trip_data['plan']['safety'])
    pdf.add_section("Trip Summary", trip_data['plan']['summary'])
    
    return pdf

def format_plan_request(form_data):
    """Format the form data into a natural language request"""
    return f"""Planning a trip to {form_data['destination']} 
    from {form_data['start_date']} to {form_data['end_date']} 
    with a budget of ${form_data['budget']}. 
    Accommodation preference: {form_data['accommodation_type']}.
    Activities interested in: {form_data['activities']}.
    Special requirements: {form_data['special_requirements']}.
    """

def generate_trip_plan(user_input):
    """Generate trip plan using the LangGraph setup"""
    response = graph.invoke({"messages": [HumanMessage(content=user_input)]})
    ai_messages = [msg for msg in response["messages"] if isinstance(msg, AIMessage)]
    
    return {
        "requirements": ai_messages[-7].content,
        "destination": ai_messages[-6].content,
        "itinerary": ai_messages[-5].content,
        "budget": ai_messages[-4].content,
        "accommodation": ai_messages[-3].content,
        "safety": ai_messages[-2].content,
        "summary": ai_messages[-1].content,
    }

def reset_form():
    """Reset all form inputs and clear the trip plan"""
    st.session_state.trip_plans = []
    st.session_state.form_submitted = False
    for key in st.session_state.keys():
        if key.startswith('form_'):
            del st.session_state[key]

# Initialize session state
if 'trip_plans' not in st.session_state:
    st.session_state.trip_plans = []
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

# Header
st.title(f"{icon} {title}")

# Create two columns for the layout
left_col, right_col = st.columns([1, 2])

with left_col:
    st.header("Plan Your Trip")
    
    # Add Reset Button
    if st.button("Reset Form", key="reset_button", help="Clear all inputs and start over"):
        reset_form()
        st.rerun()
    
    with st.form("trip_planner_form", clear_on_submit=False):
        destination = st.text_input("Destination", 
                                  placeholder="e.g., Tokyo, Japan",
                                  key="form_destination")
        
        # Calculate date ranges
        today = datetime.now().date()
        max_date = today + timedelta(days=365)
        default_start = today + timedelta(days=30)  # Default to 30 days from now
        default_end = default_start + timedelta(days=7)  # Default to 7-day trip
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=default_start,
                min_value=today,
                max_value=max_date,
                key="form_start_date"
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=min(default_end, max_date),
                min_value=start_date,
                max_value=max_date,
                key="form_end_date"
            )
        
        budget = st.number_input("Budget (USD)", 
                               min_value=100, 
                               value=1000, 
                               step=500,
                               key="form_budget")
        
        accommodation_type = st.selectbox(
            "Accommodation Preference",
            ["Hotel", "Hostel", "Apartment", "Resort", "Boutique Hotel", "Traditional (e.g., Ryokan)"],
            key="form_accommodation_type"
        )
        
        activities = st.multiselect(
            "Activities Interest",
            ["Cultural Experiences", "Food & Dining", "Shopping", "Nature & Outdoors", 
             "Historical Sites", "Adventure Sports", "Relaxation", "Nightlife",
             "Art & Museums", "Local Events"],
            key="form_activities"
        )
        
        special_requirements = st.text_area(
            "Special Requirements",
            placeholder="e.g., Dietary restrictions, accessibility needs, etc.",
            key="form_special_requirements"
        )
        
        # Add submit button with proper handling
        submitted = st.form_submit_button("Generate Trip Plan")
        
        if submitted and destination:  # Basic validation
            st.session_state.form_submitted = True
            form_data = {
                "destination": destination,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "budget": budget,
                "accommodation_type": accommodation_type,
                "activities": ", ".join(activities) if activities else "No specific activities selected",
                "special_requirements": special_requirements or "None specified"
            }
            
            # Generate the plan
            with st.spinner("Generating your trip plan..."):
                formatted_request = format_plan_request(form_data)
                plan = generate_trip_plan(formatted_request)
                
                # Save to session state
                st.session_state.trip_plans.append({
                    "form_data": form_data,
                    "plan": plan
                })
        elif submitted and not destination:
            st.error("Please enter a destination")

# Rest of the code remains the same...
with right_col:
    if st.session_state.trip_plans:
        latest_plan = st.session_state.trip_plans[-1]
        
        # Create tabs for different sections
        tabs = st.tabs([
            "📋 Requirements",
            "🗺️ Destination",
            "📅 Itinerary",
            "💰 Budget",
            "🏨 Accommodation",
            "🛡️ Safety",
            "📑 Summary"
        ])
        
        # Requirements Tab
        with tabs[0]:
            st.markdown("### Requirements Analysis")
            st.markdown(latest_plan["plan"]["requirements"])
        
        # Destination Tab
        with tabs[1]:
            st.markdown("### Destination Research")
            st.markdown(latest_plan["plan"]["destination"])
        
        # Itinerary Tab
        with tabs[2]:
            st.markdown("### Detailed Itinerary")
            st.markdown(latest_plan["plan"]["itinerary"])
        
        # Budget Tab
        with tabs[3]:
            st.markdown("### Budget Breakdown")
            st.markdown(latest_plan["plan"]["budget"])
            
        # Accommodation Tab
        with tabs[4]:
            st.markdown("### Accommodation Options")
            st.markdown(latest_plan["plan"]["accommodation"])
            
        # Safety Tab
        with tabs[5]:
            st.markdown("### Safety Information")
            st.markdown(latest_plan["plan"]["safety"])
            
        # Summary Tab
        with tabs[6]:
            st.markdown("### Trip Summary")
            st.markdown(latest_plan["plan"]["summary"])

        # Create and download PDF
        if st.button("Download Trip Plan as PDF", key="download_pdf"):
            with st.spinner("Generating PDF..."):
                pdf = create_pdf(latest_plan)
                
                # Save PDF to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    pdf.output(tmp_file.name)
                    
                    # Read the temporary file and create download button
                    with open(tmp_file.name, "rb") as file:
                        pdf_bytes = file.read()
                        b64_pdf = base64.b64encode(pdf_bytes).decode()
                        
                        # Create download link
                        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="trip_plan_{latest_plan["form_data"]["destination"]}.pdf" class="download-button">Click here to download PDF</a>'
                        st.markdown(href, unsafe_allow_html=True)
                
                # Clean up the temporary file
                os.unlink(tmp_file.name)

# Add footer
st.markdown("---")
st.markdown("Made with ❤️ by AI Trip Planner")