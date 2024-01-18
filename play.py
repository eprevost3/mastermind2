import random as rd
from collections import Counter
from board import Board
from solver import SolveBoard

class Round:
    def __init__(
            self, colors: list[str], nb_cells: int=4, max_tries: int=8
        ) -> None:
        self.colors = colors
        self.nb_cells = nb_cells
        self.max_tries = max_tries
        self.combination = self._set_combination() 

    def _set_combination(self) -> list[str]:
        """set the combination to guess"""
        low, high = 0, len(self.colors) - 1
        combination = [
            self.colors[rd.randint(low, high)] for _ in range(self.nb_cells)
        ]
        print("combination to find: ", combination)
        return combination
    
    def score_guess(self, guess: list[str]) -> dict[str, int]:
        """
        scores the guess. For every color placed in the right cell: +1 red 
        For every color not placed in the right cell but present in the combination:
        +1 white
        """
        is_same = [truth == _guess for truth, _guess in zip(self.combination, guess)]
        nb_reds = sum(is_same)

        guess_filt = [col for col, flag in zip(guess, is_same) if not flag]
        combin_filt = [
            col for col, flag in zip(self.combination, is_same) if not flag
        ]

        nb_whites = sum((Counter(guess_filt) & Counter(combin_filt)).values())

        score = {
            "nb_reds": nb_reds,
            "nb_whites": nb_whites,
        }

        return score

class Play:
    def __init__(self):
        pass 

    def start(self, debug: bool=False) -> Board:
        """start the game"""
        colors = ["red", "purple", "blue", "green", "yellow", "orange", "white", "pink"]
        round = Round(colors, nb_cells=4)
        board = Board(colors, nb_cells=4)
        solver = SolveBoard()

        if debug:
            l_boards = [board]

            nb_cols = len(colors) - 1
            guess = [
                colors[rd.randint(0, nb_cols)] for _ in range(board.nb_cells)
            ]

            turn_idx = 0
            feedback = {"nb_reds": 0}
            while feedback["nb_reds"] != board.nb_cells and round.max_tries > turn_idx:
                feedback = round.score_guess(guess)
                l_boards = solver.generate_valid_boards(l_boards, guess, feedback) 
                
                guess = solver.find_next_best_guess(l_boards, turn_idx)

                turn_idx += 1


            solved_board = l_boards[0]
            solved_board.debug() 
                
        else: 
            ai_feedback = {"nb_reds": 0}
            l_boards = [board]

            while ai_feedback["nb_reds"] != board.nb_cells:
                color_guess = input("enter the 4 colors. Separate only by a comma (e.g: red,blue,green,yellow)")
                color_guess = color_guess.split(",")
                nb_reds = int(input("AI feedback: nb red tokens?"))
                nb_whites = int(input("AI feedback: nb white tokens?"))

                ai_feedback = {"nb_reds": nb_reds, "nb_whites": nb_whites}
                l_boards = solver.generate_valid_boards(
                    l_boards, color_guess, ai_feedback
                )

            print("found!")


        return solved_board
    

if __name__ == "__main__":
    colors = ["red", "purple", "blue", "green", "yellow", "orange", "white", "pink"]
    round = Round(colors, 4)
    round.combination = ["blue"] * 4
    print(round.score_guess(["green"] * 4))
    print(round.score_guess(["blue"] * 4))
    print(round.score_guess(["blue", "blue", "white", "red"]))

    round = Round(colors, 4)
    round.combination = ["red", "red", "white", "green"]
    print(round.score_guess(["green", "white", "red", "red"])) # SOLVE!
    print(round.score_guess(["red", "white", "blue", "red"]))
    print(round.score_guess(["green", "orange", "red", "pink"]))
    print(round.score_guess(["green", "red", "white", "red"]))


    p = Play()
    p.start(debug=True)

