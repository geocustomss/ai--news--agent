import google.generativeai as genai
import os

def summarize_news(news_items):
    """
    Summarizes a list of news items using Gemini API.
    Expects a GEMINI_API_KEY to be set in the environment.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not set. Skipping AI summarization.")
        return "No summary available (set GEMINI_API_KEY for AI summaries)."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prepare the prompt
        prompt = "Create a concise, bulleted executive summary (max 200 words) of the following AI news headlines. Focus on the most impactful trends and breakthroughs. Use a professional but engaging tone.\n\n"
        for item in news_items:
            prompt += f"- {item['title']}: {item['summary']}\n"
            
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"AI Summarization failed: {e}")
        return "Failed to generate AI summary."
