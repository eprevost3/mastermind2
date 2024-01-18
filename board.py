from typing import Union
import matplotlib.pyplot as plt 
from matplotlib.pyplot import figure
from matplotlib.patches import Wedge, Rectangle
from copy import deepcopy
import numpy as np

class Board:
    def __init__(self, colors: list[str], nb_rows: int=8, nb_cells: int=4) -> None:
        """sets of colors each cell can take"""
        self.board = {k: set(colors) for k in range(nb_cells)}
        self.nb_rows = nb_rows
        self.nb_cells = nb_cells
        # contains the different moves and feedback the player had
        self.nb_moves_left = self.nb_rows
        self.logs = {
            k: {
                "guess": ["grey"] * nb_cells, 
                "mask": ["grey"] * nb_cells, 
                "options": [{"grey"}] * nb_cells
            } for k in range(nb_rows)
        }

    def _generate_circle(
            self, 
            center: tuple[float, float], 
            radius: float, 
            color: str, 
            ax, 
            start_angle: float=0, 
            end_angle: float=360
        ) -> None:
        """
        generate a circle representing either the feedback or the guess of the 
        player 
        """
        w = Wedge(center, radius, start_angle, end_angle, fc=color)
        ax.add_artist(w)

        return None
    
    def _generate_cell_and_options(
            self, cell_idx: int, row_idx: int, x: float, y: float, color: str, ax
        ) -> None:
        """plot the cells, the colors chosen and the colors that cell can take"""
        angle = 360 / len(self.logs[row_idx]["options"][cell_idx])
        for k, color_option in enumerate(self.logs[row_idx]["options"][cell_idx]):
            self._generate_circle(
                (x, y), 0.4, color_option, ax, start_angle=k * angle, end_angle=(k + 1) * angle
            )

        self._generate_circle((x, y), 0.3, color, ax)

    def _generate_rectangle(
            self, 
            ax, 
            width_rectangle: float, 
            height_rectangle: float, 
            x: float, 
            y: float,
            edgecolor: str="black",
            facecolor: str="none",
            linewidth: float=2,
        ) -> None:
        ax.add_patch(
            Rectangle(
                (x, y), 
                width_rectangle, 
                height_rectangle, 
                edgecolor=edgecolor,
                facecolor=facecolor,
                linewidth=linewidth,
            )
        )
    
    def _set_plot_limits(self, fig, ax, width, height) -> None:
        fig.set_size_inches(width, height)
        ax.set_xlim(-1, width - 1)
        ax.set_ylim(0, height)
        # ax.set_axis_off()
    
    def _get_curr_move_idx(self) -> int:
        """get the index/number of the current round/turn"""
        idx = self.nb_rows - self.nb_moves_left
        return idx
    
    def debug(self):
        """plot the board for debugging/validation purposes"""
        fig, ax = plt.subplots()

        # plot limits
        height = self.nb_rows + 1
        width_board = self.nb_cells
        width_feedback = 2
        width = width_board + width_feedback + 2
        self._set_plot_limits(fig, ax, width, height)

        # board
        self._generate_rectangle(ax, width_board, self.nb_rows, -0.5, 0.5)
        # feedback board 
        self._generate_rectangle(ax, 2, self.nb_rows, self.nb_cells - 0.5, 0.5)

        # cells to fill 
        for row in range(self.nb_rows):
            y = self.nb_rows - row
            colors = self.logs[row]["guess"]

            for x in range(self.nb_cells):
                self._generate_cell_and_options(x, row, x, y, colors[x], ax)

        # cells for AI feedback 
        for row in range(self.nb_rows):
            y = self.nb_rows - row

            if row in self.logs:
                colors = self.logs[row]["mask"]
            else: 
                colors = ["grey"] * self.nb_cells

            for i in range(self.nb_cells):
                x = width_board + i * 0.4
                self._generate_circle((x, y), 0.15, colors[i], ax)              
        plt.show()
        plt.savefig("debug.jpg")
        plt.close()
     
    def update_board(self, mask: list[str], guess: list[str]) -> None:
        """remove a color as a potential candidate for a cell"""
        red_or_white = set()
        greys = set()

        for idx in range(4):
            if mask[idx] == "red":
                red_or_white |= {guess[idx]}
                # the guess for the cell may actually contradict the constraints
                # on the board -> this is why we use the "&"
                self.board[idx] &= {guess[idx]}
            elif mask[idx] == "white":
                red_or_white |= {guess[idx]}
                self.board[idx] -= {guess[idx]}
            else: 
                greys |= {guess[idx]}
                self.board[idx] -= {guess[idx]}

        # if a guess is grey, and for that color, there are no reds or white 
        # feedbacks in the other spots, then we can remove that color everywhere
        only_grey = greys - red_or_white
        for idx in range(4):
            self.board[idx] -= only_grey
        
        self.logs[self._get_curr_move_idx()] = {
            "guess": guess[:], "mask": mask[:], "options": deepcopy(self.board)
        }

        # 1 less move before we reach the end of the board
        self.nb_moves_left -= 1
        return None

    def get_board_score(self, row: int) -> int:
        """
        The score indicates how many unknowns are left before we solve the 
        board
        if the score is 0: there are no unknowns left, we solved the board
        otherwise: there are still some colors we don't know about
        """
        options = self.logs[row]["options"]

        score = sum([len(opt) - 1 for opt in options.values()])

        return score 

    def board_status(self, guess: list[str], feedback: list[str]) -> str: 
        """
        indicates if the board is solved (all colors found), invalid (wrong 
        the color combination can't be right) or yet to determine
        """

        for k in range(self.nb_cells):  
            # check if some cells can't take any color
            if len(self.board[k]) == 0: 
                return "invalid"
            elif feedback[k] == "grey":
                # if there is only one choice left, then the feedback should be
                # red 
                if len(feedback[k]):
                    pass 
                else: 
                    return "invalid" 
            elif feedback[k] == "white":
                # if there is only one choice left, then the feedback should be
                # red 
                if len(feedback[k]):
                    pass 
                else: 
                    return "invalid" 
            else: 
                # if there is only one color left -> the feedback should 
                # be red if the color chosen corresponds to the color of the constraints
                # because otherwise the feedback should white or grey      
                if self.board[k] == {guess[k]}:
                    pass 
                else: 
                    return "invalid"
                
        # check if the board is solved
        only_one_option_left = [len(cell) == 1 for cell in self.board.values()]
        if sum(only_one_option_left) == self.nb_cells:
            return "solved"
        else:
            return "unknown"
 






 