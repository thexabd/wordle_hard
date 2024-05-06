WORDLE SOLVER USING LETTER FREQUENCIES AND INFORMATION GAIN IN PYTHON
code adapted from https://github.com/kiking0501/Wordle-Solver/tree/master

This project solves Wordle in EASY and HARD modes using two heuristics - letter frequencies and information gain (entropy loss). To run the experiments, follow the given instructions (command line)

1. Easy mode using Letter Frequencies Heuristic
`python main.py --solver heuristic --mode easy`

2. Hard mode using Letter Frequencies Heuristic
`python main.py --solver heuristic --mode hard`

3. Easy mode using Information Gain Heuristic
`python main.py --solver mig --mode easy`

4. Hard mode using Information Gain Heuristic
`python main.py --solver mig --mode hard`

The games use the word 'AUDIO' to make the initial guesses. If you wish to use a different word, add the arg `--first_guess (your word)`

NOTE: For the information gain heuristic, make sure to clear the output folder before running the algorithm with a different initial guess word. This is so that it generates a new precomputation of responses, without the program running into an error.
