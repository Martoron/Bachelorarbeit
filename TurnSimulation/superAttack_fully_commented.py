import re

# =============================================================================
# SUPER ATTACK MULTIPLIER DEFINITIONS
# =============================================================================

# Super Attack multipliers for normal cards
normal_super_attack_multipliers = {
    "Supreme": 430,
    "Immense": 505,
    "Mega-Colossal": 570,
    "Colossal": 425,
}

# Super Attack multipliers for EZA (Extreme Z-Awakened) cards
eza_super_attack_multipliers = {
    "Supreme": 530,
    "Immense": 630,
    "Mega-Colossal": 620,
    "Colossal": 450,
}


# =============================================================================
# SUPER ATTACK MULTIPLIER EXTRACTION
# =============================================================================

def extract_multiplier_from_text(text):
    """
    Extract the multiplier key (e.g., 'Colossal') from super attack text.
    
    Args:
        text (str): Super attack description text
        
    Returns:
        str: Multiplier key if found, None otherwise
    """
    for key in normal_super_attack_multipliers.keys():
        if re.search(key, text, re.IGNORECASE):  # Case-insensitive search
            return key
    return None


def get_sa_multiplier_from_text(sa_text, eza=False):
    """
    Extract the super attack multiplier from a text description.
    
    Args:
        sa_text (str): Super attack description (e.g., 'causes colossal damage')
        eza (bool, optional): Whether this is an EZA unit. Defaults to False
        
    Returns:
        float: Super attack multiplier (as decimal, e.g., 4.25 for 425%)
    """
    # Search for the super attack keyword (e.g., 'Colossal', 'Supreme')
    multiplier_key = extract_multiplier_from_text(sa_text)
    
    # Use the appropriate multiplier dictionary
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


# =============================================================================
# SUPER ATTACK EFFECT MAPPINGS
# =============================================================================

# Mapping for permanent stat increases from super attacks
stat_effects = {
    # Permanent ATK increases
    "raises ATK": 0.30,  # 30% increase
    "greatly raises ATK": 0.50,  # 50% increase
    "massively raises ATK": 1.00,  # 100% increase

    # Permanent DEF increases
    "raises DEF": 0.30,  # 30% increase
    "greatly raises DEF": 0.50,  # 50% increase
    "massively raises DEF": 1.00,  # 100% increase

    # Permanent combined ATK & DEF increases
    "raises ATK & DEF": 0.30,  # 30% increase
    "greatly raises ATK & DEF": 0.50,  # 50% increase
    "massively raises ATK & DEF": 1.00,  # 100% increase

    # Temporary ATK increases (single turn)
    "raises ATK for": 0.30,  # 30% increase
    "greatly raises ATK for": 0.50,  # 50% increase
    "massively raises ATK for": 1.00,  # 100% increase

    # Temporary DEF increases (single turn)
    "raises DEF for": 0.30,  # 30% increase
    "greatly raises DEF for": 0.50,  # 50% increase
    "massively raises DEF for": 1.00,  # 100% increase

    # Temporary combined ATK & DEF increases (single turn)
    "raises ATK & DEF for": 0.30,  # 30% increase
    "greatly raises ATK & DEF for": 0.50,  # 50% increase
    "massively raises ATK & DEF for": 1.00,  # 100% increase
}

# Mapping for additional special effects
additional_effects = {
    "high chance of performing a critical hit": 0.5,  # 50% chance of critical hit
} 

# Mapping for enemy debuffs from super attacks
enemy_debuffs = {
    # Enemy ATK debuffs
    "lowers ATK": 0.20,  # 20% decrease in enemy's ATK
    "greatly lowers ATK": 0.30,  # 30% decrease in enemy's ATK

    # Enemy DEF debuffs
    "lowers DEF": 0.40,  # 40% decrease in enemy's DEF
    "greatly lowers DEF": 0.50,  # 50% decrease in enemy's DEF
    "Massively lowers DEF": 0.80,  # 80% decrease in enemy's DEF

    # Combined enemy ATK & DEF debuffs
    "lowers ATK & DEF": 0.20,  # 20% decrease in enemy's stats
    "greatly lowers ATK & DEF": 0.30,  # 30% decrease in enemy's stats
}


# =============================================================================
# SUPER ATTACK EFFECTS PARSING
# =============================================================================

def get_sa_effects(sa_text):
    """
    Extract Super Attack effects from text and return stat multipliers and debuffs.
    
    Parses super attack description text to identify:
    - Permanent and temporary stat boosts
    - Enemy debuffs
    - Critical hit chances
    
    Args:
        sa_text (str): Super attack description text
        
    Returns:
        dict: Dictionary containing all extracted effects with their values
    """
    sa_effects = {
        "permanent_atk_multiplier": 0,  # Permanent ATK boost
        "permanent_def_multiplier": 0,  # Permanent DEF boost
        "temporary_atk_multiplier": 0,  # Temporary ATK boost (1 turn)
        "temporary_def_multiplier": 0,  # Temporary DEF boost (1 turn)
        "enemy_atk_debuff": 0,  # Enemy ATK reduction
        "enemy_def_debuff": 0,  # Enemy DEF reduction
        "crit_chance": 0,  # Critical hit chance
    }

    # Check for character stat effects (ATK, DEF increases)
    for effect, multiplier in stat_effects.items():
        if re.search(effect, sa_text, re.IGNORECASE):
            # Handle ATK-only buffs
            if "ATK for" in sa_text and "DEF" not in sa_text:
                sa_effects["temporary_atk_multiplier"] = max(
                    sa_effects["temporary_atk_multiplier"], multiplier
                )
            elif "ATK" in sa_text and "DEF" not in sa_text and "for" not in sa_text:
                sa_effects["permanent_atk_multiplier"] = max(
                    sa_effects["permanent_atk_multiplier"], multiplier
                )
                
            # Handle DEF-only buffs
            if "DEF for" in sa_text and "ATK" not in sa_text:
                sa_effects["temporary_def_multiplier"] = max(
                    sa_effects["temporary_def_multiplier"], multiplier
                )
            elif "DEF" in sa_text and "ATK" not in sa_text and "for" not in sa_text:
                sa_effects["permanent_def_multiplier"] = max(
                    sa_effects["permanent_def_multiplier"], multiplier
                )
                
            # Handle combined ATK & DEF buffs
            if "ATK & DEF for" in sa_text:
                sa_effects["temporary_atk_multiplier"] = max(
                    sa_effects["temporary_atk_multiplier"], multiplier
                )
                sa_effects["temporary_def_multiplier"] = max(
                    sa_effects["temporary_def_multiplier"], multiplier
                )
            elif "ATK & DEF" in sa_text and "for" not in sa_text:
                sa_effects["permanent_atk_multiplier"] = max(
                    sa_effects["permanent_atk_multiplier"], multiplier
                )
                sa_effects["permanent_def_multiplier"] = max(
                    sa_effects["permanent_def_multiplier"], multiplier
                )

    # Check for additional effects (critical hits, etc.)
    for effect, multiplier in additional_effects.items(): 
        if re.search(effect, sa_text, re.IGNORECASE):
            if "critical hit" in sa_text:
                sa_effects["crit_chance"] = max(sa_effects["crit_chance"], multiplier)

    # Check for enemy stat debuffs
    for debuff, value in enemy_debuffs.items():
        if re.search(debuff, sa_text, re.IGNORECASE):
            # Handle ATK-only debuffs
            if "ATK" in debuff and "DEF" not in debuff:
                sa_effects["enemy_atk_debuff"] = max(
                    sa_effects["enemy_atk_debuff"], value
                )
                
            # Handle DEF-only debuffs
            if "DEF" in debuff and "ATK" not in debuff:
                sa_effects["enemy_def_debuff"] = max(
                    sa_effects["enemy_def_debuff"], value
                )
                
            # Handle combined ATK & DEF debuffs
            if "ATK & DEF" in debuff:
                sa_effects["enemy_atk_debuff"] = max(
                    sa_effects["enemy_atk_debuff"], value
                )
                sa_effects["enemy_def_debuff"] = max(
                    sa_effects["enemy_def_debuff"], value
                )

    return sa_effects