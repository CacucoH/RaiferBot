# Raifa Telegram Bot
![ds](https://i.imgur.com/i0y6ku6.jpeg)
## Description
**Raifa Telegram Bot** - Just a simple bot that you can add to your [Telegram](https://telegram.org/) `group/supergroup`.

The main purpose of this product is to simulate the competitive game among _all group participants_.
#### The idea
Each player has their own score that is `0` at the beginning. They can grow the score in two different ways using special commands. The main goal is to be **the first in the top**.
#### Available commands
Here is the list of available commands and mechanics:
- `start` or `setup`:
	- Used only in **DM**. Basically, sets up the bot
- `raifa`:
	- This command is used to increase Raifa's size. **Be careful!** Increment is a _random value_ in range from `-10` to `10`. 
	- But even if you fail and get your size decreased, the `luck` mechanics kicks in and _increases_ your chances to pick a _positive number_ next time.
	- Important! _After executing this command you may execute it only after 24 hours again!_
- `attack`:
	- Attack a random player! There is 3 possible outcomes:
		1. **Success** - you take from `1` to `n*` points from your victim reducing their score
		2. **Fail** - you fail the attack and lose from `1` to `n*` points. These points are given to the victim
		3. **Self-attack** - yes, that's possible. You attack yourself. No changes in points, but you got time cooldown
	- Important! _After executing this command you may execute it only after 24 hours again!_
- `stat`:
	- Simply displays top players
- `rules`:
	- Displays rules of this bot

\*n - If player has 10< points, it lose only from `1` to their current score. Since score becomes >10, player lose from `1` to `10` points

## Features
- No annoying ADS
- No slurs
- Funny stuff
## Deployed versions
The **stable** version are located at the `main` branch
The **newest** versions are located into `test` branch
### Installation
This code might be used as pure code or inside a container.
To launch it as a docker container, just build it and run
```
docker-compose up --build -d
```
Container would start automatically on system startup
## Licence
**MIT licence** is used in this project