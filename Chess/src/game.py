import pygame

from src.board import *

class Game:
    def __init__(self):
        self.win = pygame.display.set_mode((800, 800))
        pygame.display.set_caption("Sjakk")
        self.clock = pygame.time.Clock()
        self.new_game()

    def new_game(self):
        self.Chessboard = Chessboard(self)

    def draw(self):
        self.Chessboard.draw_board()
        self.Chessboard.highlight_move()
        self.Chessboard.draw_pieces()

        self.Chessboard.highlight_squares()
        self.Chessboard.dragger()

    def update(self):

        pygame.display.flip()
        self.clock.tick(60)

    def check_for_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.Chessboard.handle_movement()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit()

    def main_loop(self):
        while True:
            self.draw()
            self.update()
            self.check_for_events()