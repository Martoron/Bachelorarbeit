from superAttack import extract_multiplier_from_text

# =============================================================================
# BOSS SUPER ATTACK MULTIPLIERS
# =============================================================================

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


# =============================================================================
# BOSS CLASS DEFINITION
# =============================================================================

class Boss:
    """
    Represents a boss enemy in Dokkan Battle with combat capabilities and attributes.
    
    Attributes:
        name (str): Boss name
        image (str): Image path/URL
        imageURL (str): Full image URL
        boss_class (str): Class (Super or Extreme)
        boss_type (str): Type (TEQ, AGL, PHY, INT, STR)
        hp (int): Base health points
        attack (int): Base attack stat
        defense (int): Base defense stat
        damage_reduction (float): Damage reduction percentage (0.0-1.0)
        atk_per_turn (int): Number of attacks per turn
        sa_percent (float): Chance to perform super attack
        sa_multi (float): Super attack multiplier
        sa_effect (str): Super attack effect description
        sa_atk (int): Super attack base damage
        sa_per_turn (int): Maximum super attacks per turn
        cooldown (int): Cooldown between super attacks
        passive (str): Passive skill description
        immunities (dict): Immunities to status effects
        buffs (dict): Active buffs
        debuffs (dict): Active debuffs
        passives (dict): Passive effects
        max_hp (int): Maximum health points
    """
    
    def __init__(self, name, image, imageURL, boss_class, boss_type, hp, attack, defense, 
                 damage_reduction, atk_per_turn, sa_percent, sa_multi, sa_effect, sa_atk, 
                 sa_per_turn, cooldown, passive, immunities, buffs=None, debuffs=None):
        """
        Initialize a Boss with all combat attributes and capabilities.
        
        Args:
            name (str): Boss name
            image (str): Image path
            imageURL (str): Full image URL
            boss_class (str): Class (Super or Extreme)
            boss_type (str): Type (TEQ, AGL, PHY, INT, STR)
            hp (int): Health points
            attack (int): Base attack stat
            defense (int): Base defense stat
            damage_reduction (float): Damage reduction percentage
            atk_per_turn (int): Attacks per turn
            sa_percent (float): Super attack chance
            sa_multi (float): Super attack multiplier
            sa_effect (str): Super attack effect description
            sa_atk (int): Super attack base damage
            sa_per_turn (int): Max super attacks per turn
            cooldown (int): Super attack cooldown
            passive (str): Passive skill description
            immunities (dict): Status effect immunities
            buffs (dict, optional): Active buffs. Defaults to None
            debuffs (dict, optional): Active debuffs. Defaults to None
        """
        # Basic attributes
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
        
        # Super attack attributes
        self.sa_percent = sa_percent
        self.sa_multi = sa_multi
        self.sa_effect = sa_effect  # Super attack effect (e.g., ATK +50%)
        self.sa_atk = sa_atk  # Super attack base damage
        self.sa_per_turn = sa_per_turn  # Super attacks per turn
        self.cooldown = cooldown  # Turns before next SA
        
        # Skills and immunities
        self.passive = passive
        self.immunities = immunities  # Dictionary for immunities like stun, seal, etc.
        
        # Combat state tracking
        self.sa_turn_counter = 0  # Tracks when a super attack cooldown is applied
        self.turn_counter = 0  # Track turns for overall cooldown
        self.buffs = buffs or {}
        self.debuffs = debuffs or {}
        self.passives = {}
        self.max_hp = hp  # Store max HP for healing calculations

    def calculate_effective_attack(self, is_super=False):
        """
        Calculate boss's effective attack after applying buffs and debuffs.
        
        Args:
            is_super (bool, optional): Whether this is a super attack. Defaults to False
            
        Returns:
            float: Effective attack value after all modifiers
        """
        buff_value = 0
        debuff_value = 0
        
        if is_super:
            # Apply buffs and debuffs for super attacks
            if self.buffs.get("atk_buff"):
                for buff in self.buffs["atk_buff"]:
                    buff_value += buff.get('value', 0)
            if self.debuffs.get("atk_debuff"):
                for debuff in self.debuffs["atk_debuff"]:
                    debuff_value += debuff.get('value', 0)
                    
            effective_attack = self.attack * (self.sa_multi + buff_value - debuff_value)
            print(f"Bosses effective attack: BaseAttack: {self.attack} * "
                  f"(SA Multi: {self.sa_multi} + SA ATK Buff: {buff_value}) - "
                  f"SA ATK Debuff: {debuff_value} = {effective_attack}")
        else:
            # Apply only buffs for normal attacks
            effective_attack = self.attack * (1 + buff_value)
            print(f"Bosses effective attack: BaseAttack: {self.attack} * "
                  f"Normal ATK Buff: {1 + buff_value} = {effective_attack:.0f}")
                  
        return max(0, effective_attack)  # Ensure non-negative attack value
    
    def get_boss_type(self):
        """
        Get the boss's type.
        
        Returns:
            str: Boss type (TEQ, AGL, PHY, INT, STR)
        """
        return self.boss_type
    
    def get_boss_class(self):
        """
        Get the boss's class.
        
        Returns:
            str: Boss class (Super or Extreme)
        """
        return self.boss_class

    def apply_immunity(self, effect_type):
        """
        Check if the boss is immune to a certain effect.
        
        Args:
            effect_type (str): Type of effect to check (stun, seal, etc.)
            
        Returns:
            bool: True if immune, False otherwise
        """
        return self.immunities.get(effect_type, 0) == 1
    
    def get_boss_sa_effect(self):
        """
        Parse and apply the boss's Super Attack effect.
        
        Returns:
            tuple: (atk_buff, atk_debuff, def_buff, def_debuff) values
        """
        atk_buff, atk_debuff, def_buff, def_debuff = 0, 0, 0, 0
        
        # Parse ATK buffs/debuffs
        if "ATK +" in self.sa_effect:
            atk_buff = float(self.sa_effect.split("+")[1].strip("%")) / 100
        if "ATK -" in self.sa_effect:
            atk_debuff = float(self.sa_effect.split("-")[1].strip("%")) / 100
            
        # Parse DEF buffs/debuffs
        if "DEF +" in self.sa_effect:
            def_buff = float(self.sa_effect.split("+")[1].strip("%")) / 100
        if "DEF -" in self.sa_effect:
            def_debuff = float(self.sa_effect.split("-")[1].strip("%")) / 100
        
        return atk_buff, atk_debuff, def_buff, def_debuff


# =============================================================================
# BOSS SUPER ATTACK UTILITY FUNCTIONS
# =============================================================================

def get_boss_sa_multipliers(sa_text):
    """
    Determine SA multiplier for Boss based on attack description text.
    
    Args:
        sa_text (str): Super attack description text
        
    Returns:
        float: Super attack multiplier (as decimal, e.g., 3.5 for 350%)
    """
    # Search for the super attack keyword (e.g., 'Colossal', 'Supreme')
    multiplier_key = extract_multiplier_from_text(sa_text)
    
    # Use the appropriate multiplier dictionary
    if multiplier_key:
        multiplier = boss_super_attack_multipliers.get(multiplier_key, 100) / 100.0
        print(f"boss sa multiplier: {multiplier}")
        return multiplier
    else:
        # Default value if no match is found
        return 1.0