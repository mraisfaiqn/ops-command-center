import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    api_key=GEMINI_API_KEY,
    temperature=0.3,
)


class IncidentReportOutput(BaseModel):
    summary: str = Field(
        description="A clear, structured 2-4 sentence summary of the incident, suitable for an engineering log."
    )
    root_cause_hypothesis: str = Field(
        description="A plausible root cause hypothesis based on the asset type and incident details. "
                    "Phrase it as a hypothesis for engineers to validate, not a certainty."
    )
    stakeholder_email_draft: str = Field(
        description="A short, plain-English email update for non-technical stakeholders. "
                    "Include impact and current status. Avoid technical jargon."
    )


parser = JsonOutputParser(pydantic_object=IncidentReportOutput)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an experienced site reliability engineer who writes clear, professional incident "
            "documentation. Given details about an infrastructure incident, generate a structured report. "
            "Be concise and factual, and avoid speculation beyond what's reasonable given the details provided.\n\n"
            "{format_instructions}",
        ),
        (
            "human",
            "Asset: {asset_name} ({asset_type}) at {asset_location}\n"
            "Severity: {severity}\n"
            "Description: {description}\n"
            "Start time: {start_time}\n"
            "End time: {end_time}\n"
            "Status: {status}",
        ),
    ]
).partial(format_instructions=parser.get_format_instructions())

chain = prompt | llm | parser


def generate_incident_report(asset, incident) -> dict:
    """
    Runs the LangChain chain against Gemini and returns a dict with keys:
    summary, root_cause_hypothesis, stakeholder_email_draft.
    """
    return chain.invoke(
        {
            "asset_name": asset.name,
            "asset_type": asset.asset_type.value,
            "asset_location": asset.location or "Unknown",
            "severity": incident.severity.value,
            "description": incident.description,
            "start_time": incident.start_time.isoformat(),
            "end_time": incident.end_time.isoformat() if incident.end_time else "Ongoing",
            "status": "Ongoing" if incident.end_time is None else "Resolved",
        }
    )