from collections import defaultdict
from SSNElement import SSNElement
from ChatRoom import ChatRoom


class SSNChat(SSNElement):
    """a wrapper class for client to add social network state variables"""
    def __init__(self, client, landing_room):
        super().__init__(client, landing_room)
        self.type = 'C'  # c as in client
        self.user_id = self.m_client.user_id
        self.user_name = self.user_id.split(':')[0][1:]
        self.room_handle = self.user_name + "_c"
        self.room_name = self.landing_room.split(':')[0][1:]

    def load(self, room_id_alias):
        room_name = room_id_alias.split(':')[0][1:]
        if room_name in self.room_table:
            if room_id_alias in self.loaded_rooms.keys():
                self.current_room = self.loaded_rooms[room_id_alias]
                for msg in self.all_rooms_messages[room_name]:
                    print(msg)
            else:
                self.current_room = ChatRoom(self.join_room(room_id_alias), self.init_msg_hist_for_room)
                self.loaded_rooms[room_id_alias] = self.current_room
                self.room_table[room_name]["loaded"] = True
        else:
            room_name = room_id_alias.split(':')[0][1:]
            room = self.m_client.create_room(room_name)
            room.set_room_name(room_name)
            self.room_table[self.room_handle] = {"room_id": room.room_id, "loaded": False}
            self.current_room = ChatRoom(room, self.init_msg_hist_for_room)
            self.loaded_rooms[room.room_id] = self.current_room
        self.initialized = True

        # if room_id not in self.loaded_rooms.keys():
        #     room = self.join_room(room_id_alias)
        #     self.current_room = ChatRoom(room, self.init_msg_hist_for_room)
        #     self.loaded_rooms[room_id] = self.current_room
        #     self.room_table[room_name]["loaded"] = True
        # else:
        #     self.current_room = self.loaded_rooms[room_id]
        #     for msg in self.all_rooms_messages[room_name]:
        #         print(msg)

    def on_message(self, room, event):
        if event['type'] == "m.room.member":
            if event['membership'] == "join":
                if self.is_room_setup and not self.rendered:
                    print("{0} joined".format(event['content']['displayname']))
                    self.rendered = True

        elif event['type'] == "m.room.message":
            self.send_room_message(room, event)
        self.rendered = False






