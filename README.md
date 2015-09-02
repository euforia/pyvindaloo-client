pyvindaloo-client
=================
Python vindaloo client

Usage
-----
Start by creating a credentials file in your home directory under `~/.vindaloo/credentials` similar to the contents shown below.

    {
        "auth": {
            "username": "...",
            "password": "..."
        }
    }

You can now start using the api. Here's a simple example:

```
# client connecting to localhost
client = Client()

# or 

# client connecting to a hostname
client = Client("foo.bar")

print client.GetConfig()

print client.GetTypes()

# Available methods
print dir(client)

```