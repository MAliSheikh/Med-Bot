import json


def get_guardrail_prompt(extracted_text, user_info=None, past_reports=None ):
    """
    Constructs a prompt that enforces JSON formatting and restricts hallucination.
    """
    # Truncate text to fit model context if necessary
    safe_text = extracted_text
    # safe_text = extracted_text[:2000]
    
    prompt = f'''
    You are a strict medical document data extraction system.

    Analyze the text and extract ALL important structured medical information.

    STRICT RULES:
    1. Extract ONLY data explicitly present in the text.
    2. Do NOT guess, infer, or hallucinate.
    3. If a value is missing, return null.
    4. Preserve original units and numbers exactly.
    5. Output MUST be valid JSON only.
    6. Extract EVERY laboratory test found.
    7. Do not skip abnormal values.
    8. Dates must be in YYYY-MM-DD format if present.
    9. If unsure about document type, use "Other".

    TEXT:
    """
    {safe_text}
    """

    USER INFO:
    """
    {json.dumps(user_info, ensure_ascii=False, default=str)}
    """

    PAST REPORTS:
    """
    {json.dumps(past_reports, ensure_ascii=False, default=str)}
    """

    REQUIRED JSON FORMAT:

    {{
      "document_type": "Lab Report | Prescription | Invoice | Other",

      "metadata": {{
        "patient_name": "string or null",
        "patient_id": "string or null",
        "age": "number or null",
        "gender": "Male | Female | Other | null",
        "report_date": "YYYY-MM-DD or null",
        "doctor_name": "string or null",
        "hospital_or_lab": "string or null"
      }},

      "lab_results": [
        {{
          "test_name": "string",
          "value": "string or number or null",
          "unit": "string or null",
          "reference_range": "string or null",
          "flag": "High | Low | Normal | Borderline | Abnormal | null"
        }}
      ],

      "vitals": {{
        "blood_pressure": "string or null",
        "heart_rate": "number or null",
        "temperature": "number or null",
        "oxygen_saturation": "number or null"
      }},

      "medications": [
        {{
          "name": "string",
          "dosage": "string or null",
          "frequency": "string or null",
          "duration": "string or null"
        }}
      ],

      "clinical_findings": [
        "string"
      ],

      "doctor_notes": "string or null",

      "user_info": {{
        "user_name": "string or null",
        "user_id": "string or null",
        "language_preference": "string or null"
      }},

      "past_reports": [
        {{
          "report_id": "string or null",
          "report_date": "YYYY-MM-DD or null",
          "summary": "string or null"
        }}
      ],

      "last_note": "string or null (brief plain-language note the patient can understand)",

      "summary": "Concise factual summary of the document in simple words for easy understanding with figure values shown."
    }}

    JSON OUTPUT:
    '''
    # print(prompt)

    return prompt



def get_rag_chat_guardrail_prompt(context_text, user_info, past_reports, question: str = None):
    """
    Strict RAG chat prompt for medical questions.
    Ensures structured JSON output, prevents hallucinations,
    recommends appointments without auto-booking.

    The caller should pass the original user question so the model
    knows what to answer.  If `question` is None we do not include it
    (for backwards compatibility).
    """
    user_info_str = json.dumps(user_info, ensure_ascii=False, default=str) if user_info else "{}"

    prompt = f"""
        You are a highly accurate medical assistant AI.

        Use ONLY the information provided in the MEDICAL CONTEXT below to answer the user's question.

        STRICT RULES:
        1. Do NOT hallucinate, infer, or guess.
        2. Answer ONLY based on the context provided.
        3. If the answer is unknown, say "I don't know based on the context."
        4. Always produce clear, concise, factual answers.
        5. Output MUST be valid JSON.
        6. If relevant, recommend specialists, but only if clearly indicated by the context.
        7. If an appointment is suggested, it is ONLY a recommendation; do NOT book automatically.
        8. Use simple language if summarizing for the patient.
        9. Preserve all numbers, units, and medical terminology exactly.

        MEDICAL CONTEXT:
        {context_text}

        PAST REPORTS:
        {past_reports}

        USER INFO:
        {user_info_str}
"""
    # append question if provided
    if question:
        prompt += f"\n\n        USER QUESTION:\n        {question}\n"""

    prompt += f"""

        REQUIRED JSON OUTPUT FORMAT:
        {{
          "answer_text": "Concise factual answer to user's question.",
          "recommended_specialist": "Specialist type if applicable, else null",
          "book_appointment": true/false,   # True = recommend to book, but do NOT book automatically
          "reference_sources": ["List of context sources used, e.g., book name + page"],
          "summary_for_patient": "Simple plain-language summary for patient if relevant"
        }}

        JSON OUTPUT:
        """
    return prompt