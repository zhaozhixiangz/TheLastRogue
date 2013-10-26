import random
import geometry as geo
import rng
import direction
from actor import Actor


class ChasePlayerActor(Actor):
    """
    Standard Monster AI will chase the player.
    """
    def __init__(self):
        super(ChasePlayerActor, self).__init__()


class MonsterActor(Actor):
    """
    A set of methods useful to compose an AI Actor.
    """
    def __init__(self):
        super(MonsterActor, self).__init__()

    def try_step_random_direction(self):
        """
        Tries to make the entity step to a random direction.
        If the step succeeds True is return otherwise False.
        """
        random_direction = random.sample(list(direction.DIRECTIONS), 1)[0]
        new_position = geo.add_2d(self.parent.position.value, random_direction)
        return self.parent.mover.try_move_or_bump(new_position)

    def get_entity_sharing_my_position(self):
        """
        Sometimes two entities can share a tile this method
        returns the other entity if this is currently the case.
        If the number of entities of this tile is neither 1 or 2
        raise an exception as this is an invalid state.
        """
        dungeon_level = self.parent.dungeon_level.value
        position = self.parent.position.value
        entities_on_my_tile = (dungeon_level.get_tile(position).get_entities())
        if(len(entities_on_my_tile) == 1):
            return None
        if(len(entities_on_my_tile) != 2):
            raise
        return next(entity for entity in entities_on_my_tile
                    if not entity is self)

    def try_to_escape_slime(self):
        """
        Assumes the entity is trapped by a slime,
        if escape is successful return true otherwise false.
        """
        slime = self.get_entity_sharing_my_position()
        if not slime is None:
            self.parent.attacker.hit(slime)
        escape_successful = rng.coin_flip() and rng.coin_flip()
        return escape_successful

    def get_seen_entities(self):
        """
        Gets all entities seen by this entity not including self.
        """
        seen_entities = []
        for entity in self.parent.dungeon_level.value.entities:
            if self.parent.dungeon_mask.can_see_point(entity.position):
                seen_entities.append(entity)
        return [entity for entity in seen_entities if not entity is self]

    def get_seen_entities_closest_first(self):
        """
        Gets all seen entities sorted on distance from self not including self.
        """
        return sorted(self.get_seen_entities(),
                      key=lambda entity:
                      geo.chess_distance(self.parent.position.value,
                                         entity.position.value))

    def get_closest_seen_entity(self):
        """
        Gets the closest of all seen entities not including self.
        """
        closest_seen_entities = self.get_seen_entities_closest_first()
        if(len(closest_seen_entities) < 1):
            return None
        return closest_seen_entities[0]


class StepRandomDirectonActor(MonsterActor):
    """
    Standard Monster AI will chase the player.
    """
    def __init__(self):
        super(StepRandomDirectonActor, self).__init__()

    def act(self):
        self.try_step_random_direction()
        return self.parent.movement_speed.value