## MY IMPLEMENTATION OF AN AGENT TO SOLVE WORDLE IN HARD MODE ##

from BaseWordlePlayer import BaseWordlePlayer
from utility import _get_output_path
import numpy as np
import os
import random


class HardModeWordlePlayer(BaseWordlePlayer):
    """
        A base class for playing Worldle in Hard Mode
    """

    def __init__(self, wordle, guess_list=None):
        """
            Initialize the Hard Mode Wordle Player with a reference to the Wordle game object and an optional guess list.
        """
        super().__init__(wordle, guess_list)
        self.correct_positions = [''] * self.wordle.k  # Initialize list to store correct letters' positions.
        self.misplaced_letters = [] # List to store letters that are correct but misplaced.

    def reset(self):
        """
            Reset the game state for a new game.
        """
        self.correct_positions = [''] * self.wordle.k
        self.misplaced_letters = []
        super().reset()

    def adjust_candidates(self, guess, response, candidates):
        """
            Filter the list of candidate words based on the response to a guess. This method adjusts the list of candidates
                by removing words that do not comply with the feedback given by the Wordle game, adhering to hard mode rules.
    
            Parameters:
                guess (str): The word that was guessed.
                response (list): List of responses for each character in the guess (0: incorrect, 1: misplaced, 2: correct).
                candidates (list): Current list of possible candidate words.
            
            Returns:
                list: The filtered list of candidate words that still could be the correct answer.
        """
        new_candidates = candidates[:] # Create a copy of the candidates list to modify it without altering the original list.
        char_required_count = {} # Dictionary to hold the minimum required count of each character based on feedback.
        char_occurrences = {} # Dictionary to count occurrences of each character in the guess.

        # Initialize character occurrences and required counts based on responses
        for i, char in enumerate(guess):
            char_occurrences[char] = char_occurrences.get(char, 0) + 1  # Track occurrences of each char

        # Determine the required counts for characters based on the response.
        # Needed when a character appears multiple times in the guess but is partially correct or misplaced.
        for i, char in enumerate(guess):
            if response[i] in ['1', '2'] and char_occurrences[char] > 1:
                if char in char_required_count:
                    char_required_count[char] += 1
                else:
                    char_required_count[char] = 1

        # Filter the candidate words based on the response codes.
        # Uses the response to determine if characters should be in certain positions or not in the word at all.
        for i, resp in enumerate(response):
            if resp == '2': # Correct letter, correct position
                new_candidates = [cand for cand in new_candidates if cand[i] == guess[i]]
            elif resp == '1': # Correct letter, incorrect position
                new_candidates = [cand for cand in new_candidates if guess[i] in cand and cand[i] != guess[i]]
            elif resp == '0': # Letter not in word
                # Determine if the character should be entirely removed from candidates.
                indices_of_letter = [index for index, letter in enumerate(guess) if letter == guess[i]]
                valid_for_removal = True
                for index in indices_of_letter:
                    if response[index] == '2' or response[index] == '1':
                        valid_for_removal = False
                        break
                if valid_for_removal:
                    new_candidates = [cand for cand in new_candidates if guess[i] not in cand]

        # Ensure that the remaining candidates meet the required count for characters with '1' or '2' responses
        def meets_required_counts(candidate):
            candidate_char_count = {char: candidate.count(char) for char in char_required_count}
            for char, required in char_required_count.items():
                if candidate_char_count.get(char, 0) < required:
                    return False
            return True

        new_candidates = [cand for cand in new_candidates if meets_required_counts(cand)]

        # Remove the original guess from the new candidates list
        if guess in new_candidates:
            new_candidates.remove(guess)

        return new_candidates

    def get_response(self, guess, target):
        """
            Get the response for a guess based on the target word.
        """
        return self.wordle.response_to_guess(guess, target)

    def give_guess(self, guess_words, candidates, history, fixed_guess=None, verbose=True):
        """
            Choose the next guess either by the player's input or automatically based on the hard mode constraints.
        """
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
                score = self.compute_score(guess)
            else:
                guess, score = self.generate_hard_mode_guess(candidates, attempts)

            if verbose:
                print("# Guesses: {}, Picked Guess: {} (Score: {:.2f}), # Available Candidates: {}".format(
                    num_guess, guess, score, len(candidates)))
                #print(candidates)

            # Step 2: Get a response
            response = self.get_response(guess, target)
            if verbose:
                print("# Response: {}".format(response))

            # Step 3: Update the game state based on the response
            trace.append((guess, response))
            if not self.wordle.is_correct_response(response):
                self.update_game_state(guess, response)
                candidates = self.adjust_candidates(guess, response, candidates)
                attempts.add(guess)

            if self.wordle.is_correct_response(response):
                if verbose:
                    print("Congrats! Total Guesses: {}".format(num_guess))
                break

            # Adjust candidates based on the response
            # candidates = self.adjust_candidates(guess, response, candidates)
            # attempts.add(guess)

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
        guess, score = self.give_guess(
            guess_words=candidates,
            history=attempts,
            fixed_guess=None,
            verbose=True
        )
        #return random.choice(valid_candidates)
        return guess, score

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