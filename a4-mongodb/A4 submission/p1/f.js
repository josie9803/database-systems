// f. (12 points) List the names of legislators who are currently serving 
// New York but NOT serving in any committee or subcommittee. Format each 
// of them of an element of the form { "name": "…" }. Order them by name 
// (ascending).
printjson(db.people.aggregate(
    {$unwind: "$roles"},
    {$match: {"roles.state": "NY", "roles.current": 1}},
    {$lookup: {
        from: "committees", 
        localField: "_id", 
        foreignField: "members.id", 
        as: "served_in"}},
    {$match: {served_in: {$size: 0}}},
    {$sort: {name: 1}},
    {$project: {name: 1, _id: 0}},
).toArray())