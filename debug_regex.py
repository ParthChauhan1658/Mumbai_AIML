
import re
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pattern from TextAnalyzer
regexes = {
    "urgency": re.compile(
        r"\b(urgent|immediately|asap|act now|expires|24 hours|suspended|restricted|unauthorized)\b",
        re.IGNORECASE
    ),
    "financial": re.compile(
        r"\b(wire transfer|payment|invoice|overdue|amount due|bitcoin|crypto|wallet)\b",
        re.IGNORECASE
    )
}

content = "Parth,\n\nI need you to process a wire transfer of $50,000 to this new vendor immediately. I am in a meeting so don't call me. Just get it done.\n\nThanks,\nCEO"
subject = "Urgent Wire"

print(f"Testing Content: {content}")

for key, pattern in regexes.items():
    found = pattern.findall(content)
    print(f"Pattern '{key}': Found {found}")
    
# Test Subject too just in case
print(f"Testing Subject: {subject}")
for key, pattern in regexes.items():
    found = pattern.findall(subject)
    print(f"Pattern '{key}' in SUBJECT: Found {found}")
