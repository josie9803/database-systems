// d. (10 points) List the names of current Senators who at some point 
// earlier also served as Representatives. Format each of them as in the 
// form { "name": "…" }. Order them by name (ascending).

printjson(db.people.aggregate(
    {$match: {"roles.type": "rep"}},
    {$unwind: "$roles"},
    {$match: {"roles.type": "sen", "roles.current": 1}},
    {$project: {_id: 0, name: 1}},
    {$sort: {name: 1}},
).toArray())