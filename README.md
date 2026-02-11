# 🏆 AgForecast
### 🥈 Runner-Up @ Echelon 2.0 — 24-Hour Sprint

**AgForecast: Full-stack AI agent for the Silver Prediction Market. Built in 24 hours, this Runner-Up project bridges raw data and insights by analyzing price-driving narratives. Features n8n-powered automated logic and a real-time Streamlit dashboard for high-impact sentiment visualization.**

## 🚀 Overview
AgForecast is an AI-powered narrative detection agent designed to analyze market sentiment and predict trends in the **Silver Prediction Market**. This project was built entirely from scratch in 24 hours for the Echelon 2.0 competition.

## 🏗️ System Architecture
The project utilizes a decoupled architecture to separate concerns and ensure speed:
* **Frontend:** Developed with **Streamlit** to provide a real-time, interactive dashboard for users to visualize market narratives and predictions.
* **Backend (Automation):** Powered by **n8n**, which handles the complex logic of fetching market data, running narrative detection workflows, and piping results to the frontend.

## 🛠️ Tech Stack
* **Languages:** Python (Streamlit)
* **Backend Logic:** n8n (Low-code Automation)
* **Data Handling:** JSON, Requests

## 📂 Project Structure
* `front.py`: The main Streamlit application script.
* `n8n_data.json`: **The Core Logic.** This file contains the exported n8n workflow. Since the live cloud instance is offline, this file serves as proof of the backend architecture.
* `requirements.txt`: Necessary Python dependencies for the frontend.

## 🏁 Note on Live Demo
The live site is currently offline as the 24-hour event's cloud hosting trial has concluded. However, all source code and logic workflows are provided here for evaluation to demonstrate the project's full functionality.
