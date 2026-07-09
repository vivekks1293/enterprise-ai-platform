from bcrypt import gensalt, hashpw

password = "Admin@123"

hashed = hashpw(
    password.encode(),
    gensalt()
)

print(hashed.decode())