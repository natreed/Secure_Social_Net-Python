from SSNElement import SSNElement
import json
from PostRoom import PostRoom
from WallRoom import WallRoom
import time

class FriendWall(SSNElement):
    def __init__(self, wall_store, room):
        super().__init__(self.m_client, room)
        self.wall_store = json.loads(wall_store)
        self.posts = self.wall_store["posts"]
        self.initialized = False
        self.user_id = self.m_client.user_id
        self.user_name = self.user_id.split(':')[0][1:]
        self.wall_handle = room.get_room_name()
        self.current_event_id = None

    def load(self):
        if self.wall_handle in self.room_table:
            room_id = self.room_table[self.wall_handle]["room_id"]
            if room_id in self.loaded_rooms.keys():
                self.current_room = self.loaded_rooms[room_id]
                for msg in self.all_rooms_messages[self.wall_handle]:
                    print(msg)
            else:
                self.current_room = WallRoom(self.join_room(self.landing_room))
                self.loaded_rooms[room_id] = self.current_room
                self.room_table[self.wall_handle]["loaded"] = True
        self.initialized = True

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
                    # self.post_msg(msg_dict)
                    print("you do not have permission to add post to {}'s wall"
                          .format(self.wall_handle.split('_')[0]))
                elif "comment_post" in msg_dict.keys():
                    self.comment_post(event, msg_dict)
                elif "remove_post" in msg_dict.keys():
                    # self.remove_post(msg_dict['remove_post'])
                    print("you do not have permission to remove post from {}'s wall"
                          .format(self.wall_handle.split('_')[0]))
                else:
                    print("not a valid command")
            else:
                self.send_room_message(room, event)
        self.rendered = True

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

    def post_comment(self, post_id):
        """
        join the comment room
        :param post_id:
        :return:
        """
        # self.posts[post_id].get_messages(self.m_client)
        self.join_room(self.posts[post_id].room_id)
        print(self.current_room.room.name)

    def render(self):
        """prints all the posts"""
        # call('clear')
        for post in self.posts.values():
            post.print(self.m_client.user_id)
        return

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


