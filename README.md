# SmartSpend AI - Automated Receipt & Expense Tracker

SmartSpend AI is a desktop application that automates the tedious process of expense tracking. Using Computer Vision (OpenCV) and Generative AI (Google Gemini), it scans paper receipts in real-time, extracts key financial data, and logs it into a structured CSV database.

## 🚀 Features
* **Live Camera Feed:** Real-time receipt capture using OpenCV.
* **AI-Powered OCR:** Uses Google Gemini 2.5 Flash to extract non-standard text from crumpled or blurry receipts.
* **Semantic Extraction:** Automatically identifies Vendor, Date, Total Amount, and Category (Food, Travel, etc.) from raw text.
* **Auto-Retry Mechanism:** Intelligent fallback system switches between AI models to ensure high availability and bypass rate limits.
* **Data Persistence:** Automatically appends data to a `my_expenses.csv` file for Excel integration.

## 🛠️ Tech Stack
* **Language:** Python 3.10+
* **GUI:** Tkinter (Custom Styles)
* **Computer Vision:** OpenCV (`cv2`), Pillow (`PIL`)
* **Artificial Intelligence:** Google Gemini Vision API
* **Data Handling:** CSV, JSON

## 📦 Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/SmartSpend-AI.git](https://github.com/YOUR_USERNAME/SmartSpend-AI.git)
    cd SmartSpend-AI
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup API Key**
    * Get a free API Key from [Google AI Studio](https://aistudio.google.com/).
    * Open `main.py` and paste your key into the `API_KEY` variable.

4.  **Run the App**
    ```bash
    python main.py
    ```

## 📸 Usage
1.  Click **"🔴 Start Camera"** to activate your webcam.
2.  Hold a receipt in front of the camera.
3.  Click **"SNAP RECEIPT & SAVE"**.
4.  Watch as the AI extracts the data and adds it to the table instantly!

## 🔮 Future Improvements
* Add data visualization (charts/graphs) for monthly spending.
* Integrate cloud storage (Google Sheets API) for remote access.
* Add multi-currency support.
