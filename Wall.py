from collections import OrderedDict
from matrix_client.errors import MatrixRequestError
from SSN_element import SSN_element
import json
from SSNRoom import SSNRoom

class Wall(SSN_element):
    def __init__(self, client):
        super().__init__(client)
        self.posts = OrderedDict()
        self.post_id = 1
        # friends who have access to my wall
        self.friends = {"jimmy": "jim's key", "marco": "marcos key"}
        self.initialized = False
        self.current_event_id = None

    def initialize_from_file(self, friends, saved_posts):
        self.friends = friends
        for key, post in saved_posts.items():
            self.add_post(post["msg"], post["room_id"], self.post_id)
            self.post_id += 1
        self.update_wall_store()
        self.initialized = True
        return

    def load(self):
        # iterate through rooms to find wall
        user_id = self.m_client.user_id
        user_name = user_id.split(':')[0][1:]
        wall_room = "#{0}_w:matrix.org".format(user_name)
        wall_handle = user_name + "_w"

        if wall_handle in self.room_table:
            if type(self.current_room) is not SSNRoom:
                print(type(self.current_room))
                self.current_room = SSNRoom(self.join_room(wall_room), self.init_msg_hist_for_room)
                self.current_room.set_room_name(wall_handle)
            return
        else:
            try:
                room = self.m_client.create_room(wall_handle).room_id
                self.current_room = SSNRoom(self.join_room(room.room_id), self.init_msg_hist_for_room)
            except BaseException as e:
                print(e)
                # room exists but has been left
                room = self.join_room(wall_room)
                self.current_room = SSNRoom(room, self.init_msg_hist_for_room)

            self.current_room.room.set_guest_access("can_join")

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
                self.render(self.m_client)
                return
            # Wall handler passes a json formatted dictionary
            elif msg_body.startswith('{') and msg_body.endswith('}') and self.rendered:
                """message is a json string"""
                msg_dict = json.loads(msg_body)
                if "add_post" in msg_dict.keys():
                    msg = msg_dict['add_post']
                    room = self.m_client.create_room()
                    room.set_guest_access("can_join")
                    room.name = "1_" + room.room_id
                    self.add_post(msg, room.room_id, str(self.post_id))
                    self.render(self.m_client)
                    self.post_id += 1
                    self.update_wall_store()
                elif "comment_post" in msg_dict.keys():
                    # the value for comment post is the post id
                    # self.post_comment(msg_dict['comment_post'])
                    if not self.is_room_setup:
                        self.current_event_id = event['event_id']
                        self.current_room = SSNRoom(
                            self.join_room(self.posts[int(msg_dict['comment_post'])].room_id, prepend="{}_"
                                           .format(msg_dict['comment_post'])),
                            self.init_msg_hist_for_room)
                        print("Post comment here ...\n")
                elif "remove_post" in msg_dict.keys():
                    self.remove_post(msg_dict['remove_post'])
            else:
                self.send_room_message(room, event)
        self.rendered = True
        self.is_room_setup = False

    def remove_post(self, post_id):
        post = self.posts.pop(post_id)
        try:
            self.m_client.api.leave_room(post.room_id)
        except MatrixRequestError as e:
            if e.code == 404: # not a known room
                x = None
            else:
                print(e)
        print("Post {} removed.".format(post_id))
        self.update_wall_store()

    def add_post(self, msg, room_id, post_id):
        self.posts[post_id] = Post(room_id, msg, post_id, self.m_client)

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

    def render(self, client):
        """prints all the posts"""
        # call('clear')
        for post in self.posts.values():
            post.print(client)
        return

class Post(object):
    def __init__(self, room_id, msg, post_id, client):
        """
        :param room_id:
        :param msg:
        :param post_id:
        :param client:
        """
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
