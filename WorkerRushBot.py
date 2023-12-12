import sc2
from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.data import Result
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.constants import *
from sc2.position import Point2, Point3, Pointlike
from sc2.unit import Unit
from sc2.player import Human
import random

# from sc2.player import Bot, Computer
firstSupply = False
reaperCreated = False
reapersOnPosition1 = False
reapersOnPosition2 = False
sendMarinesToBunker = False
havingResearchBay = False
makingSecondBarracks = False
makingFirstBarracks = False

class WorkerRushBot(BotAI):
    NAME: str = "MarineRushBot"
    RACE: Race = Race.Terran               
    
    async def on_step(self, iteration: int):        

        if iteration % 25 == 0:
            await self.distribute_workers()                

        if self.townhalls:
            # První Command Center
            command_center = self.townhalls[0]
            isStartLocationInTop = command_center.position == Point2((43.5, 110.5))

            if isStartLocationInTop:
                bunkerPosition = Point2((61,98))                              
            else:
                bunkerPosition = Point2((72,33))      
        
            if iteration % 10 == 0:
                idle_units = self.units(UnitTypeId.MARINE).idle

                # Check for enemies near the bunker
                enemies_near_bunker = self.enemy_units.filter(lambda unit: unit.is_visible and unit.distance_to(bunkerPosition) < 6)

                # If enemies are near, send idle marines to assist
                if enemies_near_bunker.exists and idle_units.exists:
                    for marine in idle_units:
                        self.do(marine.attack(enemies_near_bunker.closest_to(marine).position))   

            # Trénování SCV
            # Bot trénuje nová SCV, jestliže je jich méně než 17
            if self.can_afford(UnitTypeId.SCV) and self.supply_workers <= 20 and command_center.is_idle:
                command_center.train(UnitTypeId.SCV)

            global firstSupply

            # Build first Supply Depot,
            if self.supply_used >= 14 and firstSupply==False:        
                if self.can_afford(UnitTypeId.SUPPLYDEPOT):                    
                    print("first supply")
                    firstSupply = True
                    await self.build(
                    UnitTypeId.SUPPLYDEPOT,
                    near=command_center.position.towards(self.game_info.map_center, 4))

            # if self.supply_left < 6 and self.supply_used >= 14 and not self.already_pending(UnitTypeId.SUPPLYDEPOT):
            #     if self.can_afford(UnitTypeId.SUPPLYDEPOT):
            #         # Budova bude postavena poblíž Command Center směrem ke středu mapy
            #         # SCV pro stavbu bude vybráno automaticky viz dokumentace
            #         await self.build(
            #             UnitTypeId.SUPPLYDEPOT,
            #             near=command_center.position.towards(self.game_info.map_center, 8))

            global makingFirstBarracks

            # Build first Barracks
            #if self.supply_workers >= 16 and self.structures(UnitTypeId.BARRACKS).amount == 0:
            if self.supply_workers >= 16 and makingFirstBarracks == False and not self.already_pending(UnitTypeId.BARRACKS):
                print("First Barrack")
                if self.can_afford(UnitTypeId.BARRACKS):
                    makingFirstBarracks = True
                    worker_unit = self.workers[0]
                    if worker_unit is not None:    
                        makingFirstBarracks = True                    
                        if isStartLocationInTop:
                            worker_unit.build(UnitTypeId.BARRACKS, Point3((54,102,10)))                                         
                        else:
                            worker_unit.build(UnitTypeId.BARRACKS, Point3((80,29,10)))
                    # await self.build(
                    #     UnitTypeId.BARRACKS,
                    #     near=command_center.position.towards(self.game_info.map_center, 8))                         

            # Build Gas
            if (self.structures(UnitTypeId.BARRACKS).amount > 0 and self.already_pending(UnitTypeId.REFINERY) < 1 and self.structures(UnitTypeId.REFINERY).amount == 0) or (self.supply_workers >= 18 and self.structures(UnitTypeId.REFINERY).amount == 1):
                #print("Making Gas")
                # vgs = self.vespene_geyser.closer_than(10, command_center)[0]
                # for vg in vgs:
                #     if await self.can_place(UnitTypeId.REFINERY, vg.position) and self.can_afford(UnitTypeId.REFINERY):
                #         ws = self.workers.gathering
                #         if ws.exists:
                #             w = ws.closest_to(vg)
                #             await self.build(UnitTypeId.REFINERY, vg)
                #         return
                vg = self.vespene_geyser.closer_than(10, command_center)[0]
                if await self.can_place(UnitTypeId.REFINERY, vg.position) and self.can_afford(UnitTypeId.REFINERY):
                    ws = self.workers.gathering
                    if ws.exists:
                        w = ws.closest_to(vg)
                        await self.build(UnitTypeId.REFINERY, vg)
                    return
                
            global makingSecondBarracks

            # Build Proxy Barracks
            if self.supply_workers >= 16 and makingFirstBarracks == True and makingSecondBarracks == False and self.structures(UnitTypeId.BARRACKS).amount == 1:                
                if self.can_afford(UnitTypeId.BARRACKS):
                    makingSecondBarracks = True
                    print("SecondBarrack")
                    worker_unit = self.workers[0]
                    if worker_unit is not None:                        
                        if isStartLocationInTop:
                            worker_unit.build(UnitTypeId.BARRACKS, Point3((105,41)))                               
                        else:
                            worker_unit.build(UnitTypeId.BARRACKS, Point3((27,91)))
                    

            if self.structures(UnitTypeId.BARRACKS).amount >= 2:
                #print("Making Bunker")
                if self.can_afford(UnitTypeId.BUNKER):
                    worker_unit = self.workers[0]
                    if worker_unit is not None:                        
                        if isStartLocationInTop:
                            worker_unit.build(UnitTypeId.BUNKER, Point2((61,98)))                               
                        else:
                            worker_unit.build(UnitTypeId.BUNKER, Point2((72,33)))

            # if self.structures(UnitTypeId.BARRACKS).amount > 2 and self.structures(UnitTypeId.BUNKER).amount == 1:
            #     #print("Making Bunker")
            #     if self.can_afford(UnitTypeId.BUNKER):
            #         worker_unit = self.workers[0]
            #         if worker_unit is not None:                        
            #             if isStartLocationInTop:
            #                 worker_unit.build(UnitTypeId.BUNKER, Point2((34.5,108.5)))                               
            #             else:
            #                 worker_unit.build(UnitTypeId.BUNKER, Point2((99.5,23.5)))

            #if self.structures(UnitTypeId.BUNKER).amount == 2:
            if self.structures(UnitTypeId.BUNKER).ready.amount == 1:
                #print("Sent Marines")
                global sendMarinesToBunker
                # if isStartLocationInTop:
                #     PointToBunker = Point2((34.5,108.5))
                # else:
                #     PointToBunker = Point2((99.5,23.5))
                for bunker in self.structures(UnitTypeId.BUNKER):
                    marinesInRadius = [
                        reaper for reaper in self.units(UnitTypeId.MARINE)
                        if reaper.distance_to(bunker) < 30]
                
                    if len(marinesInRadius)>=4:
                        for marine in marinesInRadius:
                            if marine.is_idle and bunker.is_ready and bunker.cargo_used < bunker.cargo_max:
                                bunker(AbilityId.LOAD_BUNKER, marine)
            

            # Trénování jednotky REAPER
            # Pouze, má-li bot postavené Barracks a může si jednotku dovolit
            if self.supply_workers >= 20 and self.structures(UnitTypeId.BARRACKS) and self.can_afford(UnitTypeId.REAPER):
                # Každá budova Barracks trénuje v jeden čas pouze jednu jednotku (úspora zdrojů)
                # mainBarrack = self.structures(UnitTypeId.BARRACKS)[0]
                # proxyBarrack= self.structures(UnitTypeId.BARRACKS)[1]
                
                for barrack in self.structures(UnitTypeId.BARRACKS).idle:
                    # print(barrack.position)
                    # if barrack.position == Point2((61.5,98.5)) or barrack.position == Point2((72.5,33.5)):
                    #     barrack.train(UnitTypeId.MARINE)
                    # if barrack.position == Point2((105.5,41.5))or barrack.position == Point2((27.5,91.5)):
                    #     barrack.train(UnitTypeId.REAPER)  
                    idle_reaper = self.units(UnitTypeId.REAPER) 
                    global reaperCreated  
                    if reaperCreated == False:
                        barrack.train(UnitTypeId.REAPER)
                    if idle_reaper.amount >=4:
                        reaperCreated = True
                        if barrack.position == Point2((105.5,41.5))or barrack.position == Point2((27.5,91.5)):
                            barrack.train(UnitTypeId.REAPER)
                        else:
                            barrack.train(UnitTypeId.MARINE)
                    if(reaperCreated == True):
                        if barrack.position == Point2((105.5,41.5))or barrack.position == Point2((27.5,91.5)):
                            barrack.train(UnitTypeId.REAPER)
                        else:
                            barrack.train(UnitTypeId.MARINE)
                

            # Build second Supply Depot,
            if self.supply_workers >= 20 and self.structures(UnitTypeId.SUPPLYDEPOT).amount == 1 and not self.already_pending(UnitTypeId.SUPPLYDEPOT):
                if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                    worker_unit = self.workers[0]
                    if worker_unit is not None:                        
                        if isStartLocationInTop:
                            worker_unit.build(UnitTypeId.SUPPLYDEPOT, Point3((61,96,10)))                                       
                        else:
                            worker_unit.build(UnitTypeId.SUPPLYDEPOT, Point3((70,33,10)))

            # morph commandcenter to orbitalcommand
            if self.structures(UnitTypeId.BARRACKS).amount > 0 and self.can_afford(UnitTypeId.ORBITALCOMMAND): # check if orbital is affordable
                for cc in self.structures(UnitTypeId.COMMANDCENTER).idle: # .idle filters idle command centers
                    cc(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND)

            # Postav Supply Depot, jestliže zbývá méně než 6 supply a je využito více než 13
            if self.supply_left < 5 and self.supply_used >= 21 and self.supply_cap < 39 and not self.already_pending(UnitTypeId.SUPPLYDEPOT):
                    # Budova bude postavena poblíž Command Center směrem ke středu mapy
                    # SCV pro stavbu bude vybráno automaticky viz dokumentace
                await self.build(
                    UnitTypeId.SUPPLYDEPOT,
                    near=command_center.position.towards(self.game_info.map_center, 8))
            
            if self.supply_left < 10 and self.supply_cap >= 39 and not self.already_pending(UnitTypeId.SUPPLYDEPOT):
                    # Budova bude postavena poblíž Command Center směrem ke středu mapy
                    # SCV pro stavbu bude vybráno automaticky viz dokumentace
                await self.build(
                    UnitTypeId.SUPPLYDEPOT,
                    near=command_center.position.towards(self.game_info.map_center, 8))
                
            # Build third Barracks
            if self.supply_workers >= 20 and self.structures(UnitTypeId.BARRACKS).amount == 2 and makingSecondBarracks == True:
                print("ThirdBarrack")
                if self.can_afford(UnitTypeId.BARRACKS):
                    await self.build(
                        UnitTypeId.BARRACKS,
                        near=command_center.position.towards(self.game_info.map_center, 8))
                    # worker_unit = self.workers[0]
                    # if worker_unit is not None:                        
                    #     if isStartLocationInTop:
                    #         worker_unit.build(UnitTypeId.BARRACKS, Point3((58,104,10)))                                         
                    #     else:
                    #         worker_unit.build(UnitTypeId.BARRACKS, Point3((73,27,10)))

            if self.minerals > 450 and makingSecondBarracks == True and self.structures(UnitTypeId.BARRACKS).amount <= 6:
                if self.can_afford(UnitTypeId.BARRACKS):                      
                    await self.build(
                        UnitTypeId.BARRACKS,
                        near=command_center.position.towards(self.game_info.map_center, 8))
            
            # for depo in self.structures(UnitTypeId.SUPPLYDEPOT).ready:
            # # Check if the ability is available
            #     if self.can_afford(AbilityId.MORPH_SUPPLYDEPOT_LOWER, depo):
            #         # Use the ability on the Supply Depot
            #         self.do(depo(AbilityId.MORPH_SUPPLYDEPOT_LOWER))

            # Útok s jednotkou Marine
            # Má-li bot více než 15 volných jednotek Marine, zaútočí na náhodnou nepřátelskou budovu nebo se přesune na jeho startovní pozici
            idle_marines = self.units(UnitTypeId.MARINE).idle
            if idle_marines.amount > 20:
                target = self.enemy_structures.random_or(
                    self.enemy_start_locations[0]).position
                for marine in idle_marines:
                    marine.attack(target)
            

            for depot in self.structures(UnitTypeId.SUPPLYDEPOT).ready:
                self.do(depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER))
                # if depot.position == Point2((64,99)) or depot.position == Point2((73,36)):
                #     self.do(depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER))                
            

            if isStartLocationInTop:
                ReaperPoint1 = Point2((101,38))                                             
            else:
                ReaperPoint1 = Point2((30,95))

            
            if isStartLocationInTop:
                ReaperPoint2 = Point2((100,27))                                             
            else:
                ReaperPoint2 = Point2((35,105))

            reapers_in_radius1 = [
            reaper for reaper in self.units(UnitTypeId.REAPER)
            if reaper.distance_to(ReaperPoint1) < 2]

            reaper_count1 = len(reapers_in_radius1)

            reapers_in_radius2 = [
            reaper for reaper in self.units(UnitTypeId.REAPER)
            if reaper.distance_to(ReaperPoint2) < 2]

            reaper_count2 = len(reapers_in_radius2)

            global reapersOnPosition1
            global reapersOnPosition2

            if reaper_count1<4 and reapersOnPosition1==False:
                for r in self.units(UnitTypeId.REAPER): 
                    r.move(ReaperPoint1)
            elif reapersOnPosition1==False:
                for r in self.units(UnitTypeId.REAPER):
                    if isStartLocationInTop:
                        r.move(Point2((100,27)))                                             
                    else:
                        r.move(Point2((35,105)))
                reapersOnPosition1 = True  
            if  reapersOnPosition1 == True and reaper_count2>3:
                reapersOnPosition2=True  
            
            global havingResearchBay

            if self.structures(UnitTypeId.BARRACKS).amount > 5 and havingResearchBay == False:
                if self.can_afford(UnitTypeId.ENGINEERINGBAY):
                    havingResearchBay = True
                    await self.build(
                    UnitTypeId.ENGINEERINGBAY,
                    near=command_center.position.towards(self.game_info.map_center, 8)) 
                    

            engineering_bays = self.structures(UnitTypeId.ENGINEERINGBAY).ready

            if engineering_bays.exists:
                engineering_bay = engineering_bays.first
                # Upgrade to Infantry Weapons Level 1 if possible
                if engineering_bay.is_idle and self.can_afford(AbilityId.ENGINEERINGBAYRESEARCH_TERRANINFANTRYWEAPONSLEVEL1):
                    self.do(engineering_bay(AbilityId.ENGINEERINGBAYRESEARCH_TERRANINFANTRYWEAPONSLEVEL1))

                if engineering_bay.is_idle and self.can_afford(AbilityId.ENGINEERINGBAYRESEARCH_TERRANINFANTRYARMORLEVEL1):
                    self.do(engineering_bay(AbilityId.ENGINEERINGBAYRESEARCH_TERRANINFANTRYARMORLEVEL1))

            

            # Upgrade to Infantry Weapons Level 2 if possible
            # if self.can_afford(UpgradeId.TERRANINFANTRYARMORSLEVEL1) and engineering_bay.is_idle:
            #     self.do(engineering_bay(UpgradeId.TERRANINFANTRYARMORSLEVEL1))           

            # reaper micro
            if reapersOnPosition2 == True:                    
                for r in self.units(UnitTypeId.REAPER):               

                    # move to range 15 of closest unit if reaper is below 20 hp and not regenerating
                    enemyThreatsClose = self.enemy_units.filter(lambda x: x.can_attack_ground).closer_than(15, r) # threats that can attack the reaper
                    if r.health_percentage < 2/5 and enemyThreatsClose.exists:
                        retreatPoints = self.neighbors8(r.position, distance=2) | self.neighbors8(r.position, distance=4)
                        # filter points that are pathable
                        retreatPoints = {x for x in retreatPoints if self.in_pathing_grid(x)}
                        if retreatPoints:
                            closestEnemy = enemyThreatsClose.closest_to(r)
                            retreatPoint = closestEnemy.position.furthest(retreatPoints)
                            r.move(retreatPoint)
                            continue # continue for loop, dont execute any of the following

                    # reaper is ready to attack, shoot nearest ground unit
                    enemyGroundUnits = self.enemy_units.not_flying.closer_than(5, r) # hardcoded attackrange of 5
                    if r.weapon_cooldown == 0 and enemyGroundUnits.exists:
                        enemyGroundUnits = enemyGroundUnits.sorted(lambda x: x.distance_to(r))
                        closestEnemy = enemyGroundUnits[0]
                        r.attack(closestEnemy)
                        continue # continue for loop, dont execute any of the following
                
                    # attack is on cooldown, check if grenade is on cooldown, if not then throw it to furthest enemy in range 5
                    reaperGrenadeRange = self._game_data.abilities[AbilityId.KD8CHARGE_KD8CHARGE.value]._proto.cast_range
                    enemyGroundUnitsInGrenadeRange = self.enemy_units.not_structure.not_flying.exclude_type([UnitTypeId.LARVA, UnitTypeId.EGG]).closer_than(reaperGrenadeRange, r)
                    if enemyGroundUnitsInGrenadeRange.exists and (r.is_attacking or r.is_moving):
                        # if AbilityId.KD8CHARGE_KD8CHARGE in abilities, we check that to see if the reaper grenade is off cooldown
                        abilities = (await self.get_available_abilities(r))
                        enemyGroundUnitsInGrenadeRange = enemyGroundUnitsInGrenadeRange.sorted(lambda x: x.distance_to(r), reverse=True)
                        furthestEnemy = None
                        for enemy in enemyGroundUnitsInGrenadeRange:
                            if await self.can_cast(r, AbilityId.KD8CHARGE_KD8CHARGE, enemy, cached_abilities_of_unit=abilities):
                                furthestEnemy = enemy
                                break
                        if furthestEnemy:
                            r(AbilityId.KD8CHARGE_KD8CHARGE, furthestEnemy)
                            continue # continue for loop, don't execute any of the following

                    # move towards to max unit range if enemy is closer than 4
                    enemyThreatsVeryClose = self.enemy_units.filter(lambda x: x.can_attack_ground).closer_than(4.5, r) # hardcoded attackrange minus 0.5
                    # threats that can attack the reaper
                    if r.weapon_cooldown != 0 and enemyThreatsVeryClose.exists:
                        retreatPoints = self.neighbors8(r.position, distance=2) | self.neighbors8(r.position, distance=4)               
                        # filter points that are pathable by a reaper
                        retreatPoints = {x for x in retreatPoints if self.in_pathing_grid(x)}
                        if retreatPoints:
                            closestEnemy = enemyThreatsVeryClose.closest_to(r)
                            retreatPoint = max(retreatPoints, key=lambda x: x.distance_to(closestEnemy) - x.distance_to(r))
                            # retreatPoint = closestEnemy.position.furthest(retreatPoints)
                            r.move(retreatPoint)
                            continue # continue for loop, don't execute any of the following

                    # # move to nearest enemy ground unit/building because no enemy unit is closer than 5
                    allEnemyGroundUnits = self.enemy_units
                    if allEnemyGroundUnits.exists:
                        closestEnemy = allEnemyGroundUnits.closest_to(r)
                        r.move(closestEnemy)
                        continue # continue for loop, don't execute any of the following

                    # move to random enemy start location if no enemy buildings have been seen
                    #r.move(random.choice(self.enemy_start_locations))

            # manage orbital energy and drop mules
            for oc in self.structures(UnitTypeId.ORBITALCOMMAND).filter(lambda x: x.energy >= 50):
                mfs = self.mineral_field.closer_than(10, oc)
                if mfs:
                    mf = max(mfs, key=lambda x:x.mineral_contents)
                    oc(AbilityId.CALLDOWNMULE_CALLDOWNMULE, mf)
                

            




            # if self.supply_workers >= 16 and self.structures(UnitTypeId.BARRACKS).amount == 0:
            #     if self.can_afford(UnitTypeId.BARRACKS):
            #         worker_unit = self.workers[0]
            #         if worker_unit is not None:                        
            #             if isStartLocationInTop:
            #                 worker_unit.build(UnitTypeId.BARRACKS, Point3((61,98,10)))                                         
            #             else:
            #                 worker_unit.build(UnitTypeId.BARRACKS, Point3((72,33,10)))
    
    def neighbors4(self, position, distance=1):
        p = position
        d = distance
        return {
            Point2((p.x - d, p.y)),
            Point2((p.x + d, p.y)),
            Point2((p.x, p.y - d)),
            Point2((p.x, p.y + d)),
        }
    
    # stolen and modified from position.py
    def neighbors8(self, position, distance=1):
        p = position
        d = distance
        return self.neighbors4(position, distance) | {
            Point2((p.x - d, p.y - d)),
            Point2((p.x - d, p.y + d)),
            Point2((p.x + d, p.y - d)),
            Point2((p.x + d, p.y + d)),
        }

    #worker_unit.build(UnitTypeId.SUPPLYDEPOT, Point3((61,96,10)))
                              
                            # worker_unit.build(UnitTypeId.BARRACKS, Point3((105,41,10)))   

                            # worker_unit.build(UnitTypeId.SUPPLYDEPOT, Point3((70,33,10)))
                            
                            # worker_unit.build(UnitTypeId.BARRACKS, Point3((27,91,10)))   

                    # await self.build(
                    #     UnitTypeId.SUPPLYDEPOT,
                    #     near=command_center.position.towards(self.game_info.map_center, 20)
                    #     )

            # # Postav Supply Depot, jestliže zbývá méně než 6 supply a je využito více než 13
            # if self.supply_left < 6 and self.supply_used >= 14 and not self.already_pending(UnitTypeId.SUPPLYDEPOT):
            #     if self.can_afford(UnitTypeId.SUPPLYDEPOT):
            #         # Budova bude postavena poblíž Command Center směrem ke středu mapy
            #         # SCV pro stavbu bude vybráno automaticky viz dokumentace
            #         await self.build(
            #             UnitTypeId.SUPPLYDEPOT,
            #             near=command_center.position.towards(self.game_info.map_center, 8))

            # # Stavba Barracks
            # # Bot staví tak dlouho, dokud si může dovolit stavět Barracks a jejich počet je menší než 6
            # if self.tech_requirement_progress(UnitTypeId.BARRACKS) == 1:
            #     # Je jich méně než 6 nebo se již nějaké nestaví
            #     if self.structures(UnitTypeId.BARRACKS).amount < 6:
            #         if self.can_afford(UnitTypeId.BARRACKS) and not self.already_pending(UnitTypeId.BARRACKS):
            #             await self.build(
            #                 UnitTypeId.BARRACKS,
            #                 near=command_center.position.towards(self.game_info.map_center, 8))

            # # Trénování jednotky Marine
            # # Pouze, má-li bot postavené Barracks a může si jednotku dovolit
            # if self.structures(UnitTypeId.BARRACKS) and self.can_afford(UnitTypeId.MARINE):
            #     # Každá budova Barracks trénuje v jeden čas pouze jednu jednotku (úspora zdrojů)
            #     for barrack in self.structures(UnitTypeId.BARRACKS).idle:
            #         barrack.train(UnitTypeId.MARINE)

            # # Útok s jednotkou Marine
            # # Má-li bot více než 15 volných jednotek Marine, zaútočí na náhodnou nepřátelskou budovu nebo se přesune na jeho startovní pozici
            # idle_marines = self.units(UnitTypeId.MARINE).idle
            # if idle_marines.amount > 15:
            #     target = self.enemy_structures.random_or(
            #         self.enemy_start_locations[0]).position
            #     for marine in idle_marines:
            #         marine.attack(target)

            # # Zbylý SCV bot pošle těžit minerály nejblíže Command Center
            # for scv in self.workers.idle:
            #     scv.gather(self.mineral_field.closest_to(command_center))


            
                
run_game(maps.get("sc2-ai-cup-2022"), [
    Bot(Race.Terran, WorkerRushBot()),
    Computer(Race.Terran, Difficulty.Hard)
], realtime=False)