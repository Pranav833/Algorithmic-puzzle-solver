import random
from tkinter import *
import numpy as np
from typing import Optional
from GameState import GameState
from MinimaxAi import MinimaxAi
from time import time
import time

size_of_board = 600
number_of_dots = 4
dot_color = "#7BC043"
player1_color = "#0492CF"
player1_color_light = "#67B0CF"
player2_color = "#EE4035"
player2_color_light = "#EE7E77"
Green_color = "#7BC043"
dot_width = 0.25 * size_of_board / number_of_dots #37.5
edge_width = 0.1 * size_of_board / number_of_dots #15
distance_between_dots = size_of_board / (number_of_dots)#150
BOT_TURN_INTERVAL_MS = 100
LEFT_CLICK = "<Button-1>"


class Dots_and_Boxes:

    def __init__(self):
        self.window = Tk()
        self.window.title("Dots_and_Boxes")
        self.canvas = Canvas(
            self.window, width=size_of_board, height=size_of_board)
        self.canvas.pack()

        random.seed(time.time())

        self.player1_starts = random.choice([False, True])

        self.bot = MinimaxAi()
        self.play_again()

    def play_again(self):
        
        self.canvas.create_rectangle(
            0, 0, size_of_board, size_of_board, fill="black"
        )

        self.refresh_board()

        self.board_status = np.zeros(
            shape=(number_of_dots - 1, number_of_dots - 1))
        self.row_status = np.zeros(shape=(number_of_dots, number_of_dots - 1))
        self.col_status = np.zeros(shape=(number_of_dots - 1, number_of_dots))
        self.pointsScored = False
        self.player1_starts = not self.player1_starts
        self.player1_turn = not self.player1_starts
        self.reset_board = False
        self.turntext_handle = []
        self.already_marked_boxes = []

        self.display_turn_text()
        self.turn()

    def mainloop(self):
        self.window.mainloop()

    def is_grid_occupied(self, logical_position, type):
        x = logical_position[0]
        y = logical_position[1]
        occupied = True

        if type == "row" and self.row_status[y][x] == 0:
            occupied = False
        if type == "col" and self.col_status[y][x] == 0:
            occupied = False

        return occupied

    def convert_grid_to_logical_position(self, grid_position):
        grid_position = np.array(grid_position)
        position = (grid_position - distance_between_dots / 4) // (distance_between_dots / 2)
        type = False
        logical_position = []
        if position[1] % 2 == 0 and (position[0] - 1) % 2 == 0:
            x = int((position[0] - 1) // 2)
            y = int(position[1] // 2)
            logical_position = [x, y]
            type = "row"
        elif position[0] % 2 == 0 and (position[1] - 1) % 2 == 0:
            y = int((position[1] - 1) // 2)
            x = int(position[0] // 2)
            logical_position = [x, y]
            type = "col"


        return logical_position, type

    def pointScored(self):
        self.pointsScored = True

    def mark_box(self):
        boxes = np.argwhere(self.board_status == -4)
        for box in boxes:
            if list(box) not in self.already_marked_boxes and list(box) != []:
                self.already_marked_boxes.append(list(box))
                color = player1_color_light
                self.shade_box(box, color)

        boxes = np.argwhere(self.board_status == 4)
        for box in boxes:
            if list(box) not in self.already_marked_boxes and list(box) != []:
                self.already_marked_boxes.append(list(box))
                color = player2_color_light
                self.shade_box(box, color)

    def update_board(self, type, logical_position):
        x = logical_position[0]
        y = logical_position[1]
        
        val = 1
        playerModifier = 1
        if self.player1_turn:
            playerModifier = -1

        if y < (number_of_dots - 1) and x < (number_of_dots - 1):
            self.board_status[y][x] = (
                abs(self.board_status[y][x]) + val
            ) * playerModifier
            if abs(self.board_status[y][x]) == 4:
                self.pointScored()

        if type == "row":
            self.row_status[y][x] = 1
            if y >= 1:
                self.board_status[y - 1][x] = (
                    abs(self.board_status[y - 1][x]) + val
                ) * playerModifier
                if abs(self.board_status[y - 1][x]) == 4:
                    self.pointScored()

        elif type == "col":
            self.col_status[y][x] = 1
            if x >= 1:
                self.board_status[y][x - 1] = (
                    abs(self.board_status[y][x - 1]) + val
                ) * playerModifier
                if abs(self.board_status[y][x - 1]) == 4:
                    self.pointScored()

    def is_gameover(self):
        return (self.row_status == 1).all() and (self.col_status == 1).all()


    def make_edge(self, type, logical_position):
        if type == "row":
            start_x = (
                distance_between_dots / 2 +
                logical_position[0] * distance_between_dots
            )
            end_x = start_x + distance_between_dots
            start_y = (
                distance_between_dots / 2 +
                logical_position[1] * distance_between_dots
            )
            end_y = start_y
        elif type == "col":
            start_y = (
                distance_between_dots / 2 +
                logical_position[1] * distance_between_dots
            )
            end_y = start_y + distance_between_dots
            start_x = (
                distance_between_dots / 2 +
                logical_position[0] * distance_between_dots
            )
            end_x = start_x

        if self.player1_turn:
            color = player1_color
        else:
            color = player2_color
        self.canvas.create_line(
            start_x, start_y, end_x, end_y, fill=color, width=edge_width
        )

    def display_gameover(self):
        player1_score = len(np.argwhere(self.board_status == -4))
        player2_score = len(np.argwhere(self.board_status == 4))

        if player1_score > player2_score:
            text = "Winner: Player "
            color = player1_color
        elif player2_score > player1_score:
            text = "Winner: AI "
            color = player2_color
        else:
            text = "Its a tie"
            color = "gray"

        self.canvas.delete("all")
        self.canvas.create_text(
            size_of_board / 2,
            size_of_board / 3,
            font="cmr 60 bold",
            fill=color,
            text=text,
        )

        score_text = "Scores \n"
        self.canvas.create_text(
            size_of_board / 2,
            5 * size_of_board / 8,
            font="cmr 40 bold",
            fill=Green_color,
            text=score_text,
        )

        score_text = "Player 1 : " + str(player1_score) + "\n"
        score_text += "Player 2 : " + str(player2_score) + "\n"

        self.canvas.create_text(
            size_of_board / 2,
            3 * size_of_board / 4,
            font="cmr 30 bold",
            fill=Green_color,
            text=score_text,
        )
        self.reset_board = True

        score_text = "Click to play again \n"
        self.canvas.create_text(
            size_of_board / 2,
            15 * size_of_board / 16,
            font="cmr 20 bold",
            fill="gray",
            text=score_text,
        )

    def refresh_board(self):

        for i in range(number_of_dots):
            x = i * distance_between_dots + distance_between_dots / 2
            self.canvas.create_line(
                x,
                distance_between_dots / 2,
                x,
                size_of_board - distance_between_dots / 2,
                fill="gray",
                dash=(2, 2),
            )
            self.canvas.create_line(
                distance_between_dots / 2,
                x,
                size_of_board - distance_between_dots / 2,
                x,
                fill="gray",
                dash=(2, 2),
            )

        for i in range(number_of_dots):
            for j in range(number_of_dots):
                start_x = i * distance_between_dots + distance_between_dots / 2
                end_x = j * distance_between_dots + distance_between_dots / 2
                self.canvas.create_oval(
                    start_x - dot_width / 2,
                    end_x - dot_width / 2,
                    start_x + dot_width / 2,
                    end_x + dot_width / 2,
                    fill=dot_color,
                    outline=dot_color,
                )

    # def display_turn_text(self):
    #     text = "Next turn: "
    #     if self.player1_turn:
    #         text += "Player"
    #         color = player1_color
    #     else:
    #         text += "AI"
    #         color = player2_color

    #     self.canvas.delete(self.turntext_handle)
    #     self.turntext_handle = self.canvas.create_text(
    #         size_of_board - 5 * len(text),
    #         size_of_board - distance_between_dots / 8,
    #         font="cmr 15 bold",
    #         text=text,
    #         fill=color,
    #     )

    def shade_box(self, box, color):
        start_x = (
            distance_between_dots / 2 + box[1] *
            distance_between_dots + edge_width / 2
        )
        start_y = (
            distance_between_dots / 2 + box[0] *
            distance_between_dots + edge_width / 2
        )
        end_x = start_x + distance_between_dots - edge_width
        end_y = start_y + distance_between_dots - edge_width
        self.canvas.create_rectangle(
            start_x, start_y, end_x, end_y, fill=color, outline=""
        )

    def display_turn_text(self):
        text = "Next turn: "
        if self.player1_turn:
            text += "Player"
            color = player1_color
        else:
            text += "AI"
            color = player2_color

        self.canvas.delete(self.turntext_handle)
        self.turntext_handle = self.canvas.create_text(
            size_of_board - 5 * len(text),
            size_of_board - distance_between_dots / 8,
            font="cmr 15 bold",
            text=text,
            fill=color,
        )

    def click(self, event):
        if not self.reset_board:
            grid_position = [event.x, event.y]
            logical_position, valid_input = self.convert_grid_to_logical_position(
                grid_position
            )
            self.update(valid_input, logical_position)
        else:
            self.canvas.delete("all")
            self.play_again()
            self.reset_board = False

    def update(self, valid_input, logical_position):
        if valid_input and not self.is_grid_occupied(logical_position, valid_input):
            self.window.unbind(LEFT_CLICK)
            self.update_board(valid_input, logical_position)
            self.make_edge(valid_input, logical_position)
            self.mark_box()
            self.refresh_board()
            self.player1_turn = (
                not self.player1_turn if not self.pointsScored else self.player1_turn
            )
            self.pointsScored = False

            if self.is_gameover():
                self.display_gameover()
                self.window.bind(LEFT_CLICK, self.click)
            else:
                self.display_turn_text()
                self.turn()

    def turn(self):
        if self.player1_turn:
            self.window.bind(LEFT_CLICK, self.click)
        else:
            self.window.after(BOT_TURN_INTERVAL_MS, self.bot_turn)  # Remove the unnecessary argument



    def bot_turn(self):  # Remove the argument from here
        action = self.bot.get_action(
            GameState(
                self.board_status.copy(),
                self.row_status.copy(),
                self.col_status.copy(),
                self.player1_turn,
            )
        )
        self.update(action.action_type, action.position)



if __name__ == "__main__":
    game_instance = Dots_and_Boxes(
    )
    game_instance.mainloop()
