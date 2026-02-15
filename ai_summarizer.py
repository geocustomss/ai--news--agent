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
        prompt = """
        Analyze the following AI news headlines and summaries for today.
        
        1. Create a concise "Executive Summary" (3-4 bullet points) of the overall trends.
        2. Identify the SINGLE most impactful story.
        3. For that top story, create a "Key Takeaway: Why it Matters" section explaining the industry impact or future implications (max 100 words).
        
        SPECIAL INSTRUCTIONS for Sources:
        - If a story is from "ArXiv AI", it is a research paper. TRANSLATE the technical/academic title into clear, plain English.
        - If a story is a "HOT REPO" from "GitHub Radar", explain why exactly people are starring it.
        
        4. For EVERY story provided, assign ONE of these badges: Breakthrough, Policy, Market, Tool.
        
        FORMAT:
        SUMMARY: [Your bullet points here]
        DEEP DIVE: [Your takeaway here]
        BADGES & TITLES:
        - [Original Title] | [Badge Name] | [Simplified Plain-English Title]
        ...
        
        News items:
        """
        for item in news_items:
            prompt += f"- {item['title']}: {item['summary']}\n"
            
        response = model.generate_content(prompt)
        text = response.text
        
        # Simple parsing
        summary = ""
        deep_dive = ""
        
        if "DEEP DIVE:" in text:
            summary_part, rest = text.split("DEEP DIVE:", 1)
            summary = summary_part.replace("SUMMARY:", "").strip()
            
            if "BADGES & TITLES:" in rest:
                deep_dive, badges_part = rest.split("BADGES & TITLES:", 1)
                deep_dive = deep_dive.strip()
                
                # Parse badges and titles
                for line in badges_part.split('\n'):
                    if '|' in line:
                        parts = [p.strip() for p in line.strip('- ').split('|')]
                        if len(parts) >= 2:
                            orig_title = parts[0].lower()
                            badge = parts[1]
                            simplified_title = parts[2] if len(parts) >= 3 else ""
                            
                            for item in news_items:
                                if item['title'].lower() in orig_title or orig_title in item['title'].lower():
                                    item['badge'] = badge
                                    if simplified_title and item['source'] == "ArXiv AI":
                                        item['title'] = simplified_title
            else:
                deep_dive = rest.strip()
        else:
            summary = text.replace("SUMMARY:", "").strip()
            
        return {"summary": summary, "deep_dive": deep_dive}
        
    except Exception as e:
        print(f"AI Summarization failed: {e}")
        return {"summary": "Failed to generate AI summary.", "deep_dive": ""}
