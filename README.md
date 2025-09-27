# Outback_Early_Warning 

**AI in the Outback Hackathon Submission (2025)**  
A collaborative project by **Yash Singh** and **Trusha Sonawane**

---

## Overview
Outback_Early_Warning is a Streamlit-based dashboard that provides rural and regional Australians with **early-warning insights** into bushfires, floods, and severe weather events.  

By combining **official government feeds** (NSW Rural Fire Service, Bureau of Meteorology, AFDRS) with a transparent **AI-driven risk scoring system** and **ArcGIS geospatial integration**, the app empowers communities to prepare and respond effectively.

---

## Features
- **Unified Map Dashboard**: Live bushfire incidents (NSW RFS), BOM warnings, and NASA FIRMS hotspots.  
- **AFDRS Ratings**: Today’s Fire Danger Rating with actionable, plain-English guidance.  
- **Local Risk Score**: Personalized scoring system with explainable tags.  
- **Offline Safety Pack**: One-click PDF checklist + hotline contacts for low-connectivity areas.  
- **ArcGIS Integration**: Export ArcGIS-ready GeoJSON, publish as a Hosted Feature Layer, and embed an interactive Web Map/Dashboard.  
- **Low-Bandwidth Mode**: Optimized UI for rural internet environments.  

---

## Tech Stack
- **Frontend**: Streamlit, PyDeck (map layers)  
- **Backend**: Python, GeoPandas, Shapely, Requests  
- **Geospatial**: ArcGIS Online, NASA FIRMS  
- **Packaging**: venv, pip  
- **Collaboration**: GitHub, pair programming  

---

## Team
- **Yash Singh** — Co-engineered backend data fetchers, geospatial risk model, and ArcGIS integration; co-designed Streamlit UI and offline resources.  
- **Trusha Sonawane** — Co-engineered data ingestion and scoring workflows; co-designed UI/UX, visualization elements, and authored offline safety pack.  

> We worked closely together across all aspects of the project, ensuring true end-to-end collaboration and all-rounder contributions.

---

## Getting Started
Clone the repository and set up the environment:

```bash
git clone https://github.com/singhyash2209/Outback_Early_Warning.git
cd Outback_Early_Warning
python -m venv .venv
.venv\Scripts\Activate.ps1   # on Windows
pip install -r requirements.txt
streamlit run Home.py
```
---

## Demo



---

## Disclaimer

- This is a prototype built for the AI in the Outback Hackathon.
- It aggregates official data but is not an official warning service.
- Always follow directions from the NSW Rural Fire Service and Bureau of Meteorology.
