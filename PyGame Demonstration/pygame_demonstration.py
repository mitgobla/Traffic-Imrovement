import itertools
import os
import random
import sys
import traceback
import time

import pygame


class Environment:

    def __init__(self):
        self.vehicles = {
            "northbound": [],
            "southbound": []
        }

        self.traffic_lights = {
            "northbound": [],
            "southbound": []
        }

    def remove_vehicle(self, direction):
        del self.vehicles[direction][0]
        # print(direction, ":", len(self.vehicles[direction]))

    def add_vehicle(self, vehicle, direction):
        data = dict(name=vehicle.name, vehicle_obj=vehicle, direction=direction, rect=vehicle.rect)
        self.vehicles[direction].append(data)

    def add_traffic_light(self, light, direction):
        self.traffic_lights[direction].append(light)


class TrafficLight(pygame.sprite.DirtySprite):

    def __init__(self, env: Environment, group: pygame.sprite.Group, direction: str):
        pygame.sprite.DirtySprite.__init__(self)

        self.image = pygame.Surface([16, 16])
        self.image.fill((0, 0, 0))
        # self.image.set_colorkey((0, 0, 0))
        self.colours = itertools.cycle(
            [(255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 255, 0)])
        # self.colours = itertools.cycle(
        #     [(255, 0, 0), (255, 0, 0), (255, 0, 0), (255, 0, 0)])
        self.current_colour = next(self.colours)

        self.frame = 0

        self.direction = direction
        if self.direction == "northbound":
            self.current_colour = next(self.colours)
            self.current_colour = next(self.colours)
            self.rect = pygame.draw.ellipse(
                self.image, self.current_colour, [0, 0, 16, 16])
            self.rect = self.rect.move(48, 304)
        elif self.direction == "southbound":
            self.rect = pygame.draw.ellipse(
                self.image, self.current_colour, [0, 0, 16, 16])
            self.rect = self.rect.move(96, 224)

    def update(self):
        self.frame += 1
        if self.frame == 256:
            self.current_colour = next(self.colours)
            # self.image.fill(self.current_colour, rect=self.rect)
            self.rect = pygame.draw.ellipse(
                self.image, self.current_colour, [0, 0, 16, 16])
            if self.direction == "northbound":
                self.rect = self.rect.move(48, 304)
            elif self.direction == "southbound":
                self.rect = self.rect.move(96, 224)
            self.frame = 0


class Vehicle(pygame.sprite.DirtySprite):

    def __init__(self, env: Environment, group: pygame.sprite.Group, name, direction: str):
        pygame.sprite.DirtySprite.__init__(self)

        self.env = env
        self.group = group
        self.name = str(name)

        self.image = pygame.Surface((16, 16))
        self.colour = random.choice([(50, 50,  random.uniform(
            100, 255)), (50, random.uniform(100, 255), 50), (random.uniform(100, 255), 50, 50)])
        self.image.fill((0, 0, 0))
        self.image.set_colorkey((0, 0, 0))

        self.dirty = 1
        self.direction = direction
        self.stopped = False

        if self.direction == "northbound":
            # self.rect = pygame.draw.rect(self.image, self.colour, [64, 512, 16, 16])
            self.rect = pygame.draw.ellipse(
                self.image, self.colour, [0, 0, 16, 16])
            if len(self.env.vehicles[self.direction]) <= 11:
                self.rect = self.rect.move(64, 512)
            else:
                self.rect = self.rect.move(64, (514 + 16*(len(self.env.vehicles[self.direction])-10)))
        elif self.direction == "southbound":
            # self.rect = pygame.draw.rect(self.image, self.colour, [80, 0, 16, 16])
            self.rect = pygame.draw.ellipse(
                self.image, self.colour, [0, 0, 16, 16])
            if len(self.env.vehicles[self.direction]) <= 14:
                self.rect = self.rect.move(80, 0)
            else:
                self.rect = self.rect.move(80, (-2 - 16*(len(self.env.vehicles[self.direction])-12)))
        # self.image.fill(self.colour, rect=self.rect)

    def vehicle_property(self):
        return dict(rect=self.rect, name=self.name, direction=self.direction)

    def update(self):
        self.move()
        if (self.rect.y < -16 and self.direction == "northbound") or (self.rect.y > 576 and self.direction == "southbound"):
            self.group.remove(self)
            self.dirty = 1

    def move(self):
        if self.direction == "northbound":

            try:
                vehicle_pos = self.env.vehicles["northbound"].index(next(item for item in self.env.vehicles["northbound"] if item["name"] == self.name))*16
                if self.rect.y == (320 + vehicle_pos) and self.env.traffic_lights["northbound"][0].current_colour == (255, 0, 0):
                    self.stopped = True
                elif self.rect.y >= (320 + vehicle_pos) and self.env.traffic_lights["northbound"][0].current_colour == (0, 255, 0):
                    self.stopped = False
            except StopIteration:
                pass

            if self.rect.y == 320 and self.env.traffic_lights["northbound"][0].current_colour == (0, 255, 0):
                self.rect.move_ip(16, -2)
                self.env.remove_vehicle(self.direction)
                self.stopped = False
            elif self.rect.y == 320:
                self.stopped = True

            if self.rect.y == 224:
                self.rect.move_ip(-16, 0)
                self.stopped = False

            if self.rect.y > 320:
                if not self.stopped:
                    self.rect.move_ip(0, -2)
                    self.stopped = False

            if self.rect.y < 320 and not self.stopped:
                self.rect.move_ip(0, -2)
                self.stopped = False

            self.dirty = 1

        elif self.direction == "southbound":

            try:
                vehicle_pos = self.env.vehicles["southbound"].index(next(item for item in self.env.vehicles["southbound"] if item["name"] == self.name))*16
                if self.rect.y <= (208 - vehicle_pos) and self.env.traffic_lights["southbound"][0].current_colour == (0, 255, 0):
                    self.stopped = False
                elif self.rect.y == (208 - vehicle_pos) and self.env.traffic_lights["southbound"][0].current_colour == (255, 0, 0):
                    self.stopped = True
            except StopIteration:
                pass

            if self.rect.y == 208 and self.env.traffic_lights["southbound"][0].current_colour == (0, 255, 0):
                self.stopped = False
                self.env.remove_vehicle(self.direction)
                self.rect.move_ip(0, 2)
            elif self.rect.y == 208:
                self.stopped = True

            if self.rect.y < 208 and not self.stopped:
                self.rect.move_ip(0, 2)
                self.stopped = False

            if self.rect.y > 208:
                self.rect.move_ip(0, 2)
                self.stopped = False

            self.dirty = 1


class SimulationGame:

    def __init__(self):
        self.surface = pygame.display.set_mode([512, 512])
        self.running = True

        self.vehicle_group = pygame.sprite.Group()
        self.traffic_light_group = pygame.sprite.Group()

        self.clock = pygame.time.Clock()

        self.env = Environment()

        self.northbound_light = TrafficLight(
            self.env, self.traffic_light_group, "northbound")
        self.southbound_light = TrafficLight(
            self.env, self.traffic_light_group, "southbound")

        self.traffic_light_group.add(
            self.northbound_light, self.southbound_light)
        self.env.add_traffic_light(self.northbound_light, "northbound")
        self.env.add_traffic_light(self.southbound_light, "southbound")

        self.secure_random = random.SystemRandom()

    def run(self):
        self.surface.fill((100, 230, 100))
        pygame.display.flip()

        can_spawn_northbound = 0
        can_spawn_southbound = 0

        while self.running:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.running = False

            if random.choice(["northbound", "southbound"]) == "northbound":
                if random.random() < 0.05 and can_spawn_northbound == 0:
                    vehicle = Vehicle(self.env, self.vehicle_group,
                                      self.secure_random.random(), "northbound")
                    self.vehicle_group.add(vehicle)
                    self.env.add_vehicle(vehicle, "northbound")
                    can_spawn_northbound = 16
            else:
                if random.random() < 0.05 and can_spawn_southbound == 0:
                    vehicle = Vehicle(self.env, self.vehicle_group,
                                      self.secure_random.random(), "southbound")
                    self.vehicle_group.add(vehicle)
                    self.env.add_vehicle(vehicle, "southbound")
                    can_spawn_southbound = 16

            if can_spawn_northbound:
                can_spawn_northbound -= 1

            if can_spawn_southbound:
                can_spawn_southbound -= 1

            self.vehicle_group.update()
            self.traffic_light_group.update()

            pygame.draw.rect(self.surface, (20, 20, 20), [64, 0, 32, 512])
            pygame.draw.rect(self.surface, (120, 120, 20), [64, 240, 16, 64])
            self.vehicle_group.draw(self.surface)
            self.traffic_light_group.draw(self.surface)
            pygame.draw.line(self.surface, (255, 255, 255),
                             [80, 0], [80, 512], 1)
            pygame.draw.rect(self.surface, (60, 20, 20), [60, 0, 40, 16])
            pygame.draw.rect(self.surface, (60, 20, 20), [60, 496, 40, 16])
            # pygame.display.update(rects)
            pygame.display.flip()


GAME = SimulationGame()

if __name__ == "__main__":
    GAME.run()
