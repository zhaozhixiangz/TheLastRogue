import random
import entityeffect
import rng
from compositecore import Leaf
from equipment import EquipmentSlots


class Attacker(Leaf):
    """
    Component for attacking and checking if an attacking is legal.
    """
    def __init__(self, melee_damage_modifier=1.0, rock_damage_modifier=1.0):
        super(Attacker, self).__init__()
        self.component_type = "attacker"
        self.melee_damage_modifier = melee_damage_modifier
        self.rock_damage_modifier = rock_damage_modifier

    @property
    def throw_rock_mean_damage(self):
        return int(2 * self.parent.strength.value * self.rock_damage_modifier / 3)

    @property
    def throw_rock_damage_variance(self):
        return int(self.throw_rock_mean_damage / 2)

    def try_hit(self, position):
        """
        Tries to hit an entity at a position.

        Returns False if there is no entity
        there or the entity is of the same faction.
        """
        entity = (self.parent.dungeon_level.value.
                  get_tile(position).get_first_entity())
        if(entity is None or
           entity.faction.value == self.parent.faction.value):
            return False
        self.hit(entity)
        return True

    def throw_rock_damage_entity(self, target_entity):
        """
        Makes entity to hit the target entity with the force of a thrown rock.
        """
        damage_types = [DamageTypes.BLUNT, DamageTypes.PHYSICAL]
        thrown_damage = Damage(self.throw_rock_mean_damage, self.throw_rock_damage_variance,
                               damage_types, self.parent.hit.value)
        thrown_damage.damage_entity(self.parent, target_entity)

    def hit(self, target_entity):
        """
        Causes the entity to hit the target entity.
        """
        equipment = self.parent.equipment
        if equipment.slot_is_equiped(EquipmentSlots.MELEE_WEAPON):
            weapon = self.parent.equipment.get(EquipmentSlots.MELEE_WEAPON)
            weapon.damage_provider.damage_entity(self.parent, target_entity)
        else:
            self._unarmed_damage().damage_entity(self.parent, target_entity)

    def _unarmed_damage(self):
        """
        Calculates an instance of damage
        caused by an unarmed hit by the entity.
        """
        damage_types = [DamageTypes.BLUNT, DamageTypes.PHYSICAL]
        damage_strength = int(self.parent.strength.value * self.melee_damage_modifier)
        return Damage(1 + damage_strength / 2, damage_strength / 4, damage_types,
                      self.parent.hit.value)


class Dodger(Leaf):
    """
    Component for calculating dodge.
    """
    def __init__(self):
        super(Dodger, self).__init__()
        self.component_type = "dodger"

    def is_a_hit(self, hit):
        """
        Returns true if it is a hit, false otherwise.
        """
        return rng.stat_check(hit + 5, self.parent.evasion.value)


class DamageTypes(object):
    PHYSICAL = 0
    MAGIC = 1
    BLUNT = 2
    PIERCING = 3
    CUTTING = 4
    ACID = 5


class Damage(object):
    def __init__(self, damage, variance,
                 damage_types, hit, damage_multiplier=1):
        self.damage = damage
        self.variance = variance
        self.damage_multiplier = damage_multiplier
        self.damage_types = damage_types
        self.hit = hit

    def damage_entity(self, source_entity, target_entity, bonus_damage=0, bonus_hit=0):
        damage = rng.random_variance_no_negative(self.damage + bonus_damage, self.variance)
        damage_effect =\
            entityeffect.DamageEntityEffect(source_entity,
                                            damage * self.damage_multiplier,
                                            self.damage_types, self.hit + bonus_hit)
        target_entity.effect_queue.add(damage_effect)
