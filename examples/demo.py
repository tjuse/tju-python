from tju import Session
from tju.client import Client

session = Session()
session.login()

client = Client(session=session)
print(client.stu_id)
print(client.stu_name)
print(client.semester)
print(client.stu_type)
print(client.has_minor)
