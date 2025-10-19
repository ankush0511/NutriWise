import time
from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.groq import Groq
from agno.tools.reasoning import ReasoningTools
import os
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
load_dotenv()