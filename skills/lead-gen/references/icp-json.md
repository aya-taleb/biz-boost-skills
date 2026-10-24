# sales/icp.json

The tool reads this to score each lead from 0 to 100. The score is the share of points a row
earns. A disqualify rule sets the score to 0 and says why.

Fields you can match on are any column in leads.csv or lead-facts.csv (see `columns.md`). Match types:

| match | meaning |
| --- | --- |
| contains_any | the field contains any of `values` (not case sensitive) |
| equals_any | the field is exactly one of `values` |
| range | the field holds a number (or a range like 11-50) between `min` and `max` |
| present | the field is not empty |

Example for an invoicing app for small law firms:

```json
{
  "criteria": [
    {"name": "law firm", "field": "industry", "match": "contains_any",
     "values": ["law", "legal", "attorney"], "points": 30},
    {"name": "5 to 50 staff", "field": "size", "match": "range", "min": 5, "max": 50,
     "points": 25},
    {"name": "uses a competitor or asks for one", "field": "signals", "match": "contains_any",
     "values": ["clio", "alternative", "switching"], "points": 30},
    {"name": "decision maker known", "field": "role", "match": "present", "points": 15}
  ],
  "disqualify": [
    {"name": "over 200 staff", "field": "size", "match": "range", "min": 201},
    {"name": "already a customer", "field": "status", "match": "equals_any", "values": ["won"]}
  ]
}
```

Example for a lunch subscription for offices near one street:

```json
{
  "criteria": [
    {"name": "office with 20+ people on site", "field": "size", "match": "range", "min": 20,
     "points": 35},
    {"name": "inside the delivery area", "field": "city", "match": "contains_any",
     "values": ["{{your neighborhood}}"], "points": 30},
    {"name": "no staff cafeteria", "field": "signals", "match": "contains_any",
     "values": ["no cafeteria", "no kitchen", "catered lunches"], "points": 20},
    {"name": "office manager or people team named", "field": "role", "match": "present",
     "points": 15}
  ]
}
```

Keep 3 to 6 criteria. More rules make the score look precise without making it better.
