import bcrypt

def hash_senha(senha):
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

def check_senha(senha, hashed):
    return bcrypt.checkpw(senha.encode('utf-8'), hashed)

