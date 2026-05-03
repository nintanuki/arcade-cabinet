## Working agreements
- After every code change (yours, an AI assistant's, or a copilot tool's), append a new entry to `docs/CHANGELOG.md` following the format documented at the top of that file. One entry per logical change, newest first under the `---` separator, line numbers reflect the file at the time of edit.

## Game Ideas
- [ ] Tetris Attack / Panel de Pon
- [ ] Pazaak

## Launcher Ideas
- [ ] Seperate games into the following categories:
  - Mr. Navarro's Games
    - Original Games (Star Hero, Dungeon Digger,etc)
    - Tribute Games (Amazons, Pazaak, etc)
    - Made using a Tutorial (Runner, Space Invaders, etc)
  - Student Games

^ Figure out how we want to handle previews and the messages under the previews after we make this change. Either their won't be previews in these top menus or we can use that space for a description of the category.

Also, since the main menu will only have two options, and Mr. Navarro's games will have three, let's make the carousel conditional, it should only be in effect if there are more than 5 options in a menu, otherwise it's just a normal style menu.

## Questions
- [ ] I notice the CRT effect looks bad in some games, and looks better when the screen is NOT full screen. Consider disabling CRT when full screen? Why does this happen though?