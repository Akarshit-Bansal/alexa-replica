import spacy

# Load NLP model
nlp = spacy.load("en_core_web_sm")

def parse_command_spacy(command):
    """
    Uses spaCy to extract intents and entities from the command.
    """
    doc = nlp(command.lower())

    # Simple keyword-based intent detection
    if "play" in command:
        return "play", command.replace("play", "").strip()

    if "time" in command:
        return "time", None

    if "weather" in command:
        # Extract city name if available
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC"]:  # GPE = GeoPolitical Entity (cities, countries)
                return "weather", ent.text
        return "weather", None

    if "reminder" in command:
        # Find time + task
        time_text = None
        task_text = None
        for ent in doc.ents:
            if ent.label_ in ["TIME", "DATE"]:
                time_text = ent.text
        task_text = command.replace("set reminder", "").strip()
        return "reminder", (time_text, task_text)

    if "alarm" in command:
        for ent in doc.ents:
            if ent.label_ in ["TIME"]:
                return "alarm", ent.text
        return "alarm", None

    if "shopping" in command:
        if "add" in command:
            item = command.replace("add", "").replace("to shopping list", "").strip()
            return "shopping_add", item
        else:
            return "shopping_read", None

    if "news" in command:
        return "news", None

    if "joke" in command:
        return "joke", None

    if "traffic" in command:
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC"]:
                return "traffic", ent.text
        return "traffic", None

    if "score" in command:
        team = command.replace("score of", "").strip()
        return "score", team

    if "who" in command:
        person = command.replace("who is", "").strip()
        return "who", person

    if "date" in command:
        return "date", None

    if "stop" in command or "quit" in command or "exit" in command:
        return "stop", None

    return None, None

class NLU:
    def __init__(self, model_name='en_core_web_sm'):
        pass  # Not needed, but keep for compatibility

    async def parse(self, message):
        return self.parse_sync(message)

    def parse_sync(self, message):
        intent, data = parse_command_spacy(message)
        entities = []
        if data:
            if intent == "play":
                entities = [{"text": data, "label": "song"}]
            elif intent == "weather":
                entities = [{"text": data, "label": "GPE"}]
            elif intent == "reminder":
                if isinstance(data, tuple) and len(data) == 2:
                    entities = [{"text": data[0], "label": "TIME"}, {"text": data[1], "label": "task"}]
            elif intent == "alarm":
                entities = [{"text": data, "label": "TIME"}]
            elif intent == "shopping_add":
                entities = [{"text": data, "label": "item"}]
            elif intent == "traffic":
                entities = [{"text": data, "label": "GPE"}]
            elif intent == "score":
                entities = [{"text": data, "label": "team"}]
            elif intent == "who":
                entities = [{"text": data, "label": "person"}]
            # For others, no entities
        return {"intent": {"name": intent or "unknown", "confidence": 1.0}, "entities": entities}
