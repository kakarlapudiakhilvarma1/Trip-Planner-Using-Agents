import os
from dotenv import load_dotenv
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import Annotated
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
load_dotenv()

# Get GROQ API Key from Env variables
os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")

# Define state
class GraphState(TypedDict):
    messages: Annotated[list, add_messages]

# Create the graph
builder = StateGraph(GraphState)

# Create the LLM
llm = ChatGroq(model_name="gemma2-9b-It")

def create_node(state, system_prompt):
    human_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
    ai_messages = [msg for msg in state["messages"] if isinstance(msg, AIMessage)]
    system_message = [SystemMessage(content=system_prompt)]
    messages = system_message + human_messages + ai_messages
    message = llm.invoke(messages)
    return {"messages": [message]}

# Define specialized agents for trip planning
requirement_analyzer = lambda state: create_node(
    state,
    """You are a travel requirement analyzer. Review the user's trip requirements and break them down into:
    1. Destination details
    2. Travel dates
    3. Budget constraints
    4. Accommodation preferences
    5. Activity preferences
    6. Special requirements (dietary, accessibility, etc.)
    Be thorough and organized in your analysis."""
)

destination_researcher = lambda state: create_node(
    state,
    """You are a destination research specialist. Based on the analyzed requirements:
    1. Provide detailed information about the destination
    2. Suggest the best time to visit
    3. Highlight local customs and requirements
    4. Identify potential challenges or considerations
    Focus on practical, actionable information."""
)

itinerary_planner = lambda state: create_node(
    state,
    """You are an itinerary planning expert. Create a detailed day-by-day itinerary that includes:
    1. Daily activities and timing
    2. Restaurant recommendations
    3. Transportation options
    4. Backup plans for weather issues
    Make it realistic and well-paced."""
)

budget_calculator = lambda state: create_node(
    state,
    """You are a travel budget specialist. Create a detailed budget breakdown including:
    1. Transportation costs (flights, local transport)
    2. Accommodation costs
    3. Activity and entrance fees
    4. Estimated food costs
    5. Emergency fund recommendations
    Provide realistic estimates with sources where possible."""
)

accommodation_finder = lambda state: create_node(
    state,
    """You are an accommodation specialist. Based on the requirements and budget:
    1. Suggest suitable accommodation options
    2. Compare amenities and locations
    3. Provide booking tips and timing
    4. Highlight cancellation policies
    Focus on value for money and location benefits."""
)

safety_advisor = lambda state: create_node(
    state,
    """You are a travel safety expert. Provide comprehensive safety advice including:
    1. Health and vaccination requirements
    2. Local emergency numbers
    3. Areas to avoid
    4. Common scams to watch for
    5. Travel insurance recommendations
    Be thorough but not alarmist."""
)

trip_summarizer = lambda state: create_node(
    state,
    """You are a trip documentation specialist. Create a comprehensive summary including:
    1. Complete itinerary
    2. Budget breakdown
    3. Important contacts and bookings
    4. Safety tips and emergency info
    5. Packing recommendations
    Make it easy to reference and share."""
)

# Add nodes to the graph
builder.add_node("requirement_analyzer", requirement_analyzer)
builder.add_node("destination_researcher", destination_researcher)
builder.add_node("itinerary_planner", itinerary_planner)
builder.add_node("budget_calculator", budget_calculator)
builder.add_node("accommodation_finder", accommodation_finder)
builder.add_node("safety_advisor", safety_advisor)
builder.add_node("trip_summarizer", trip_summarizer)

# Set entry point and edges
builder.add_edge(START, "requirement_analyzer")
builder.add_edge("requirement_analyzer", "destination_researcher")
builder.add_edge("destination_researcher", "itinerary_planner")
builder.add_edge("itinerary_planner", "budget_calculator")
builder.add_edge("budget_calculator", "accommodation_finder")
builder.add_edge("accommodation_finder", "safety_advisor")
builder.add_edge("safety_advisor", "trip_summarizer")
builder.add_edge("trip_summarizer", END)

# Compile the graph
graph = builder.compile()

# Draw the graph
try:
    graph.get_graph(xray=True).draw_mermaid_png(output_file_path="trip_planner_graph.png")
except Exception:
    pass

# Create a main loop
def main_loop():
    print("Welcome to the Trip Planner! Please provide your trip details.")
    print("(Type 'quit', 'exit', or 'q' to end the session)")
    
    while True:
        user_input = input(">> ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Thank you for using Trip Planner. Have a great trip!")
            break

        response = graph.invoke({"messages": [HumanMessage(content=user_input)]})
        print("\nRequirement Analysis:")
        print(response["messages"][-7].content)
        print("\nDestination Research:")
        print(response["messages"][-6].content)
        print("\nItinerary Plan:")
        print(response["messages"][-5].content)
        print("\nBudget Calculation:")
        print(response["messages"][-4].content)
        print("\nAccommodation Suggestions:")
        print(response["messages"][-3].content)
        print("\nSafety Advisory:")
        print(response["messages"][-2].content)
        print("\nTrip Summary:")
        print(response["messages"][-1].content)

if __name__ == "__main__":
    main_loop()