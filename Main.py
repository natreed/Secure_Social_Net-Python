from ssn import ssn


if __name__ == '__main__':
    """Login will be implemented in Web Application. For now there are two users to log in as for testing."""



    natreed_args = {"homeserver": 'http://www.matrix.org',
                    "m_username": '@natreed:matrix.org',
                    "pw": 'vatloc4evr',
                    "chat_landing_room": '#my_room:matrix.org',
                    "wall_landing_room": '#natreed_w:matrix.org'}
    nat_reed_args = {"homeserver": 'http://www.matrix.org',
                     "m_username": '@nat-reed:matrix.org',
                     "pw": 'vatloc4evr',
                     "chat_landing_room": '#nat-reed-chat:matrix.org',
                     "wall_landing_room": '#nat-reed_wall:matrix.org'}
    ssn(natreed_args).run()
