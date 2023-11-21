from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty

#https://burnysc2.github.io/python-sc2/docs/text_files/introduction.html

from WorkerRushBot import WorkerRushBot

run_game(maps.get("sc2-ai-cup-2022"), [
    Bot(Race.Terran, WorkerRushBot()),
    Computer(Race.Terran, Difficulty.Medium)
], realtime=True)