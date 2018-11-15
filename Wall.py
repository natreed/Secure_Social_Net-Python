from collections import OrderedDict
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
        self.friends = {"jimmy": "jim's pub key", "marco": "marcos pub key"}
        self.rendered = False
        self.in_post_comments = False

    def initialize_from_file(self, friends, saved_posts):
        self.friends = friends
        for key, post in saved_posts.items():
            self.add_post(post["msg"], post["room_id"], post["post_id"])
        self.post_id = len(self.posts) + 1

    def load(self):
        # iterate through rooms to find wall
        # user_id = @natreed:matrix.org
        # Not sure if a wall room is necessary. Joins the wall room.
        # TODO: figure out if wall_room is really needed or can everything be done in the
        # console. Right now all message passing is done in the context of a room. This will
        # probably come up when we address friends posting to the wall.
        user_id = self.m_client.user_id
        user_name = user_id.split(':')[0][1:]
        wall_room = "#{0}_wall:matrix.org".format(user_name)
        for value in self.m_client.rooms.values():
            if value.canonical_alias == wall_room:
                self.current_room = self.join_room(wall_room)
                return
        if self.current_room is None:
            self.current_room = self.m_client.create_room(user_name + "_wall")
            self.room.set_guest_access("can_join")
            self.join_room(self.current_room)

    def leave(self):
        """write current state to a file when finished. Can be brought back when
        Client starts again."""
        posts_info = {}
        for key, post in self.posts.items():
            posts_info[key] = {"room_id": post.room_id,
                               "msg": post.message,
                               "post_id": post.post_id}

        state = {"friends": self.friends, "posts": posts_info}
        # serialized = pickle.dumps(state)
        #just test and take a look
        state_string = json.dumps(state)
        with open('./Stores/Wall_Store.txt', 'w') as outfile:
            outfile.write(state_string)
        return

    def on_message(self, room, event):
        """ TODO: Set up a handler for viewing other people's walls
            Room messages can be parsed into different message types using json objects."""
        if event['type'] == "m.room.member":
            if event['membership'] == "join":
                print("{0} joined".format(event['content']['displayname']))
        elif event['type'] == "m.room.message":
            msg_body = event['content']['body']
            if msg_body == 'show_wall':
                self.render(self.m_client)
            # Wall handler passes a json formatted dictionary
            elif msg_body.startswith('{') and msg_body.endswith('}') and self.is_room_setup:
                """message is a json string"""
                msg_dict = json.loads(msg_body)
                if "add_post" in msg_dict.keys():
                    msg = msg_dict['add_post']
                    room = self.m_client.create_room()
                    room.set_guest_access("can_join")
                    self.add_post(msg, room.room_id, str(self.post_id))
                    self.render(self.m_client)
                    self.post_id += 1
                elif "comment" in msg_dict.keys():

                    self.post_comment(msg_dict['post_id'], msg_dict['comment'])
            else:
                # print(msg_body) #printing all the messages can be good for debugging
                return

    def add_post(self, msg, room_id, post_id):
        """TODO: right now an integer is used for the dictionary key
        that is how the user will access the post's room to comment"""
        self.posts[post_id] = Post(room_id, msg, post_id, self.m_client)
        # call('clear')
        # self.render()

    def invite(self, user_id, handle):
        print("not yet implemented")
        return

    def post_comment(self, post_id, msg):
        """
        join the room, post a message and leave room
        :param post_id:
        :param msg:
        :param client:
        :return:
        """
        self.posts[post_id].print(self.m_client)
        room = self.join_room(self.posts[post_id].room_id)
        room.send_text('-\t{0}'.format(msg))



    def invite_friend(self, user_name):
        """friends will be able to see the Wall"""
        self.friends[user_name] = ""

    def render(self, client):
        """prints all the posts"""
        # call('clear')
        for post in self.posts.values():
            post.print(client)

class Post(object):
    def __init__(self, room_id, msg, post_id, client):
        self.message = msg
        self.room_id = room_id
        self.post_id = post_id
        self.user_id = client.user_id
        self.comments = []

    def get_room(self):
        return self.room_id

    # TODO: The reason for the client argument is so that we know which client to
    # send the post to. First I want to get the bugs worked out.
    def print(self, client):
        print("id={0}: {1}: {2}".format(self.post_id, self.user_id, self.message))

    # def show_comments(self):
    # TODO: this is part of the code from matrix join_room function
    # No longer being used in program. The base class join-room function does the trick
    # although an override may be necessary.
    def _get_messages(self, client, reverse=False, limit=10):
        """Backfill handling of previous messages.
        Args:
            reverse (bool): When false messages will be backfilled in their original
                order (old to new), otherwise the order will be reversed (new to old).
            limit (int): Number of messages to go back.
        """
        res = client.api.get_room_messages(self.room_id, self.room.prev_batch,
                                                direction="b", limit=limit)
        events = res["chunk"]
        if not reverse:
            events = reversed(events)
        return events
