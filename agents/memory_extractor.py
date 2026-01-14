import requests

class MemoryExtractor:
    def __init__(self, fast_model_url: str = "http://localhost:8000/v1/chat/completions"):
        self.fast_model_url = fast_model_url

    def extract(self, text: str) -> list[str]:
        """
        Extract key factual statements from text.
        Returns a list of short, standalone sentences suitable for long-term memory.
        """
        prompt = f"""
        Extract the key factual statements from the following text.
        Only include facts that would be useful for long-term story and world memory:
        - character traits and relationships
        - world rules and constraints
        - important events and decisions
        - setting details that matter
        - political, religious, or technological structures

        Text:
        \"\"\"{text}\"\"\"

        Return the facts as a numbered list of short sentences.
        Do NOT include commentary, explanation, or headings. Just the facts.
        """

        payload = {
            "model": "Qwen/Qwen2.5-3B-Instruct",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }

        response = requests.post(self.fast_model_url, json=payload)
        data = response.json()
        raw = data["choices"][0]["message"]["content"]

        lines = raw.split("\n")
        facts: list[str] = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Accept numbered or dash bullets
            if line[0].isdigit() and "." in line:
                fact = line.split(".", 1)[1].strip()
            elif line.startswith("- "):
                fact = line[2:].strip()
            else:
                fact = line
            if fact:
                facts.append(fact)

        return facts
