from tju import Session
from tju.client import Client

session = Session()

client = Client(session=session)

# print(client.stu_id)
# print(client.stu_name)
# print(client.semester)
# print(client.stu_type)
# print(client.has_minor)

# print(client.schedule(semester="19201"))

# print(client.profile)

# print(client.query_courses())

# print(client.exam(semester="21222"))

# print(client.score())

print(client.exp_score(semester="20211"))
