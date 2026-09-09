from flask import Flask, request, jsonify, abort
from flask_pymongo import PyMongo
import time, datetime
from datetime import datetime

app = Flask(__name__)

# Update the below configuration with your existing MongoDB details
app.config["MONGO_URI"] = "mongodb://mongodb:27017/congress"
# app.config["MONGO_URI"] = "mongodb://localhost:27017/congress"

mongo = PyMongo(app)

@app.route('/')
def example():
    # Note that the regex syntax in Pymongo is different from the JSON
    res = mongo.db.people.find({"name": {'$regex':' Smith$'} })
    return jsonify(res)
   

@app.route("/getByState/<state_code>")
def getByState(state_code):
    """
        This HTTP method takes state_code as input, and returns the name, district, and party 
        of each current Representative of the given state (state_code) in the format of 
        {"name": "…", "district": …, "party": "…" } and sorts the result according to the district.
    """
    # COMPLETE THE PIPELINE DEFINITION by filling in your code
    pipeline = [
        { "$unwind": "$roles" },
        { "$match": {
            "roles.current": 1,
            "roles.type": "rep",
            "roles.state": state_code
        }},
        { "$project": {
            "_id": 0,
            "name": "$name",
            "district": "$roles.district",
            "party": "$roles.party"
        }},
        { "$sort": { "district": 1 } }
    ]
    # DO NOT change the aggregate query below
    res = mongo.db.people.aggregate(pipeline)
    return jsonify(res)


def check_status(roles):
    """
    Args:
        roles: a list of roles objects

    Returns:
        is_current: True indicates that the last role is current (end date later than 
              datetime.strptime("2025-07-07", "%Y-%m-%d")), 
              or the last role has already been set to non-current
              False if the last role ends no later than datetime.strptime("2025-07-07", "%Y-%m-%d"))
				but with current = 1
        new_roles: a list of roles objects; 
                  if the most recent role is not current, change its "current" field to 0
    """
    # COMPLETE THIS FUNCTION
    # no MongoDB queries are needed here
    import copy
    new_roles = copy.deepcopy(roles)
  
    last_role = new_roles[-1]
    cutoff = datetime.strptime("2025-07-07", "%Y-%m-%d")
    enddate = last_role.get('enddate')

    if enddate > cutoff:
        return True, new_roles # end date later than cutoff
    
    if last_role.get('current', 1) == 0:
        return True, new_roles # last role has already been set to non-current

    if enddate <= cutoff and last_role.get('current', 1) == 1: # last role <= cutoff AND still set to current
        last_role['current'] = 0
        return False, new_roles

    return True, roles
    
@app.route("/update/<lid>")
def update(lid):
    """
    Args:
        lid: the legislator's _id

    Returns:
        {"res": "current"} if the legislator is still serving in the congress;
        {"res": person object} if the legislator's information needs to be updated
        if the lid is not found, directly call `abort(404, description=f"Legislator {lid} not found")`
        
	Same as in A3, you should use HTTP POST or PUT requests for such editing requests, 
	but we just choose GET for easier test
	NOTE: either create a separate copy of congress db before you work on this problem,
		or remember to reload the db contents if you need to test the queries
    """
    
    # REPLACE THE NEXT LINE to find the given legislator
    person = mongo.db.people.find_one({"_id": lid})
    if person is None:
        abort(404, description=f"Legislator {lid} not found")

    # COMPLETE THE check_status() FUNCTION above to get the current status
    is_current, new_roles = check_status(person['roles'])
    # If no need to update, exit  
    if is_current:
        return jsonify({"res": "current"}), 200
    
    # COMPLETE THE STATEMENT BELOW to update the roles
    res = mongo.db.people.update_one(
        {"_id": lid},
        {"$set": {"roles": new_roles}}
    )
    
    # Check if the update statement finds a legislator (actually we already check that above)
    if res.matched_count == 0:
        abort(404, description=f"Legislator {lid} not found")

    # Since the role has ended, remove the committee memberships, 
    # we will leave removing the memberships to you as an optional extension
    person = mongo.db.people.find_one({"_id": lid})
    return jsonify(person), 200


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=7000)

