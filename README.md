# AI Trip Planner Pro 🌍✈️

AI Trip Planner Pro is an advanced travel planning application that leverages artificial intelligence to create comprehensive, personalized travel itineraries. Built with LangGraph and Streamlit, it provides a seamless experience for planning your next adventure.

## Features

- 🎯 **Requirement Analysis**: Intelligent breakdown of your travel preferences and needs
- 🗺️ **Destination Research**: Detailed information about your chosen destination
- 📅 **Smart Itinerary Planning**: Day-by-day activity scheduling with timing
- 💰 **Budget Calculator**: Comprehensive cost breakdown and estimates
- 🏨 **Accommodation Finder**: Personalized lodging recommendations
- 🛡️ **Safety Advisor**: Important safety and health information
- 📑 **Trip Documentation**: Complete trip summary with all essential details
- 📱 **User-Friendly Interface**: Clean, intuitive Streamlit web interface
- 📄 **PDF Export**: Download your complete trip plan as a PDF

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-trip-planner-pro.git
cd ai-trip-planner-pro
```

2. Create a virtual environment (recommended):
```bash
conda create -p myenv python==3.10 -y
conda activate myenv/  # On Windows
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your GROQ API key:
```
GROQ_API_KEY=your_api_key_here
```

## Usage

1. Start the Streamlit application:
```bash
cd src
streamlit run src/trip_planner_app_ui.py
```

2. Access the application in your web browser (typically at `http://localhost:8501`)

3. Fill in your trip details:
   - Destination
   - Travel dates
   - Budget
   - Accommodation preferences
   - Activity interests
   - Special requirements

4. Click "Generate Trip Plan" to receive your personalized travel plan

5. View your plan across different tabs and download it as a PDF if desired

## Project Structure

```
ai-trip-planner-pro/
├── src/
│   ├── trip_planner_app.py     # Core logic and LangGraph implementation
│   └── trip_planner_app_ui.py  # Streamlit user interface
├── requirements.txt            # Project dependencies
├── .env                       # Environment variables
└── README.md                  # Project documentation
```

## Dependencies

- Python 3.8+
- LangGraph
- Streamlit
- FPDF
- Groq API
- python-dotenv
- Other dependencies listed in `requirements.txt`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Powered by Groq's LLM technology
- Built with Streamlit and LangGraph
- Inspired by the need for intelligent travel planning

---

Made with ❤️ by AI Trip Planner 
