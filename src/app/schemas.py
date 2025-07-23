from typing import TypedDict, Sequence, Annotated, Literal, List, Optional
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field
import operator

# --- Pydantic Models for Data Structuring ---

class StudentProfile(BaseModel):
    """A profile for a student user to personalize interactions."""
    user_name: Optional[str] = Field(
        description="The student's name, if they mention it.",
        default=None
    )
    grade_or_class: Optional[str] = Field(
        description="The student's academic grade or class (e.g., 'Class 10', 'HSC Candidate').",
        default=None
    )
    topics_of_interest: List[str] = Field(
        description="A list of subjects or specific topics the student has asked about (e.g., 'কবিতা', 'অপরিচিতা', 'ব্যাকরণ').",
        default_factory=list
    )
    last_topic_discussed: Optional[str] = Field(
        description="The main topic of the last question asked by the user to maintain context.",
        default=None
    )

class Grade(BaseModel):
    """Produce binary output based on the document's relevance."""
    binary_output: Literal["yes", "no"] = Field(
        description="If the document is relevant to the query, say 'yes', otherwise say 'no'."
    )

# --- Graph State Definition ---

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        messages: The history of messages in the current conversation.
        docs: Documents retrieved from the vector store.
        grade: The relevance grade of the retrieved documents ('yes' or 'no').
        src_docs: Documents retrieved from a web search.
    """
    messages: Annotated[Sequence[BaseMessage], operator.add]
    docs: list
    grade: Literal['yes', 'no']
    src_docs: str