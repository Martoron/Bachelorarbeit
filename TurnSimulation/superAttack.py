import re

# Super Attack multipliers for normal and EZA cards
normal_super_attack_multipliers = {
    "Supreme": 430,
    "Immense": 505,
    "Mega-Colossal": 570,
    "Colossal": 425,
}

eza_super_attack_multipliers = {
    "Supreme": 530,
    "Immense": 630,
    "Mega-Colossal": 620,
    "Colossal": 450,
}

# Function to extract Super Attack multiplier keyword from text
def extract_multiplier_from_text(text):
    """Extracts the multiplier key (e.g., 'Colossal') from the text string."""
    for key in normal_super_attack_multipliers.keys():
        if re.search(key, text, re.IGNORECASE):  # Case-insensitive search
            return key
    return None

# Determine SA multipliers for LR (12 Ki and 18 Ki) or TUR (12 Ki)
def get_sa_multiplier_from_text(sa_text, eza=False):
    """
    Extract the super attack multiplier from a text description (e.g., 'causes colossal damage').
    
    :param sa_text: A string description of the super attack (e.g., 'causes colossal damage').
    :param eza: Boolean indicating if this is an EZA unit (True/False).
    :return: The corresponding super attack multiplier.
    """
    # Search for the super attack keyword (e.g., 'Colossal', 'Supreme')
    multiplier_key = extract_multiplier_from_text(sa_text)
    
    # Use the appropriate multiplier dictionary (normal or EZA)
    if multiplier_key:
        if eza:
            # Get the EZA multiplier
            return eza_super_attack_multipliers.get(multiplier_key, 100) / 100.0
        else:
            # Get the normal multiplier
            return normal_super_attack_multipliers.get(multiplier_key, 100) / 100.0
    else:
        # Default value if no match is found
        return 1.0

# Mapping for keyword effects on the character's stats
stat_effects = {
    #permanent stat increases
    "raises ATK": 0.30,  # 30% increase
    "greatly raises ATK": 0.50,  # 50% increase
    "massively raises ATK": 1.00,  # 100% increase

    "raises DEF": 0.30,  # 30% increase
    "greatly raises DEF": 0.50,  # 50% increase
    "massively raises DEF": 1.00,  # 100% increase

    "raises ATK & DEF": 0.30,  # 30% increase
    "greatly raises ATK & DEF": 0.50,  # 50% increase
    "massively raises ATK & DEF": 1.00,  # 100% increase

    #temporary stat increases
    "raises ATK for": 0.30,  # 30% increase
    "greatly raises ATK for": 0.50,  # 50% increase
    "massively raises ATK for": 1.00,  # 100% increase

    "raises DEF for": 0.30,  # 30% increase
    "greatly raises DEF for": 0.50,  # 50% increase
    "massively raises DEF for": 1.00,  # 100% increase

    "raises ATK & DEF for": 0.30,  # 30% increase
    "greatly raises ATK & DEF for": 0.50,  # 50% increase
    "massively raises ATK & DEF for": 1.00,  # 100% increase
}

additional_effects = {
    "high chance of performing a critical hit": 0.5,  # 50% chance of critical hit
} 

# Mapping for keyword debuffs on the enemy's stats
enemy_debuffs = {
    "lowers ATK": 0.20,  # 20% decrease in enemy's ATK
    "greatly lowers ATK": 0.30,  # 30% decrease in enemy's ATK

    "lowers DEF": 0.40,  # 40% decrease in enemy's DEF
    "greatly lowers DEF": 0.50,  # 50% decrease in enemy's DEF
    "Massively lowers DEF": 0.80,  # 80% decrease in enemy's DEF

    "lowers ATK & DEF": 0.20,  # 20% decrease in enemy's DEF
    "greatly lowers ATK & DEF": 0.30,  # 30% decrease in enemy's DEF
}

def get_sa_effects(sa_text):
    """
    Extracts the Super Attack effects from the given text and returns
    a dictionary with stat multipliers and debuffs.
    """
    sa_effects = {
        "permanent_atk_multiplier": 0,  # Default no ATK buff
        "permanent_def_multiplier": 0,  # Default no DEF buff
        "temporary_atk_multiplier": 0,  # Default no temporary ATK buff
        "temporary_def_multiplier": 0,  # Default no temporary DEF buff
        "enemy_atk_debuff": 0,  # Default no ATK debuff on the enemy
        "enemy_def_debuff": 0,  # Default no DEF debuff on the enemy
        "crit_chance": 0,  # Default no critical hit chance
    }

    # Check for character stat effects (ATK, DEF increases)
    for effect, multiplier in stat_effects.items():
        if re.search(effect, sa_text, re.IGNORECASE):
            if "ATK for" in sa_text and "DEF" not in sa_text:  # ATK-only buffs
                sa_effects["temporary_atk_multiplier"] = max(
                    sa_effects["temporary_atk_multiplier"], multiplier
                )
            elif "ATK" in  sa_text and "DEF" not in  sa_text:  # ATK-only buffs
                sa_effects["permanent_atk_multiplier"] = max(
                    sa_effects["permanent_atk_multiplier"], multiplier
                )
            if "DEF for" in sa_text and "ATK" not in sa_text:  # DEF-only buffs
                sa_effects["temporary_def_multiplier"] = max(
                    sa_effects["temporary_def_multiplier"], multiplier
                )
            elif "DEF" in  sa_text and "ATK" not in sa_text:  # DEF-only buffs
                sa_effects["permanent_def_multiplier"] = max(
                    sa_effects["permanent_def_multiplier"], multiplier
                )
            if "ATK & DEF for" in sa_text:  # Both ATK and DEF buffs
                sa_effects["temporary_atk_multiplier"] = max(
                    sa_effects["temporary_atk_multiplier"], multiplier
                )
                sa_effects["temporary_def_multiplier"] = max(
                    sa_effects["temporary_def_multiplier"], multiplier
                )
            elif "ATK & DEF" in sa_text:  # Both ATK and DEF buffs
                sa_effects["permanent_atk_multiplier"] = max(
                    sa_effects["permanent_atk_multiplier"], multiplier
                )
                sa_effects["permanent_def_multiplier"] = max(
                    sa_effects["permanent_def_multiplier"], multiplier
                )

    for effect, multiplier in additional_effects.items(): 
        if re.search(effect, sa_text, re.IGNORECASE):
            if "critical hit" in sa_text:
                sa_effects["crit_chance"] = max(sa_effects["crit_chance"], multiplier)

    # Check for enemy stat debuffs (ATK, DEF decreases)
    for debuff, value in enemy_debuffs.items():
        if re.search(debuff, sa_text, re.IGNORECASE):
            if "ATK" in debuff and "DEF" not in debuff:  # ATK-only debuffs
                sa_effects["enemy_atk_debuff"] = max(
                    sa_effects["enemy_atk_debuff"], value
                )
            if "DEF" in debuff and "ATK" not in debuff:  # DEF-only debuffs
                sa_effects["enemy_def_debuff"] = max(
                    sa_effects["enemy_def_debuff"], value
                )
            if "ATK & DEF" in debuff:  # Both ATK and DEF debuffs
                sa_effects["enemy_atk_debuff"] = max(
                    sa_effects["enemy_atk_debuff"], value
                )
                sa_effects["enemy_def_debuff"] = max(
                    sa_effects["enemy_def_debuff"], value
                )

    return sa_effects



