from SSNElement import SSNElement


class SSNHome(SSNElement):
    """Here we can store state relating to our friends and permissions. SSNHome
    will also handle all requests for access. The first example would be to get state
    from the wall and forward it to the requestor, if they have permissions. The room
    used will be the room '#<user_id_home>:matrix.org'"""
    def __init__(self, room):
        super().__init__(self.m_client, room)

