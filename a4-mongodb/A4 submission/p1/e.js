// e. (12 points) Find who serves the role of "Ranking Member" for 
// the House subcommittee on "Energy and Mineral Resources" (under 
// House Committee HSII, "House Committee on Natural Resources"). 
// Simply print the entire person document.

printjson(db.committees.aggregate(
    {$match: {_id: "HSII"}},
    {$unwind: "$subcommittees"},
    {$match: {"subcommittees.displayname": "Energy and Mineral Resources"}},
    {$unwind: "$subcommittees.members"},
    {$match: {"subcommittees.members.role": "Ranking Member"}},
    {$lookup: {
        from: "people",
        localField: "subcommittees.members.id",
        foreignField: "_id",
        as: "person"
    }},
    {$unwind: "$person"},
    {$replaceRoot: {newRoot: "$person"}}, // only show the person document
).toArray())