from collections import OrderedDict
from subprocess import call
import SSNClient
from SSN_element import SSN_element
from matrix_client.client import MatrixClient
import json


class Wall(SSN_element):
    def __init__(self, client):
        super().__init__(client)
        self.posts = OrderedDict()
        self.post_id = 1
        # friends who have access to my wall
        self.friends = {}

    def on_message(self, room, event):
        if event['type'] == "m.room.member":
            if event['membership'] == "join":
                print("{0} joined".format(event['content']['displayname']))
        elif event['type'] == "m.room.message":
            msg_body = event['content']['body']
            if msg_body == 'show_wall':
                if self.is_room_setup:
                    self.render()
            # TODO: This section is for handling serialized json objects. Maybe a  way to bypass the need
            # Room messages can be parsed into different message types this way.
            elif msg_body.startswith('{') and msg_body.endswith('}') and self.is_room_setup:
                """message is a json string"""
                msg_dict = json.loads(msg_body)
                if "add_post" in msg_dict.keys():
                    post = msg_dict['add_post']
                    self.add_post(post)
            else:
                print("OOOH that hurts.")

    def add_post(self, msg):
        """TODO: right now an integer is used for the dictionary key
        that is how the user will access the post's room to comment"""

        self.posts[self.post_id] = Post(self.m_client, msg)
        self.post_id += 1
        self.render(self.m_client)

    def invite(self, user_id, handle):
        print("not yet implemented")
        return

    def post_comment(self, post_id, msg, client):
        """
        join the room, post a message and leave room
        :param post_id:
        :param msg:
        :param client:
        :return:
        """
        room = self.join_room(client.wall.posts[post_id].room)
        room.send_text(msg)
        # TODO: there needs to be a whole other class set up
        # to render other client walls. That will involve lots of back and forth
        # communication.
        self.render(self.m_client)

    def invite_friend (self, user_name):
        """friends will be able to see the Wall"""
        self.friends[user_name] = ""

    def render(self, client):
        call('clear')
        print("WELCOME TO THE WALL")
        for post in self.posts:
            print("{0}: {1}".format(self.m_client.user_id, self.posts[post].message))
            room = self.join_room(self.posts[post].room.room_id)

    def run_wall(self):
        # TODO: I'd like to pass control to the wall if the user decides to view
        # this would probably happen in SSN's input handler
        # I haven't decided if this is a dumb idea or not
        print("not yet implemented")


class Post(object):
    def __init__(self, client, msg):
        self.message = msg
        self.room = client.create_room()
        self.room.set_guest_access("can_join")

    def add_msg(self, msg):
        self.room.send_text(msg)

    def get_room(self):
        return self.room

    # def show_comments(self):
    def _get_messages(self, client, reverse=False, limit=10):
        """Backfill handling of previous messages.

        Args:
            reverse (bool): When false messages will be backfilled in their original
                order (old to new), otherwise the order will be reversed (new to old).
            limit (int): Number of messages to go back.
        """

        res = client.api.get_room_messages(self.room.room_id, self.room.prev_batch,
                                                direction="b", limit=limit)
        events = res["chunk"]
        if not reverse:
            events = reversed(events)
        return events
