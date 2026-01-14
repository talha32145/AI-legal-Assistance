⚖️ PakLaw Assist — AI Legal Helper (Pakistan)

PakLaw Assist is an AI-powered legal guidance chatbot for Pakistan, built with Streamlit, NLP, and Google Gemini.
It provides safe, non-advocacy, step-by-step procedural guidance for common legal and government matters in Pakistan.

⚠️ This app provides general guidance only — not legal advice.

🚀 Key Features
🔐 Secure User System

Login & Signup system

Password hashing (SHA-256)

User data stored locally (CSV)

Persistent chat history per user

💬 Smart Chat Experience

Multiple saved chats per user

Chat titles auto-generated

Search chat history

Session memory handling

Clean chat UI with user/bot bubbles

🧠 Hybrid AI System

Online Mode: Google Gemini (Gemini 2.5 Flash Lite)

Offline Mode: TF-IDF + Cosine Similarity from legal CSV

Automatic internet availability detection

🚨 Emergency Safety Mode

Triggers on keywords like:
danger, threat, violence, kidnapping, harassment

Emergency mode:

Safety-first responses

Pakistan emergency helplines (15, FIA 1991)

Evidence preservation guidance

Calm bilingual reassurance

📚 Pakistan-Specific Legal Domains

FIR registration & police procedure

Cybercrime (FIA reporting)

Property disputes & mutation

Tenant–landlord issues

Traffic challans

NADRA CNIC / B-Form / Smart Card

Passport services

Nikahnama, Talaq, Khula

Consumer courts & complaints

Police harassment reporting

🛠️ Tech Stack
Category	Tools
Frontend	Streamlit
AI Model	Google Gemini
NLP	NLTK, TF-IDF
ML	Scikit-learn
Auth	SHA-256 hashing
Storage	CSV, JSON
Language	Python


2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Setup Environment Variable

Create a file named Secret_key.env

YOUR_API_KEY=your_google_gemini_api_key

4️⃣ Run the App
streamlit run app.py

📦 Required Python Packages
streamlit
pandas
nltk
scikit-learn
google-generativeai
python-dotenv
requests

🧠 How It Works
User logs in
User asks a legal question

App checks:
🚨 Emergency keywords → Emergency Mode
🌐 Internet available → Gemini AI

Response is formatted into:
Steps
Documents
Offices
Fees

Escalation paths
Chat is saved automatically
⚠️ Legal & Safety Disclaimer
This app does NOT provide legal advice
It offers general procedural guidance only
Always consult a licensed lawyer for legal matters
In emergencies, contact authorities immediately

⭐ Support & Contribution
If you find this project useful:
⭐ Star the repository
🛠 Contribute improvements
📢 Share feedback
