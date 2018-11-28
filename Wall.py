from collections import OrderedDict
from matrix_client.errors import MatrixRequestError
from SSNElement import SSNElement
import json
from PostRoom import PostRoom
from WallRoom import WallRoom
import time

class Wall(SSNElement):
    def __init__(self, client, landing_room):
        super().__init__(client, landing_room)
        self.posts = OrderedDict()
        self.post_id = 1
        # friends who have access to my wall
        self.friends = {"jimmy": "jim's key", "marco": "marcos key"}
        self.initialized = False
        self.current_event_id = None

    def initialize_from_file(self, friends, saved_posts):
        self.friends = friends

        for key, post in saved_posts.items():
            room_id_alias = post["room_id"]
            try:

                rm = self.join_room(room_id_alias)
                room = PostRoom(rm, self.init_msg_hist_for_room)
                self.add_post(post["msg"], room, self.post_id)
            except BaseException as e:
                print(e)
                print("comment history was lost for this post")
                try:
                    self.remove_post(post["post_id"])
                except BaseException as e:
                    print(e)
                    print("creating new room for post")
                    room = PostRoom(self.m_client.create_room(room_id_alias), self.init_msg_hist_for_room)
                    self.add_post(post["msg"], room, self.post_id)
            self.post_id += 1
        self.initialized = True
        return




    def load(self):
        # iterate through rooms to find wall
        user_id = self.m_client.user_id
        user_name = user_id.split(':')[0][1:]
        wall_handle = user_name + "_w"
        room_name = self.landing_room.split(':')[0][1:]
        # TODO: COMMEMT OUT THIS LINE
        # self.remove_all_posts()

        if wall_handle in self.loaded_rooms.keys():
            self.current_room = self.loaded_rooms[room_name]
            for msg in self.all_rooms_messages[room_name].values():
                print(msg)
        elif room_name in self.room_table:
            self.current_room = WallRoom(self.join_room(self.landing_room), self.init_msg_hist_for_room)
            self.loaded_rooms[self.current_room.get_room_name()] = self.current_room
        else:
            room = self.m_client.create_room(wall_handle)
            self.current_room = WallRoom(room, self.init_msg_hist_for_room)
        self.initialized = True

    def update_wall_store(self):
        """write current state to a file when finished. Can be brought back when
        Client starts again."""
        posts_info = {}
        for key, post in self.posts.items():
            posts_info[key] = {"room_id": post.room_id,
                               "msg": post.message,
                               "post_id": post.post_id}
        state = {"friends": self.friends, "posts": posts_info}
        state_string = json.dumps(state)
        with open('./Stores/Wall_Store.txt', 'w') as outfile:
            outfile.write(state_string)
        return

    def on_message(self, room, event):
        """Todo: I understand that this may cause unexplained behavior.
        Somehow messages are being sent before the wall is initialized. I don't know why.
        I didn't plan on dealing with asynchronous behavior in python. Possibly the debugger."""
        if event['event_id'] == self.current_event_id:
            return
        elif not self.initialized:
            return

        if event['type'] == "m.room.member":
            if event['membership'] == "join":
                if self.rendered and self.is_room_setup:
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
        self.is_room_setup = False

    def post_msg(self, msg_dict):
        msg = msg_dict['add_post']
        room = self.m_client.create_room()
        room.set_guest_access("can_join")
        room.name = "p_{}".format(room.room_id)
        pst_room = PostRoom(room, self.init_msg_hist_for_room)
        self.loaded_rooms[pst_room.get_room_name()] = pst_room
        self.add_post(msg, pst_room, str(self.post_id))
        self.render()
        self.post_id += 1
        self.update_wall_store()

    def comment_post(self, event, msg_dict):
        if not self.is_room_setup:
            self.current_event_id = event['event_id']
            room_id_alias = self.posts[int(msg_dict['comment_post'])].room_id
            room = self.join_room(room_id_alias)
            self.current_room = PostRoom(room, self.init_msg_hist_for_room)
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


    def add_post(self, msg, post_room, post_id):
        self.posts[post_id] = Post(post_room, msg, post_id, self.m_client)

    def invite(self, user_id, handle):
        print("not yet implemented")
        return

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
            post.print()
        return

class Post(object):
    def __init__(self, post_room, msg, post_id, client):
        """
        :param room_id:
        :param msg:
        :param post_id:
        :param client:
        """
        self.message = msg
        self.post_room = post_room
        self.post_id = post_id
        self.room_id = self.post_room.get_room_id()
        self.user_id = client.user_id
        self.comments = []

    def get_room_name(self):
        return self.post_room.get_room_name()


    # TODO: The reason for the client argument is so that we know which client to
    # send the post to. First I want to get the bugs worked out.
    def print(self, user_id):
        print("id={0}: {1}: {2}".format(self.post_id, user_id, self.message))
