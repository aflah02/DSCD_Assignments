import pika
import sys
import json

class Youtuber:
    def __init__(self, youtuber_name, video_name):
        self.connection = pika.SelectConnection(pika.ConnectionParameters('34.172.69.158'), self.on_connection_open)
        self.channel = None
        self.youtuber_name = youtuber_name
        self.video_name = video_name

    def on_connection_open(self, _unused_connection):
        self.connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        self.channel = channel
        self.channel.queue_declare(queue='youtuber_requests', callback=self.on_queue_declare)

    def on_queue_declare(self, _unused_frame):
        self.publish_video()

    def publish_video(self):
        request = {"youtuber": self.youtuber_name, "video": self.video_name}
        self.channel.basic_publish(exchange='', routing_key='youtuber_requests', body=json.dumps(request))
        print(f"{self.youtuber_name} published {self.video_name}")
        print("SUCCESS")

    def start(self):
        try:
            self.connection.ioloop.start()
        except KeyboardInterrupt:
            self.connection.close()

def format_video_name(args):
    stripped_args = map(str.strip, args)
    return " ".join(stripped_args)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 Youtuber.py <YoutuberName> <VideoName>")
    else:
        youtuber_name = sys.argv[1]
        video_name = format_video_name(sys.argv[2:])
        youtuber = Youtuber(youtuber_name, video_name)
        youtuber.start()
