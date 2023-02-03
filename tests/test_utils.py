import tool.utils as utils

RULES = {
    "text": r"[a-zA-Z0-9 ]*",
    "title": r"(text) \n",
    "space": r"\ *",
    "milestone": r"(?| \* (text) | () text)",
    "bar": r"(space =*)",
    "row": r"(text) \| bar milestone \n",
    "rows": r"(?: row)+",
    "titles": r"(?: space \| (text))+ \n",
    "label": r"([a-zA-Z0-9\-]*)",
    "caption": r"(text) \n?"
}

EXPANDED_RULES = {
    "text": r"[a-zA-Z0-9 ]*",
    "title": r"([a-zA-Z0-9 ]*) \n",
    "space": r"\ *",
    "milestone": r"(?| \* ([a-zA-Z0-9 ]*) | () [a-zA-Z0-9 ]*)",
    "bar": r"(\ * =*)",
    "row": r"([a-zA-Z0-9 ]*) \| (\ * =*) (?| \* ([a-zA-Z0-9 ]*) | () [a-zA-Z0-9 ]*) \n",
    "rows": r"(?: ([a-zA-Z0-9 ]*) \| (\ * =*) (?| \* ([a-zA-Z0-9 ]*) | () [a-zA-Z0-9 ]*) \n)+",
    "titles": r"(?: \ * \| ([a-zA-Z0-9 ]*))+ \n",
    "label": r"([a-zA-Z0-9\-]*)",
    "caption": r"([a-zA-Z0-9 ]*) \n?"
}

