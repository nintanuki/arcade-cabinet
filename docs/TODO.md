## Working agreements
- After every code change (yours, an AI assistant's, or a copilot tool's), append a new entry to `docs/CHANGELOG.md` following the format documented at the top of that file. One entry per logical change, newest first under the `---` separator, line numbers reflect the file at the time of edit.

# IDEAS
- [ ] Add requirements.txt to every game for Pygame and Python

## Game Ideas
- [ ] Tetris Attack / Panel de Pon
- [ ] Pazaak
- [ ] Fishy
- [ ] Rodent's Revenge

## Launcher Ideas

## Issues
- [ ] This code desperately needs to be re-factored. Put main.py and the ArcadeLauncher class on a diet. The run method should only be calling functions in a loop but it's checking for input. There are only two files for code, main.py and settings.py, split these up into different files in different folders. Seperate responsibilities. There is also legacy code that needs to be deleted. Let's see if we can do this without breaking anything.

## Questions
- [ ] I notice the CRT effect looks bad in some games, and looks better when the screen is NOT full screen. Consider disabling CRT when full screen? Why does this happen though?