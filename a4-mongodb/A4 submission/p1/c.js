// c. (10 points) List all current female Democratic legislators. 
// Format each of them as { "name": "…", "age": …, "state": "…", 
// "type": "sen_or_rep" }, where age is an approximation obtained by 
// subtracting their birth year from 2025. Order them by the age attribute 
// (descending), with ties broken by name (ascending).

printjson(db.people.aggregate(
    {$match: {gender: "F"}},
    {$unwind: "$roles"},
    {$match: {"roles.current" : 1, "roles.party" : "Democrat"}},
    {$addFields: {age: {$subtract: [2025, {$year: "$birthday"}]}}},
    {$project: {_id: 0, name : 1, age: 1, state: "$roles.state", type: "$roles.type"}},
    {$sort: {age: -1, name: 1}},
).toArray())