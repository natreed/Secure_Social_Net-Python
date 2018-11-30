from collections import OrderedDict
from matrix_client.errors import MatrixRequestError
from SSNElement import SSNElement
import json
from PostRoom import PostRoom
from WallRoom import WallRoom
import time

class SSNWall(SSNElement):
    def __init__(self, client, landing_room):
        super().__init__(client, landing_room)
        self.owner = True
        self.posts = OrderedDict()
        self.post_id = 1
        # friends who have access to my wall
        self.friends = {"jimmy": "jim's key", "marco": "marcos key"}
        self.initialized = False
        self.current_event_id = None
        self.user_id = self.m_client.user_id
        self.user_name = self.user_id.split(':')[0][1:]
        self.wall_handle = self.user_name + "_w"
        self.wall_room_name = self.landing_room.split(':')[0][1:]

    def initialize_from_file(self, friends, saved_posts):
        self.friends = friends
        for key, post in saved_posts.items():
            room_id_alias = post["room_id"]
            self.add_post(post["msg"], room_id_alias, self.post_id, post["room_name"])
            self.post_id += 1
        self.initialized = True
        return

    def initialize_from_events_state(self):
        """build self from event state stored in wall room in a json object"""

    def load(self):
        # TODO: COMMENT OUT THIS LINE IMMEDIATELY
        # self.remove_all_posts()
        if self.wall_room_name in self.room_table:
            room_id = self.room_table[self.wall_room_name]["room_id"]
            if room_id in self.loaded_rooms.keys():
                self.current_room = self.loaded_rooms[room_id]
                for msg in self.all_rooms_messages[self.wall_room_name]:
                    print(msg)
            else:
                self.current_room = WallRoom(self.join_room(self.landing_room))
                self.loaded_rooms[room_id] = self.current_room
                self.room_table[self.wall_room_name]["loaded"] = True
        else:
            room = self.m_client.create_room(self.wall_handle)
            room.set_room_name(self.wall_handle)
            self.room_table[self.wall_handle] = {"room_id": room.room_id, "loaded": False}
            self.current_room = WallRoom(room)
            self.loaded_rooms[room.room_id] = self.current_room
        self.initialized = True

    def update_wall_store(self):
        """write current state to a file when finished. Can be brought back when
        Client starts again."""
        posts_info = {}
        for key, post in self.posts.items():
            posts_info[key] = {"room_id": post.room_id,
                               "msg": post.message,
                               "post_id": post.post_id,
                               "room_name": post.get_room_name()}
        state = {"friends": self.friends, "posts": posts_info}
        state_string = json.dumps(state)
        with open('./Stores/Wall_Store.txt', 'w') as outfile:
            outfile.write(state_string)
        return

    def update_wall_state(self):
        """
        Called on program exit. Sends state to wall_room so that friends can reproduce wall
        :return:
        """
        wall_store = open('Stores/Wall_Store.txt', 'r+').read()
        landing_room_id = self.room_table[self.landing_room.split(':')[0].lstrip('#')]
        landing_room = self.loaded_rooms[landing_room_id["room_id"]]
        t = time.time()
        wall_store_with_time = {"time_of_update": str(t).split('.')[0], "wall_store": wall_store}
        msg = json.dumps(wall_store_with_time)
        landing_room.room.send_notice(msg)

    def on_message(self, room, event):
        if event['event_id'] == self.current_event_id:
            return
        elif not self.initialized:
            return
        if event['type'] == "m.room.member":
            if event['membership'] == "join":
                if self.rendered and self.is_room_setup \
                        and self.current_room.get_room_id() not in self.loaded_rooms:
                    print("{0} joined".format(event['content']['displayname']))
        elif event['type'] == "m.room.message":
            msg_body = event['content']['body']
            if msg_body == 'show_wall':
                self.render()
                return
            # Wall handler passes a json formatted dictionary
            elif msg_body.startswith('{') and msg_body.endswith('}') and self.rendered:
                """message is a json string"""
                msg_dict = json.loads(msg_body)
                if "add_post" in msg_dict.keys():
                    self.post_msg(msg_dict)
                elif "comment_post" in msg_dict.keys():
                    self.comment_post(event, msg_dict)
                elif "remove_post" in msg_dict.keys():
                    self.remove_post(msg_dict['remove_post'])
            else:
                self.send_room_message(room, event)
        self.rendered = True
        # self.is_room_setup = False

    def post_msg(self, msg_dict):
        msg = msg_dict['add_post']
        room = self.m_client.create_room()
        room.set_guest_access("can_join")
        room.name = "p_{}".format(room.room_id)
        pst_room = PostRoom(room, self.init_msg_hist_for_room)
        self.loaded_rooms[pst_room.get_room_id()] = pst_room
        self.room_table[room.name] = pst_room.get_room_id()
        self.add_post(msg, pst_room.get_room_id(), self.post_id, room.name)
        self.render()
        self.post_id += 1
        self.update_wall_store()

    def comment_post(self, event, msg_dict):
        self.current_event_id = event['event_id']
        post_id = msg_dict['comment_post']
        post = self.posts[int(post_id)]
        room_id_alias = post.room_id
        room = self.join_room(room_id_alias)
        room_name = post.room_name
        if not post.post_room:
            post.post_room = PostRoom(room, self.init_msg_hist_for_room)
            self.loaded_rooms[room.room_id] = post.post_room
            post.set_room_name(room_name)
        self.current_room = post.post_room
        for msg in self.all_rooms_messages[room_name]:
            print("\t" + msg)
        print("Post comment here ...\n")

    def remove_post(self, post_id):
        post = self.posts.pop(post_id)
        try:
            self.m_client.api.leave_room(post.room_id)
        except MatrixRequestError as e:
            if e.code == 404: # not a known room
                print("not a known room")
            else:
                print(e)
        print("Post {} removed.".format(post_id))
        self.update_wall_store()

    def remove_all_posts(self):
        """for when shit hits the fan"""
        for key, post in self.posts.items():
            self.remove_post(post.post_id)
        self.update_wall_store()

    def add_post(self, msg, post_room_id, post_id, room_name):
        self.posts[post_id] = Post(post_room_id, msg, post_id, room_name)

    def post_comment(self, post_id):
        """
        join the comment room
        :param post_id:
        :return:
        """
        # self.posts[post_id].get_messages(self.m_client)
        self.join_room(self.posts[post_id].room_id)
        print(self.current_room.room.name)

    def invite_friend(self, user_name):
        """friends will be able to see the Wall"""
        self.friends[user_name] = ""

    def render(self):
        """prints all the posts"""
        # call('clear')
        for post in self.posts.values():
            post.print(self.m_client.user_id)
        return

    # def load_post_to_room_callback(self, post_room_id):
    #     """Function called in Post/load_post_room when user wants to comment"""
    #     room = PostRoom(self.m_client.join_room(post_room_id), self.init_msg_hist_for_room)
    #     return room, self.m_client.user_id

class Post(object):
    def __init__(self, post_room_id, msg, post_id, room_name):
        """
        :param room_id:
        :param msg:
        :param post_id:
        :param client:

        The post comment room is not joined until someone wants to post a comment in that room.
        After a room is joined it is added to the loaded rooms list.
        """
        self.message = msg
        # post rooms need to be set asynchronously
        self.post_room = None
        self.post_id = post_id
        self.room_id = post_room_id
        self.room_name = room_name
        self.user_id = None
        self.comments = []

    def get_room_name(self):
        if self.post_room:
            return self.post_room.get_room_name()
        else:
            return None

    def set_room_name(self, name):
        if self.post_room:
            return self.post_room.set_room_name(name)
        else:
            return None

    #TODO: Need to learn to work with python async library
    # load post room loads the post room asynchronously
    async def load_post_room(self, load_post_callback):
        self.post_room, self.user_id = await load_post_callback(self.room_id)


    # TODO: The reason for the client argument is so that we know which client to
    # send the post to. First I want to get the bugs worked out.
    def print(self, user_id):
        print("id={0}: {1}: {2}".format(self.post_id, user_id, self.message))


