from typing import Dict, List
import time

# In-memory session storage. 
# Key: Phone number (string)
# Value: Dict containing last_interaction timestamp, chat history, and needs_human flag
sessions: Dict[str, dict] = {}
SESSION_TIMEOUT_SECONDS = 3600  # 1 hour

# sessions: Dict[str, dict] = {} # No longer needed, using DB
# SESSION_TIMEOUT_SECONDS = 3600  # 1 hour # No longer needed, using DB

def get_session_history(db, phone_number: str) -> List[dict]:
    # current_time = time.time() # No longer needed, DB handles timestamps
    
    # if phone_number in sessions: # No longer needed, using DB
    #     session = sessions[phone_number]
    #     # Check if session has timed out. If so, clear history but KEEP human flag if active
    #     if current_time - session["last_interaction"] > SESSION_TIMEOUT_SECONDS:
    #         needs_human = session.get("needs_human", False)
    #         sessions[phone_number] = {"last_interaction": current_time, "history": [], "needs_human": needs_human}
    #     else:
    #         session["last_interaction"] = current_time
    # else:
    #     sessions[phone_number] = {"last_interaction": current_time, "history": [], "needs_human": False}
    
    # return sessions[phone_number]["history"] # No longer needed, using DB
    return crud.get_chat_history(db, phone_number)

def append_to_history(db, phone_number: str, role: str, message: str):
    # Ensure session exists # No longer needed, crud handles user creation
    # get_session_history(phone_number)
    
    # history = sessions[phone_number]["history"] # No longer needed, using DB
    # history.append({"role": role, "content": content}) # No longer needed, using DB
    
    # Keep only the last 10 messages for context window management # No longer needed, DB handles this or we manage it on retrieval
    # if len(history) > 10:
    #     sessions[phone_number]["history"] = history[-10:] # No longer needed, using DB
    crud.add_message(db, phone_number, role, message)

def is_human_handoff_active(db, phone_number: str) -> bool:
    """Checks if the user's session is currently locked to a human mentor in the DB."""
    # if phone_number not in sessions: # No longer needed, crud handles user creation
    #     get_session_history(phone_number)
    # return sessions[phone_number].get("needs_human", False) # No longer needed, using DB
    user = crud.get_or_create_user(db, phone_number)
    return user.is_escalated

def trigger_human_handoff(db, phone_number: str):
    """Locks the session in the DB, bypassing AI for all future messages until resolved."""
    # if phone_number not in sessions: # No longer needed, crud handles user creation
    #     get_session_history(phone_number)
    
    # sessions[phone_number]["needs_human"] = True # No longer needed, using DB
    crud.set_user_escalation(db, phone_number, is_escalated=True)
    
    # --- MOCK NOTIFICATION SYSTEM ---
    print("\n" + "="*50)
    print("🚨 EMERGENCY ESCALATION TRIGGERED 🚨")
    print(f"👉 SENDING SMS/EMAIL NOTIFICATION TO MENTOR ON DUTY")
    print(f"👉 User: {phone_number}")
    print(f"👉 Please log in to http://localhost:8001/mentor to reply.")
    print("="*50 + "\n")

def resolve_human_handoff(db, phone_number: str):
    """Unlocks the session in the DB, returning control to the AI."""
    # if phone_number in sessions: # No longer needed, crud handles user existence
    #     sessions[phone_number]["needs_human"] = False # No longer needed, using DB
    crud.set_user_escalation(db, phone_number, is_escalated=False)

def clear_session(db, phone_number: str):
    # if phone_number in sessions: # No longer needed, crud handles user existence
    #     sessions[phone_number]["history"] = [] # No longer needed, using DB
    #     sessions[phone_number]["needs_human"] = False # No longer needed, using DB
    crud.clear_chat_history(db, phone_number)
    crud.set_user_escalation(db, phone_number, is_escalated=False)
