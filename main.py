import os
import numpy as np
from utility import _bucket_count, _get_output_path


def get_words(size="large"):
    """
        small word list: 2315
        extra word list: 12972
    """
    if size not in ("small", "large"):
        raise ValueError("choose from size 'small' / 'large")

    words = []
    with open("data/small.txt") as f:
        for line in f.readlines():
            word = line.strip()
            words.append(word)

    if size == "small":
        return words
    elif size == "large":
        word_set = set(words)
        with open("data/large.txt") as f:
            for line in f.readlines():
                extra_word = line.strip()
                if extra_word not in word_set:
                    words.append(extra_word)
        return words


def get_first_guess_performance(wordle, player, first_guess, verbose=True):
    """
        Use the input first guess word for all possible targets
            and get statistics about the number of guesses
    """
    try:
        from tqdm import tqdm
    except ImportError:
        print("Download tqdm to display progress bar in command line")

    def _get_stats(all_guesses):
        """
            Print message for the statistics of a list of guesses
        """
        guess_dict = _bucket_count(all_guesses)
        msg = "Mean: {:.3f}, Min: {}, Max: {}".format(
            np.mean(all_guesses), min(guess_dict), max(guess_dict))
        msg += ", Count of Guesses:"
        for i in range(min(guess_dict), max(guess_dict) + 1):
            msg += " [{}] {}".format(i, guess_dict.get(i, 0))
        return msg

    if verbose:
        print("#" * 50)
        print("### Checking performance of '{}' as a first guess for all possible targets... ###".format(first_guess))
        print("#" * 50)

    all_guesses = []
    for target in tqdm(wordle.words):
        num_guess, trace = player.play(target=target, first_guess=first_guess, verbose=True)
        all_guesses.append(num_guess)
    msg = _get_stats(all_guesses)
    if verbose:
        print(msg)
    return msg


if __name__ == "__main__":
    from Wordle import Wordle
    from HeuristicWordlePlayer import HeuristicWordlePlayer
    from MaxInformationGainWordlePlayer import MaxInformationGainWordlePlayer
    from HardHeuristicWordlePlayer import HardHeuristicWordlePlayer
    from HardMaxInformationGainWordlePlayer import HardMaxInformationGainWordlePlayer
    import argparse

    # solver
    parser = argparse.ArgumentParser(
        description='Wordle Solvers in Python!')

    parser.add_argument(
        "--solver", choices=["heuristic", "mig"], default="mig",
        help="Specify the solver to use (heuristic/mig)")
    parser.add_argument(
        "--first_guess", default="salet",
        help="Specify a fixed word for the solver to use in the first guess, default 'audio'")
    parser.add_argument(
        "--mode", default="hard",
        help="Specify the difficulty, default 'hard'")

    args = parser.parse_args()

    ####################################################
    words_size = "large"
    wordle = Wordle(5, get_words(words_size))

    if args.solver == "heuristic" and args.mode == "easy":
        print("\n[Loading the Heuristic Player ({} word list)]\n".format(words_size))
        player = HeuristicWordlePlayer(wordle, guess_list=get_words(words_size))

    elif args.solver == "mig" and args.mode == "easy":
        print("\n[Loading the Max Information Gain Player (large word list)]\n")
        player = MaxInformationGainWordlePlayer(wordle, guess_list=get_words("large"), precompute="large")

    elif args.solver == "heuristic" and args.mode == "hard":
        print("\n[Loading the Max Information Gain Player (large word list)]\n")
        player = HardHeuristicWordlePlayer(wordle, guess_list=get_words(words_size))

    elif args.solver == "mig" and args.mode == "hard":
        print("\n[Loading the Max Information Gain Player (large word list)]\n")
        player = HardMaxInformationGainWordlePlayer(wordle, guess_list=get_words("large"), precompute="large")

    get_first_guess_performance(wordle, player, first_guess=args.first_guess)
