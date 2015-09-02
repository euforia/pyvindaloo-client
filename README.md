pyvindaloo-client
=================
Python vindaloo client


Example:

```
# client connecting to localhost
client = Client()
# or 
# new client connecting to a hostname
client = Client("foo.bar")

print client.GetConfig()

print client.GetTypes()

# Available methods
print dir(client)

```