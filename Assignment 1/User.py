import pika
import sys
import json

class User:
    def __init__(self, username, action=None, youtuber_name=None):
        self.connection = pika.SelectConnection(pika.ConnectionParameters('localhost'), self.on_connection_open)
        self.channel = None
        self.username = username
        self.action = action
        self.youtuber_name = youtuber_name

    def on_connection_open(self, _unused_connection):
        self.connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        self.channel = channel
        self.channel.queue_declare(queue='notifications', callback=self.on_queue_declare)

    def on_queue_declare(self, _unused_frame):
        if self.action and self.youtuber_name:
            self.update_subscription()
        else:
            self.receive_notifications()

    def update_subscription(self):
        request = {"user": self.username, "youtuber": self.youtuber_name, "subscribe": self.action == 's'}
        self.channel.basic_publish(exchange='', routing_key='user_requests', body=json.dumps(request))
        action_message = "Subscribed" if self.action == 's' else "Unsubscribed"
        print(f"{action_message} to {self.youtuber_name}")
        print("SUCCESS")

    def receive_notifications(self):
        def callback(ch, method, properties, body):
            notification = json.loads(body.decode('utf-8'))
            print(f"New Notification: {notification['youtuber']} uploaded {notification['video']}")

        self.channel.basic_consume(queue='notifications', on_message_callback=callback, auto_ack=True)

    def start(self):
        try:
            self.connection.ioloop.start()
        except KeyboardInterrupt:
            self.connection.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 User.py <username> [<s/u> <YoutuberName>]")
    else:
        username = sys.argv[1]
        user = User(username)

        if len(sys.argv) == 4:
            action = sys.argv[2]
            youtuber_name = sys.argv[3]
            user.action = action
            user.youtuber_name = youtuber_name

        user.start()
