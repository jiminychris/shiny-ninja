import unittest
import pygame
from Rendering import Renderer2d

class TestRenderer2d(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self._renderer2d = Renderer2d.Renderer2d()

    def tearDown(self):
        del self._renderer2d
        pygame.quit()

    def test_open_window(self):
        self.assertTrue(self._renderer2d.openWindow())

if __name__ == '__main__':
    unittest.main()
