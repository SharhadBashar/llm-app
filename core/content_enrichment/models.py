# app/models/generated_content.py
import enum, uuid
from sqlalchemy import (
    Column, Text, DateTime, Boolean, Integer, Numeric, Enum, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from db.base import Base

class Function(str, enum.Enum):
    GENERATE = "generate"
    SHORTEN = "shorten"
    ELABORATE = "elaborate"
    POLISH = "polish"
    CHANGE_MY_TONE = "change_my_tone"

class OutputFormat(str, enum.Enum):
    TEXT = "text"
    HTML = "html"
    
class Tone(str, enum.Enum):
    # Standard tones
    SOPHISTICATED = "sophisticated"
    FRIENDLY = "friendly" 
    CASUAL = "casual"
    
    # Easter eggs
    SHAKESPEARE = "shakespeare"
    VICTORIAN = "victorian"
    JANE_AUSTEN = "jane_austen"
    CHARLES_DICKENS = "charles_dickens"
    HEMINGWAY = "hemingway"
    HOMER = "homer"
    RENAISSANCE = "renaissance"
    MEDIEVAL = "medieval"
    OLD_ENGLISH = "old_english"
    TRANSCENDENTALIST = "transcendentalist"
    BEAT_GENERATION = "beat_generation"
    FLAPPER_1920S = "flapper_1920s"
    KING_ARTHUR = "king_arthur"
    SHERLOCK_HOLMES = "sherlock_holmes"
    YODA = "yoda"
    GANDALF = "gandalf"
    GOLLUM = "gollum"
    TONY_STARK = "tony_stark"
    CAPTAIN_JACK_SPARROW = "captain_jack_sparrow"
    STARFLEET_OFFICER = "starfleet_officer"
    EIGHTIES_ACTION_HERO = "80s_action_hero"
    MARIE_ANTOINETTE = "marie_antoinette"
    QUEEN_ELIZABETH_I = "queen_elizabeth_i"
    WINSTON_CHURCHILL = "winston_churchill"
    ALBERT_EINSTEIN = "albert_einstein"
    GOTHIC_NOVEL = "gothic_novel"
    FAIRY_TALE = "fairy_tale"
    HORROR = "horror"
    THRILLER = "thriller"
    SCI_FI = "sci_fi"
    FANTASY = "fantasy"
    WESTERN = "western"
    MYSTERY = "mystery"
    SATIRE = "satire"
    PHILOSOPHICAL = "philosophical"
    ROMANTIC = "romantic"
    HAIKU = "haiku"
    SARCASTIC = "sarcastic"
    DRAMATIC = "dramatic"
    MELANCHOLIC = "melancholic"
    OPTIMISTIC = "optimistic"
    APATHETIC = "apathetic"
    EUPHORIC = "euphoric"
    PASSIVE_AGGRESSIVE = "passive_aggressive"
    MATTER_OF_FACT = "matter_of_fact"
    CYNICAL = "cynical"
    NYC_TAXI_DRIVER = "nyc_taxi_driver"
    TRAVEL_BLOGGER = "travel_blogger"
    SPORTS_COMMENTATOR = "sports_commentator"
    FASHION_CRITIC = "fashion_critic"
    SOUTHERN_GENTLEMAN = "southern_gentleman"
    KINDERGARTEN_TEACHER = "kindergarten_teacher"
    DRILL_SERGEANT = "drill_sergeant"
    STARTUP_BRO = "startup_bro"
    GRANDPARENT = "grandparent"
    LIBRARIAN = "librarian"
    STREAMER = "streamer"
    POLITICIAN = "politician"
    NEWS_ANCHOR = "news_anchor"
    YOUTUBER = "youtuber"
    LAWYER = "lawyer"
    DOCTOR = "doctor"
    SOFTWARE_ENGINEER = "software_engineer"
    PROFESSOR = "professor"
    CHEF = "chef"
    AIRLINE_PILOT = "airline_pilot"
    REDDIT_AMA_ANSWER = "reddit_ama_answer"
    TWITTER_THREAD = "twitter_thread"
    LINKEDIN_BRAG_POST = "linkedin_brag_post"
    AUSSIE_OUTBACK_EXPLORER = "aussie_outback_explorer"
    PIRATE = "pirate"
    SURFER_DUDE = "surfer_dude"
    SCI_FI_AI = "sci_fi_ai"

class ContentEnrichmentResponse(Base):
    __tablename__ = "content_enrichment_response"
    __table_args__ = {"schema": "ai"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_metadata = Column("metadata", JSON) # SQLAlchemy has a built in 'metadata' field that we can't override or use, forcing us to name the member 'content_metadata' however the column in the db will be as 'metadata'
    function = Column(Enum(Function, name="content_function", schema="ai", values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    tone = Column(Text) # We keep this as text because we don't want Postgres to enforce this -- it needs to be more configurable than that
    user_instructions = Column(Text)
    existing_text = Column(Text)
    ai_response = Column(Text, nullable=False)
    output_format = Column(Enum(OutputFormat, name="output_format", schema="ai", values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    accepted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False)
    failed = Column(Boolean, nullable=False, default=False)
    ai_model = Column(Text)
    latency_ms = Column(Integer)
    cost_usd = Column(Numeric(10, 4))