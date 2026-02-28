import os
import json
import smtplib
import random
import google.generativeai as genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- CONFIGURATION ---
# REPLACE THESE VALUES WITH YOUR ACTUAL KEYS AND EMAILS
GEMINI_API_KEY = "AIzaSyBvgvRv1xy-hKI-dWV9HGh_BqBMpxn0454" 
SENDER_EMAIL = "mr.jenny.vd@gmail.com"
SENDER_PASSWORD = "julc jajw qtyo pbms" # Google App Password (16 chars, no spaces needed)
RECEIVER_EMAIL = "mr.jenny.vd@gmail.com"

# Initialize AI
genai.configure(api_key=GEMINI_API_KEY)

def load_topic():
    """
    Loads the curriculum and picks a random topic (or sequential based on logic).
    For this demo, we pick a random one to ensure variety during testing.
    """
    try:
        with open('p_and_c_curriculum.json', 'r') as f:
            topics = json.load(f)
            return random.choice(topics)
    except FileNotFoundError:
        print("Curriculum file not found. Creating a default topic.")
        return {
            "topic": "Introduction to Homeowners Insurance",
            "focus": "General overview of why insurance exists.",
            "form_context": "General"
        }

def generate_story(topic_data):
    """
    Uses the LLM to generate the educational story.
    Includes fallback logic to try multiple model names if one fails.
    """
    # List of models to try in order of preference
    # 'gemini-1.5-flash': The standard alias
    # 'gemini-1.5-flash-001': The specific version
    # 'gemini-pro': The classic stable model
    models_to_try = ['gemini-2.5-flash']

    prompt = f"""
    You are an expert Property & Casualty Insurance Underwriter and Educator.
    Your goal is to teach me about P&C insurance through storytelling.

    TODAY'S LESSON:
    - Topic: {topic_data['topic']}
    - Focus: {topic_data['focus']}
    - Context: {topic_data['form_context']}

    TASK:
    Write a short story (approx 300-400 words) formatted as a dialogue script.
    
    CHARACTERS:
    1. "The Agent": Experienced, calm, helpful, explains things simply but accurately.
    2. "The Homeowner": A new buyer, slightly confused, asks the questions a normal person would ask.

    STRUCTURE:
    1. **The Scenario**: Set the scene briefly (e.g., looking at a house, sitting in an office, storm approaching).
    2. **The Conversation**: The dialogue where the specific concept is explained. Use analogies.
    3. **The "Underwriter's Note"**: A summary box at the end explaining the technical takeaway in 1 sentence.

    Make it engaging but technically accurate regarding ISO forms.
    """

    for model_name in models_to_try:
        try:
            print(f"Attempting to generate with model: {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Failed with {model_name}: {e}")
            continue

    # If all attempts fail, list what IS available to help debug
    print("\nCRITICAL ERROR: All model attempts failed.")
    print("Listing available models for your API Key to help debugging:")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Could not list models: {e}")
        
    return None

def send_email(story, topic):
    """
    Sends the generated story via SMTP.
    """
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = f"🏠 Daily P&C Insight: {topic}"

    # Simple HTML styling
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
          <h2 style="color: #2c3e50;">{topic}</h2>
          <hr>
          {story.replace(chr(10), '<br>')} 
          <hr>
          <p style="font-size: 12px; color: #777;">
            This is an AI-generated educational story to help you learn P&C domain knowledge.
          </p>
        </div>
      </body>
    </html>
    """

    msg.attach(MIMEText(html_content, 'html'))

    try:
        # Connect to Gmail SMTP (Standard port 587 for TLS)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    print("--- Starting Agent ---")
    
    # 1. Get Topic
    todays_lesson = load_topic()
    print(f"Selected Topic: {todays_lesson['topic']}")
    
    # 2. Generate Content
    story_text = generate_story(todays_lesson)
    
    if story_text:
        # 3. Send Email
        send_email(story_text, todays_lesson['topic'])
    else:
        print("Skipping email due to generation failure.")

if __name__ == "__main__":
    main()