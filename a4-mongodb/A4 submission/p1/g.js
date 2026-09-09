// g. (12 points) Find the number of current legislators for each state 
// and territory (both are stored in the state attribute) by gender. Sort 
// the states/territories by name (two-letter abbreviation) alphabetically. 
// Your output should look like the following (whitespace is unimportant):
// [
//   { state: 'AK', M: 1, F: 2 },
//   { state: 'AL', M: 7, F: 2 },
//   { state: 'AR', M: 6, F: 0 },
//   { state: 'AS', M: 0, F: 1 },
// …]
printjson(db.people.aggregate(
    {$unwind: "$roles"},
    {$match: {"roles.current": 1}},
    {$group: {
      _id: {state: "$roles.state", gender: "$gender"},
      count: {$sum: 1}
    }},
    {$group: {
      _id: "$_id.state",
      M: {
        $sum: {$cond: [{ $eq: ["$_id.gender", "M"] }, "$count", 0]}
      },
      F: {
        $sum: {$cond: [{ $eq: ["$_id.gender", "F"] }, "$count", 0]}
      }
    }},
    {$project: {_id: 0, state: "$_id", M: 1, F: 1}},
    {$sort: {state: 1}}
).toArray())

