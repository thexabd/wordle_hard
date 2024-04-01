from BaseWordlePlayer import BaseWordlePlayer
from utility import _get_output_path
import numpy as np
import os
import random


class HardModeWordlePlayer(BaseWordlePlayer):
    def __init__(self, wordle, guess_list=None):
        super().__init__(wordle, guess_list)
        self.correct_positions = [''] * self.wordle.k  # Create a list with the length of the word.
        self.misplaced_letters = []

    def reset(self):
        self.correct_positions = [''] * self.wordle.k
        self.misplaced_letters = []
        super().reset()

    def adjust_candidates(self, guess, response, candidates):
        # Override the base method to enforce hard mode constraints.
        new_candidates = []
        for candidate in candidates:
            if self.is_valid_candidate(guess, response, candidate):
                new_candidates.append(candidate)
        return new_candidates

    def is_valid_candidate(self, guess, response, candidate):
        """
        Check if a candidate word is valid according to the rules of hard mode.
        """
        for i, char in enumerate(candidate):
            if self.correct_positions[i] and char != self.correct_positions[i]:
                return False  # Incorrect letter in a position already known

            '''
            # Check that misplaced letters are not in the position they were misplaced in
            if char in self.misplaced_letters and guess[i] == char:
                return False  # Misplaced letter in the same wrong position
            '''

        # Ensure all misplaced letters are included somewhere in the candidate
        for char in self.misplaced_letters:
            if char not in candidate:
                return False
            # Check if the letter is not placed back in the incorrect position
            # if any(candidate[i] == char and guess[i] == char for i in range(len(candidate))):
            #    return False

        return True

    def give_guess(self, guess_words, candidates, history, fixed_guess=None, verbose=True):
        # Override to use hard mode constraints when picking a guess.
        if fixed_guess is not None:
            return fixed_guess, self.compute_score(fixed_guess)

        if verbose:
            while (1):
                guess = input(
                    "## Input Your Own Guess? (<{}-letter word>/empty):\n".format(self.wordle.k))
                if guess in self.wordle.words and guess not in history:
                    return guess, self.compute_score(guess)
                elif not guess:
                    break
                print("(invalid guess: not in the Wordle list)")
        guess = random.choice([word for word in set(guess_words) - history
                               if self.is_guess_valid(word)])
        return guess, self.compute_score(guess)

    def play(self, target=None, first_guess=None, verbose=True):
        """
        Solve a Wordle game by adhering to the constraints of hard mode.
        """
        self.reset()  # Reset the game state, including correct_positions and misplaced_letters
        if verbose:
            print("\nTARGET: ", "UNKNOWN" if target is None else target)

        target, first_guess = self.lowercase(target), self.lowercase(first_guess)
        guess_words = [x.lower() for x in self.guess_list]
        candidates = [x.lower() for x in self.wordle.words]
        attempts = set()
        trace = []

        num_guess = 0
        while len(candidates) >= 1:
            num_guess += 1

            # Step 1: Generate a guess considering the hard mode rules
            if num_guess == 1 and first_guess:
                guess = first_guess
            else:
                guess = self.generate_hard_mode_guess(candidates, attempts)

            # Ensure the guess complies with the rules
            if not self.is_guess_valid(guess):
                if verbose:
                    print("Invalid guess based on previous hints, picking a new guess...")
                continue

            if verbose:
                print("# Guesses: {}, Picked Guess: {}, # Available Candidates: {}".format(
                    num_guess, guess, len(candidates)))

            # Step 2: Get a response
            response = self.get_response(guess, target)
            if verbose:
                print("# Response: {}".format(response))

            # Step 3: Update the game state based on the response
            trace.append((guess, response))
            self.update_game_state(guess, response)

            if self.wordle.is_correct_response(response):
                if verbose:
                    print("Congrats! Total Guesses: {}".format(num_guess))
                break

            # Adjust candidates based on the response
            candidates = self.adjust_candidates(guess, response, candidates)
            attempts.add(guess)

            if len(candidates) == 0:
                print("Failed to guess: no more available candidates!")
                break

        print(num_guess)

        # Reset the lists
        self.correct_positions = [''] * self.wordle.k
        self.misplaced_letters.clear()

        return num_guess, trace

    def update_game_state(self, guess, response):
        """
        Update the game state including the correct_positions and misplaced_letters based on the response.
        """
        for i, (g, r) in enumerate(zip(guess, response)):
            if r == '2':  # Correct letter in the correct position
                self.correct_positions[i] = g
            elif r == '1' and g not in self.correct_positions:  # Correct letter in the wrong position
                if g not in self.misplaced_letters:
                    self.misplaced_letters.append(g)

    def generate_hard_mode_guess(self, candidates, attempts):
        """
        Generate a valid guess for hard mode by choosing a word from candidates that respects
        the already known correct positions and misplaced letters.
        """

        valid_candidates = [word for word in candidates if self.is_guess_valid(word) and word not in attempts]
        if not valid_candidates:
            raise ValueError("No valid candidates available that meet hard mode constraints.")
        return random.choice(valid_candidates)

    def is_guess_valid(self, guess):
        """
        Check if a guess is valid according to the correct positions and misplaced letters for hard mode.
        """
        # Check correct positions
        for i, char in enumerate(guess):
            if self.correct_positions[i] and char != self.correct_positions[i]:
                return False  # Incorrect letter in a position already known

        '''
        # Check for misplaced letters not to be in the same wrong position
        for i, char in enumerate(guess):
            if char in self.misplaced_letters:
                # Check if the current position is one where this letter was previously misplaced
                if self.correct_positions[i] == char:
                    return False  # Misplaced letter in a wrong position again
        '''

        # Ensure all misplaced letters are included somewhere in the guess
        for char in self.misplaced_letters:
            if char not in guess:
                return False

        return True

    def print_initial_top_guesses(self, output_dir="output", output_name="top_scores"):
        """
            Save and return a sorted list of computed scores for all guess words

            Return:
                a list of (word, score) ordered by a decreasing score
        """
        self.reset()
        top_guesses = sorted(
            [(word, self.compute_score(word)) for word in self.guess_list],
            key=lambda x: (-x[1], x[0]))

        output_path = _get_output_path(output_dir, output_name, type(self).__name__) + ".txt"
        with open(output_path, "w") as f:
            for word, score in top_guesses:
                f.write("\t".join([word, str(score)]) + "\n")
            print("{} saved.".format(f.name))

        return top_guesses