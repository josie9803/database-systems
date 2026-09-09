//b. (8 points) List all current legislators born after the first version 
// of Microsoft SQL Server released (April 24, 1989) but before the first 
// version of Postgres released (July 8, 1996). Format each of them simply 
// as {"name" : "...", "birthday": ...}. Order them by the name attribute. 

//find() takes in 2 {query} {project}
//aggregate() takes in a lot of {} {} ...
//$match, $sort only takes in 1 {}
//need double quote: nested field, start with number, spacing, dash, etc
//id will always be printed out if not specified
printjson(db.people.aggregate(
    {$match: {"roles.current": 1}},
    {$match: {birthday: {$gt: ISODate("1989-04-24"), $lt: ISODate("1996-07-08")}} },
    {$project: {_id: 0, name: 1, birthday: 1}},
    {$sort: {name: 1}}
).toArray())
