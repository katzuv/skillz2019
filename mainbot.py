from elf_kingdom import *
import math
# Game constants
CENTER = Location(1800, 3500) #default before calculation

setup_boolean = True  # prevent the setup from running more than once TODO: replace with a turn counter
# Constants
BUILD_THRESH = 100  # threshold where the elf will build in when trying to build a portal.
DEFENSE_PORTAL_DISTANCE = 2000  # the radius from the castle, in it all portals are defined as defence portals.
portals_lower = [Location(1200, 4600), Location(1800, 3500)]  # preset locations of portals when our color is orange
portals_upper = [Location(2500, 1500), Location(1800, 3500)]  # preset locations of portals when our color is blue
our_portals = []  # current preset locations (game reads our team color and assigns this to the correct array.

# Globals
IS_PURPLE_TEAM = False  # is our team on the top right corner (is our color purple)
elves_building = {}  # dict of the elves building a portal. used to govern mana usage and prevent elf overtasking.
                     # the key in the dictionary is the elf, its value is the location it wants to build at.


def setup(game):
    """
    Runs on the first turn of the match.

    :param game: the current game state.
    :type game: Game
    """
    global CENTER, IS_PURPLE_TEAM, setup_boolean
    CENTER = location_average(game.get_enemy_castle(), game.get_my_castle())
    IS_PURPLE_TEAM = game.get_my_castle().get_location().row > game.get_enemy_castle().get_location().row
    setup_boolean = False


def do_turn(game):
    """
    Makes the bot run a single turn.

    :param game: the current game state.
    :type game: Game
    """
    if setup_boolean:
        setup(game)

    handle_elves(game)  # Whether the elves should build
    portal_handling(game)  # Generating creatures
    fix_center_portal(game)  # fix the center portal if its broken TODO: change this temporary method


def handle_elves(game):
    """
    Make each elf build a portal.

    :param game: the current game state.
    :type game: Game
    """
    #TODO: This method is broken as heck
    if not game.get_my_living_elves():
        return
    portals = portals_upper if IS_PURPLE_TEAM else portals_lower
    if len(game.get_my_portals()) <= 1 or len(game.get_my_living_elves()) < 2:
        try:
            build_portal(game.get_my_living_elves()[0], portals[0])
            if len(game.get_my_portals()) <= 2:  # TODO: understand this
                build_portal(game.get_my_living_elves()[1], portals[1])
        except Exception as e:
            print(e)

    handle_builds()
    elf_attack_nearest_target(game)  # Elf attacking nearest important target


def handle_builds():
    """Uses the elves_building dictionary and moves each elf accordingly"""

    global elves_building, BUILD_THRESH
    for elf, loc in elves_building.items():
        print elf
        if elf is None:
            continue
        try:
            if elf.get_location().distance(loc) < BUILD_THRESH:
                print("Building portal")
                elf.build_portal()
                elves_building.pop(elf)
            else:
                elf.move_to(loc)
        except AttributeError:
            continue


def elf_attack_nearest_target(game):
    """
    Tell the elf to attack the nearest target (returned from 'nearest_target_for_elf')

    :param game: the current game state.
    :type game: Game
    """
    for elf in game.get_my_living_elves():
        print("cond: {}".format(elf not in elves_building and not elf.is_building))
        if elf not in elves_building and not elf.is_building:
            attack_object(game, elf, nearest_target_for_elf(game, elf))  # tells the elf to attack the nearest target


def fix_center_portal(game):
    """Run the build method on the cener portal if it is broken"""
    print game.get_my_living_elves()
    if not game.get_my_living_elves():
        return
    for portal in game.get_my_portals():
        print portal.get_location()
        if portal.get_location().distance(CENTER) <= BUILD_THRESH:
            print "Equals"
            return
    nearest_elf = min(game.get_my_living_elves(), key=lambda elf: elf.distance(CENTER))
    build_portal(nearest_elf, CENTER)


def nearest_target_for_elf(game, friendly_object):
    """
    Go through all important targets (enemy portals and enemy elves),
    and return the target which is closest to the friendly_object.

    :param game: the current game state.
    :param friendly_object: the center object which the method finds the closest target from (usually the attacking elf).
    :return: the closest target to the friendly_object
    """
    targets = game.get_enemy_portals() + game.get_enemy_living_elves()
    try:
        return min(targets, key=lambda target: friendly_object.distance(target))
    except ValueError:
        return


def is_portal_endangered(game, portal):
    """Return whether an enemy Elf is endangering a Portal."""
    return any(portal.distance(enemy_elf.get_location()) < game.elf_attack_range
               for enemy_elf in game.get_enemy_living_elves())


def portal_handling(game):
    """Decide what portals produce what creatures."""
    if elves_building and game.get_my_mana() < 120:
        return

    defense_portals = [portal for portal in game.get_my_portals() if
                       game.get_my_castle().distance(portal) < DEFENSE_PORTAL_DISTANCE]
    attack_portals = [portal for portal in game.get_my_portals() if portal not in defense_portals]

    for portal in game.get_my_portals():
        if is_portal_endangered(game, portal):
            portal.summon_ice_troll()

    for defense_portal in defense_portals:
        if defense_portal.can_summon_ice_troll():
            defense_portal.summon_ice_troll()
    for attack_portal in attack_portals:
        if attack_portal.can_summon_lava_giant():
            attack_portal.summon_lava_giant()


### METHODS ###
def build_portal(elf, loc):
    """Build a Portal."""
    global elves_building
    print("Moving to {}".format(loc))
    if elf not in elves_building:
        elves_building[elf] = loc


def attack_object(game, elf, obj):
    """Attack an object."""
    if not obj or not elf.is_alive() or elf in elves_building or elf.is_building:
        return
    if elf.get_location().distance(obj) < game.elf_attack_range:
        elf.attack(obj)
    else:
        elf.move_to(obj)


### UTILITIES ###
def location_average(l1, l2):
    """
    Return the average location of two points
    :param l1: first object
    :param l2: second object
    :return: the average between the location of both objects, as a Location class
    """
    return Location((l1.get_location().row + l2.get_location().row) / 2,
                    (l1.get_location().col + l2.get_location().col) / 2)
