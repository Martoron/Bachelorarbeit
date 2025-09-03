from colorama import Fore, Style, init
import csv
import os
import json
import re
import random
from collections import deque
import sys
import math
from datetime import datetime
from links import get_shared_links_multiplier
from superAttack import get_sa_effects, get_sa_multiplier_from_text
from boss import Boss, get_boss_sa_multipliers

# Initialize colorama for text coloring
init(autoreset=True)
CURRENT_JSON_PATH = None

# Define the Unit class
class Unit:
    def __init__(self,id, name, priority, image, leaderskill, character_type, character_class, defense, attack, hp, ki_multiplier, links, sa_12_multiplier, sa_18_multiplier, sa_12_effects, sa_18_effects, categories, rarity=None, damage_reduction=0, buffs=None, debuffs=None, active_skill=None, active_skill_condition=None, active_skill_code_condition=None, active_skill_buffs=None, transformed= False, transformations=[]):   
        self.id = id    
        self.name = name
        self.priority = priority
        self.image = image
        self.leaderskill = leaderskill
        self.character_type = character_type
        self.character_class = character_class
        self.defense = defense
        self.attack = attack
        self.hp = hp
        self.ki_multiplier = ki_multiplier 
        self.links = links
        self.sa_12_multiplier = sa_12_multiplier 
        self.sa_18_multiplier = sa_18_multiplier
        self.sa_12_effects = sa_12_effects
        self.sa_18_effects = sa_18_effects
        self.categories = categories
        self.rarity = rarity or "UR"  # Default to UR if not provided
        self.damage_reduction = damage_reduction  # Percentage (e.g., 0.3 for 30%)
        self.buffs = buffs or {}  # Buffs like {"def_buff": +150%, "atk_buff": +200%}
        self.debuffs = debuffs or {}  # Debuffs like {"def_debuff": -50%}
        self.active_skill = active_skill 
        self.active_skill_condition = active_skill_condition
        self.active_skill_code_condition = active_skill_code_condition
        self.active_skill_buffs = active_skill_buffs
        #transformation
        self.transformed = transformed
        # If the unit has a transformation, store its data
        self.transformations = transformations
        
        # Initialize manually applied values
        self.manual_percentage_items = 1
        self.manual_flat_boost_items = 0
        self.manual_active_skill_buffs = 1
        self.temp_ki_multiplier = 1
        self.ki = 0
        self.ki_gained = 0
        self.crit_chance = 0
        self.effective_attack = 0
        self.effective_attack_for_reseting = 0
        self.sa_12_multiplier_for_reseting = sa_12_multiplier
        self.sa_18_multiplier_for_reseting = sa_18_multiplier
        self.effective_defense = 0
        self.effective_defense_for_reseting = 0
        self.leaderskill_hp_multiplier = 1
        self.leaderskill_atk_multiplier = 0
        self.leaderskill_def_multiplier = 0
        self.leaderskill_ki_multiplier = 0
        self.passives = {}
        # tracker
        self.attacks = 0
        self.super_attacks = 0
        self.dodges = 0
        self.crit_this_turn = False
        self.evaded_this_turn = False 
        self.sim_evade_this_turn = False
        self.additional_attack_this_turn = False
        self.additional_super_attack_this_turn = False
        self.ki_18_attack_this_turn = False
        self.ki_12_attack_this_turn = False
        self.additional_atk_boost_this_turn = False
        self.additional_def_boost_this_turn = False
        self.additional_ki_boost_this_turn = False 
        self.guard_this_turn = False
        self.damage_dealt_this_turn = 0
        self.hits_taken = 0
        self.was_attacked_this_turn = 0
        self.damage_taken_this_turn = 0
        self.guard_activations = 0
        self.revive = False
        self.has_revived = False
        self.has_healed = False
        self.can_use_active_skill = False
        self.used_active_skill = False

    def check_transformation(self, current_turn, current_hp):
        """Checks if the character should transform and applies the transformation."""
        if self.transformed or not self.transformations:
            return  # No transformation or already transformed
        
        transformation = self.transformations  # Assuming only one transformation

        # **Check Passive Transformation Condition**
        if "transformation" in self.buffs:
            transformation = self.transformations[0]  # Get the transformation dictionary
            condition = self.buffs["transformation"].get("condition", "")  # Extract condition string

            # Apply transformation only if the condition is met
            if "when HP is 50%" in condition:
                print(f"{current_hp}")
                if current_hp <= 0.50:  # HP is 50% or less
                    print(f"{self.name} meets the transformation condition: {condition}")
                    self.apply_transformation(transformation)  # Call the function to transform
            else:
                print(f"{self.name} does not meet the transformation condition: {condition}")
        else:
            print(f"{self.name} does not have a transformation passive.")

    def apply_transformation(self, transformation):
        """Applies the transformation by modifying character attributes."""
        self.name = transformation["transformedName"]
        self.id = transformation["transformedID"]
        self.super_attack = transformation["transformedSuperAttack"]
        self.passive = transformation["transformedPassive"]
        self.buffs = transformation["transformedBuffs"]
        self.links = transformation["transformedLinks"]
        self.image = transformation["transformedImage"]
        self.image_url = transformation["transformedImageURL"]
        self.transformed = True  # Mark as transformed
        if 'atk_buff' in self.passives:
            del self.passives['atk_buff']

    def load_image(self, image_path):
        # Logic to load the image, e.g., using PIL or another library
        self.imageURL = image_path  # Just storing the path for now, can load actual image later

    def check_evasion(self):
        """Check if the unit evades the attack."""
        # Check if the unit has a dodge passive
        dodge_chance = 0 
        for buff_name, buff_details in self.passives.items():
            if "conditional_evasion" in buff_name:  # Check for conditional evasion passives
                for details in buff_details:
                    print(f"Dodge chance from conditional: {details['value']}")
                    dodge_chance += details["value"]
                    
                
        if self.buffs.get("evasion") is not None:
            dodge_chance += self.buffs["evasion"]["value"]
            print(f"Dodge chance from passive: {self.buffs['evasion']['value']}")
        
        print(f"Total dodge chance: {dodge_chance}")

        if random.random() < dodge_chance:
            print(f"{Fore.GREEN}{self.name} evasion check returned TRUE!")
            return True
           
        print(f"{Fore.RED}{self.name} evasion check returned FALSE!")
        return False
    
    def check_guard(self):
        """Check if the unit guards the attack."""
        # Check if the unit has a guard passive
        if self.buffs.get("guard") is not None:
            guard_change = self.buffs["guard"]["value"]
            if random.random() < guard_change:
                print(f"{Fore.GREEN}{self.name} guard check returned TRUE!")
                return True
        print(f"{Fore.RED}{self.name} guard check returned FALSE!")
        return False
    
    def check_counter(self):
        """Check if the unit counters the attack."""
        # Check if the unit has a counter passive
        if self.buffs.get("counter") is not None:
            return True
        return False
    
    def check_additional_attack_that_can_be_super(self):
        """Check if the unit performs an additional attack."""
        # Check if the unit has an additional attack passive
        check = 0
        if self.buffs.get("additional_atk") is not None:
            check = 1
            print(f"Unit has additional attack")
            if self.buffs["additional_atk"]["can_be_super"]:
                check = 2
                print(f"Additional Attack can be super")
                additional_attack_chance = self.buffs["additional_atk"]["chance"]
                print(f"Additional Attack Chance: {additional_attack_chance}")
                if random.random() < additional_attack_chance:
                    check = 3
                    print("Check for additional attack to become super returned True")
                    return check
                else:
                    print("Check for additional attack to become super returned False")
                    return check
            else:
                print("Additional Attack cannot be super")
                return check
        print("no additional attack")
        return check
    
    def check_additional_super_attack(self):
        """Check if the unit performs an additional Super Attack."""
        # Check if the unit has an additional Super Attack passive
        if self.buffs.get("additional_super_atk") is not None:
            additional_sa_chance = self.buffs["additional_super_atk"]["chance"]
            print("Unit has additional super attack chance")
            print(f"Additional SA Chance: {additional_sa_chance}")
            if random.random() < additional_sa_chance:
                print("additional super attack check returned True")
                return True
            else:
                print("additional super attack check returned False")
                return False
        print("Unit has no additional super attack")
        return False
   
    def check_critical_hit(self, is_super=True):
        """Check if the unit lands a critical hit."""
        crit_chance = 0
        conditional_crit_chance = 0
        # Check if the unit has a critical hit passive
        if self.buffs.get("crit") is not None:
            print("Unit has crit chance from passive")
            crit_chance = self.buffs["crit"]["chance"]
            print(f"Critical Hit Chance from passive: {crit_chance}")
            if random.random() < crit_chance:
                print("crit check for passive returned True")
                return True
            else:
                print("crit check for passive returned False")
        if self.ki >= 18 and is_super:
            if not self.sa_18_effects.get("crit_chance",0) == 0:
                self.crit_chance += self.sa_18_effects.get("crit_chance")
                print("Unit has crit chance from SA 18")
                print(f"Critical Hit Chance from SA 18: {self.sa_18_effects.get('crit_chance')}")
                print(f"Overall Critical Hit Chance: {self.crit_chance}")
                if random.random() < self.crit_chance:
                    print("crit check for 18 ki returned True")
                    return True
                else:
                    print("crit check for 18 ki returned False")
        if self.ki >= 12 and self.ki < 18 and  is_super:
            if not self.sa_12_effects.get("crit_chance") == 0:
                self.crit_chance += self.sa_12_effects.get("crit_chance")
                print("Unit has crit chance from SA 12")
                print(f"Critical Hit Chance from SA 12: {self.sa_12_effects.get('crit_chance')}")
                print(f"Overall Critical Hit Chance: {self.crit_chance}")
                if random.random() < self.crit_chance:
                    print("crit chance for 12 ki returned True")
                    return True
                else:
                    print("crit chance for 12 ki returned False")
        for buff_name, buff_details in self.passives.items():
            if "conditional_crit" in buff_name:
                for details in buff_details:
                    conditional_crit_chance += details["value"]
                    print(f"Conditional Crit Chance: {details['value']}")
        if random.random() < conditional_crit_chance:
            print("crit check for conditional crit returned True")
            return True
        else:
            print("crit check for conditional crit returned False")

        print("All crit procs missed or Unit has no crit chance")
        return False

    def calculate_effective_defense(self, link_def_multiplier):
        """Calculate effective defense after applying buffs and debuffs."""
        # Calculate the base defense with the leader skill multiplier 
        effective_defense = self.defense * self.leaderskill_def_multiplier
        effective_defense = int(round(effective_defense, 2))  # Round to the nearest integer
        print(f"Base defense after leader skill multiplier: {effective_defense}")
        # Apply each defense buff sequentially
        buff_multiplier = 1
        revive_multiplier = 0

        for buff_name, buff_details in self.buffs.items():
            if "revive" in buff_name:
                revive_multiplier = 0.3
                print(f"Revive multiplier from {buff_name}: {revive_multiplier}")  # Debugging line
        for buff_name, buff_details in self.passives.items():
            if "def" in buff_name and not "boost" in buff_name:  # Only process defense buffs
                print(f"Processing {buff_name}")  # Debugging line to see which buff is processed
                def_multiplier = 0
                def_per_ki_multiplier = 0
                for details in buff_details:
                    if details.get("is_sot", False):  # Only process Start-of-Turn buffs
                        if "def_buff" in buff_name:
                            def_multiplier = sum(buff["value"] for buff in self.passives["def_buff"])  # Add 1 to convert percentage to multiplier
                            print(f"DEF multiplier from {buff_name}: {def_multiplier}")  # Debugging line
                        if "def_per_ki_sphere" in buff_name:
                            def_per_ki_multiplier = sum(buff["value"] for buff in self.passives["def_per_ki_sphere"])
                            print(f"DEF multiplier from {buff_name}: {def_per_ki_multiplier}")  # Debugging line
                if def_multiplier > 0:
                    buff_multiplier += def_multiplier
                    print(f"{Fore.GREEN}{self.name}'s defense is boosted by {(def_multiplier) * 100:.0f}% from Start of Turn buffs.")
                if revive_multiplier > 0:
                    buff_multiplier += revive_multiplier
                    print(f"{Fore.GREEN}{self.name}'s defense is boosted by {revive_multiplier * 100:.0f}% from revive mulitplier.")
                if def_per_ki_multiplier > 0:
                    buff_multiplier += def_per_ki_multiplier
                    print(f"{Fore.GREEN}{self.name}'s defense is boosted by {def_per_ki_multiplier * 100:.0f}% per Ki Sphere obtained.")

        if buff_multiplier > 1:
            # Apply all buffs at once
            effective_defense *= buff_multiplier
            effective_defense = int(round(effective_defense, 2))  # Round to the nearest integer
            print(f"After applying {(buff_multiplier - 1) * 100:.0f}%: {effective_defense}")
           
        for debuff_name, debuff_details in self.debuffs.items():
            if "def_debuff" in debuff_name:
                debuff_multiplier = debuff_details.get("value", 0) + 1  # Add 1 to convert percentage to multiplier
                effective_defense *= debuff_multiplier
                effective_defense = int(round(effective_defense, 2))  # Round to the nearest integer
                print(f"{Fore.RED}{self.name}'s defense is reduced by {debuff_details['value'] * 100}% for {debuff_details['duration']} turns.")
                print(f"After applying {debuff_name} ({debuff_details['value'] * 100:.0f}%): {effective_defense}")

        effective_defense *= self.manual_percentage_items  # Apply percentage based items
        effective_defense += self.manual_flat_boost_items  # Apply flat boost items
        effective_defense *= link_def_multiplier  # Apply link skills
        effective_defense = int(round(effective_defense, 2))  # Round to the nearest integer
        print(f"afer applying linkskill multiplier of {int(round((link_def_multiplier-1)*100))}%: {effective_defense}")
        effective_defense *= self.manual_active_skill_buffs  # Apply active skill buffs
        additional_buff_multiplier = 1
        for buff_name, buff_details in self.passives.items():
            if "def" in buff_name and "boost" in buff_name:
                additional_def_multiplier = 0
                additional_sa_buff_multiplier = 0
                for details in buff_details:
                    if details.get("is_sot", False) == False:
                        if "additional_def_boost" in buff_name:
                            additional_def_multiplier = sum(buff["value"] for buff in self.passives["additional_def_boost"])
                            
                        if "perm_sa_def_boost" in buff_name:
                            additional_sa_buff_multiplier = sum(buff["value"] for buff in self.passives["perm_sa_def_boost"])
               
                if additional_def_multiplier > 0:
                    print(f"{Fore.GREEN}{self.name}'s defense is boosted by an additional {additional_def_multiplier * 100:.0f}% from attacking.")
                    additional_buff_multiplier += additional_def_multiplier
                if additional_sa_buff_multiplier > 0:
                    print(f"{Fore.GREEN}{self.name}'s defense is boosted by an additional {additional_sa_buff_multiplier * 100:.0f}% from Superattacks.")
                    additional_buff_multiplier += additional_sa_buff_multiplier
        if additional_buff_multiplier > 1:
            effective_defense *= additional_buff_multiplier
            effective_defense = int(round(effective_defense, 2))
            print(f"After applying {(additional_buff_multiplier - 1) * 100:.0f}%): {effective_defense}")

        print(f"\n")
    

        return max(0, int(round(effective_defense, 2))) # Round to the nearest integer)  # Ensure defense is not negative

    def calculate_effective_attack(self, link_atk_multiplier, active_buff_multiplier=1):
        """Calculate effective attack after applying buffs and debuffs."""
        # Calculate effective attack  
        effective_attack = self.attack * self.leaderskill_atk_multiplier
        effective_attack = int(round(effective_attack, 2))  # Round to the nearest integer
        print(f"Base attack after leader skill multiplier: {effective_attack}")
        # Start building the output string for the calculations

        buff_multiplier = 1
        revive_multiplier = 0

        for buff_name, buff_details in self.buffs.items():
            if "revive" in buff_name:
                revive_multiplier = 0.3
                print(f"Revive multiplier from {buff_name}: {revive_multiplier}")  # Debugging line
        for buff_name, buff_details in self.passives.items():
            if "atk" in buff_name and not "boost" in buff_name:
                print(f"Processing {buff_name}")  # Debugging line to see which buff is processed
                atk_multiplier = 0
                conditional_buff_multiplier = 0
                atk_per_ki_multiplier = 0
                for details in buff_details:
                    if details.get("is_sot", False):  # Only process Start-of-Turn buffs
                        # Apply base ATK boost
                        if "atk_buff" in buff_name and not "buffs" in buff_name:
                            atk_multiplier = sum(buff["value"] for buff in self.passives.get("atk_buff", []))
                            print(f"Base ATK multiplier from {buff_name}: {atk_multiplier}")  # Debugging line

                        # Apply conditional ATK boost separately for each buff in the list
                        if "conditional_atk_buffs" in buff_name:
                            if "slot_1" in buff_name:
                                conditional_buff_multiplier = details["value"]
                                print(f"Conditional ATK multiplier from {buff_name}: {conditional_buff_multiplier}")  # Debugging line
                            if "slot_2" in buff_name:
                                conditional_buff_multiplier = details["value"]
                                print(f"Conditional ATK multiplier from {buff_name}: {conditional_buff_multiplier}")  # Debugging line
                            if "HP" in buff_name:
                                conditional_buff_multiplier = details["value"]
                                print(f"Conditional ATK multiplier from {buff_name}: {conditional_buff_multiplier}")  # Debugging line
                    
                        # Apply ATK per Ki Sphere buff
                        if "atk_per_ki_sphere" in buff_name:
                            atk_per_ki_multiplier = sum(buff["value"] for buff in self.passives.get("atk_per_ki_sphere", []))
                            print(f"ATK per Ki Sphere multiplier from {buff_name}: {atk_per_ki_multiplier}")  # Debugging line

                if atk_multiplier > 0:
                    print(f"{Fore.GREEN}{self.name}'s attack is boosted by {atk_multiplier * 100:.0f}% from Start of Turn buffs.")
     
                    buff_multiplier += atk_multiplier

                if conditional_buff_multiplier > 0:
                    print(f"{Fore.GREEN}{self.name}'s attack is boosted by an additional {conditional_buff_multiplier * 100:.0f}% from conditional buffs.")
  
                    buff_multiplier += conditional_buff_multiplier
                if revive_multiplier > 0:
                    print(f"{Fore.GREEN}{self.name}'s attack is boosted by an additional {revive_multiplier * 100:.0f}% from revive multiplier.")
  
                    buff_multiplier += revive_multiplier
                if atk_per_ki_multiplier > 0:
                    print(f"{Fore.GREEN}{self.name}'s attack is boosted by an additional {atk_per_ki_multiplier * 100:.0f}% per Ki Sphere obtained.")
      
                    buff_multiplier += atk_per_ki_multiplier
                
        if buff_multiplier > 1:
            # Apply all buffs at once
            effective_attack *= buff_multiplier
            effective_attack = int(round(effective_attack, 2))  # Round to the nearest integer
            print(f"After applying {(buff_multiplier-1) * 100:.0f}%: {effective_attack}")

        for debuff_name, debuff_details in self.debuffs.items():
            if "atk_debuff" in debuff_name:
                debuff_multiplier = debuff_details.get("value", 0) + 1  # Add 1 to convert percentage to multiplier
                effective_attack *= debuff_multiplier
                effective_attack = int(round(effective_attack, 2))  # Round to the nearest integer
                print(f"{Fore.RED}{self.name}'s attack is reduced by {debuff_details['value'] * 100}% for {debuff_details['duration']} turns.")
                print(f"After applying {debuff_name} ({debuff_details['value'] * 100:.0f}%): {effective_attack}")
        effective_attack *= self.manual_percentage_items  # Apply percentage based items
        effective_attack += self.manual_flat_boost_items  # Apply flat boost items
        effective_attack *= link_atk_multiplier  # Apply link skills
        effective_attack = int(round(effective_attack, 2))  # Round to the nearest integer
        print(f"afer applying linkskill multiplier of {int(round((link_atk_multiplier-1)*100))}%: {effective_attack}")

        if not active_buff_multiplier == 1:
            effective_attack *= (active_buff_multiplier + 1)  # Apply active skill buffs
            effective_attack = int(round(effective_attack, 2))  # Round to the nearest integer
            print(f"After applying active skill multiplier of {active_buff_multiplier * 100:.0f}%: {effective_attack}")
    
        effective_attack *= self.temp_ki_multiplier  # Apply temporary ki multiplier
        effective_attack = int(round(effective_attack, 2))  # Round to the nearest integer
        print(f"After applying ki multiplier of {self.temp_ki_multiplier * 100:.0f}%: {effective_attack}")

        additional_buff_multiplier = 1
        for buff_name, buff_details in self.passives.items():
            if "atk" in buff_name and "boost" in buff_name:
                additional_atk_multiplier = 0
                additional_sa_atk_multiplier = 0
                guard_buff_multiplier = 0
                for details in buff_details:
                    if details.get("is_sot", False) == False:
                        if "additional_atk_boost" in buff_name:
                            additional_atk_multiplier = sum(buff["value"] for buff in self.passives.get("additional_atk_boost",[])) 
                                                    
                        if "additional_atk_boost_on_18_ki_super" in buff_name:
                            additional_sa_atk_multiplier = sum(buff["value"] for buff in self.passives.get("additional_atk_boost_on_18_ki_super",[]))
                            
                        if "guard_atk_boost" in buff_name:
                            guard_buff_multiplier = sum(buff["value"] for buff in self.passives.get("guard_atk_boost",[]))
            
                if additional_atk_multiplier > 0:
                    print(f"{Fore.GREEN}{self.name}'s attack is boosted by an additional {additional_atk_multiplier * 100:.0f}% from attacking.")
      
                    additional_buff_multiplier += additional_atk_multiplier 
                if additional_sa_atk_multiplier > 0:
                    print(f"{Fore.GREEN}{self.name}'s attack is boosted by an additional {additional_sa_atk_multiplier * 100:.0f}% after a Super Attack.")
    
                    additional_buff_multiplier += additional_sa_atk_multiplier
                if guard_buff_multiplier > 0:
                    print(f"{Fore.GREEN}{self.name}'s attack is boosted by an additional {guard_buff_multiplier * 100:.0f}% when guarding.")
 
                    additional_buff_multiplier += guard_buff_multiplier
        
        if additional_buff_multiplier > 1:
            effective_attack *= additional_buff_multiplier
            effective_attack = int(round(effective_attack, 2))  # Round to the nearest integer
            print(f"After applying {(additional_buff_multiplier - 1) * 100:.0f}%): {effective_attack}")

        print(f"[DEBUG] Effective Attack: {effective_attack}")
        return max(0, int(round(effective_attack)))  # Ensure attack is not negative

    def get_sa_multiplier(self,ki):
        sa_def_multiplier = 1
        normal_attack_multiplier = 1
        if ki >= 18:
            sa_atk_multiplier = self.sa_18_multiplier
            super_attack_stat = self.effective_attack * sa_atk_multiplier
            normal_attack_stat = self.effective_attack * normal_attack_multiplier
            final_defense_stat = self.effective_defense * sa_def_multiplier
            if self.super_attacks == 0 and self.sa_18_effects.get("permanent_atk_multiplier") > 0:
                super_attack_stat = self.effective_attack * sa_atk_multiplier
                normal_attack_stat = self.effective_attack * normal_attack_multiplier
            if self.super_attacks > 0 and self.sa_18_effects.get("permanent_atk_multiplier") > 0:
                sa_atk_multiplier += (self.sa_18_effects.get("permanent_atk_multiplier")*self.super_attacks)
                super_attack_stat = self.effective_attack * sa_atk_multiplier
                normal_attack_multiplier += self.sa_18_effects.get("permanent_atk_multiplier", 0)
                normal_attack_stat = self.effective_attack * normal_attack_multiplier
            if self.sa_18_effects.get("permanent_def_multiplier") > 0:
                sa_def_multiplier += self.sa_18_effects.get("permanent_def_multiplier")
                final_defense_stat = self.effective_defense * sa_def_multiplier
            if self.sa_18_effects.get("temporary_atk_multiplier") > 0:
                sa_atk_multiplier = self.sa_18_multiplier + self.sa_18_effects.get("temporary_atk_multiplier", 0)
                super_attack_stat = self.effective_attack * sa_atk_multiplier
                normal_attack_multiplier = normal_attack_multiplier + self.sa_18_effects.get("temporary_atk_multiplier", 0)
                normal_attack_stat = self.effective_attack * normal_attack_multiplier
            if self.sa_18_effects.get("temporary_def_multiplier") > 0:
                sa_def_multiplier = self.sa_18_effects.get("temporary_def_multiplier", 0) + 1
                final_defense_stat = self.effective_defense * sa_def_multiplier
            sa_chrit_chance = self.sa_18_effects.get("crit_chance", 0)
            super_attack_stat = int(round(super_attack_stat, 2))
            final_defense_stat = int(round(final_defense_stat, 2))  
            print(f"{Fore.YELLOW}Calculating effective stats for {self.name}...")
            print(f"{Fore.CYAN}Stats After SuperAttack:\n")
            if not sa_chrit_chance == 0:
                print(f"{Fore.CYAN} Additional Super Attack Effects: {sa_chrit_chance*100}% chance of performing a critical hit")
 
            print(f"{Fore.CYAN}Effective Attack after applying sa multiplier of {int(round(sa_atk_multiplier*100,2))}%: {super_attack_stat}")
  
            if sa_def_multiplier > 1:
                print(f"{Fore.CYAN}Effective Defense after applying sa effect of {int(round((sa_def_multiplier - 1)*100,2))}%: {final_defense_stat}")
               
        elif ki >= 12:
            sa_atk_multiplier = self.sa_12_multiplier
            super_attack_stat = self.effective_attack * sa_atk_multiplier
            normal_attack_stat = self.effective_attack * normal_attack_multiplier
            final_defense_stat = self.effective_defense * sa_def_multiplier
            if self.super_attacks == 0 and self.sa_12_effects.get("permanent_atk_multiplier") > 0:
                super_attack_stat = self.effective_attack * sa_atk_multiplier
                normal_attack_stat = self.effective_attack * normal_attack_multiplier
            if self.super_attacks > 0 and self.sa_12_effects.get("permanent_atk_multiplier") > 0:
                sa_atk_multiplier += (self.sa_12_effects.get("permanent_atk_multiplier")*self.super_attacks)
                super_attack_stat = self.effective_attack * sa_atk_multiplier
                normal_attack_multiplier += self.sa_12_effects.get("permanent_atk_multiplier", 0)
                normal_attack_stat = self.effective_attack * normal_attack_multiplier
            if self.sa_12_effects.get("permanent_def_multiplier") > 0:
                sa_def_multiplier += self.sa_12_effects.get("permanent_def_multiplier")
                final_defense_stat = self.effective_defense * sa_def_multiplier
            if self.sa_12_effects.get("temporary_atk_multiplier") > 0:
                sa_atk_multiplier = self.sa_12_multiplier + self.sa_12_effects.get("temporary_atk_multiplier", 0)
                super_attack_stat = self.effective_attack * sa_atk_multiplier
                normal_attack_multiplier = normal_attack_multiplier + self.sa_12_effects.get("temporary_atk_multiplier", 0)
                normal_attack_stat = self.effective_attack * normal_attack_multiplier
            if self.sa_12_effects.get("temporary_def_multiplier") > 0:
                print(f"Temporary Def Multiplier: {self.sa_12_effects.get('temporary_def_multiplier')}")
                sa_def_multiplier = self.sa_12_effects.get("temporary_def_multiplier", 0) + 1
                print(f"Temporary Def Multiplier: {sa_def_multiplier}")
                final_defense_stat = self.effective_defense * sa_def_multiplier
            sa_chrit_chance = self.sa_12_effects.get("crit_chance", 0)
            super_attack_stat = int(round(super_attack_stat, 2))
            final_defense_stat = int(round(final_defense_stat, 2))  
            print(f"{Fore.YELLOW}Calculating effective stats for {self.name}...")
            print(f"{Fore.CYAN}Stats After SuperAttack:\n")
   
            print(f"{Fore.CYAN}Effective Attack after applying sa multiplier of {int(round(sa_atk_multiplier*100,2))}%: {super_attack_stat}")

            if sa_def_multiplier > 1:
                print(f"{Fore.CYAN}Effective Defense after applying sa effect of {int(round((sa_def_multiplier - 1)*100,2))}%: {final_defense_stat}")

        return super_attack_stat, normal_attack_stat, final_defense_stat

    def calculate_damage_dealt(self, effective_attack, boss, TaB, is_crit=False, is_super=True):
        attack_stat = effective_attack
        modifier = self.get_type_modifier_for_atk(TaB, boss.boss_type, boss.boss_class)  # Get type modifier
        variance = self.get_variance()
        boss_effective_defense = boss.defense
        if is_super:
            print(f"AttackStatAfterSa {attack_stat}, Modifier: {modifier}, Variance: {variance}, EnemeyDefense: {boss.defense}, EnemyDamageReductio: {boss.damage_reduction}")
            if boss.debuffs.get("def_debuff"):
                for debuff in boss.debuffs["def_debuff"]:
                    debuff_value = debuff.get('value', 0)
                    debuff_duration = debuff.get('duration', 0)
                    boss_effective_defense *= (1 - debuff_value)
                print(f"{boss.name}'s defense after applying debuffs: {boss_effective_defense}")
        else:
            print(f"AttackStat {attack_stat}, Modifier: {modifier}, Variance: {variance}, EnemeyDefense: {boss.defense}, EnemyDamageReductio: {boss.damage_reduction}")
        if is_crit:
            # For critical hits, ignore enemy defense
            damage = attack_stat * modifier * 1.25 * variance * (1 - boss.damage_reduction/100) # * 1,25 is crit
            print(f"Damage calculation with crit: ({attack_stat} *{modifier}* 1.25 * {variance} * (1 - {boss.damage_reduction/100})")
        else:
            damage = (attack_stat * modifier * variance - boss_effective_defense) * (1 - (boss.damage_reduction/100))
            print(f"Damage calculation without crit: ({attack_stat} *{modifier}* {variance} - {boss_effective_defense}) * (1 - {boss.damage_reduction/100})")

        return int(round(damage,2))  # Ensure damage is not negative
    
    def get_type_modifier_for_atk(self, TaB, enemy_type, enemy_class):
        # Define type advantages/disadvantages
        type_advantages = {
            'STR': {'weak': 'AGL', 'strong': 'PHY', 'neutral': {'TEQ', 'INT', 'STR'}},
            'AGL': {'weak': 'TEQ', 'strong': 'STR', 'neutral': {'PHY', 'INT', 'AGL'}},
            'TEQ': {'weak': 'INT', 'strong': 'AGL', 'neutral': {'STR', 'PHY', 'TEQ'}},
            'INT': {'weak': 'PHY', 'strong': 'TEQ', 'neutral': {'STR', 'AGL', 'INT'}},
            'PHY': {'weak': 'STR', 'strong': 'INT', 'neutral': {'AGL', 'TEQ', 'PHY'}},
        }
        class_advantages = {
            "Super": {'strong': 'Extreme', 'neutral': 'Super'},
            'Extreme': {'strong': 'Super', 'neutral': 'Extreme'},
        }

        # Check the enemy type to apply modifiers
        enemy_type = enemy_type
        enemy_class = enemy_class
        print(f"{enemy_class,enemy_type,self.character_type,self.character_class}")
        if self.character_type == type_advantages[enemy_type]['weak'] and self.character_class == class_advantages[enemy_class]['strong']:
            return 1.5 +(TaB * 0.05) # TaB is TypeAdvantageBonus from HiPo and per level you get 0.05
        elif self.character_type == type_advantages[enemy_type]['weak'] and self.character_class == class_advantages[enemy_class]['neutral']:
            if not self.buffs.get("super_effective_against_all_types") == None:
                return 1.5 + (TaB * 0.05)
            else:
                return 1.25  + (TaB * 0.05)
        elif self.character_type == type_advantages[enemy_type]['neutral'] and self.character_class == class_advantages[enemy_class]['strong']:
             if not self.buffs.get("super_effective_against_all_types") == None:
                return 1.5
             else:
                return 1.15 
        elif self.character_type == type_advantages[enemy_type]['neutral'] and self.character_class == class_advantages[enemy_class]['neutral']:
            if not self.buffs.get("super_effective_against_all_types") == None:
                return 1.5
            else:
                return 1.0 
        elif self.character_type == type_advantages[enemy_type]['strong'] and self.character_class == class_advantages[enemy_class]['strong']:
            if not self.buffs.get("super_effective_against_all_types") == None:
                return 1.5
            elif not self.buffs.get("disable_guard") == None:
                return 1.0
            else:
                return 0.5 
        elif self.character_type == type_advantages[enemy_type]['weak'] and self.character_class == class_advantages[enemy_class]['neutral']:  
            if not self.buffs.get("super_effective_against_all_types") == None:
                return 1.5
            elif not self.buffs.get("disable_guard") == None:
                return 1.0
            else:
                return 0.45  
        else:
            return 1.0  
        
    def get_variance(self):
        # Random variance from 1 to 1.03
        return random.uniform(1, 1.03)
    
    def get_type_modifier_for_def(self, TDB, enemy_type, enemy_class, guard=False):
        # Define type advantages/disadvantages
        type_advantages = {
            'STR': {'weak': 'AGL', 'strong': 'PHY', 'neutral': {'TEQ', 'INT', 'STR'}},
            'AGL': {'weak': 'TEQ', 'strong': 'STR', 'neutral': {'PHY', 'INT', 'AGL'}},
            'TEQ': {'weak': 'INT', 'strong': 'AGL', 'neutral': {'STR', 'PHY', 'TEQ'}},
            'INT': {'weak': 'PHY', 'strong': 'TEQ', 'neutral': {'STR', 'AGL', 'INT'}},
            'PHY': {'weak': 'STR', 'strong': 'INT', 'neutral': {'AGL', 'TEQ', 'PHY'}},
        }
        class_advantages = {
            "Super": {'strong': 'Extreme', 'neutral': 'Super'},
            'Extreme': {'strong': 'Super', 'neutral': 'Extreme'},
        }

        # Determine type and class relations
        is_type_neutral = self.character_type in type_advantages[enemy_type]['neutral']
        is_type_weak = self.character_type == type_advantages[enemy_type]['weak']
        is_type_strong = self.character_type == type_advantages[enemy_type]['strong']
        is_class_strong = self.character_class == class_advantages[enemy_class]['strong']
        is_class_neutral = self.character_class == class_advantages[enemy_class]['neutral']

        # Apply guard in specific scenarios
        if guard:
            if is_type_weak or (is_type_neutral and is_class_neutral):
                return 0.8 - (TDB * 0.01)
            else:
                return 0.8

        # Handle scenarios without guard
        if is_type_neutral and is_class_strong:
            return 1.15
        elif is_type_neutral and is_class_neutral:
            return 1.0
        elif is_type_weak:
            if is_class_strong:
                return 1.0 - (TDB * 0.01)
            else:
                return 0.9 - (TDB * 0.01)
        elif is_type_strong:
            if is_class_strong:
                return 1.5
            else:
                return 1.25
        else:
            return 1.0  # Default case

    def calculate_damage_taken(self, boss, boss_attack_power, TDB, item_used, guard=False, is_super=False):
        modifier = self.get_type_modifier_for_def(TDB, boss.boss_type, boss.boss_class, guard)  # Get type modifier
        variance = self.get_variance()
        atk_down = 0
        damage_reduction = 0
        for buff_name, buff_details in self.buffs.items():
            if "damage_reduction" in buff_name and not "additional" in buff_name:
                damage_reduction = buff_details.get("value", 0)
                print(f"[DEBUG] Using damage_reduction = {damage_reduction}")
        if guard:
            guard_modifier = 0.5
        elif modifier <= 0.9:           
            guard_modifier = 0.5
        else:
            guard_modifier = 1.0

        if is_super and item_used:
            damage = (boss_attack_power * modifier * variance * (1 - (damage_reduction + 0.4)) - self.effective_defense) * guard_modifier
            print(f"Damage calculation for Super and Item used: ({boss_attack_power} *{modifier}* {variance} * (1 - {atk_down}) * (1 - {damage_reduction + 0.4}) - {self.effective_defense}) * {guard_modifier}")
        elif is_super and not item_used:
            damage = (boss_attack_power * modifier * variance * (1 - damage_reduction) - self.effective_defense) * guard_modifier
            print(f"Damage calculation for Super: ({boss_attack_power} *{modifier}* {variance} * (1 - {atk_down}) * (1 - {damage_reduction}) - {self.effective_defense}) * {guard_modifier}")
        elif not is_super and item_used:
            damage = (boss_attack_power * modifier * variance * (1 - atk_down) * (1 - (damage_reduction + 0.4)) - self.effective_defense) * guard_modifier
            print(f"Damage calculation for normals and Item used: ({boss_attack_power} *{modifier}* {variance} * (1 - {atk_down}) * (1 - {damage_reduction + 0.4}) - {self.effective_defense}) * {guard_modifier}")
        else:
            if boss.debuffs.get("atk_debuff"):
                for debuff in boss.debuffs["atk_debuff"]:
                    atk_down = debuff.get('value', 0)
            damage = (boss_attack_power * modifier * variance * (1 - atk_down) * (1 - damage_reduction) - self.effective_defense) * guard_modifier
            print(f"Damgae calculation for normals: ({boss_attack_power} *{modifier}* {variance} * (1 - {atk_down}) * (1 - {damage_reduction}) -{self.effective_defense}) * {guard_modifier}")
        
        if damage < 150:
            damage = random.randint(9, 132)
        return int(round(damage,2))

class RotationManager:
    def __init__(self, team):
        self.all_units = {unit.number: unit for unit in team}  # {unit_num: unit}
        self.rotation_history = deque(maxlen=4)  # Stores last 3 rotations
        self.initial_pool = list(self.all_units.values())  # Track initial 7 units
        self.leftover_unit = None  # Stores the last remaining unit after Turn 2
        self.turn_count = 0
        
        print(f"\n{Fore.YELLOW}=== Rotation Manager Initialized ===")
        print(f"All Units: {[unit.number for unit in self.initial_pool]}")
        print(f"Unit Priorities: {[f'{u.number}(P:{u.priority})' for u in self.initial_pool]}{Style.RESET_ALL}")

    def get_effective_priority(self, unit):
        """Applies priority adjustments (e.g. transformed Unit 6)"""
        priority = unit.priority
        if unit.number == 6 and getattr(unit, 'transformed', False):
            print(f"{Fore.BLUE}Unit 6 transformed! Priority {priority}->{3}{Style.RESET_ALL}")
            return 3
        return priority

    def get_auto_rotation(self):
        self.turn_count += 1
        current_units = []
        
        print(f"\n{Fore.CYAN}=== Turn {self.turn_count} ===")
        print(f"Rotation History: {[ [u.number for u in rot] for rot in self.rotation_history]}")

        # --- Rotation Selection Logic ---
        if self.turn_count == 1:
            print(f"{Fore.GREEN}Selecting 3 random units from initial pool{Style.RESET_ALL}")
            current_units = random.sample(self.initial_pool, 3)
            self.initial_pool = [u for u in self.initial_pool if u not in current_units]
            print(f"Selected: {[u.number for u in current_units]}")
            print(f"Remaining Pool: {[u.number for u in self.initial_pool]}")
            
        elif self.turn_count == 2:
            print(f"{Fore.GREEN}Selecting 3 units from remaining pool{Style.RESET_ALL}")
            current_units = random.sample(self.initial_pool, 3)
            self.leftover_unit = [u for u in self.initial_pool if u not in current_units][0]
            print(f"Selected: {[u.number for u in current_units]}")
            print(f"{Fore.MAGENTA}Leftover Unit: {self.leftover_unit.number}{Style.RESET_ALL}")
            
        elif self.turn_count == 3:
            print(f"{Fore.GREEN}Using first 2 from Turn 1 + leftover unit{Style.RESET_ALL}")
            if len(self.rotation_history) >= 1:
                current_units = self.rotation_history[0][:2] + [self.leftover_unit]
                print(f"First two from Turn 1: {[u.number for u in self.rotation_history[0][:2]]}")
                print(f"Added leftover unit: {self.leftover_unit.number}")
                
        else:
            print(f"{Fore.GREEN}Cycling pattern: first two from (n-2) + last from (n-3){Style.RESET_ALL}")
            if len(self.rotation_history) >= 3:
                current_units = self.rotation_history[-2][:2] + [self.rotation_history[-3][-1]]
                print(f"First two from Turn {self.turn_count-2}: {[u.number for u in self.rotation_history[-2][:2]]}")
                print(f"Last from Turn {self.turn_count-3}: {self.rotation_history[-3][-1].number}")

        # --- Priority Sorting ---
        print(f"\n{Fore.YELLOW}Pre-sort units: {[u.number for u in current_units]}")
        current_units_sorted = sorted(current_units, key=lambda u: self.get_effective_priority(u))
        print(f"Effective priorities: {[f'{u.number}(P:{self.get_effective_priority(u)})' for u in current_units_sorted]}")
        
        # Special Rule: Force Gohan kid to slot 6 when with Caulifa
        unit_numbers = [u.name for u in current_units_sorted]
        print(f"\n{Fore.MAGENTA}Current Units: {[u.name for u in current_units_sorted]}{Style.RESET_ALL}")
        if "Gohan (Kid)" in unit_numbers and "Caulifla" in unit_numbers:
            print(f"{Fore.RED}Applying special rule: Gohan (Kid) forced to slot 6{Style.RESET_ALL}")
            unit5 = next(u for u in current_units_sorted if u.name == "Gohan (Kid)")
            current_units_sorted.remove(unit5)
            current_units_sorted.append(unit5)
            print(f"New order: {[u.name for u in current_units_sorted]}")

        # --- Finalize Rotation ---
        self.rotation_history.append(current_units_sorted)
        
        print(f"\n{Fore.GREEN}Final Rotation: [_, {current_units_sorted[0].number}, _, {current_units_sorted[1].number}, _, {current_units_sorted[2].number}, _]")
        print(f"{Fore.MAGENTA}Cooldown Tracking:")
        print(f"- Slot 2 (Unit {current_units_sorted[0].number}): {'1 turn' if current_units_sorted[0].number in [2,4] else 'No cooldown'}")
        print(f"- Slot 4 (Unit {current_units_sorted[1].number}): {'1 turn' if current_units_sorted[1].number in [2,4] else 'No cooldown'}")
        print(f"- Slot 6 (Unit {current_units_sorted[2].number}): {'2 turns' if current_units_sorted[2].number == 6 else 'No cooldown'}{Style.RESET_ALL}")
        
        return current_units_sorted

def load_units_from_json(json_file):
    global CURRENT_JSON_PATH
    CURRENT_JSON_PATH = json_file  # Store the path

    with open(json_file, 'r') as file:
        data = json.load(file)
    team = []

    for unit_data in data:
      
    # Initialize default values for sa_multiplier_12 and sa_multiplier_18
        sa_multiplier_12 = ""  # Default value if not used
        sa_multiplier_18 = ""  # Default value if not used
        sa_effect_12 = ""  # Default value if not used
        sa_effect_18 = ""  # Default value if not used

        eza_passive = unit_data.get("ezaLeaderSkill", None)

        if not eza_passive == None:
            if unit_data['rarity'] == "LR":
                # Get SA multipliers, considering 12 Ki and 18 Ki for LRs
                sa_multiplier_18 = get_sa_multiplier_from_text(unit_data["ezaUltraSuperAttack"], eza=True)
                sa_effect_18 = get_sa_effects(unit_data["ezaUltraSuperAttack"])
                sa_multiplier_12 = get_sa_multiplier_from_text(unit_data["ezaSuperAttack"], eza=True)
                sa_effect_12 = get_sa_effects(unit_data["ezaSuperAttack"])
            else:
                sa_multiplier_12 = get_sa_multiplier_from_text(unit_data["ezaSuperAttack"], eza=True)
                sa_effect_12 = get_sa_effects(unit_data["ezaSuperAttack"])
        else:
            if unit_data["rarity"] == "LR":
                sa_multiplier_18 = get_sa_multiplier_from_text(unit_data["ultraSuperAttack"])
                sa_effect_18 = get_sa_effects(unit_data["ultraSuperAttack"])
                sa_multiplier_12 = get_sa_multiplier_from_text(unit_data["superAttack"])
                sa_effect_12 = get_sa_effects(unit_data["superAttack"])
            else:
                sa_multiplier_12 = get_sa_multiplier_from_text(unit_data["superAttack"])
                sa_effect_12 = get_sa_effects(unit_data["superAttack"])

        unit = Unit(
            id=unit_data["id"],
            name=unit_data["name"],
            priority=unit_data["priority"],
            image=unit_data.get("image"),
            leaderskill=unit_data.get("leaderSkill") or unit_data.get("ezaLeaderSkill"),
            character_type=unit_data["type"],
            character_class=unit_data["class"],
            defense=unit_data["rainbowDefence"],
            attack=unit_data["rainbowAttack"],
            hp=unit_data["rainbowHP"],
            ki_multiplier=unit_data.get("kiMultiplier"),
            links=unit_data.get("links"),
            sa_12_multiplier=sa_multiplier_12,
            sa_18_multiplier=sa_multiplier_18,
            sa_12_effects=sa_effect_12,
            sa_18_effects=sa_effect_18,
            categories=unit_data.get("categories"),
            rarity=unit_data.get("rarity"),
            buffs=unit_data.get("buffs"),
            active_skill=unit_data.get("activeSkill"),
            active_skill_condition=unit_data.get("activeSkillCondition"),
            active_skill_code_condition=unit_data.get("activeSkillCodeCondition"),
            active_skill_buffs=unit_data.get("activeSkillBuffs"),
            transformed=False,
            transformations=unit_data.get("transformations"),
        )

        unit.load_image(unit_data.get("imageURL"))
        team.append(unit)
    # Add a 'number' attribute to each unit for easier reference (1-7)
    for i, unit in enumerate(team, start=1):
        unit.number = i
    
    return team

# Function to load bosses from JSON
def load_bosses_from_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    bosses = []
    for boss_data in data:
        boss_sa_multi = get_boss_sa_multipliers(boss_data["sa-multi"])

        # Create the boss instance
        boss = Boss(
            name=boss_data["name"],
            image=boss_data["image"],
            imageURL=boss_data["imageURL"],
            boss_class=boss_data["class"],
            boss_type=boss_data["type"],
            hp=boss_data["baseHP"],
            attack=boss_data["baseAttack"],
            defense=boss_data["baseDefence"],
            damage_reduction=boss_data["damageReduction"],
            atk_per_turn=boss_data["atk/turn"],
            sa_percent=boss_data["sa-percent"],
            sa_multi=boss_sa_multi,
            sa_effect=boss_data["sa-effect"],
            sa_atk=boss_data["sa-atk"],
            sa_per_turn=boss_data["sa/turn"],
            cooldown=boss_data["cooldown"],
            passive=boss_data["passive"],
            immunities={
                "stun": boss_data["stunImmun"],
                "seal": boss_data["sealImmun"],
                "atkReduction": boss_data["atkReductionImmun"],
                "defReduction": boss_data["defReductionImmun"]
            }
        )
        bosses.append(boss)
    
    return bosses
    
def apply_buff(char, name, value, duration, sot=False):
    """Apply a buff with a value and duration, stacking if already active."""
    if not hasattr(char, "passives"):
        char.passives = {}

    if name not in char.passives:
        char.passives[name] = []  # Ensure it's a list

    # If passives[name] was a dictionary instead of a list, convert it
    if isinstance(char.passives[name], dict):
        char.passives[name] = [char.passives[name]]

    # Ensure it is a list before appending
    if not isinstance(char.passives[name], list):
        raise TypeError(f"ERROR: Expected list for {name}, found {type(char.passives[name])} -> {char.passives[name]}")

    # Check if the same buff is already applied in this turn
    for existing_buff in char.passives[name]:
        if existing_buff["value"] == value and existing_buff["is_sot"] == True:
            return  # Avoid adding duplicate buffs
    # Add the new buff to the list of active buffs
    if sot:
        char.passives[name].append({"value": value, "duration": duration, "is_sot": True})
    else:
        char.passives[name].append({"value": value, "duration": duration, "is_sot": False})

def update_buffs(char):
    """Update all buffs, decrementing their durations and removing expired ones."""
    for name in list(char.passives.keys()):
        updated_buffs = []
        for buff in char.passives[name]:
            if buff.get("duration",None) == None:
                continue
            else:  
                buff["duration"] -= 1
                if buff["duration"] > 0:
                    updated_buffs.append(buff)
        if updated_buffs:
            char.passives[name] = updated_buffs
        else:
            del char.passives[name] # Remove buff if no active instances remain
            print(f"{Fore.RED}{char.name}'s {name} has expired.")

def apply_debuff(char, name, value, duration):
    """Apply a debuff with a value and duration, stacking if already active."""
    if name not in char.debuffs:
        char.debuffs[name] = []

    # Add the new debuff to the list of active debuffs
    char.debuffs[name].append({"value": value, "duration": duration})

def update_debuffs(char):
    """Update all debuffs, decrementing their durations and removing expired ones."""
    for name in list(char.debuffs.keys()):
        updated_debuffs = []
        for debuff in char.debuffs[name]:
            debuff["duration"] -= 1
            if debuff["duration"] > 0:
                updated_debuffs.append(debuff)
        if updated_debuffs:
            char.debuffs[name] = updated_debuffs
        else:
            del char.debuffs[name]  # Remove debuff if no active instances remain
            print(f"{Fore.RED}{char.name}'s {char.debuffs[name]} has expired.")

def get_buffs_and_debuffs_from_super(char, ki):
    debuffs = {"atk_debuff": 0, "def_debuff": 0}
    sa_buffs = {"temp_sa_atk_boost": 0, "temp_sa_def_boost": 0, "perm_sa_atk_boost": 0, "perm_sa_def_boost": 0}

    if ki >= 18:
        debuffs["def_debuff"] = char.sa_18_effects.get("enemy_def_debuff", 0)
        debuffs["atk_debuff"] = char.sa_18_effects.get("enemy_atk_debuff", 0)
        if char.transformed:
            sa_buffs["temp_sa_atk_boost"] = char.sa_18_effects.get("temporary_atk_multiplier", 0)
            sa_buffs["temp_sa_def_boost"] = char.sa_18_effects.get("temporary_def_multiplier", 0)
            sa_buffs["perm_sa_atk_boost"] = char.sa_18_effects.get("permanent_atk_multiplier", 0)
            sa_buffs["perm_sa_def_boost"] = char.sa_18_effects.get("permanent_def_multiplier", 0)
        sa_buffs["temp_sa_atk_boost"] = char.sa_18_effects.get("temporary_atk_multiplier", 0)
        sa_buffs["temp_sa_def_boost"] = char.sa_18_effects.get("temporary_def_multiplier", 0)
        sa_buffs["perm_sa_atk_boost"] = char.sa_18_effects.get("permanent_atk_multiplier", 0)
        sa_buffs["perm_sa_def_boost"] = char.sa_18_effects.get("permanent_def_multiplier", 0)
    elif ki >= 12:
        debuffs["def_debuff"] = char.sa_12_effects.get("enemy_def_debuff", 0)
        debuffs["atk_debuff"] = char.sa_12_effects.get("enemy_atk_debuff", 0)
        sa_buffs["temp_sa_atk_boost"] = char.sa_12_effects.get("temporary_atk_multiplier", 0)
        sa_buffs["temp_sa_def_boost"] = char.sa_12_effects.get("temporary_def_multiplier", 0)
        sa_buffs["perm_sa_atk_boost"] = char.sa_12_effects.get("permanent_atk_multiplier", 0)
        sa_buffs["perm_sa_def_boost"] = char.sa_12_effects.get("permanent_def_multiplier", 0)
    
    print(f"Defense Debuff: {debuffs['def_debuff']}, Attack Debuff: {debuffs['atk_debuff']}")
    print(f"Temporary Attack Buff: {sa_buffs['temp_sa_atk_boost']}, Temporary Defense Buff: {sa_buffs['temp_sa_def_boost']}")
    print(f"Permanent Attack Buff: {sa_buffs['perm_sa_atk_boost']}, Permanent Defense Buff: {sa_buffs['perm_sa_def_boost']}")
    return debuffs, sa_buffs


def buff_debuff_duration(char):
    """Reduce Buff Duration and remove expired buffs."""
    expired_buffs = []
    expired_debuffs = []

    for buff_name, buff_details in char.buffs.items():  
        # Ensure 'duration' exists, default to 0 if missing
        duration = buff_details.get("duration", 0)

        if buff_details.get("is_sot", False):
            continue  # Skip reducing duration for SOT buffs
        
        # Decrease the duration
        buff_details["duration"] = duration - 1

        if buff_details["duration"] <= 0:
            expired_buffs.append(buff_name)

    # Remove expired buffs outside the iteration
    for buff_name in expired_buffs:
        del char.buffs[buff_name]
        print(f"{Fore.RED}{char.name}'s {buff_name} has expired.")

    for debuff_name, debuff_details in char.debuffs.items():
        duration = debuff_details.get("duration", 0)
        debuff_details["duration"] = duration - 1
        if debuff_details["duration"] <= 0:
            expired_debuffs.append(debuff_name)

    for debuff_name in expired_debuffs:
        del char.debuffs[debuff_name]
        print(f"{Fore.GREEN}{char.name}'s {debuff_name} has expired.")


def parse_leader_skill(leaderskill):
    # Regular expression pattern to match the leader skill string
    pattern = r'\"([^\"]+)\" Category Ki \+(\d+), ATK \+(\d+)% and HP & DEF \+(\d+)%'

    # Find all matches in the leader skill string
    matches = re.findall(pattern, leaderskill)
   
    # Initialize the dictionaries for category multipliers
    categories_and_multipliers = {}

    # Loop through all matches and extract the data
    for match in matches:
        category_name, ki_value, atk_value, hp_def_value = match
        categories_and_multipliers[category_name.lower()] = {
            'ki_multiplier': int(ki_value),
            'atk_multiplier': int(atk_value),
            'hp_multiplier': int(hp_def_value),
            'def_multiplier': int(hp_def_value)  # HP and DEF have the same multiplier in this case
        }

    # Return the categories and their multipliers as a list of tuples (for easier access)
    return categories_and_multipliers

def apply_leader_skill_multipliers(team, leaderskill):
    # Parse the leader skill to get category multipliers
    categories_and_multipliers = parse_leader_skill(leaderskill)

    # Loop through the units in the team and apply the correct multipliers
    for unit in team:
        # Default multipliers
        unit_ki_mulitplier = 0
        unit_atk_multiplier = 0
        unit_hp_multiplier = 0
        unit_def_multiplier = 0

        # Iterate over the categories in categories_and_multipliers in order
        for category_key in categories_and_multipliers:
            # Check if the unit's categories list contains this key
            if category_key.lower() in [category.lower() for category in unit.categories]:
                # If a match is found, apply the multipliers
                multipliers = categories_and_multipliers[category_key]
                unit_ki_mulitplier = multipliers['ki_multiplier']
                unit_atk_multiplier = multipliers['atk_multiplier']
                unit_hp_multiplier = multipliers['hp_multiplier']
                unit_def_multiplier = multipliers['def_multiplier']
                
                # Stop checking further categories as we found a match
                break

        # Set the multipliers for this unit
        unit.leaderskill_ki_multiplier = unit_ki_mulitplier * 2
        unit.leaderskill_atk_multiplier = (unit_atk_multiplier / 100) * 2 + 1
        unit.leaderskill_hp_multiplier = (unit_hp_multiplier / 100) * 2 + 1
        unit.leaderskill_def_multiplier = (unit_def_multiplier / 100) * 2 + 1

    return

def apply_conditional_buffs(char, team_hp, position, sot=True):
    for buff_name, buff_details in char.buffs.items():
        if "conditional" in buff_name:
            condition = buff_details.get("condition")
            value = buff_details.get("value")
            is_sot = buff_details.get("is_sot", False)
            duration = buff_details.get("duration", 1)
            limit = buff_details.get("limit", None)  # Get limit (None if no limit is set)

            # Debug print to check limit before applying the buff
            print(f"Checking {buff_name}: Initial limit is {limit}")
            print(f"Condition: {condition}, Value: {value}, Duration: {duration}, Limit: {limit}, sot: {is_sot}")

            # Check if the condition is met (for both SOT and non-SOT)
            condition_met = False
            if condition == "Slot 1" and position == 1:
                condition_met = True
            elif condition == "Slot 2" and position == 2:
                condition_met = True
            elif condition == "HP <= 30%" and team_hp <= 0.3:
                condition_met = True
            elif condition == "for 1 turn after Awakening" and char.transformed:
                condition_met = True

            # If condition is met, proceed to apply the buff
            if condition_met:
                # Handle start-of-turn (SOT) buffs
                if sot:
                    if is_sot:  # Apply if it's marked as a start-of-turn buff
                        if limit is not None:  # Check if a limit is set
                            if limit > 0:  # Apply if limit is greater than 0
                                apply_buff(char, buff_name, value, duration, sot=True)
                                buff_details["limit"] = limit - 1  # Decrease limit after applying
                                print(f"Applied {buff_name} with value {value} (limit remaining: {buff_details['limit']})")
                            else:
                                print(f"Limit reached for {buff_name}, buff will not be applied.")
                        else:  # No limit, so apply the buff every time
                            apply_buff(char, buff_name, value, duration, sot=True)
                            print(f"Applied {buff_name} with value {value} (no limit)")

                # If it's not a start-of-turn buff, apply it normally without a limit
                else:
                    if not is_sot:  # Apply non-SOT buffs here
                        if limit is not None:  # Check if a limit is set
                            if limit > 0:  # Apply if limit is greater than 0
                                apply_buff(char, buff_name, value, duration, sot=False)
                                buff_details["limit"] = limit - 1  # Decrease limit after applying
                                print(f"Applied {buff_name} with value {value} (limit remaining: {buff_details['limit']})")
                            else:
                                print(f"Limit reached for {buff_name}, buff will not be applied.")
                        else:  # No limit, so apply the buff every time
                            apply_buff(char, buff_name, value, duration, sot=False)
                            print(f"Applied {buff_name} with value {value} (no limit)")
            else:
                print(f"Condition not met for {buff_name}, buff will not be applied.")

def apply_pre_sa_buffs(char, team_hp, position):
    """Apply buffs that trigger before the character attacks."""
    for buff_name, buff_details in char.buffs.items():
        if "buff" in buff_name and not "buffs" in buff_name:
            apply_buff(char, buff_name, buff_details["value"], 99, sot=True)
        if "atk_per_ki_sphere" in buff_name:
            apply_buff(char, buff_name, buff_details["value"] * char.ki_gained, 1, sot=True)
        if "def_per_ki_sphere" in buff_name:
            apply_buff(char, buff_name, buff_details["value"] * char.ki_gained, 1, sot=True)
        if "ki_per_ki_sphere" in buff_name:
            apply_buff(char, buff_name, buff_details["value"] * char.ki_gained, 1, sot=True)
    apply_conditional_buffs(char, team_hp, position)
    print(f"{char.passives}")


def apply_after_sa_buffs(char):
    """Apply buffs that trigger when the character attacks."""
    atk_limit = False
    def_limit = False
    ki_limit = False  
    for buff_name, buff_details in char.buffs.items():
        if "additional_atk_boost" in buff_name and buff_details.get("condition") == "attack":
            if buff_details.get("reset", True) == False:  # Default to True if missing
                if buff_details.get("limit", 0) != 0:  # Default to 0 if missing
                    buff_details["limit"] -= 1
                    apply_buff(char, buff_name, buff_details["value"], 99)
                else:
                    print(f"Limit reached")
                    atk_limit = True
            else:
                apply_buff(char, buff_name, buff_details["value"], 1)
                

        if "additional_def_boost" in buff_name and buff_details.get("condition") == "attack":
            if buff_details.get("reset", True) == False:
                if buff_details.get("limit", 0) != 0:
                    buff_details["limit"] -= 1
                    apply_buff(char, buff_name, buff_details["value"], 99)
                else:
                    print(f"Limit reached")
                    def_limit = True
            else:
                apply_buff(char, buff_name, buff_details["value"], 1)


        if "additional_ki_boost" in buff_name and buff_details.get("condition") == "attack":
            if buff_details.get("reset", True) == False:
                if buff_details.get("limit", 0) != 0:
                    buff_details["limit"] -= 1
                    apply_buff(char, buff_name, buff_details["value"], 99)
                else:
                    print(f"Limit reached")
                    ki_limit = True
            else:
                apply_buff(char, buff_name, buff_details["value"], 1)

        if "additional_atk_boost_on_18_ki_super" in buff_name and char.ki >= 18:
            apply_buff(char, buff_name, buff_details["value"], 1)


        if "guard_atk_boost" in buff_name and char.guard_activations >= 1:
            apply_buff(char, buff_name, buff_details["value"], buff_details["duration"])
           
    print(f"{char.passives}")

    return atk_limit, def_limit, ki_limit

def check_revive(char, team_hp):
    """Check if the character has a revive passive and apply it if conditions are met."""
    for buff_name, buff_details in char.buffs.items():
        if "revive" in buff_name:
            if "HP is 50%" in buff_details.get("condition"):
                if team_hp <= 0.5 and char.hits_taken >= 1:
                    char.revive = True
                    print(f"{char.name}'s revive is now active because hp is under 50%.")
            elif "HP is 30%" in buff_details.get("condition"):
                if team_hp <= 0.3 and char.hits_taken >= 5:
                    char.revive = True
                    print(f"{char.name}'s revive is now active because hp is under 30%.")

def get_ki_multiplier_random(char):
    # Define the max ki for each rarity
    max_ki = 12 if char.rarity.upper() == "UR" else 24
    initial_ki = char.ki

    if initial_ki >= max_ki:
        ki =  initial_ki  # If already at max ki, return the initial ki
    
    else:
        # Define range
        ki_values = list(range(1, 23))

        # Define weights based on distance from 6
        weights = [max(1, 23 - abs(6 - i)) for i in ki_values]

        # Generate a random ki based on the new weight distribution
        random_ki = random.choices(ki_values, weights=weights)[0]
        print(f"Random Ki: {random_ki}")

        if "ki_per_ki_sphere" in char.buffs:
            print("Random ki doubled due to per ki sphere buff.")
            ki = initial_ki + (random_ki * 2)
            char.ki = ki
        else:
            ki = initial_ki + random_ki
            char.ki = ki
        if char.rarity.upper() == "UR" and ki >= 12:
            ki = 12
            char.ki = ki
        elif char.rarity.upper() == "LR" and ki >= 24:
            ki = 24
            char.ki = ki   
        char.ki_gained = random_ki

    # Check the character's rarity and Ki conditions
    if char.rarity == "UR":
        if ki > 12:
            raise ValueError("UR character cannot have more than 12 Ki.")  # Raise error if Ki > 12 for UR
        elif ki < 12:
            ki_multiplier = 100
        else:
            match = re.search(r'12 Ki Multiplier is (\d+)%', char.ki_multiplier)
            if match:
                ki_multiplier = int(match.group(1))  # Get the numeric part as an integer
    elif char.rarity == "LR":
        if ki > 24:
            raise ValueError("LR character cannot have more than 24 Ki.")  # Raise error if Ki > 24 for LR
        elif ki == 24:
            ki_multiplier = 200
        elif ki == 12:
            match = re.search(r'12 Ki Multiplier is (\d+)%', char.ki_multiplier)
            if match:
                ki_multiplier = int(match.group(1))  # Get the numeric part as an integer
        elif 12 < ki < 24:
            match = re.search(r'12 Ki Multiplier is (\d+)%', char.ki_multiplier)
            if match:
                temp_ki_multiplier = int(match.group(1))  # Get the numeric part as an integer
            ki_multiplier = ((200 - temp_ki_multiplier) / 12) * (ki - 12) + temp_ki_multiplier
        elif ki < 12:
            ki_multiplier = 100

    return ki_multiplier / 100  # Return the Ki multiplier and Ki value

def print_buffs_debuffs(char):
    """Print active buffs and debuffs for a character."""
    active_buffs = "None"
    active_debuffs = "None"

    if char.passives:
        grouped_buffs = {}

        # Group buffs by name, summing values and keeping the last duration
        for name, details_list in char.passives.items():
            total_value = sum(details["value"] for details in details_list if "value" in details)
            last_duration = details_list[-1]["duration"] if "duration" in details_list[-1] else None
            is_sot = any(details.get("is_sot", False) for details in details_list)

            grouped_buffs[name] = {"value": total_value, "duration": last_duration, "is_sot": is_sot}

        # Format the buffs as a string
        active_buffs = ", ".join(
            f"{name} ({buff['value'], buff['duration']} turns)"
            if name == "additional_ki_boost" or name == "ki_buff" or name == "conditional_ki_boost"
            else f"{name} ({buff['value'] * 100:.0f}%, {buff['duration']} turns)"
            for name, buff in grouped_buffs.items()
        )


    # Process debuffs
    if char.debuffs:
        active_debuffs = ", ".join(
            [
                f"{name} ({((details['value']) * 100):.0f}%, {details['duration']} turns)"
                if "duration" in details
                else f"{name} ({((details['value']) * 100):.0f}%)"
                for name, details_list in char.debuffs.items()
                for details in details_list  # Iterate over list of dictionaries
                if isinstance(details, dict) and "value" in details  # Ensure 'details' is a dictionary and has 'value'
            ]
        )

    # Print the result
    print(f"{char.name}: {Fore.GREEN}{active_buffs}{Style.RESET_ALL}, {Fore.RED}{active_debuffs}{Style.RESET_ALL}")

def get_total_hp(team):
    """Calculate the total HP of the team."""
    return int(round(sum((unit.hp * unit.leaderskill_hp_multiplier) for unit in team),2))

# Global rotation manager (initialize it once at the start of the simulation)
rotation_manager = None

def get_active_rotation(team):
    global rotation_manager
    if rotation_manager is None:
        rotation_manager = RotationManager(team)
    return rotation_manager.get_auto_rotation()

def check_active_skill_condition(condition_str, current_hp, current_turn):
    # Define the pattern for conditions (e.g., HP <= 59% and Turn 3)
    hp_pattern = r"HP\s*<=\s*(\d+)%|HP\s*>=\s*(\d+)%"
    turn_pattern = r"Turn\s*(\d+)"
    print(f"Checking active skill condition: {condition_str}")
    print(f"Current HP: {current_hp}, Current Turn: {current_turn}")
    # Initialize condition flags
    hp_condition_met = True
    turn_condition_met = True
    is_and_condition = "and" in condition_str.lower()  # Check if "and" exists for AND condition

    # Check for HP condition
    hp_match = re.search(hp_pattern, condition_str)
    if hp_match:
        # HP condition is present, extract and compare
        if hp_match.group(1):  # HP <= condition
            hp_limit = int(hp_match.group(1))/100
            if current_hp > hp_limit:
                hp_condition_met = False

    # Check for Turn condition
    turn_match = re.search(turn_pattern, condition_str)
    if turn_match:
        # Turn condition is present, extract and compare
        turn_limit = int(turn_match.group(1))
        if current_turn < turn_limit:
            turn_condition_met = False

    # Determine if the conditions are met based on AND/OR logic
    if is_and_condition:
        # If "and" exists, both conditions must be met
        if hp_condition_met and turn_condition_met:
            return True
        else:
            if not hp_condition_met:
                print(f"Active skill condition not fulfilled: HP must be as per condition {hp_limit}.")
            if not turn_condition_met:
                print(f"Active skill condition not fulfilled: It must be Turn {turn_limit}.")
            return False

def generate_boss_attack_distribution(boss_max_attacks):
    """
    Generates a random distribution of boss attacks across fixed positions.

    :param boss_max_attacks: Fixed number of attacks the boss must perform in a turn.
    :return: A dictionary representing the number of attacks in each position.
    """
    boss_positions = [1, 3, 5, 7]  # Boss can attack in these positions
    boss_attack_distribution = {position: 0 for position in boss_positions}  # Initialize distribution

    # Randomly distribute boss attacks across available positions
    for _ in range(boss_max_attacks):
        position = random.choice(boss_positions)
        boss_attack_distribution[position] += 1

    return boss_attack_distribution

def resolve_boss_attacks(boss_attack_distribution, boss_sa_percent, boss_max_sa, boss_cooldown, current_cooldown):
    """
    Resolves boss attacks by determining which attacks are super attacks.

    :param boss_attack_distribution: Dictionary of attacks per position.
    :param boss_sa_percent: Percentage chance for each boss attack to be a super attack.
    :param boss_max_sa: Fixed maximum number of super attacks the boss can perform in a turn.
    :param boss_cooldown: Cooldown period for boss super attacks.
    :return: A list representing the resolved boss attacks.
    """
    resolved_attacks = []
    boss_sa_used = 0
    print(f"Current boss super cooldown: {current_cooldown}")
    for position, num_attacks in boss_attack_distribution.items():
        for _ in range(num_attacks):
            is_super = False
            if current_cooldown <= 0 and boss_sa_used < boss_max_sa and random.random() < (boss_sa_percent / 100):
                is_super = True
                boss_sa_used += 1
                current_cooldown = boss_cooldown  # Reset cooldown after a super attack
            else:
                current_cooldown = max(0, current_cooldown - 1)  # Decrease cooldown for normal attacks

            resolved_attacks.append((position, "super" if is_super else "normal"))

    return resolved_attacks, current_cooldown

def build_attack_pattern(rotation, boss_attack_distribution, resolved_boss_attacks, active_skill=False):
    """
    Builds the full attack pattern by combining unit attacks and resolved boss attacks.

    :param rotation: List of units in the current rotation (slot1, slot2, slot3).
    :param boss_attack_distribution: Dictionary of attacks per position.
    :param resolved_boss_attacks: List of resolved boss attacks (position, attack type).
    :return: A list representing the full attack pattern.
    """
    attack_pattern = []
    unit_positions = {2: rotation[0].number, 4: rotation[1].number, 6: rotation[2].number}  # Unit positions

    # Iterate through positions 1 to 7
    for position in range(1, 8):
        if position in boss_attack_distribution:
            # Add resolved boss attacks for this position
            for attack in resolved_boss_attacks:
                if attack[0] == position:
                    if position == 1:
                        attack_pattern.append(("boss", attack[1], rotation[0].number))
                    else:
                        attack_pattern.append(("boss", attack[1], unit_positions.get(position - 1, None)))
        else:
            # Add unit attack for this position
            unit_number = unit_positions.get(position, None)
            if unit_number:
                if active_skill:
                    attack_pattern.insert(0,((str(unit_number), "active", "boss")))
                    attack_pattern.append((str(unit_number), "attacks", "boss"))
                else:
                    attack_pattern.append((str(unit_number), "attacks", "boss"))

    return attack_pattern,1

def generate_attack_pattern(rotation, boss_max_attacks, boss_sa_percent, boss_max_sa, boss_cooldown):
    """
    Generates a random attack pattern with boss attacks distributed across fixed positions.

    :param rotation: List of units in the current rotation (slot1, slot2, slot3).
    :param boss_max_attacks: Fixed number of attacks the boss must perform in a turn.
    :param boss_sa_percent: Percentage chance for each boss attack to be a super attack.
    :param boss_max_sa: Fixed maximum number of super attacks the boss can perform in a turn.
    :param boss_cooldown: Cooldown period for boss super attacks.
    :return: A list representing the attack pattern.
    """
    attack_pattern = []
    boss_attacks_used = 0
    boss_sa_used = 0
    current_cooldown = 0  # Tracks the cooldown for super attacks

    # Fixed positions for boss and unit attacks
    boss_positions = [1, 3, 5, 7]  # Boss can attack in these positions
    unit_positions = [2, 4, 6]     # Units attack in these positions

    # Randomly distribute boss attacks across available positions
    boss_attack_distribution = [0] * len(boss_positions)  # Initialize distribution
    for _ in range(boss_max_attacks):
        # Randomly choose a position to add an attack
        position_index = random.randint(0, len(boss_positions) - 1)
        boss_attack_distribution[position_index] += 1

    # Build the attack pattern
    for position in range(1, 8):  # Positions 1 to 7
        if position in boss_positions:
            # Add boss attacks for this position
            position_index = boss_positions.index(position)
            num_attacks = boss_attack_distribution[position_index]
            for _ in range(num_attacks):
                # Determine if this is a super attack
                is_super = False
                if current_cooldown <= 0 and boss_sa_used < boss_max_sa and random.random() < (boss_sa_percent / 100):
                    is_super = True
                    boss_sa_used += 1
                    current_cooldown = boss_cooldown  # Reset cooldown after a super attack
                else:
                    current_cooldown = max(0, current_cooldown - 1)  # Decrease cooldown for normal attacks

                # Determine the target based on the position
                if position == 1:
                    target = rotation[0].number  # Before slot1: target slot1
                elif position == 3:
                    target = rotation[0].number  # After slot1: target slot1
                elif position == 5:
                    target = rotation[1].number  # After slot2: target slot2
                elif position == 7:
                    target = rotation[2].number  # After slot3: target slot3

                # Add the boss attack to the sequence
                attack_pattern.append(("boss", "super" if is_super else "normal", target))
                boss_attacks_used += 1
        else:
            # Add unit attack for this position
            unit_index = unit_positions.index(position)
            attack_pattern.append((str(rotation[unit_index].number), "normal", "boss"))

    return attack_pattern,1

def execute_attack_pattern(rotation, boss, attack_pattern, active_damage_multiplier, max_team_hp, team_hp, max_boss_hp, rounds, item_used):
    max_team_hp = max_team_hp

    def log_and_apply_debuff(target, debuffs, duration, unit_name):
        for debuff_type, value in debuffs.items():
            if value > 0:  # Only apply debuffs with non-zero values
                apply_debuff(target, debuff_type, value, duration)
                print(f"{Fore.RED}{unit_name} lowered the {debuff_type} of {target.name} by {value * 100:.0f}% for {duration} turns!{Style.RESET_ALL}")

    def log_and_apply_sa_def_buffs(unit, sa_def_buffs):
        for buff, value in sa_def_buffs.items():
            if value > 0:
                if buff == "perm_sa_atk_boost":
                    print(f"{Fore.GREEN}{unit.name} raised the {buff} by {value * 100:.0f}% for {99} turns!{Style.RESET_ALL}")
  
                elif buff == "temp_sa_atk_boost":
                    print(f"{Fore.GREEN}{unit.name} raised the {buff} by {value * 100:.0f}% for {1} turns!{Style.RESET_ALL}")
 
                if buff == "perm_sa_def_boost":
                    unit.effective_defense *= (1 + value)
                    apply_buff(unit, buff, value, 99)
                    print(f"{Fore.GREEN}{unit.name} raised the {buff} by {value * 100:.0f}% for {99} turns!{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}{unit.name}'s effective defense is now {unit.effective_defense:.0f}{Style.RESET_ALL}")
  
                elif buff == "temp_sa_def_boost":
                    unit.effective_defense *= (1 + value)
                    apply_buff(unit, buff, value, 1)
                    print(f"{Fore.GREEN}{unit.name} raised the {buff} by {value * 100:.0f}% for {1} turns!{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}{unit.name}'s effective defense is now {unit.effective_defense:.0f}{Style.RESET_ALL}")

    def log_and_apply_buff(unit):
    # Apply additional buffs if there are any
        atk_limit, def_limit, ki_limit = apply_after_sa_buffs(unit)
        
        log_message = ""
        total_message = ""
        # Iterate over all buff types in the passives dictionary
        for buff_type, buffs in unit.passives.items():
            if buff_type == "additional_atk_boost" or buff_type == "additional_def_boost" or buff_type == "additional_ki_boost":
                if not buffs:  # If no buffs exist for this buff_type, skip it
                    continue

                # Log and apply each buff in the list for the given buff_type
                total_value = sum(buff["value"] for buff in buffs)  # Total of all buff values for this type

                 # Apply the latest buff sequentially
                latest_buff = buffs[-1]  # Get the latest (last) buff in the list
                latest_value = latest_buff["value"]
                duration = latest_buff["duration"]

                # Determine the print format based on buff_type
                if buff_type == "additional_ki_boost":
                    if ki_limit:
                        total_message = f"• Max for additional ki boost reached at {total_value}\n"
                    else:
                        unit.additional_ki_boost_this_turn = True
                        log_message = f"{unit.name} gained {latest_value} additional Ki for {duration} turns!\n"
                        unit.ki += latest_value
                        if unit.rarity == "LR" and unit.ki > 24:
                            unit.ki = 24
                        elif unit.rarity == "UR" and unit.ki > 12:
                            unit.ki = 12
                        log_message += f"{unit.name}'s Ki is now {unit.ki}"
                        total_message = f"Total {buff_type} boost: {total_value}"
                elif buff_type == "additional_def_boost":
                    if def_limit:
                        log_message = f"{unit.name}'s effective defense is now {unit.effective_defense:.0f}"
                        total_message = f"• Max for additional defense boost reached at {total_value*100:.0f}%\n"
                    else:
                        unit.additional_def_boost_this_turn = True
                        unit.effective_defense *= (1 + latest_value)
                        log_message = f"{unit.name} raised the {buff_type} by {latest_value * 100:.0f}% for {duration} turns!\n"
                        log_message += f"{unit.name}'s effective defense is now {unit.effective_defense:.0f}"
                        total_message = f"Total {buff_type} boost: {total_value * 100:.0f}%"
                else:
                    if atk_limit:
                        log_message = f"{unit.name}'s effective attack is now {unit.effective_attack:.0f}"
                        total_message = f"• Max for additional attack boost reached at {total_value*100:.0f}%\n"
                    else:
                        unit.additional_atk_boost_this_turn = True
                        unit.effective_attack *= (1 + latest_value)
                        log_message = f"{unit.name} raised the {buff_type} by {latest_value * 100:.0f}% for {duration} turns!\n"
                        log_message += f"{unit.name}'s effective attack is now {unit.effective_attack:.0f}"
                        total_message = f"Total {buff_type} boost: {total_value * 100:.0f}%"

                # Print and log the buff
                if log_message == "":
                    continue
                else:
                    print(f"{Fore.GREEN}{log_message}{Style.RESET_ALL}")

                # Print and log the total value
                if total_message == "":
                    continue
                else:
                    print(f"{Fore.GREEN}{total_message}{Style.RESET_ALL}")

    def handle_boss_attack(rotation, target_unit, attack_type, max_team_hp, team_hp):
        revived = False
        boss_power = boss.calculate_effective_attack(is_super=(attack_type == "super"))
        if target_unit.check_evasion():
            target_unit.dodges += 1
            target_unit.was_attacked_this_turn += 1
            target_unit.sim_evade_this_turn = True 
            print(f"{Fore.GREEN}{target_unit.name} evaded the attack!{Style.RESET_ALL}")

            for buff_name, buff_details in target_unit.buffs.items():
                if "additional_def_boost" in buff_name:
                    if target_unit.evaded_this_turn == False:
                        target_unit.additional_def_boost_this_turn = True
                        if "LLM" in buff_name:
                            target_unit.effective_defense *= (1 + buff_details["value"])
                            print(f"{Fore.GREEN}{target_unit.name}'s got an adjusted additional def boost of {buff_details['value'] * 100:.0f}%{Style.RESET_ALL}")
                        else:   
                            target_unit.effective_defense *= (1.2 + buff_details["value"])
                            print(f"{Fore.GREEN}{target_unit.name}'s got an additional def boost of {buff_details['value'] * 100:.0f}%{Style.RESET_ALL}")
                        print(f"{Fore.GREEN}{target_unit.name}'s got a def boost of {buff_details['value'] * 100:.0f}%{Style.RESET_ALL}")
          
                    target_unit.evaded_this_turn = True
                if "additional_ki_boost" in buff_name:
                    if target_unit.dodges <= 5:
                        target_unit.additional_ki_boost_this_turn = True
                        target_unit.ki += buff_details["value"]
                        apply_buff(target_unit, buff_name, buff_details["value"], 99)
                        print(f"{Fore.GREEN}{target_unit.name}'s got a ki boost of {buff_details['value']}{Style.RESET_ALL}")
    
        else:
            target_unit.hits_taken += 1
            target_unit.was_attacked_this_turn += 1
            if target_unit.check_guard():
                target_unit.guard_activations += 1
                target_unit.guard_this_turn = True
                target_unit.effective_attack *= 0.4
                damage = target_unit.calculate_damage_taken(boss, boss_power, 15, item_used, guard=True, is_super=(attack_type == "super"))
                print(f"{Fore.RED}{target_unit.name} activated guard!{Style.RESET_ALL}")

                print(f"{Fore.GREEN}{target_unit.name}'s attack goes up by 40% because of guard {Style.RESET_ALL}")
    
            else:
                damage = target_unit.calculate_damage_taken(boss, boss_power, 15, item_used, is_super=(attack_type == "super"))
                if "damage_reduction" in target_unit.buffs:
                    reduction = target_unit.buffs["damage_reduction"].get("value", 0)
                    print(f"{target_unit.name} has a damage reduction of {reduction * 100:.0f}%")
                    #Hard coded damage reduction original is 0.4, LLM Suggestion 0.3
                    if reduction > 0 and reduction < 0.3:
                        target_unit.buffs["damage_reduction"]["value"] = min(
                            target_unit.buffs["damage_reduction"]["value"] + 0.1, 0.3
                        )
                        print(f"{Fore.GREEN}{target_unit.name}'s damage reduction increased to {target_unit.buffs['damage_reduction']['value'] * 100:.0f}%!{Style.RESET_ALL}")

            target_unit.damage_taken_this_turn += damage
            team_hp -= damage
            if team_hp <= 0:
                print(f"{Fore.RED}Boss attacks {target_unit.name} with a {attack_type} attack, causing {damage} damage!{Style.RESET_ALL}")
                print(f"{Fore.RED}Team HP has dropped to 0! The team has been defeated!{Style.RESET_ALL}")
 
                revivable_units = [unit for unit in rotation if unit.revive and unit.has_revived == False]
                if len(revivable_units) > 0:
                    print(f"{Fore.GREEN}Team has been revived!{Style.RESET_ALL}")

                    revivable_unit = revivable_units[0]
                    print(f"[DEBUG]{revivable_unit.name}: {revivable_unit.buffs['revive']['effect']}")
                    if "70% HP" in revivable_unit.buffs["revive"]["effect"]:
                        print(f"[DEBUG]{revivable_unit.name} has revived with 70% HP!")
                        team_hp = int(max_team_hp * 0.7)
                    elif "50% HP" in revivable_unit.buffs["revive"]["effect"]:
                        print(f"[DEBUG]{revivable_unit.name} has revived with 50% HP!")
                        print(f"[DEBUG] Team HP after revival: {team_hp}")
                        print(f"[DEBUG] Max Team HP: {max_team_hp}")
                        team_hp = int(max_team_hp * 0.5)
                    revivable_units[0].has_revived = True
                    revived = True
                    print(f"[DEBUG] Team HP after revival: {team_hp}")
                    return team_hp, revived
                else:
                    team_hp = 0
                    return team_hp, revived
            else:
                print(f"{Fore.RED}Boss attacks {target_unit.name} with a {attack_type} attack, causing {damage} damage!{Style.RESET_ALL}")

                print(f"Team Total HP: {Fore.GREEN}{team_hp} ({math.floor((team_hp / max_team_hp) * 100)}%)")

        return team_hp, revived

    def perform_attack(attacker, ki, use_active_stat=False, active_multiplier=1):
        """Handles attacks, including Active Skills."""
        if use_active_stat:
            attack_stat = attacker.effective_attack * active_multiplier
            attacker.attacks += 1
            attacker.super_attacks += 1
            print(f"{Fore.GREEN}{attacker.name} launches an Active Skill!{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Active damage multiplier: {active_multiplier}{Style.RESET_ALL} -> {Fore.GREEN}Super Attack Stat: {attack_stat}{Style.RESET_ALL}")

        else:
            if ki >= 18:
                attack_stat = attacker.get_sa_multiplier(ki)[0]
                attacker.attacks += 1
                attacker.super_attacks += 1
                print(f"{Fore.GREEN}{attacker.name} launches an Ultra Super Attack!{Style.RESET_ALL}")

            elif ki >= 12:
                attack_stat = attacker.get_sa_multiplier(ki)[0]
                attacker.attacks += 1
                attacker.super_attacks += 1
                print(f"{Fore.GREEN}{attacker.name} launches a Super Attack!{Style.RESET_ALL}")
   
            else:
                attacker.attacks += 1
                attack_stat = attacker.effective_attack
                print(f"{Fore.GREEN}{attacker.name} launches a normal attack!{Style.RESET_ALL}")


        is_crit = attacker.check_critical_hit()
        if is_crit:
            attacker.crit_this_turn = True
            print(f"{Fore.GREEN}{attacker.name} landed a critical hit!{Style.RESET_ALL}")


        if ki >= 18:
            attacker.ki_18_attack_this_turn = True
        elif ki >= 12:
            attacker.ki_12_attack_this_turn = True
        debuffs, sa_def_buffs = get_buffs_and_debuffs_from_super(attacker, ki)
        log_and_apply_debuff(boss, debuffs, 3, attacker.name)
        log_and_apply_sa_def_buffs(attacker, sa_def_buffs)
       
        log_and_apply_buff(attacker)
        print(f"{attacker.passives}")
        damage = attacker.calculate_damage_dealt(attack_stat, boss, 15, is_crit=is_crit)
        attacker.damage_dealt_this_turn += damage
        boss.hp -= damage
        print(f"{attacker.name} attacks the Boss for {Fore.RED}{damage} damage!{Style.RESET_ALL}")

        print(f"Boss HP: {Fore.GREEN}{boss.hp} ({math.floor((boss.hp / max_boss_hp) * 100)}%)\n")


        return boss.hp <= 0

    for action in attack_pattern:
        attacker, attack_type, target = action
        if attacker.lower() == "boss":
            target_unit = next((unit for unit in rotation if unit.number == int(target)), None)
            if target_unit:
                team_hp, revived = handle_boss_attack(rotation, target_unit, attack_type, max_team_hp, team_hp)
                if revived:
                    return team_hp
                elif team_hp == 0:
                    return team_hp
            continue

        attacking_unit = next((unit for unit in rotation if unit.number == int(attacker)), None)
        if not attacking_unit:
            continue

        if attack_type == "active":
            if attacking_unit.active_skill is not None:
                if attacking_unit.active_skill_buffs["damage"] == None:
                    print("no damage because transformation")
                    continue
                else:        
                    if attacking_unit.id == "12031":
                        active_multiplier = 6
                    else:
                        active_multiplier = 6.5
                    if perform_attack(attacking_unit, 0, use_active_stat=True, active_multiplier=active_multiplier):
                        print(f"{Fore.GREEN}The Boss has been defeated!{Style.RESET_ALL}")
                        return team_hp
        else:
            if perform_attack(attacking_unit, attacking_unit.ki):
                print(f"{Fore.GREEN}The Boss has been defeated!{Style.RESET_ALL}")
                return team_hp

            # Handle Additional Attacks
            additional_check = attacking_unit.check_additional_attack_that_can_be_super()
            if not additional_check == 0:
                additional_attack_ki = 12 if additional_check == 3  else 0  # 2 means it can be super
                attacking_unit.ki = additional_attack_ki
                if additional_attack_ki == 12:
                    attacking_unit.additional_super_attack_this_turn = True
                    attacking_unit.ki_12_attack_this_turn = True
                elif additional_attack_ki == 0:
                    attacking_unit.additional_attack_this_turn = True
                print(f"additional_attack_ki", additional_attack_ki) 
                print(f"{Fore.YELLOW}{attacking_unit.name} launches an additional {'Super ' if additional_attack_ki == 12 else ''} attack!{Style.RESET_ALL}")

                if perform_attack(attacking_unit, additional_attack_ki):
                    print(f"{Fore.GREEN}The Boss has been defeated!{Style.RESET_ALL}")
                    return team_hp

            if attacking_unit.check_additional_super_attack():
                attacking_unit.ki = 12
                attacking_unit.additional_super_attack_this_turn = True
                attacking_unit.ki_12_attack_this_turn = True
                print(f"{Fore.YELLOW}{attacking_unit.name} launches an additional Super Attack!{Style.RESET_ALL}")

                if perform_attack(attacking_unit, 12):  # Always a Super Attack
                    print(f"{Fore.GREEN}The Boss has been defeated!{Style.RESET_ALL}")
                    return team_hp

    return team_hp
        
def simulate_turn(team, max_team_hp, team_hp, team_hp_for_percent, boss, max_boss_hp, boss_hp_for_percent, current_boss_cooldown, rounds, revived_this_run, item_count, item_used, item_cooldown):
    sim_data = []
    """ use_item = False """
    """Simulate a single turn with dynamic input for buffs, debuffs, and attack patterns."""
    if rounds == 1:
        team_hp_for_percent = team_hp
        boss_hp_for_percent = boss.hp
        
    
    print(f"\n{Fore.MAGENTA}=== Start of Turn {rounds} ===")
    print(f"Boss HP: {Fore.GREEN}{boss.hp}({math.floor((boss.hp/boss_hp_for_percent)*100)}%){Style.RESET_ALL}, Team Total HP: {Fore.GREEN}{team_hp}({math.floor((team_hp/ team_hp_for_percent)*100)}%){Style.RESET_ALL}")

    relative_team_hp = team_hp / team_hp_for_percent
    
    boss_attack_distribution = generate_boss_attack_distribution(boss.atk_per_turn)
    print(f"{Fore.LIGHTGREEN_EX}Boss Attack Distribution: {boss_attack_distribution}")
   
    # Input active rotation
    rotation = get_active_rotation(team)
    if not rotation:  # Handle None or empty list
        print("No valid rotation selected.")
        return team_hp, "Error"
    # Track if any unit transformed THIS TURN
    transformed_this_turn = False
    
    for char in rotation:
        # Save original state before checking transformation
        was_transformed = char.transformed  
        char.check_transformation(rounds, relative_team_hp)
        
        # Only modify priority if transformation JUST happened
        if char.transformed and not was_transformed:
            char.priority = 3  # One-time priority boost
            transformed_this_turn = True
            print(f"{Fore.RED}{char.name} TRANSFORMED this turn! "
                  f"Priority {7}->{char.priority}{Style.RESET_ALL}")

    # Re-sort ONLY if a transformation happened this turn
    if transformed_this_turn:
        print(f"{Fore.YELLOW}Re-sorting rotation this turn only{Style.RESET_ALL}")
        rotation = sorted(rotation, key=lambda x: x.priority)
        
        # Re-apply special rules if needed
        unit_numbers = [char.number for char in rotation]
        if 3 in unit_numbers and 5 in unit_numbers:
            unit5 = next(char for char in rotation if char.number == 5)
            rotation.remove(unit5)
            rotation.append(unit5)

        # Update the rotation history with the new order
        if rotation_manager.rotation_history:  # Check if history exists
            rotation_manager.rotation_history[-1] = rotation.copy()  # Update the most recent entry
            print(f"{Fore.BLUE}Updated rotation history with transformed order: {[u.number for u in rotation]}{Style.RESET_ALL}")
    
    # Process buffs, debuffs for the turn and calculate effective stats
    print(f"Active {Fore.GREEN}Buffs{Style.RESET_ALL} and {Fore.RED}Debuffs:")
    for char in rotation:
        #char.check_transformation(rounds, relative_team_hp)
        print(f"{Fore.YELLOW}Calculating effective stats for {char.name}...")
        additional_ki = sum(buff["value"] for buff in char.passives["additional_ki_boost"]) if char.passives.get("additional_ki_boost") else 0
        link_atk_multiplier, link_def_multiplier, link_ki_bonus, shared_links = get_shared_links_multiplier(char, rotation, char.ki, relative_team_hp, print_output=False)
        char.ki = char.leaderskill_ki_multiplier + link_ki_bonus + additional_ki
        print(f"{Fore.CYAN} {char.name}'s Ki before Ki Collection: {char.ki} = From Leaderskill:{char.leaderskill_ki_multiplier} + From Links:{link_ki_bonus} + From passives:{additional_ki}")
        char.temp_ki_multiplier = get_ki_multiplier_random(char)
        print(f"{Fore.CYAN} {char.name}'s Ki after Ki Collection: {char.ki}")
        link_atk_multiplier, link_def_multiplier, link_ki_bonus, shared_links = get_shared_links_multiplier(char, rotation, char.ki, relative_team_hp, print_output=True)
        print(f"{relative_team_hp}")
        apply_pre_sa_buffs(char,relative_team_hp,rotation.index(char) + 1)
        for buff_name, buff_details in char.passives.items():
            if "recover_hp" in buff_name:
                team_hp = max_team_hp
                relative_team_hp = team_hp / team_hp_for_percent
                sim_data.append("heal")
                print(f"{Fore.GREEN}{char.name} recovered all HP!{Style.RESET_ALL}")
                print(f"Boss HP: {Fore.GREEN}{boss.hp}({math.floor((boss.hp/boss_hp_for_percent)*100)}%){Style.RESET_ALL}, Team Total HP: {Fore.GREEN}{team_hp}({math.floor((team_hp/ team_hp_for_percent)*100)}%){Style.RESET_ALL}")
        check_revive(char, relative_team_hp)
        if char.active_skill is not None:
            if check_active_skill_condition(char.active_skill_code_condition, relative_team_hp, rounds):
                print(f"{Fore.GREEN}{char.name} can use the active skill!{Style.RESET_ALL}")
                char.can_use_active_skill = True
            else:
                print(f"{Fore.RED}{char.name} cannot use the active skill!{Style.RESET_ALL}")
                char.can_use_active_skill = False

        print_buffs_debuffs(char)
        print(f"{Fore.CYAN}Before SuperAttack:\n")
        char.effective_attack = char.calculate_effective_attack(link_atk_multiplier)
        char.effective_defense = char.calculate_effective_defense(link_def_multiplier)
        char.effective_attack_for_reseting = char.effective_attack
        char.effective_defense_for_reseting = char.effective_defense
        print(f"{Fore.CYAN}Active link Skills: {', '.join(shared_links)}")
    
    # use item if needed
    # 1. Process existing item effect first
    if item_used:
        if item_cooldown > 0:
            print(f"{Fore.CYAN}Item effect active ({item_cooldown} turns remaining){Style.RESET_ALL}")
            item_cooldown -= 1
        else:
            item_used = False  # Only disable when cooldown fully expires
    
    # 2. Check for new item activation (only if no active effect)
    if not item_used and item_count > 0 and rounds in {1, 3}:
        item_used = True
        item_cooldown = 1 
        item_count -= 1
        print(f"{Fore.GREEN}Using item!{Style.RESET_ALL}")
        sim_data.append(("item used", rounds))

    # Get attack pattern
    resolved_boss_attacks, current_boss_cooldown = resolve_boss_attacks(boss_attack_distribution, boss.sa_percent, boss.sa_per_turn, boss.cooldown, current_boss_cooldown)
    for unit in rotation:
        if unit.can_use_active_skill and unit.used_active_skill == False:
            sim_data.append(["active skill",unit.id,unit.name])
            unit.used_active_skill = True
            attack_pattern, active_damage_multiplier = build_attack_pattern(rotation, boss_attack_distribution, resolved_boss_attacks, active_skill=True)
        else:
            attack_pattern, active_damage_multiplier = build_attack_pattern(rotation, boss_attack_distribution, resolved_boss_attacks)
    print(f"{Fore.LIGHTYELLOW_EX}Attack pattern: {attack_pattern}")
    # Execute attack pattern
    team_hp = execute_attack_pattern(rotation, boss, attack_pattern, active_damage_multiplier, max_team_hp, team_hp, max_boss_hp, rounds, item_used)
    
    revived = False
    revivable_units = [unit for unit in rotation if unit.has_revived]
    if team_hp >= 0 and len(revivable_units) > 0 and revived_this_run == False:
        revived = True
    
    for unit in rotation:
        # Get all conditional passives (excluding atk_buff and def_buff)

        conditional_passives = []
        for passive, data in unit.buffs.items():
            if passive not in ["atk_buff", "def_buff", "ki_buff"]:  # Exclude unconditional passives
                if isinstance(data, dict) and "value" in data:  # If it has a value
                    value = data["value"]
                    formatted_value = f"{round(value * 100)}%" if "ki_boost" not in passive and "ki_per" not in passive else str(value)
                    conditional_passives.append(f"{passive}: {formatted_value}")
                else:
                    conditional_passives.append(passive)  # No value, just name
        
        sim_data.append([rounds, unit.id, unit.name, unit.was_attacked_this_turn, unit.damage_taken_this_turn, unit.damage_dealt_this_turn])
    if revived:

        reviver_unit = revivable_units[0]
        sim_data.append(["revive", reviver_unit.id, reviver_unit.name])
        return team_hp,boss.hp, team_hp_for_percent,boss_hp_for_percent, current_boss_cooldown, "Turn Complete", sim_data, True, item_count, item_used, item_cooldown
    elif team_hp <= 0:
        return team_hp,boss.hp, team_hp_for_percent,boss_hp_for_percent, current_boss_cooldown, "Team Defeated!", sim_data, revived_this_run, item_count, item_used, item_cooldown
    elif boss.hp <= 0:
        return team_hp,boss.hp, team_hp_for_percent,boss_hp_for_percent, current_boss_cooldown, "Boss Defeated!" , sim_data, revived_this_run, item_count, item_used, item_cooldown
    else:
        # Reduce buff and debuff duration
        for unit in team:
            update_buffs(unit)
            update_debuffs(unit)
            unit.temp_ki_multiplier = 1
            unit.ki = 0
            unit.ki_gained = 0
            unit.crit_chance = 0
            unit.crit_this_turn = False
            unit.evaded_this_turn = False 
            unit.sim_evade_this_turn = False
            unit.additional_attack_this_turn = False
            unit.additional_super_attack_this_turn = False
            unit.ki_18_attack_this_turn = False
            unit.ki_12_attack_this_turn = False
            unit.additional_atk_boost_this_turn = False
            unit.additional_def_boost_this_turn = False
            unit.additional_ki_boost_this_turn = False 
            unit.guard_this_turn = False
            unit.damage_dealt_this_turn = 0
            unit.damage_taken_this_turn = 0
            unit.was_attacked_this_turn = 0
            unit.effective_attack = unit.effective_attack_for_reseting
            unit.effective_defense = unit.effective_defense_for_reseting

        # End-of-turn status
        print(f"\n{Fore.MAGENTA}=== End of Turn {rounds}===")
        print(f"Active Buffs and Debuffs:")
        for char in rotation:
            print_buffs_debuffs(char)
        print_buffs_debuffs(boss)
        print(f"Boss HP: {Fore.GREEN}{boss.hp}({math.floor((boss.hp/boss_hp_for_percent)*100)}%){Style.RESET_ALL}, Team Total HP: {Fore.GREEN}{team_hp}({math.floor((team_hp/ team_hp_for_percent)*100)}%)")

        return team_hp, boss.hp, team_hp_for_percent, boss_hp_for_percent, current_boss_cooldown, "Turn Complete" , sim_data, revived_this_run, item_count,item_used, item_cooldown

def save_simulation_data(boss, max_team_hp, max_boss_hp, sim_data, seed=None):
    global CURRENT_JSON_PATH
    """
    Save SIM data to CSV, mirroring the input JSON's directory structure
    
    Args:
        input_json_path: Path to the input JSON file (e.g., "../Teams/TeamsForAglUI/TeamsWithIntUI/file.json")
        Other params remain the same
    """
    
     # Determine output path
    if CURRENT_JSON_PATH:
        input_path = os.path.normpath(CURRENT_JSON_PATH)
        parts = input_path.split(os.sep)
        
        # Remove leading relative markers (../ or ./)
        if parts[0] in ('..', '.'):
            parts = parts[1:]
        
        # Build output path
        output_folder = os.path.join("Simulation_results", *parts[:-1])
        base_name = os.path.splitext(parts[-1])[0] + "_metrics"
    else:
        # Fallback to original behavior
        output_folder = os.path.join("Simulation_results", "BenchmarkUndefined")
        base_name = "BenchmarkUndefined.csv"
    
    # Create directory if needed
    os.makedirs(output_folder, exist_ok=True)
    
    # 3. Generate unique filename if needed
    file_number = 1
    while True:
        output_file = os.path.join(output_folder, 
                                 f"{base_name}_{file_number}.csv" if file_number > 1 
                                 else f"{base_name}.csv")
        if not os.path.exists(output_file):
            break
        file_number += 1

    # Define headers
    headers = [
        "Turn", "Unit ID", "Unit Name", "Hits Taken", "Damage Received", 
        "Team HP", "Damage Dealt", "Boss HP"
    ]

    # Initialize tracking variables
    total_turns = 0
    total_damage_received = 0
    total_damage_dealt = 0
    max_team_hp = max_team_hp  # Track current HP directly
    turn_numbers = set()
  
    # Determine the winner
    winner = "Boss defeated" if boss.hp <= 0 else "Team defeated"

    # Write the Simulation data to a CSV file
    with open(output_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([f"RNG Seed: {seed}"])  # Log seed in CSV
        writer.writerow(headers)

        for row in sim_data:

            print("SIM ENTRY:", row)

            if "revive" in row:
                # Try to extract the unit's name from the row text
                reviver_name = row[2]

                # Log who revived and reset HP
                total_damage_received = int(max_team_hp * 0.3)
                writer.writerow([turn, 12031, reviver_name, "revive", "revive", f"{max_team_hp*0.7:.0f} (70%)", "revive", "revive"])
                print(f"{reviver_name} triggered a revive! Team HP reset to 70% of max HP.")
                continue

            if row == "heal":
                # If a heal entry exists, reset team HP to max
                total_damage_received = 0
                writer.writerow([turn+1, 11751, "Gohan (Kid)", "heal", "heal", f"{max_team_hp} (100%)", "heal", "heal"])
                print(f"Team HP reset to max HP due to heal.")
                continue
            
            if row == "item used" or (isinstance(row, tuple) and row[0] in ("item used", "item_used")):
                turn_used = row[1] if isinstance(row, tuple) and len(row) > 1 else (turn + 1 if 'turn' in locals() else 1)
                writer.writerow([turn_used, "Item", "used", "for", "40", "percent", "damage", "reduction"])
                continue

            if row[0] == "active skill":
                # If an active skill entry exists
                _, unit_id, unit_name = row
                writer.writerow([
                    turn+1, unit_id, unit_name, 
                    "active skill", "active skill",
                    "active skill", "active skill",
                    "active skill", "ACTIVE SKILL USED"
                ])
                continue

            
            turn, unit_id, unit_name, hits_taken, damage_received, damage_dealt = row[:6]

            
            # Update damage tracking
            total_damage_received += damage_received
            total_damage_dealt += damage_dealt
            turn_numbers.add(turn)
            
            # Calculate current HP before healing checks
            current_team_hp = max(max_team_hp - total_damage_received, 0)
            
            # Calculate boss HP
            current_boss_hp = max(max_boss_hp - total_damage_dealt, 0)
            
            # Calculate percentages
            team_hp_percentage = round((current_team_hp / max_team_hp) * 100)
            boss_hp_percentage = round((current_boss_hp / max_boss_hp) * 100)
            
            # Format the row
            formatted_row = [
                turn, unit_id, unit_name, hits_taken, damage_received,
                f"{current_team_hp} ({math.floor(team_hp_percentage)}%)",
                damage_dealt,
                f"{current_boss_hp} ({math.floor(boss_hp_percentage)}%)"
            ]
            
            writer.writerow(formatted_row)
        # Calculate averages
        total_turns = len(turn_numbers) if turn_numbers else 1
        avg_dmg_received = total_damage_received / total_turns
        avg_dmg_dealt = total_damage_dealt / total_turns

        writer.writerow(["Result:", winner])
        # Add averages at the end
        writer.writerow([])  # Empty row for separation
        writer.writerow(["Average damage received per turn:", f"{avg_dmg_received:.2f}"])
        writer.writerow(["Average damage dealt per turn:", f"{avg_dmg_dealt:.2f}"])

    print(f"Metrics for run {file_number} saved to {output_file}")

def run_simulation(team, boss, seed=None):
    current_seed = seed
    team_hp = get_total_hp(team)
    boss.hp = boss.max_hp  # Store boss initial HP
    max_team_hp = team_hp
    boss_hp = boss.hp  # Store boss initial HP
    max_boss_hp = boss_hp
    team_hp_for_percent = team_hp  # Store initial team HP for percentage calculations
    boss_hp_for_percent = boss_hp  # Store initial boss HP for percentage calculations
    current_boss_cooldown = 0 # Initialize boss superattack cooldown
    simulation_data = []
    rounds = 1
    revived_this_run = False
    item_used = False
    item_cooldown = 0
    item_count = 2
    # Main simulation loop
    while team_hp > 0 and boss_hp > 0:

        team_hp, boss_hp, team_hp_for_percent, boss_hp_for_percent, current_boss_cooldown, status, sim_data, has_revived, item_count, item_used, item_cooldown = simulate_turn(
            team, max_team_hp, team_hp, team_hp_for_percent, boss, max_boss_hp, boss_hp_for_percent, current_boss_cooldown, rounds, revived_this_run, item_count, item_used, item_cooldown
        )
        if has_revived:
            revived_this_run = True
        simulation_data.extend(sim_data)

        if status != "Turn Complete":
            print(status)
            break

        rounds += 1

    save_simulation_data(boss, max_team_hp, max_boss_hp, simulation_data,seed=current_seed)
    print("Simulation Over!")

# Main simulation loop
def main():
     # Get seed from command line or use timestamp
    if len(sys.argv) > 1:
        seed = int(sys.argv[1])
    else:
        seed = int(datetime.now().timestamp())
    
    random.seed(seed)
    print(f"Simulation Seed: {seed}")  # Log seed
    # Example initialization
    team = load_units_from_json("../Teams/TEST/LLMTeamVvariableSlotTypeAdvantage.json")  # Adjust the path as needed
    bosses = load_bosses_from_json("../boss.json")  # Adjust the path as needed
    boss = bosses[2]  # Select the boss to battle
    leader_number = 1
    if not (1 <= leader_number <= len(team)):  # Check if valid leader number
        raise ValueError("Invalid leader number")
    leader = next(unit for unit in team if unit.number == leader_number)
    apply_leader_skill_multipliers(team, leader.leaderskill)  # Apply leader skill multipliers
    run_simulation(team, boss, seed)

if __name__ == "__main__":
    main()

