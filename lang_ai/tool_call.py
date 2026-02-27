from langchain_core.tools import Tool
from api.func.hospitals.appointments_crud import (
    book_appointment,
    cancel_appointment,
    get_appointment,
    get_user_appointments,
    update_appointment,
)
from api.func.hospitals.doctors_crud import (
    create_doctor,
    delete_doctor,
    get_all_doctors,
    get_doctor,
    get_doctors_by_hospital,
    update_doctor,
)
from api.func.hospitals.hospitals_crud import (
    create_hospital,
    delete_hospital,
    get_all_hospitals,
    get_hospital,
    update_hospital,
)
from api.func.reports.reports import (
    create_report,
    get_reports_by_user,
    get_report_by_id,
    delete_report_by_id,
    ai_analyze_report
)
from services.rag.qa import answer_query

tools = [
    # RAG QA
    Tool.from_function(
        name="AnswerQuery",
        func=answer_query,
        description="Answer a medical question using RAG and return the answer with source documents"
    ),
    # Appointments
    Tool.from_function(
        name="BookAppointment",
        func=book_appointment,
        description="Book a new appointment. Required arguments: doctor_id (from GetAllDoctors), user_id (auto-injected), date_time (from doctor's available_slots)"
    ),
    Tool.from_function(
        name="CancelAppointment",
        func=cancel_appointment,
        description="Cancel an appointment and return the slot to the doctor. Required argument: appointment_id (from GetUserAppointments)"
    ),
    Tool.from_function(
        name="GetAppointment",
        func=get_appointment,
        description="Retrieve a specific appointment by ID"
    ),
    Tool.from_function(
        name="GetUserAppointments",
        func=get_user_appointments,
        description="Retrieve all appointments for the current user with their appointment IDs. Use this before cancelling an appointment."
    ),
    Tool.from_function(
        name="UpdateAppointment",
        func=update_appointment,
        description="Update an appointment in MongoDB"
    ),
    # Doctors
    Tool.from_function(
        name="CreateDoctor",
        func=create_doctor,
        description="Create a new doctor in MongoDB"
    ),
    Tool.from_function(
        name="DeleteDoctor",
        func=delete_doctor,
        description="Delete a doctor from MongoDB"
    ),
    Tool.from_function(
        name="GetAllDoctors",
        func=get_all_doctors,
        description="Retrieve all doctors from MongoDB with their IDs, specialties, and available time slots. Use this before booking an appointment."
    ),
    Tool.from_function(
        name="GetDoctor",
        func=get_doctor,
        description="Retrieve a specific doctor by ID"
    ),
    Tool.from_function(
        name="GetDoctorsByHospital",
        func=get_doctors_by_hospital,
        description="Retrieve all doctors for a specific hospital"
    ),
    Tool.from_function(
        name="UpdateDoctor",
        func=update_doctor,
        description="Update a doctor in MongoDB"
    ),
    # Hospitals
    Tool.from_function(
        name="CreateHospital",
        func=create_hospital,
        description="Create a new hospital in MongoDB"
    ),
    Tool.from_function(
        name="DeleteHospital",
        func=delete_hospital,
        description="Delete a hospital from MongoDB"
    ),
    Tool.from_function(
        name="GetAllHospitals",
        func=get_all_hospitals,
        description="Retrieve all hospitals from MongoDB"
    ),
    Tool.from_function(
        name="GetHospital",
        func=get_hospital,
        description="Retrieve a specific hospital by ID"
    ),
    Tool.from_function(
        name="UpdateHospital",
        func=update_hospital,
        description="Update a hospital in MongoDB"
    ),
    # Reports
    Tool.from_function(
        name="CreateReport",
        func=create_report,
        description="Create a new medical report in MongoDB for a user"
    ),

    Tool.from_function(
        name="GetUserReports",
        func=get_reports_by_user,
        description="Retrieve all medical reports for a specific user"
    ),

    Tool.from_function(
        name="GetReport",
        func=get_report_by_id,
        description="Retrieve a specific medical report by report ID and user ID"
    ),

    Tool.from_function(
        name="DeleteReport",
        func=delete_report_by_id,
        description="Delete a medical report by ID for a specific user"
    ),

    Tool.from_function(
        name="AnalyzeReport",
        func=ai_analyze_report,
        description="Analyze an uploaded medical report (PDF or image) using AI and return insights"
    ),
]