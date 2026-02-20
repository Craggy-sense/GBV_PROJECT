import json
from groq import Groq
from app.core.config import settings
from app.chatbot.dholuo_dict import get_dholuo_examples_prompt

client = Groq(api_key=settings.GROQ_API_KEY)

def detect_and_translate_to_english(user_text: str) -> tuple[str, str]:
    """
    Detects the language of the incoming text (English, Swahili, or Dholuo) 
    and translates it to English for the core NLP engine.
    """
    if not settings.GROQ_API_KEY:
        return user_text, "English"

    dholuo_examples = get_dholuo_examples_prompt()

    prompt = f"""
    You are an expert linguist specializing in East African languages, specifically Swahili and Dholuo (Luo).
    Analyze the following text. 
    1. Identify the language (English, Swahili, or Dholuo/Luo). Use 'Dholuo' strictly instead of 'Luo'.
    2. Translate the text to exact English.
    
    If you suspect the text might be Dholuo, use this dictionary for reference to understand the context:
    {dholuo_examples}
    
    Format your response EXACTLY as a JSON object like this:
    {{"language": "Swahili", "translation": "I need help"}}
    
    Text to analyze: {user_text}
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        lang = result.get("language", "English")
        translation = result.get("translation", user_text)
        return translation, lang
        
    except Exception as e:
        print(f"Translation detection failed: {e}")
        return user_text, "English"


def translate_from_english(english_text: str, target_language: str) -> str:
    """
    Translates the bot's response back to the user's original language.
    """
    if target_language.lower() in ["english", "en"]:
        return english_text
        
    if not settings.GROQ_API_KEY:
        return english_text

    dholuo_injection = ""
    if "dholuo" in target_language.lower() or "luo" in target_language.lower():
         dholuo_examples = get_dholuo_examples_prompt()
         dholuo_injection = f"""
*** CRITICAL SYSTEM INSTRUCTION FOR DHOLUO ***
You are translating into Dholuo (Luo). 
Here is a vocabulary cheat sheet. You MUST use these words IF the concept appears in the English text.
However, DO NOT output the whole dictionary. DO NOT repeat words that don't belong in the sentence.

SAFETY FALLBACK: Please respond in Dholuo where possible. However, if you are unsure of the correct Dholuo phrasing for a complex medical or emotional concept, you MUST seamlessly switch to Swahili or English to ensure your advice remains safe, clear, and accurate. Do not invent fake Dholuo words.

Your ONLY job is to output the final translated sentence. 

[DHOLUO VOCABULARY REFERENCE]
{dholuo_examples}
"""

    prompt = f"""
    You are an expert, professional translator specializing in East African languages.
    Translate the following English text accurately into strictly {target_language}.
    Maintain the empathetic, professional, and supportive tone.
    CRITICAL: TRANSLATE CONCISELY. DO NOT WRITE MORE THAN 2 SENTENCES. DO NOT ADD ANY NEW INFORMATION.
    Output ONLY A VALID JSON OBJECT containing the translation, like this:
    {{"translation": "the translated text here"}}
    
    {dholuo_injection}
    
    [ENGLISH TEXT TO TRANSLATE]
    {english_text}
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Switched to a larger model for stricter instruction following
            messages=[{"role": "system", "content": prompt}],
            max_tokens=250,
            temperature=0.1, # Lowered temperature to stop hallucinations
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        return result.get("translation", english_text).strip()
    except Exception as e:
        print(f"Translation back to {target_language} failed: {e}")
        return english_text
