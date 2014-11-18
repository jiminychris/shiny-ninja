import sys
import pygame

from Networking import Client

if __name__ == '__main__':
    peers = Client.find_peers()
