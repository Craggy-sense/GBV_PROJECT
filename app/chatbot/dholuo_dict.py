# A curated dictionary of conversational and medical Dholuo phrases 
# serving as In-Context Learning (Few-Shot) examples for the AI Translator.

DHOLUO_DICTIONARY = [
    # Greetings & Common Expressions
    {"english": "Hello / Greetings", "dholuo": "Misawa"},
    {"english": "How are you?", "dholuo": "Idhi nade?"},
    {"english": "I am fine.", "dholuo": "Adhi maber."},
    {"english": "I am not fine.", "dholuo": "Ok adhi maber."},
    {"english": "Good morning", "dholuo": "Oywore"},
    {"english": "Good afternoon", "dholuo": "Osaore"},
    {"english": "Good night", "dholuo": "Otuoma"},
    {"english": "Thank you", "dholuo": "Erokamano"},
    {"english": "Thank you very much", "dholuo": "Erokamano ahinya"},
    {"english": "Please", "dholuo": "Kwayo"},
    {"english": "Yes", "dholuo": "Ee"},
    {"english": "No", "dholuo": "Ooyo"},
    {"english": "Okay", "dholuo": "Kare / Ber"},
    {"english": "I understand", "dholuo": "Awinjo"},
    {"english": "I don't understand", "dholuo": "Ok awinji"},
    {"english": "I am here", "dholuo": "An kae"},
    {"english": "Welcome", "dholuo": "Karibu"},
    {"english": "Goodbye", "dholuo": "Oriti"},
    
    # Emotional Support & Listening
    {"english": "I need help.", "dholuo": "Aonge kony."},
    {"english": "Help me.", "dholuo": "Konya."},
    {"english": "I want to talk to someone.", "dholuo": "Adwaro wuoyo gi ng'ato."},
    {"english": "I am listening to you.", "dholuo": "Awinji."},
    {"english": "I am here to listen.", "dholuo": "An kae mondo awinji."},
    {"english": "How can I help you today?", "dholuo": "Anyalo konyi nade kawuono?"},
    {"english": "Tell me what happened.", "dholuo": "Nyisa gima notimore."},
    {"english": "You are safe here.", "dholuo": "In ritore kae."},
    {"english": "I am sorry that happened.", "dholuo": "Mos kuom gima otimoreno."},
    {"english": "It is going to be okay.", "dholuo": "Duto biro bedo maber."},
    {"english": "Take a deep breath.", "dholuo": "Yue matek."},
    {"english": "You are not alone.", "dholuo": "Ok in kende."},
    {"english": "Don't cry.", "dholuo": "Kik ywagri."},
    {"english": "Take your time.", "dholuo": "Kaw thuoloni kendo winji maten."},
    
    # Distress Emotions (User inputs to recognize)
    {"english": "I am stressed.", "dholuo": "Chunya chandore malit."},
    {"english": "I am sad.", "dholuo": "Kuyo omaka."},
    {"english": "I am angry.", "dholuo": "Ager."},
    {"english": "I am scared / frightened.", "dholuo": "Aluor."},
    {"english": "I am anxious / worried.", "dholuo": "Chunya chandore."},
    {"english": "I feel bad.", "dholuo": "Awinjo marach."},
    {"english": "It hurts.", "dholuo": "Rem."},
    {"english": "It is painful.", "dholuo": "Lit ahinya."},
    {"english": "There is a problem.", "dholuo": "Kech nitie."},
    {"english": "My heart is heavy.", "dholuo": "Chunya pek."},
    
    # GBV & Physical Danger Terminology
    {"english": "Gender-based violence", "dholuo": "Sand mar jathari"},
    {"english": "Someone hurt me.", "dholuo": "Ng'ato ohinga."},
    {"english": "He beat me.", "dholuo": "Ochwada."},
    {"english": "She beat me.", "dholuo": "Ochwada."},
    {"english": "They hit me.", "dholuo": "Gigoya."},
    {"english": "I was raped.", "dholuo": "Oninja gi thuon / Otura."},
    {"english": "Sexual assault", "dholuo": "Ninjo gi thuon / Ketho ng'ato"},
    {"english": "My husband hit me.", "dholuo": "Chuora ogoya."},
    {"english": "My wife hit me.", "dholuo": "Chienga ogoya."},
    {"english": "My partner is hurting me.", "dholuo": "Ng'at madak godo asandora."},
    {"english": "I am being threatened.", "dholuo": "Itwega."},
    {"english": "He has a weapon.", "dholuo": "Onwang'o gige lweny."},
    {"english": "I am afraid to go home.", "dholuo": "Aluor dhi pacho."},
    {"english": "I am in danger.", "dholuo": "An e masira."},
    {"english": "Violence", "dholuo": "Pidhruok marach / Gero"},
    {"english": "Abuse", "dholuo": "Sand."},
    {"english": "Domestic violence", "dholuo": "Sand e ot / Gero e dala"},
    {"english": "Run away", "dholuo": "Ringi."},
    {"english": "Hide", "dholuo": "Pondo."},
    {"english": "Get out of the house.", "dholuo": "A e ot."},
    {"english": "Do you need a safe place?", "dholuo": "Idwaro kar pondo maber?"},
    {"english": "I want to report to the police.", "dholuo": "Adwaro dhi kar obila."},
    
    # Medical, Action & Emergency Directives
    {"english": "Please come quickly.", "dholuo": "Bi mapiyo."},
    {"english": "Mental health", "dholuo": "Ngima mar paro"},
    {"english": "Doctor", "dholuo": "Jathieth"},
    {"english": "Medicine", "dholuo": "Yath"},
    {"english": "Police", "dholuo": "Obila"},
    {"english": "Police station", "dholuo": "Kar obila"},
    {"english": "Call this number", "dholuo": "Go namba ni"},
    {"english": "Emergency", "dholuo": "Masira"},
    {"english": "Where is the hospital?", "dholuo": "Osiptal nitie kanye?"},
    {"english": "Clinic / Dispensary", "dholuo": "Kilini"},
    {"english": "Hospital", "dholuo": "Osiptal"},
    {"english": "Treatment / Care", "dholuo": "Thieth"},
    {"english": "Safe house", "dholuo": "Kar pondo maber"}
]

def get_dholuo_examples_prompt() -> str:
    """Formats the dictionary into a prompt-ready string for Few-Shot Learning."""
    prompt = "--- DHOLUO TRANSLATION DICTIONARY ---\n"
    for item in DHOLUO_DICTIONARY:
        prompt += f"English: '{item['english']}' -> Dholuo: '{item['dholuo']}'\n"
    prompt += "--------------------------------------"
    return prompt
