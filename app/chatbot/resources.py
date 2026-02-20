from typing import List

# In a production environment, this would be a real database (PostgreSQL/MongoDB)
# with geographic coordinates, operating hours, and active statuses.
SUPPORT_RESOURCES = [
    {
        "id": "1",
        "name": "Jaramogi Oginga Odinga Teaching and Referral Hospital (JOOTRH)",
        "type": "GBV & Psychosocial Support",
        "location": "Kisumu (Serving South Nyanza)",
        "contact": "0734 812 360",
        "description": "Major referral hospital offering comprehensive SGBV and mental health services."
    },
    {
        "id": "2",
        "name": "Homa Bay County Referral Hospital - GBV Recovery Center",
        "type": "GBV Response & Medical",
        "location": "Homa Bay",
        "contact": "Walk-in or 1195 for referral",
        "description": "Provides free medical treatment and psychosocial support to survivors of sexual and gender-based violence in Homa Bay county."
    },
    {
        "id": "3",
        "name": "Migori County Referral Hospital",
        "type": "Psychiatry & GBV Support",
        "location": "Migori",
        "contact": "Walk-in",
        "description": "Offers psychiatric services and GBV response for Migori residents."
    },
    {
        "id": "4",
        "name": "MSF (Médecins Sans Frontières) Clinic",
        "type": "Medical & GBV Support",
        "location": "Homa Bay",
        "contact": "Walk-in",
        "description": "Provides dedicated care for HIV/AIDS and Sexual Gender-Based Violence survivors."
    },
    {
        "id": "5",
        "name": "Nascop / Ministry of Health Toll-Free GBV Hotline",
        "type": "National Crisis Hotline",
        "location": "National (Toll-Free)",
        "contact": "1195",
        "description": "National toll-free GBV helpline providing immediate assistance and referrals across Kenya."
    }
]

def get_all_resources() -> List[dict]:
    return SUPPORT_RESOURCES

def format_resources_to_text() -> str:
    """Formats the top resources into a readable WhatsApp string."""
    text = "*Important Support Resources in Kenya:*\n\n"
    for r in SUPPORT_RESOURCES:
        text += f"🏥 *{r['name']}*\n"
        text += f"📞 Contact: {r['contact']}\n"
        text += f"ℹ️ {r['description']}\n\n"
    text += "Please reach out to them if you need immediate, professional help."
    return text
