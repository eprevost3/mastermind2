import random as rd
from copy import deepcopy
from board import Board        

class SolveBoard:
    def __init__(self): 
      pass

    def _generate_masks(
            self,
            nb_reds: int, 
            nb_whites: int, 
            l_masks: list,
            idx: int=0,
            mask: list[str]=["grey", "grey", "grey", "grey"], 
        ) -> None:
        """
        generate all the possible combinations of white, red and unknown based
        on the AI feedback
        """
        if idx == 4: 
            if (nb_reds == 0) and (nb_whites == 0):
                l_masks.append(mask[:])
            else: 
                pass 

            return None
        else: 
            pass 

        # set the current idx to be red (right color, right position)
        if nb_reds:
            new_mask = mask[:]
            new_mask[idx] = "red"
            self._generate_masks(nb_reds - 1, nb_whites, l_masks, idx + 1, new_mask)
        
        # select the current idx to be white (right color, wrong position)
        if nb_whites:
            new_mask = mask[:]
            new_mask[idx] = "white"
            self._generate_masks(nb_reds, nb_whites - 1, l_masks, idx + 1, new_mask)

        # set the current idx to be open (not the right color)
        self._generate_masks(nb_reds, nb_whites, l_masks, idx + 1, mask)

        return None

    def generate_valid_boards(
            self, l_boards: list[Board], color_guess: list[str], feedback_ai: dict[str, int]
        ) -> list[Board]:
        """based on the feedback of the AI, generate all boards valid boards"""
        l_masks = []
        self._generate_masks(feedback_ai["nb_reds"], feedback_ai["nb_whites"], l_masks)

        # find all the boards that align with the current and former AI feedback
        l_valid_boards = []
        for board in l_boards: 
            for mask in l_masks:
                new_board = deepcopy(board)
                new_board.update_board(mask, color_guess)

                if new_board.board_status(color_guess, mask) != "invalid":
                    l_valid_boards.append(new_board)
                else: 
                    pass


        return l_valid_boards

    def find_next_best_guess(
            self, l_boards: list[Board], turn_idx: int
        ) -> list[str]:
        """returns the best guess to make for next turn"""
        scores = [board.get_board_score(turn_idx) for board in l_boards]
        
        best_idx = min(enumerate(scores), key=lambda x: x[1])[0]
        best_board = l_boards[best_idx]

        # color option we have 
        best_guess = []
        color_options = best_board.board
        for k in range(best_board.nb_cells):
            color_idx = rd.randint(0, len(color_options[k]) - 1)

            best_guess.append(list(color_options[k])[color_idx])

        return best_guess


