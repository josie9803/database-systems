// a. (8 points) Find legislators with the exact last name of “Smith”. 
// Simply print the entire person documents. 
printjson(db.people.find({name: / Smith$/}).toArray())
