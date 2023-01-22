from datetime import datetime, timedelta, timezone

_url = "https://zmnebi.com"
updates = [
    {
        "title": "Added RSS feed",
        "description": "Added an RSS feed :)",
        "link": f"{_url}",
        "date": datetime(2022, 2, 18, 14, 55, 0, tzinfo=timezone(-timedelta(hours=6))),
    },
    {
        "title": "Added unprefixed AOR form",
        "description": "Added information on how to use the unprefixed AOR form.",
        "link": f"{_url}#how-to-use-aor",
        "date": datetime(2022, 2, 18, 15, 0, 0, tzinfo=timezone(-timedelta(hours=6))),
    },
    {
        "title": "Added FAQ item on saying 'to go'",
        "description": "Added information on when to use the two different forms for saying 'to go'.",
        "link": f"{_url}#which-motion-verb-should-be-used-for-to-go",
        "date": datetime(2022, 3, 28, 7, 0, 0, tzinfo=timezone(-timedelta(hours=6))),
    },
    {
        "title": "Added additional m-class person marker information",
        "description": "Added information regarding m-class verb forms which take the PRS 'to be' conjugation as the object marker.",
        "link": f"{_url}#person-markers",
        "date": datetime(2022, 5, 16, 21, 0, 0, tzinfo=timezone(-timedelta(hours=6))),
    },
    {
        "title": "Add FAQ item on formal variations on 'to be'",
        "description": "Added information on different variations one might encounter in formal writing or speech for the verb 'to be'.",
        "link": f"{_url}#person-markers",
        "date": datetime(2022, 11, 5, 8, 30, 0, tzinfo=timezone(-timedelta(hours=5))),
    },
    {
        "title": "Update information on 3PL.OPT 'to be' form",
        "description": "Add additional information on variation in 3PL.OPT 'to be' forms.",
        "link": f"{_url}#how-to-form-opt",
        "date": datetime(2023, 1, 22, 15, 30, 0, tzinfo=timezone(-timedelta(hours=5))),
    },
]
