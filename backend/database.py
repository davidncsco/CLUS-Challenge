import motor.motor_asyncio
import os, random, json
from model import DemoQuestion, User, Car
from utils import get_time, get_uuid, get_meta

# Read environment variables from meta file
meta = get_meta()
environments_vars = meta['env'][0]
cars_list = meta['cars']
DB_CONNECT_URL              = environments_vars['database_url']
DB_NAME                     = environments_vars['database_name']
MAX_QUESTIONS_TO_GENERATE   = environments_vars['questions_to_generate']
CAR_SIMULATION              = environments_vars['car_simulation']
CAR_URL_TEMPLATE            = environments_vars['car_url_template']
CAR_BACKWARD_FACTOR         = environments_vars['car_backward_factor']

try:
    print('Connecting to MongoDB...')
    client = motor.motor_asyncio.AsyncIOMotorClient(DB_CONNECT_URL)
    client.server_info() # will throw an exception
except:
    print(f'Cannot connect DB with {DB_CONNECT_URL}')
    exit()
    
database = client[DB_NAME]

def get_environment_vars():
    return environments_vars

async def fetch_one_question(qnumber: str):
    collection = database.question
    document = await collection.find_one({"_id": qnumber})
    return document

async def fetch_many_questions(maxQuestions=MAX_QUESTIONS_TO_GENERATE):
    # Only return maxQuestions from the database in random order
    questions = []
    # Fetch all questions from DB
    collection = database.question
    cursor = collection.find({})
    async for document in cursor:
        questions.append(DemoQuestion(**document))
    # Generate a random list of maxQuestions questions from all questions in DB
    totalQuestions = len(questions)
    if (maxQuestions > 0):
        randomlist = random.sample(range(0, totalQuestions), maxQuestions )
    else:
        randomlist = random.sample(range(0, totalQuestions), totalQuestions)
    new_questions = list(map(questions.__getitem__, randomlist))

    return new_questions

# Create and register new user in DB, record startTime and return car id assigned to this user
async def create_user(user):
    collection = database.user
    print('Creating DB user ',user)
    user_in_db = await collection.find_one({"email": user.email.lower()})
    if( user_in_db ):
        print(f'User with email={user.email} already exists in database')
        print(type(user_in_db))
        if( ('timetaken' in user_in_db) and (user_in_db['timetaken'] > 0) ):  # Don't allow user on leaderboard to retake the challenge
            return {}
        else:
            print('User already registered but have not taken or completed challenge, permission to take challenge granted',user_in_db['_id'])
            return { "id": user_in_db['_id'] }
    user_id = get_uuid()
    document = { "_id": user_id, "email": user.email.lower(), "first": user.first, "last": user.last }
    result = await collection.insert_one(document)
    return { "id" :user_id }

async def fetch_user_by_id(userid: str):
    collection = database.user
    document = await collection.find_one({"_id": userid})
    return document

async def fetch_all_cars():
    cars = []
    collection = database.car
    cursor = collection.find({})
    async for document in cursor:
        cars.append(Car(**document))
    return cars
    
async def start_the_challenge(userid: str):
    collection = database.car
    filter = { 'start': None }
    epoch = get_time()
    car = await collection.find_one(filter) # Find first available
    if( car ):
        print(f'car #{car["number"]} is assigned to user:{userid}')
        await collection.update_one(filter, {"$set": {"userid": userid,"start": epoch,"position": 0}})
        car = await collection.find_one({'number' : car['number']})
    return car

async def update_user_time(userid: str, carid: int):
    collection = database.car
    filter = {'number': carid}
    car = await collection.find_one(filter)
    if car and 'start' in car:
        timetaken = get_time() - car['start']
        current_position = car['position']
    print(f'Time taken for user {userid} is {timetaken} secs')
    collection = database.user
    filter = {'_id': userid }
    user = collection.find(filter)
    if( user ):
        print(f'update user time: {userid}, timetaken: {timetaken}')
        await collection.update_one(filter, {"$set": {"timetaken": timetaken}})
        return current_position
    return 0

async def reset_car_in_db(carid: int) -> int:
    collection = database.car
    filter = {'number': carid}
    current_position = 0
    # Admin request to reset car record in DB and send it to starting position
    document = await collection.find_one(filter)
    if( document ):      
        current_position = document['position']
        document['position'] = 0                    
        # remove _id and optional fields before replace
        for key in { '_id','userid', 'start' }:  
            if key in document:
                document.pop(key)
        await collection.replace_one(filter,document)                                     
    return current_position

async def fetch_leaderboard_users():
    collection = database.user
    users= []
    cursor = collection.find({})
    async for document in cursor:
        users.append(User(**document))
    return users

async def get_car_position( carid: int ):
    collection = database.car
    filter = {'number': carid}
    document = await collection.find_one(filter)
    if( document ):
        return document['position']
    return 0

async def set_car_position( carid: int, position: int ):
    collection = database.car
    filter = {'number': carid}
    document = await collection.find_one(filter)
    if( document ):
        await collection.update_one(filter, {"$set": {"position": position}})
        return 1
    return 0
    
async def get_car_payload(carid: int,weight: int):
    ''' Get car payload by car id (car number) and set current car position
        base on the value of weight and current car position
    '''
    car = cars_list[carid-1]   # current car
    current_position = await get_car_position(carid)
    print(f'Getting payload, car #{carid}, current position={current_position}, weight={weight}')
    new_position     = current_position + weight
    if( new_position < 0 and weight < 0 ):
        weight = current_position * -1
        new_position = 0
    await set_car_position(carid, new_position)
    if weight != 0:
        car_url = CAR_URL_TEMPLATE % car['ip']
        direction = 'forward' if (weight > 0) else 'backward'
        weight = abs(weight) * CAR_BACKWARD_FACTOR if (weight < 0) else weight
        payload = '{"speed": %s,"weight": %s, "direction": "%s"}' % (car['speed'], weight, direction)
        car['position'] = new_position
        print(f'car #{carid}, new position {new_position}')
        return (car_url,payload)
    else:
        return( None, None)
        