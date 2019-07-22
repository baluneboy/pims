import sys
sys.path.insert(0, '/usr/local/lib/python3.6/site-packages')
from pythonosc import osc_message_builder
from pythonosc import udp_client

sender = udp_client.SimpleUDPClient('127.0.0.1', 4559)
sender.send_message('/trigger/prophet', [70, 100, 8]) 
