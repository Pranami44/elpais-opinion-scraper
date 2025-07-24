# 📰 El País Opinion Scraper & Translator

This script scrapes opinion article headlines from El País, translates them to English using RapidAPI, and analyzes the most repeated keywords.

---

## 🚀 Features

- Scrapes top 5 opinion article titles
- Translates Spanish titles to English using RapidAPI
- Analyzes repeated words in translated titles
- Saves article images locally

---

## 🔧 Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/elpais-translator.git
   cd elpais-translator

   ```

2. **Create and activate a virtual environment**  
   python3.11 -m venv venv
   source venv/bin/activate # On macOS/Linux

   OR

   venv311\Scripts\activate # On Windows

3. **Install dependencies**  
   pip install -r requirements.txt

4. **Create a .env file and add your RapidAPI key**  
   RAPIDAPI_KEY=your_actual_api_key_here

5. **Run the Script**
   python elpais_scraper.py
