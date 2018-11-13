from collections import OrderedDict
from subprocess import call
import SSNClient
import tests
from SSN_element import SSN_element
import json



# TODO: Maybe wall should be split into two classes with a common base.
# One class could be for operations receiving and one for sending (client and friend)
# This could also give better separation for permissions and privacy
class Wall(SSN_element):
    def __init__(self, client):
        super().__init__(client)
        self.posts = OrderedDict()
        self.post_id = 1
        # friends who have access to my wall
        self.friends = {}
        self.rendered = False

        self.initiate_wall()

    def initiate_wall(self):
        # iterate through rooms to find wall
        # user_id = @natreed:matrix.org
        user_id = self.m_client.user_id
        user_name = user_id.split(':')[0][1:]
        wall_room = "#{0}_wall:matrix.org".format(user_name)
        # A list of dictionaries
        for value in self.m_client.rooms.values():
            if value.canonical_alias == wall_room:
                self.current_room = self.join_room(wall_room)
                return
        if self.current_room is None:
            self.current_room = self.m_client.create_room(user_name + "_wall")
            self.join_room(self.current_room)

    def on_message(self, room, event):
        """ TODO: Set up a handler for viewing other people's walls
            Room messages can be parsed into different message types using json objects."""
        if event['type'] == "m.room.member":
            if event['membership'] == "join":
                print("{0} joined".format(event['content']['displayname']))
        elif event['type'] == "m.room.message":
            msg_body = event['content']['body']
            if msg_body == 'show_wall':
                if not self.rendered:
                    self.render()
                self.rendered = True
            # Wall handler passes a json formatted dictionary
            elif msg_body.startswith('{') and msg_body.endswith('}') and self.is_room_setup:
                """message is a json string"""
                msg_dict = json.loads(msg_body)
                if "add_post" in msg_dict.keys():
                    post = msg_dict['add_post']
                    self.add_post(post)
            else:
                print(msg_body)

    def add_post(self, msg):
        """TODO: right now an integer is used for the dictionary key
        that is how the user will access the post's room to comment"""

        self.posts[self.post_id] = Post(self.m_client, msg)
        self.post_id += 1
        self.render()

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
        self.render()

    def invite_friend (self, user_name):
        """friends will be able to see the Wall"""
        self.friends[user_name] = ""

    def render(self):
        call('clear')
        print("WELCOME TO THE WALL")
        for post in self.posts:
            print("{0}: {1}".format(self.m_client.user_id, self.posts[post].message))
            self.join_room(self.posts[post].room.room_id)

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
