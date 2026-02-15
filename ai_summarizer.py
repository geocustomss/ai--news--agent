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
        4. For EVERY story provided, assign ONE of these badges: Breakthrough, Policy, Market, Tool.
        
        Format your response exactly like this:
        SUMMARY: [Your bullet points here]
        DEEP DIVE: [Your takeaway here]
        BADGES:
        - [Story Title] | [Badge Name]
        - [Story Title] | [Badge Name]
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
            
            if "BADGES:" in rest:
                deep_dive, badges_part = rest.split("BADGES:", 1)
                deep_dive = deep_dive.strip()
                
                # Parse badges and apply to news_items
                for line in badges_part.split('\n'):
                    if '|' in line:
                        title_part, badge_part = line.strip('- ').split('|', 1)
                        title_part = title_part.strip().lower()
                        badge_part = badge_part.strip()
                        for item in news_items:
                            if item['title'].lower() in title_part or title_part in item['title'].lower():
                                item['badge'] = badge_part
            else:
                deep_dive = rest.strip()
        else:
            summary = text.replace("SUMMARY:", "").strip()
            
        return {"summary": summary, "deep_dive": deep_dive}
        
    except Exception as e:
        print(f"AI Summarization failed: {e}")
        return {"summary": "Failed to generate AI summary.", "deep_dive": ""}
