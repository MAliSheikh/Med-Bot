from fastapi import APIRouter, Depends
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage
from core.config import GROQ_API_KEY, GROQ_API_URL
from lang_ai.tool_call import tools
import asyncio
import json
import inspect
from api.func.auth.jwt_handler import get_current_user
from api.func.hospitals.doctors_crud import get_all_doctors, get_doctor
from api.func.hospitals.appointments_crud import get_user_appointments, delete_appointment
from bson.objectid import ObjectId
from dateutil.parser import parse
from difflib import SequenceMatcher

router = APIRouter()

# Initialize LLM
llm = ChatOpenAI(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
    base_url=GROQ_API_URL,
    temperature=0,
)

# Async agent runner
async def run_agent(user_message: str, user_id: str):
    """
    Simple AI router:
    1. Sends user message + tool list to LLM
    2. LLM returns tool name + JSON arguments
    3. Calls the tool function dynamically
    """
    # Build prompt
    prompt = "You are a helpful assistant. Decide which tool to use based on the user message.\n\n"
    prompt += f"User message: {user_message}\n\n"
    prompt += "Available tools:\n"
    for tool in tools:
        prompt += f"- {tool.name}: {tool.description}\n"
    prompt += "\nReturn ONLY a valid JSON object with 'tool_name' and 'arguments' fields. Do not include any other text or markdown formatting.\n"

    # Ask LLM
    response = await llm.agenerate([[HumanMessage(content=prompt)]])
    text = response.generations[0][0].text
    print(f"[DEBUG] Raw LLM Output: {text}")

    # Try parse LLM JSON output
    try:
        # Clean up potential markdown code blocks
        clean_text = text.strip()
        if "```" in clean_text:
            parts = clean_text.split("```")
            if len(parts) >= 2:
                clean_text = parts[1].strip()
                if clean_text.lower().startswith("json"):
                    clean_text = clean_text[4:]
        
        output = json.loads(clean_text.strip())
        tool_name = output.get("tool_name")
        arguments = output.get("arguments", {})
        print(f"[DEBUG] Parsed tool_name: {tool_name}")
    except Exception as e:
        print("[DEBUG] JSON parsing failed:", e)
        print("[DEBUG] Fallback to AnswerQuery RAG tool")
        tool_name = "AnswerQuery"
        arguments = {"query": user_message}

    # Find tool by name
    selected_tool = next((t for t in tools if t.name == tool_name), None)
    if not selected_tool:
        print(f"[DEBUG] Tool '{tool_name}' not found, fallback to AnswerQuery")
        selected_tool = next(t for t in tools if t.name == "AnswerQuery")
        arguments = {"query": user_message}

    # Dynamically map arguments based on function signature
    try:
        # Pre-process arguments for specific tools
        if tool_name == "AnswerQuery" and "query" in arguments:
            arguments["user_question"] = arguments.pop("query")

        if tool_name == "CancelAppointment" and "appointment_id" in arguments:
            appointment_id = arguments.get("appointment_id")
            try:
                ObjectId(appointment_id)
            except:
                user_appointments = await get_user_appointments(user_id)
                scheduled_appointments = [apt for apt in user_appointments if apt.status == "Scheduled"]
                
                if not scheduled_appointments:
                    return "You have no scheduled appointments to cancel."
                else:
                    # Take the first scheduled appointment and delete it.
                    appointment_to_delete = scheduled_appointments[0]
                    success = await delete_appointment(appointment_to_delete.id)
                    if success:
                        return f"Appointment {appointment_to_delete.id} has been automatically cancelled and deleted."
                    else:
                        return f"Failed to cancel appointment {appointment_to_delete.id}."

        if tool_name in ["BookAppointment", "UpdateAppointment"]:
            if tool_name == "BookAppointment" and "doctor_id" in arguments:
                doctor_identifier = arguments.get("doctor_id", "")
                try:
                    ObjectId(doctor_identifier)
                except:
                    all_doctors = await get_all_doctors()
                    best_match = None
                    highest_score = 0.0
                    for doc in all_doctors:
                        score = SequenceMatcher(None, doc.name.lower(), doctor_identifier.lower()).ratio()
                        if score > highest_score:
                            highest_score = score
                            best_match = doc
                    
                    if best_match and highest_score > 0.6: # Confidence threshold
                        arguments["doctor_id"] = best_match.id
                    else:
                        return f"Could not find a doctor matching '{doctor_identifier}'."

            if "date_time" in arguments:
                date_time_val = arguments.get("date_time")
                if isinstance(date_time_val, str):
                    try:
                        arguments['date_time'] = parse(date_time_val)
                    except (ValueError, TypeError):
                        if tool_name == "BookAppointment":
                            doctor_id = arguments.get("doctor_id")
                            if doctor_id:
                                doctor = await get_doctor(doctor_id)
                                if doctor and doctor.available_slots:
                                    arguments["date_time"] = doctor.available_slots[0]
                                else:
                                    return f"Doctor {doctor.name if doctor else 'ID: '+doctor_id} has no available slots."
                            else:
                                return "Could not determine the doctor to book an appointment with."
                        else: # UpdateAppointment
                            return "Please provide a specific date and time to update the appointment."

        sig = inspect.signature(selected_tool.func)
        final_arguments = {}

        # Iterate through function parameters and map arguments
        for param_name in sig.parameters:
            if param_name == "user_id":
                final_arguments["user_id"] = user_id
            elif param_name in arguments:
                final_arguments[param_name] = arguments[param_name]
            elif param_name in ["doctor_id", "appointment_id", "hospital_id", "report_id"]:
                for key, value in arguments.items():
                    if isinstance(value, dict) and "id" in value:
                        final_arguments[param_name] = value["id"]
                        break
            elif param_name == "user_question" and user_message and not arguments.get("user_question"):
                final_arguments["user_question"] = user_message
            elif param_name == "date_time" and "date_time" not in arguments:
                if "available_slots" in arguments:
                    final_arguments["date_time"] = arguments["available_slots"]
                elif "slot" in arguments:
                    final_arguments["date_time"] = arguments["slot"]

        arguments = final_arguments if final_arguments else arguments
    except Exception as e:
        print(f"[DEBUG] Argument mapping failed: {e}")
        if not arguments:
            arguments = {"query": user_message}
            if selected_tool.name == "AnswerQuery":
                arguments["user_question"] = arguments.pop("query")


    # Call tool function
    print(f"[DEBUG] Calling tool: {selected_tool.name} with arguments: {arguments}")
    try:
        result = await selected_tool.func(**arguments)
        print(f"[DEBUG] Tool result: {result}")
        return result
    except Exception as e:
        print(f"[ERROR] Tool execution failed: {e}")
        return f"Error executing tool {selected_tool.name}: {str(e)}"

# FastAPI endpoint
@router.post("/chat")
async def chat(message: str, current_user = Depends(get_current_user)):
    user_id = current_user.get("user_id") or current_user.get("id") or current_user.get("_id")
    result = await run_agent(message, str(user_id))
    return {"response": result}