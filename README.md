BytePy is a simple game made solely so I could try an implementation of the bytecode design pattern. To clearify that the bytecode is the only thing communicated between the 'programmer' and the 'game' I've tried to use events as much as possible.

---GAME INSTRUCTIONS---
The game is quite simple, you're programming a robot (shown as an arrow on the gameboard) and your goal is to get it to the flag at the bottom right.
You can make a list of commands by pressing the top 6 buttons on the right, and make the robot execute them by hitting the 7th button labelled 'Run Code', the commands will be executed in the order they were given.

--COMMANDS--
1. 'Push'takes the number the robot is standing on and pushes it onto the stack, please note that the stack operates in a first-in-last-out fashion, meaning that the last number (which haven't been used yet) that was pushed onto the stack will be the number the next command uses.
2. 'Add' takes the two last numbers that was put onto the stack, adds them together, and pushes the result onto the stack.
3. 'Subtract' takes the two last numbers that was put onto the stack,  subtracts one from the other, and pushes the result onto the stack.
4. 'Forward' takes the top number off the stack, and moves the robot that many squares forwards.
5. 'Turn R' takes the top number off the stack, and makes the robot turn right/clockwise that many turns.
6. 'Turn L' takes the top number off the stack, and makes the robot turn left/counter-clockwise that many turns.
