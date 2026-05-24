#======================================#
#               main.py                #
#======================================#


from .config.security import *


if __name__ == "__main__":
    hashed = hash_password("test-password")
    logger.info(f"hash generated: {hashed}")
    logger.info(f"correct password verify: {verify_password('test-password', hashed)}")
    logger.warning(f"wrong password verify: {verify_password('wrong-password', hashed)}")
    logger.info(f"token created: {create_access_token(data={'id': 1, 'name': 'user'})}")