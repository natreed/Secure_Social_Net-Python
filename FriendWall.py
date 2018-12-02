from SSNWall import SSNWall
import json
from PostRoom import PostRoom
from WallRoom import WallRoom
import time


class FriendWall(SSNWall):
    """Friend wall extends SSNElement, NOT Wall. This allows for
    isolation from wall functions that a friend should not have access to."""
    def __init__(self,  m_client, room):
        super().__init__(m_client, room)
        self.owner = False

    def on_message(self, room, event):
        if not self.initialized:
            return
        elif event['type'] == "m.room.message":
            msg_body = event['content']['body']
            if msg_body == 'show_wall':
                self.render()
                return
            # Wall handler passes a json formatted dictionary
            elif msg_body.startswith('{') and msg_body.endswith('}') and self.rendered:
                """message is a json string"""
                msg_dict = json.loads(msg_body)
                msg_dict['sender'] = event['sender']
                if "comment_post" in msg_dict.keys():
                    self.post_comment(msg_dict)
                else:
                    print("friends are only allowed to leave comments: cp <post-id>")
            else:
                self.send_room_message(room, event)
        self.rendered = True
