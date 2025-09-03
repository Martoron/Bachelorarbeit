import random
from superAttack import extract_multiplier_from_text

# Super Attack multipliers for normal and EZA cards
boss_super_attack_multipliers = {
    "Low": 130,
    "Damage": 170,
    "Huge": 200,
    "Destructive": 200,
    "Extreme": 220,
    "Mass": 220,
    "Supreme": 250,
    "Immense": 280,
    "Mega-Colossal": 300,
    "Colossal": 350,
}

class Boss:
    def __init__(self, name, image, imageURL, boss_class, boss_type, hp, attack, defense, damage_reduction, atk_per_turn, sa_percent, sa_multi, sa_effect, sa_atk, sa_per_turn, cooldown, passive, immunities, buffs=None, debuffs=None):
        self.name = name
        self.image = image
        self.imageURL = imageURL
        self.boss_class = boss_class  # Super or Extreme
        self.boss_type = boss_type  # Type (TEQ, AGL, etc.)
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.damage_reduction = damage_reduction  # Convert percentage to decimal
        self.atk_per_turn = atk_per_turn  # Number of attacks per turn
        self.sa_percent = sa_percent
        self.sa_multi = sa_multi
        self.sa_effect = sa_effect  # Super attack effect (e.g., ATK +50%)
        self.sa_atk = sa_atk  # Super attack base damage
        self.sa_per_turn = sa_per_turn  # Super attacks per turn (e.g., 2 super attacks)
        self.cooldown = cooldown  # Turns before next SA
        self.passive = passive
        self.immunities = immunities  # Dictionary for immunities like stun, seal, etc.
        self.sa_turn_counter = 0  # Tracks when a super attack cooldown is applied
        self.turn_counter = 0  # Track turns for overall cooldown
        self.buffs = buffs or {}
        self.debuffs = debuffs or {}

        self.passives = {}
        self.max_hp = hp  # Store max HP for healing calculations

    def calculate_effective_attack(self, is_super=False):
        """Calculate boss's effective attack after applying buffs and debuffs."""
        buff_value = 0
        debuff_value = 0
        if is_super:
            if self.buffs.get("atk_buff"):
                for buff in self.buffs["atk_buff"]:
                    buff_value += buff.get('value', 0)
            if self.debuffs.get("atk_debuff"):
                for debuff in self.debuffs["atk_debuff"]:
                    debuff_value += debuff.get('value', 0)
            effective_attack = self.attack * (self.sa_multi + buff_value - debuff_value)
            print(f"Bosses effective attack: BaseAttack: {self.attack} * (SA Multi: {self.sa_multi} + SA ATK Buff: {buff_value}) - SA ATK Debuff: {debuff_value} = {effective_attack}")
        else:
            effective_attack = self.attack * (1 + buff_value)
            print(f"Bosses effective attack: BaseAttack: {self.attack} * Normal ATK Buff: {1 + buff_value} = {effective_attack:.0f}")
        return max(0, effective_attack)  # Ensure non-negative attack value
    
    def take_damage(self, damage):
        """Boss takes damage and applies damage reduction."""
        effective_damage = damage * (1 - self.damage_reduction)
        self.current_hp -= effective_damage
        return max(0, effective_damage)  # Ensure non-negative damage dealt

    def is_alive(self):
        """Check if the boss is still alive."""
        return self.current_hp > 0
    
    def get_boss_type(self):
        return self.boss_type
    
    def get_boss_class(self):
        return self.boss(self)

    def apply_immunity(self, effect_type):
        """Check if the boss is immune to a certain effect (stun, seal, etc.)."""
        return self.immunities.get(effect_type, 0) == 1
    
    def get_boss_sa_effect(self):
        """Apply the boss's Super Attack effect."""
        # Apply the Super Attack effect (e.g., ATK +50%)
        atk_buff, atk_debuff, def_buff, def_debuff = 0, 0, 0, 0
        if "ATK +" in self.sa_effect:
            atk_buff = float(self.sa_effect.split("+")[1].strip("%")) / 100
        if "ATK -" in self.sa_effect:
            atk_debuff = float(self.sa_effect.split("-")[1].strip("%")) / 100
        if "DEF +" in self.sa_effect:
            def_buff = float(self.sa_effect.split("+")[1].strip("%")) / 100
        if "DEF -" in self.sa_effect:
            def_debuff = float(self.sa_effect.split("-")[1].strip("%")) / 100
        
        return atk_buff, atk_debuff, def_buff, def_debuff


# Determine SA multiplier for Boss
def get_boss_sa_multipliers(sa_text):
    # Search for the super attack keyword (e.g., 'Colossal', 'Supreme')
    multiplier_key = extract_multiplier_from_text(sa_text)
    
    # Use the appropriate multiplier dictionary
    if multiplier_key:
        print(f"boss sa multiplier:{boss_super_attack_multipliers.get(multiplier_key, 100) / 100.0}")
        return boss_super_attack_multipliers.get(multiplier_key, 100) / 100.0
    else:
        # Default value if no match is found
        return 1.0
    

