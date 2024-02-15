import pika
import json

class YoutubeServer:
    def __init__(self):
        self.connection = pika.SelectConnection(pika.ConnectionParameters('localhost'), self.on_connection_open)
        self.channel = None
        self.users = {}  # Dictionary to store user data
        self.youtubers = {}  # Dictionary to store YouTuber data

    def on_connection_open(self, _unused_connection):
        self.connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        print("Youtube server started.")
        self.channel = channel
        self.channel.exchange_declare(exchange='notifications', exchange_type='direct')
        # Declare queues
        self.channel.queue_declare(queue='user_requests')
        self.channel.queue_declare(queue='youtuber_requests')

        # Set up consumers for user and YouTuber requests
        self.channel.basic_consume(queue='user_requests', on_message_callback=self.consume_user_requests, auto_ack=True)
        self.channel.basic_consume(queue='youtuber_requests', on_message_callback=self.consume_youtuber_requests, auto_ack=True)

    def consume_user_requests(self, ch, method, properties, body):
        request = json.loads(body.decode('utf-8'))

        username = request['user']
        if username not in self.users:
            self.users[username] = {'subscriptions': []}
            print(f"{username} logged in")

        # Check for subscribe/unsubscribe request
        if 'subscribe' in request and 'youtuber' in request:
            subscribe = request['subscribe']
            youtuber_name = request['youtuber']

            if subscribe is not None and youtuber_name is not None:
                action = 'subscribed' if subscribe else 'unsubscribed'

                if username in self.users:
                    if action == 'subscribed' and youtuber_name not in self.users[username]['subscriptions']:
                        self.users[username]['subscriptions'].append(youtuber_name)
                    elif action == 'unsubscribed' and youtuber_name in self.users[username]['subscriptions']:
                        self.users[username]['subscriptions'].remove(youtuber_name)
                    print(f"{username} {action} to {youtuber_name}")

    def consume_youtuber_requests(self, ch, method, properties, body):
        request = json.loads(body.decode('utf-8'))

        youtuber_name = request['youtuber']
        video_name = request['video']

        # Process YouTuber's video upload request
        if youtuber_name not in self.youtubers:
            self.youtubers[youtuber_name] = []
        self.youtubers[youtuber_name].append(video_name)

        print(f"{youtuber_name} uploaded {video_name}")
        self.notify_users(youtuber_name, video_name)

    def notify_users(self, youtuber_name, video_name):
        notification = {"youtuber": youtuber_name, "video": video_name}
        property = pika.BasicProperties(delivery_mode=2)
        for username, data in self.users.items():

            if youtuber_name in data['subscriptions']:
                # Publish with username as routing key
                self.channel.basic_publish(
                    exchange='notifications',
                    routing_key=username,
                    body=json.dumps(notification),
                    properties=property
                )
        print(f"Notifications sent to {youtuber_name}'s subscribers")

    def start(self):
        try:
            self.connection.ioloop.start()
        except KeyboardInterrupt:
            self.connection.close()

if __name__ == "__main__":
    server = YoutubeServer()
    server.start()
