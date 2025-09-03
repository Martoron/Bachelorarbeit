from colorama import Fore, Style, init
import tkinter as tk

link_skills={
    
"High Compatibility": {
        "level_1": {
            "ki": 1
        },
        "level_10": {
            "ki": 2,
            "ATK": 10,
            "DEF": 10
        }
    },
    
"Courage": {
        "level_1": {
            "ki": 1
        },
        "level_10": {
            "ki": 2,
            "ATK": 10
        }
    },
    
"The Students": {
        "level_1": {
            "DEF": 20
        },
        "level_10": {
            "DEF": 30
        }
    },
    
"The Innocents": {
        "level_1": {
            "ATK": 10
        },
        "level_10": {
            "ATK": 15
        }
    },
    
"Crane School": {
        "level_1": {
            "ATK": 15
        },
        "level_10": {
            "ATK": 20
        }
    },
    
"Demonic Ways": {
        "level_1": {
            "ki": 1
        },
        "level_10": {
            "ki": 2,
            "ATK": 10,
            "DEF": 10
        }
    },
    
"Demonic Power": {
        "level_1": {
            "ATK": 20
        },
        "level_10": {
            "ATK": 20,
            "DEF": 10
        }
    },
    
"Brainiacs": {
        "level_1": {
            "ATK": 10,
            "DEF": 10
        },
        "level_10": {
            "ATK": 15,
            "DEF": 15
        }
    },
    
"Golden Warrior": {
        "level_1": {
            "ki": 1,
            "enemy_DEF": -5
        },
        "level_10": {
            "ki": 1,
            "enemy_DEF": -10
        }
    },
    
"Money Money Money": {
        "level_1": {
            "ki": 1
        },
        "level_10": {
            "ki": 1,
            "DEF": 20
        }
    },
    
"Evil Autocrats": {
        "level_1": {
            "ki": 1
        },
        "level_10": {
            "ki": 2,
            "enemy_DEF": -20
        }
    },
    
"Flee": {
        "level_1": {
            "ki": 1,
            "condition": {
                "HP": 30
            }
        },
        "level_10": {
            "ki": 2,
            "HP": 50,
            "Dodge": 10
        }
    },
    
"Telekinesis": {
        "level_1": {
            "enemy_DEF": -10
        },
        "level_10": {
            "enemy_DEF": -20
        }
    },
    
"More Than Meets the Eye": {
        "level_1": {
            "ATK": 10
        },
        "level_10": {
            "ATK": 10,
            "DEF": 10
        }
    },
    
"Hero": {
        "level_1": {
            "DEF": 20
        },
        "level_10": {
            "DEF": 25
        }
    },
    
"Supreme Warrior": {
        "level_1": {
            "ki": 1
        },
        "level_10": {
            "ki": 2,
            "ATK": 10
        }
    },
    
"Gentleman": {
        "level_1": {
            "ki": 2
        },
        "level_10": {
            "ki": 2,
            "DEF": 10
        }
    },
    
"Brutal Beatdown": {
        "level_1": {
            "ATK": 10
        },
        "level_10": {
            "ATK": 15
        }
    },
    
"Messenger from the Future": {
        "level_1": {
            "ATK": 5
        },
        "level_10": {
            "ATK": 10
        }
    },
    
"World Tournament Reborn": {
        "level_1": {
            "ATK": 15
        },
        "level_10": {
            "ATK": 20
        }
    },
    
"New": {
        "level_1": {
            "ATK": 20
        },
        "level_10": {
            "ATK": 20,
            "DEF": 20
        }
    },
    
"Saiyan Warrior Race": {
        "level_1": {
            "ATK": 5
        },
        "level_10": {
            "ATK": 10
        }
    },
    
"All in the Family": {
        "level_1": {
            "DEF": 15
        },
        "level_10": {
            "DEF": 20
        }
    },
    
"Telepathy": {
        "level_1": {
            "ki": 1
        },
        "level_10": {
            "ki": 2,
            "Crit": 5
        }
    },
    
"Respect": {
        "level_1": {
            "ATK": 15
        },
        "level_10": {
            "ATK": 20
        }
    },
    
"Prodigies": {
        "level_1": {
            "ATK": 10
        },
        "level_10": {
            "ATK": 15
        }
    },
    
"World Tournament Champion": {
        "level_1": {
            "ki": 1
        },
        "level_10": {
            "ki": 2,
            "DEF": 10
        }
    },
    
"Metamorphosis": {
        "level_1": {
            "Heal": 5
        },
        "level_10": {
            "Heal": 5,
            "ATK": 10,
            "DEF": 10
        }
    },
    
"Super Saiyan": {
        "level_1": {
            "ATK": 10
        },
        "level_10": {
            "ATK": 15
        }
    },
    
"Experienced Fighters": {
        "level_1": {
            "ATK": 10
        },
        "level_10": {
            "ATK": 15
        }
    },
    
"Twin Terrors": {
        "level_1": {
            "ki": 2
        },
        "level_10": {
            "ki": 2,
            "ATK": 5,
            "DEF": 5,
            "Dodge": 5
        }
    },
    
"Coward": {
        "level_1": {
            "ki": 1
        },
        "level_10": {
            "ki": 2,
            "Crit": 5
        }
    },
    
"Attack of the Clones": {
        "level_1": {
            "ki": 1
        },
        "level_10": {
            "ki": 2,
            "Dodge": 5
        }
    },
    
"The Saiyan Lineage": {
        "level_1": {
            "ki": 1
        },
        "level_10": {
            "ki": 2,
            "ATK": 5,
            "DEF": 5
        }
    },
    
"Android Assault": {
        "level_1": {
            "DEF": 10
        },
        "level_10": {
            "ki": 2,
            "DEF": 20
        }
    },
    
"Turtle School": {
        "level_1": {
            "ATK": 10,
            "DEF": 10
        },
        "level_10": {
            "ki": 2,
            "ATK": 20,
            "DEF": 20
        }
    },
    
"Solid Support": {
        "level_1": {
            "ATK": 10,
            "enemy_DEF": -15
        },
        "level_10": {
            "ATK": 15,
            "enemy_DEF": -20
        }
    },
    
"Mechanical Menaces": {
        "level_1": {
            "ki": 1
        },
        "level_10": {
            "ki": 2,
            "Damage_Reduction": 5
        }
    },
    
"Cold Judgment": {
        "level_1": {
            "DEF": 20
        },
        "level_10": {
            "DEF": 25
        }
    },
    
"Royal Lineage": {
        "level_1": {
            "ki": 1
        },
        "level_10": {
            "ki": 2,
            "ATK": 5
        }
    },
    
"The Ginyu Force": {
        "level_1": {
            "ATK": 25
        },
        "level_10": {
            "ATK": 25,
            "Crit": 5
        }
    },
    
"Infighter": {
        "level_1": {
            "ATK": 10,
            "enemy_DEF": -10
        },
        "level_10": {
            "ATK": 15,
            "enemy_DEF": -15
        }
    },
    
"Frieza's Minion": {
        "level_1": {
            "ATK": 20
        },
        "level_10": {
            "ATK": 20,
            "DEF": 10
        }
    },
    
"Champion's Strength": {
        "level_1": {
            "ki": 1
        },
        "level_10": {
            "ki": 2,
            "Damage_Reduction": 5
        }
    },
    
"Z-Fighters": {
        "level_1": {
            "ATK": 15
        },
        "level_10": {
            "ATK": 20
        }
    },
    
"Dodon Ray": {
        "level_1": {
           "ConditionalATK": {"ATK": 10, "condition": "On Superattack" }
        },
        "level_10": {
            "ConditionalATK": {"ATK": 15, "condition": "On Superattack" } 
        }
    },
    
"Kamehameha": {
        "level_1": {
            "ConditionalATK": {"ATK": 5, "condition": "On Superattack" }
        },
        "level_10": {
            "ConditionalATK": {"ATK": 10, "condition": "On Superattack" }
        }
    },
    
"Namekians": {
        "level_1": {
            "Heal": 5
        },
        "level_10": {
            "Heal": 7,
            "ATK": 7,
            "DEF": 7
        }
    },
    
"Berserker": {
        "level_1": {
            "ConditionalATK": {"ATK": 20, "condition": "HP below 50%" }
        },
        "level_10": {
            "ConditionalATK": {"ATK": 30, "condition": "HP below 50%" }
        }
    },
    
"Big Bad Bosses": {
        "level_1": {
            "ATK": 25,
            "DEF": 25,
            "condition": {
                "HP": 80
            }
        },
        "level_10": {
            "ATK": 25,
            "DEF": 25
        }
    },
    
"Frieza's Army": {
        "level_1": {
            "DEF": 20
        },
        "level_10": {
            "ATK": 10,
            "DEF": 20
        }
    },
    
"Tough as Nails": {
        "level_1": {
            "DEF": 15
        },
        "level_10": {
            "DEF": 20,
            "Damage_Reduction": 5
        }
    },
    
"Speedy Retribution": {
        "level_1": {
            "ATK": 10
        },
        "level_10": {
            "ATK": 15,
            "Dodge": 5
        }
    },
    
"Tag Team of Terror": {
        "level_1": {
            "ATK": 15
        },
        "level_10": {
            "ATK": 20
        }
    },
    
"Red Ribbon Army": {
        "level_1": {
            "ATK": 10
        },
        "level_10": {
            "ATK": 10,
            "DEF": 10
        }
    },
    
"Gaze of Respect": {
        "level_1": {
            "ki": 2
        },
        "level_10": {
            "ki": 2,
            "DEF": 10
        }
    },
    
"Patrol": {
        "level_1": {
            "ki": 2
        },
        "level_10": {
            "ki": 2,
            "DEF": 20
        }
    },
    
"Over 9000": {
        "level_1": {
            "ATK": 10
        },
        "level_10": {
            "ATK": 10,
            "DEF": 10
        }
    },
    
"Signature Pose": {
        "level_1": {
            "ATK": 7
        },
        "level_10": {
            "ATK": 7,
            "Crit": 5
        }
    },
    
"Tough Luck": {
        "level_1": {
            "Crit": 5
        },
        "level_10": {
            "Crit": 7
        }
    },
    
"Z Fighters": {
        "level_1": {
            "ATK": 15
        },
        "level_10": {
            "ATK": 20
        }
    },
    
"Thirst for Conquest": {
        "level_1": {
            "ATK": 15
        },
        "level_10": {
            "ATK": 15,
            "DEF": 15
        }
    },
    
"The Hera Clan": {
        "level_1": {
            "Ki": 2
        },
        "level_10": {
            "Ki": 2,
            "ATK": 5,
            "Crit": 5
        }
    },
    
"Galactic Warriors": {
        "level_1": {
            "ATK": 20
        },
        "level_10": {
            "Ki": 2,
            "ATK": 20,
            "DEF": 20
        }
    },
    
"Over in a Flash": {
        "level_1": {
            "Ki": 3
        },
        "level_10": {
            "Ki": 3,
            "ATK": 7
        }
    },
    
"The Incredible Adventure": {
        "level_1": {
            "Ki": 2
        },
        "level_10": {
            "Ki": 2,
            "ATK": 7,
            "DEF": 7
        }
    },
    
"Cooler's Underling": {
        "level_1": {
            "Ki": 1
        },
        "level_10": {
            "Ki": 2,
            "Crit": 5
        }
    },
    
"Cooler's Armored Squadron": {
        "level_1": {
            "ATK": 25
        },
        "level_10": {
            "ATK": 25,
            "DEF": 25
        }
    },
    
"Hero of Justice": {
        "level_1": {
            "ATK": 25
        },
        "level_10": {
            "ATK": 25,
            "Crit": 5
        }
    },
    
"Signature Pose": {
        "level_1": {
            "Ki": 2
        },
        "level_10": {
            "Ki": 3,
            "ATK": 7
        }
    },
    
"GT": {
        "level_1": {
            "Ki": 2
        },
        "level_10": {
            "Ki": 2,
            "ATK": 10,
            "DEF": 10
        }
    },
    
"Infinite Regeneration": {
        "level_1": {
            "Heal": 3
        },
        "level_10": {
            "Ki": 2,
            "DEF": 10,
            "Heal": 3
        }
    },
    
"Prepared for Battle": {
        "level_1": {
            "Ki": 2
        },
        "level_10": {
            "Ki": 2,
            "ATK": 5,
            "DEF": 5
        }
    },
    
"Destroyer of the Universe": {
        "level_1": {
            "ATK": 25
        },
        "level_10": {
            "ATK": 25,
            "DEF": 15
        }
    },
    
"Team Turles": {
        "level_1": {
            "Ki": 1
        },
        "level_10": {
            "Ki": 2,
            "Crit": 5
        }
    },
    
"Fortuneteller Baba's Fighter": {
        "level_1": {
            "Ki": 2
        },
        "level_10": {
            "Ki": 3,
            "ATK": 5,
            "DEF": 5
        }
    },
    
"Guidance of the Dragon Balls": {
        "level_1": {
            "ATK": 20
        },
        "level_10": {
            "ATK": 20,
            "Crit": 7
        }
    },
    
"Power Bestowed by God": {
        "level_1": {
            "ConditionalATK": {"ATK": 5, "condition": "On Superattack" }
        },
        "level_10": {
            "ConditionalATK": {"ATK": 10, "condition": "On Superattack" }
        }
    },
    
"Hardened Grudge": {
        "level_1": {
            "Ki": 1
        },
        "level_10": {
            "Ki": 2,
            "ATK": 10
        }
    },
    
"Auto Regeneration": {
        "level_1": {
            "Heal": 3
        },
        "level_10": {
            "Heal": 5,
            "Damage Reduction": 5
        }
    },
    
"Fusion": {
        "level_1": {
            "Ki": 2
        },
        "level_10": {
            "Ki": 2,
            "ATK": 10,
            "DEF": 10
        }
    },
    
"Deficit Boost": {
        "level_1": {
            "ATK": 15
        },
        "level_10": {
            "ATK": 20
        }
    },
    
"Ultimate Lifeform": {
        "level_1": {
            "Ki": 2
        },
        "level_10": {
            "Ki": 2,
            "ATK": 10,
            "DEF": 10,
            "Heal": 3
        }
    },
    
"Fierce Battle": {
        "level_1": {
            "ATK": 15
        },
        "level_10": {
            "ATK": 20
        }
    },
    
"Infinite Energy": {
        "level_1": {
            "Ki": 2
        },
        "level_10": {
            "Ki": 2,
            "ATK": 5,
            "DEF": 5,
            "Crit": 5
        }
    },
    
"Formidable Enemy": {
        "level_1": {
            "ATK": 10
        },
        "level_10": {
            "ATK": 15
        }
    },
    
"Fused Fighter": {
        "level_1": {
            "Ki": 2
        },
        "level_10": {
            "Ki": 2,
            "ATK": 5,
            "DEF": 5
        }
    },
    
"Fusion Failure": {
        "level_1": {
            "Heal": 3
        },
        "level_10": {
            "Heal": 7
        }
    },
    
"Scientist": {
        "level_1": {
            "Ki": 2
        },
        "level_10": {
            "Ki": 2,
            "DEF": 20
        }
    },
    
"Hatred of Saiyans": {
        "level_1": {
            "Ki": 2
        },
        "level_10": {
            "Ki": 3,
            "ATK": 10
        }
    },
    
"Limit-Breaking Form": {
        "level_1": {
            "ConditionalATK": {"ATK": 5, "condition": "On Superattack" }
        },
        "level_10": {
            "ConditionalATK": {"ATK": 10, "condition": "On Superattack" }
        }
    },
    
"The First Awakened": {
        "level_1": {
            "ATK": 25
        },
        "level_10": {
            "ATK": 25,
            "DEF": 10
        }
    },
    
"Shattering the Limit": {
        "level_1": {
            "Ki": 2
        },
        "level_10": {
            "Ki": 2,
            "ATK": 5,
            "DEF": 5
        }
    },
    
"Nightmare": {
        "level_1": {
            "ATK": 10
        },
        "level_10": {
            "ATK": 15
        }
    },
    
"Fear and Faith": {
        "level_1": {
            "Ki": 2
        },
        "level_10": {
            "Ki": 2,
            "enemy_DEF_down": 10
        }
    },
    
"Xenoverse": {
        "level_1": {
            "ATK": 20
        },
        "level_10": {
            "ATK": 20,
            "DEF": 10
        }
    },
    
"Super Strike": {
        "level_1": {
            "ATK": 20
        },
        "level_10": {
            "ATK": 25
        }
    },
    
"Transform": {
        "level_1": {
            "Ki": 2
        },
        "level_10": {
            "Ki": 3,
            "DEF": 10
        }
    },
    
"Saiyan Roar": {
        "level_1": {
            "ATK": 25
        },
        "level_10": {
            "ATK": 25,
            "DEF": 10
        }
    },
    
"Legendary Power": {
        "level_1": {
            "ConditionalATK": {"ATK": 10, "condition": "On Superattack" }
        },
        "level_10": {
            "ConditionalATK": {"ATK": 15, "condition": "On Superattack" }
        }
    },
    
"Warriors of Universe 6": {
        "level_1": {
            "Ki": 2
        },
        "level_10": {
            "Ki": 2,
            "ATK": 6,
            "DEF": 6
        }
    },
    
"Shadow Dragon": {
        "level_1": {
            "ATK": 15
        },
        "level_10": {
            "ATK": 20,
            "DEF": 20
        }
    },
    
"Penguin Village Adventure": {
        "level_1": {
            "ATK": 15
        },
        "level_10": {
            "ATK": 20
        }
    },
    
"Otherworld Warriors": {
        "level_1": {
            "ATK": 20
        },
        "level_10": {
            "ATK": 20,
            "DEF": 10
        }
    },
    
"Tournament of Power": {
        "level_1": {
            "Ki": 3
        },
        "level_10": {
            "Ki": 3,
            "ATK": 7,
            "DEF": 7
        }
    },
    
"Blazing Battle": {
        "level_1": {
            "ATK": 15
        },
        "level_10": {
            "ATK": 20
        }
    },
    
"Soul vs Soul": {
        "level_1": {
            "Ki": 1
        },
        "level_10": {
            "Ki": 1,
            "ATK": 5,
            "DEF": 5
        }
    },
    
"Golden Z-Fighter": {
        "level_1": {
            "Ki": 2
        },
        "level_10": {
            "Ki": 3,
            "Crit": 5
        }
    },
    
"Supreme Power": {
        "level_1": {
            "ATK": 5,
            "DEF": 5
        },
        "level_10": {
            "ATK": 10,
            "DEF": 10
        }
    },
    
"The Wall Standing Tall": {
        "level_1": {
            "ATK": 15
        },
        "level_10": {
            "ATK": 20
        }
    },
    
"Shocking Speed": {
        
"level_1": {
            "ki": 2
        },
        
"level_10": {
            "ki": 2,
            "DEF": 5
        }
    },
    
"Majin": {
        
"level_1": {
            "ATK": 10,
            "DEF": 10
        },
        
"level_10": {
            "ki": 2,
            "ATK": 15,
            "DEF": 15
        }
    },
    
"New Frieza Army": {
        
"level_1": {
            "ATK": 20,
            "DEF": 20
        },
        
"level_10": {
            "ATK": 25,
            "DEF": 25
        }
    },
    
"Universe's Most Malevolent": {
        
"level_1": {
            "ATK": 15
        },
        
"level_10": {
            "ATK": 20
        }
    },
    
"Strongest Clan in Space": {
        
"level_1": {
            "ki": 2
        },
        
"level_10": {
            "ki": 2,
            "enemy_DEF": -10
        }
    },
    
"Revival": {
        
"level_1": {
            "ki": 2
        },
        
"level_10": {
            "ki": 2,
            "ATK": 5,
            "DEF": 5,
            "Heal": 5
        }
    },
    
"Super God Combat": {
        
"level_1": {
            "ATK": 15
        },
        
"level_10": {
            "ATK": 20
        }
    },
    
"Warrior Gods": {
        
"level_1": {
            "ATK": 10
        },
        
"level_10": {
            "ATK": 10,
            "ConditionalATK": {"ATK": 5, "condition": "On Superattack" }
        }
    },
    
"Majin Revival Plan": {
        
"level_1": {
            "ki": 2
        },
        
"level_10": {
            "ki": 2,
            "DEF": 20
        }
    },
    
"Budding Warrior": {
        
"level_1": {
            "ATK": 10
        },
        
"level_10": {
            "ATK": 15
        }
    },
    
"Bombardment": {
        
"level_1": {
            "ATK": 15
        },
        
"level_10": {
            "ATK": 20
        }
    },
    
"Resurrection F": {
        
"level_1": {
            "ATK": 10
        },
        
"level_10": {
            "ki": 1,
            "ATK": 10,
            "DEF": 10
        }
    },
    
"Loyalty": {
        
"level_1": {
            "ki": 1
        },
        
"level_10": {
            "ki": 2,
            "Damage_Reduction": 5
        }
    },
    
"Energy Absorption": {
        
"level_1": {
            "ki": 2
        },
        
"level_10": {
            "ki": 3,
            "Heal": 3
        }
    },
    
"Godly Power": {
        
"level_1": {
            "ATK": 15
        },
        
"level_10": {
            "ATK": 15,
            "Crit": 5
        }
    },
    
"Team Bardock": {
        
"level_1": {
            "ki": 1
        },
        
"level_10": {
            "ki": 2,
            "ATK": 10,
            "DEF": 10
        }
    },
    
"Dismal Future": {
        
"level_1": {
            "ki": 1
        },
        
"level_10": {
            "ki": 2,
            "Crit": 5
        }
    },
    
"Magician": {
        
"level_1": {
            "ATK": 15
        },
        
"level_10": {
            "ATK": 15,
            "enemy_DEF": -10
        }
    },
    
"Strength in Unity": {
        
"level_1": {
            "ki": 1
        },
        
"level_10": {
            "ki": 2,
            "Heal": 3
        }
    },
    
"Unbreakable Bond": {
        
"level_1": {
            "ki": 2
        },
        
"level_10": {
            "ki": 2,
            "DEF": 20
        }
    },
    
"Organic Upgrade": {
        
"level_1": {
            "ki": 2
        },
        
"level_10": {
            "ki": 2,
            "ATK": 5,
            "DEF": 5,
            "Crit": 5
        }
    },
    
"Saiyan Pride": {
        
"level_1": {
            "ATK": 15
        },
        
"level_10": {
            "ATK": 20
        }
    },
    
"Connoisseur": {
        
"level_1": {
            "Heal": 5
        },
        
"level_10": {
            "Heal": 7,
            "DEF": 7
        }
    },
    
"Galactic Visitor": {
        
"level_1": {
            "ki": 1
        },
        
"level_10": {
            "ki": 2,
            "DEF": 20
        }
    },
    
"Battlefield Diva": {
        
"level_1": {
            "ki": 2
        },
        
"level_10": {
            "ki": 2,
            "Dodge": 5
        }
    },
    
"Family Ties": {
        
"level_1": {
            "ki": 2
        },
        
"level_10": {
            "ki": 2,
            "ATK": 10
        }
    }
}

# Check shared categories between two characters
def share_category(char1, char2):
    # Assuming both characters have a 'categories' attribute, which is a list of categories
    return any(category in char1.categories for category in char2.categories)

def count_shared_links(char1, char2):
    # Assume char1.links and char2.links are lists of link names (strings)
    shared_links = set(char1.links) & set(char2.links)
    
    return len(shared_links)  # Return the count of shared links

# Get the best linking partner for a character
def get_best_linking_partner(character, all_characters):
    best_partner = None
    best_shared_links = 0

    for candidate in all_characters:
        if candidate.name != character.name and share_category(character, candidate):
            shared_links = count_shared_links(character, candidate)
            if shared_links > best_shared_links:
                best_shared_links = shared_links
                best_partner = candidate

    return best_partner

# Activate shared links between two characters
def activate_shared_links(char1, char2):
    shared_links = set(char1.links) & set(char2.links)
    active_links = {}

    for link in shared_links:
        link_effect = link_skills[link]['level_10']  # Assuming level 10
        active_links[link] = link_effect

    return active_links

""" def get_shared_links_multiplier(character, partners, ki, relative_team_hp):
   
    total_atk = 0
    total_def = 0
    total_ki = 0

    # Ensure partners is always a list
    if not isinstance(partners, list):
        partners = [partners]
        print(f"{partners} is not a list. Converting to list.")

    # Calculate shared links across all partners
    character_links = set(character.links)
    shared_links = set()
    partner_link_activations = {}  # Dictionary to track which partner activated which link

    for partner in partners:
        partner_links = set(partner.links)
        shared_links_for_partner = character_links.intersection(partner_links)
        shared_links.update(shared_links_for_partner)
        partner_link_activations[partner.name] = shared_links_for_partner

    print (f"Shared links: {shared_links}")
    print (f"Partner link activations: {partner_link_activations}")
    removed_links = []  # Store links to remove later

    # Process each shared link
    for link in shared_links:
        if link in link_skills:
            # Fetch link effects at level 10
            effects = link_skills[link].get("level_10", {})

            # Process each stat in the link
            for stat, value in effects.items():
                condition_met = False
                added_value = 0

                if isinstance(value, dict) and "condition" in value:
                    condition = value["condition"]

                    if condition == "On Superattack" and ki >= 12:
                        condition_met = True
                    elif condition == "HP below 50%" and relative_team_hp < 0.5:
                        condition_met = True

                    if condition_met:
                        if stat == "ConditionalATK":
                            added_value = value.get("ATK", 0)
                            total_atk += added_value
                        elif stat == "ConditionalDEF":
                            added_value = value.get("DEF", 0)
                            total_def += added_value
                        elif stat == "ConditionalKi":
                            added_value = value.get("ki", 0)
                            total_ki += added_value
                        print(f"{Fore.YELLOW}{link} link activated by {partner.name}:{Style.RESET_ALL} Condition met. Adding {added_value} to {stat}. Total {stat.split('Conditional')[1]}: {total_atk if stat == 'ConditionalATK' else total_def if stat == 'ConditionalDEF' else total_ki}")
                    else:
                        removed_links.append(link)
                        print(f"{Fore.RED}Condition not met for {link}. Skipping link effect.{Style.RESET_ALL}")
                elif isinstance(value, (int, float)):
                    added_value = value
                    if stat == "ATK":
                        total_atk += added_value
                    elif stat == "DEF":
                        total_def += added_value
                    elif stat == "ki":
                        total_ki += added_value
                    print(f"{Fore.YELLOW}{link} link activated by {partner.name}:{Style.RESET_ALL} Adding {added_value} to {stat}. Total {stat}: {total_atk if stat == 'ATK' else total_def if stat == 'DEF' else total_ki}")

    # Remove links that did not meet conditions
    for link in removed_links:
        shared_links.remove(link)

    return (1 + total_atk / 100), (1 + total_def / 100), total_ki, shared_links """

def get_shared_links_multiplier(character, rotation, ki, relative_team_hp, print_output=True):
    """Calculate shared link multipliers for ATK, DEF, and KI, handling conditional buffs dynamically."""
    total_atk = 0
    total_def = 0
    total_ki = 0

    # Calculate shared links across all partners
    character_links = set(character.links)
    shared_links = set()
    partners = {}

    # Get unique partners (excluding characters with same ID)
    unique_partners = []
    seen_ids = set()
    
    for unit in rotation:
        if unit.id != character.id and unit.id not in seen_ids:
            unique_partners.append(unit)
            seen_ids.add(unit.id)

    # Determine partner configuration based on character's position
    if character.id == rotation[0].id:
        # First position - check partner to the right
        if len(unique_partners) > 0:
            partner = unique_partners[0]
            partners[partner.name] = partner.links
            shared_links.update(character_links.intersection(partner.links))
    elif character.id == rotation[1].id:
        # Middle position - check both sides if unique partners exist
        if len(unique_partners) > 0:
            left_partner = unique_partners[0]
            partners[left_partner.name] = left_partner.links
            shared_links.update(character_links.intersection(left_partner.links))
            
            if len(unique_partners) > 1:
                right_partner = unique_partners[1]
                partners[right_partner.name] = right_partner.links
                shared_links.update(character_links.intersection(right_partner.links))
    elif character.id == rotation[2].id:
        # Last position - check partner to the left
        if len(unique_partners) > 0:
            partner = unique_partners[-1]
            partners[partner.name] = partner.links
            shared_links.update(character_links.intersection(partner.links))

    removed_links = []  # Store links to remove later
    # Dictionary to track which units activate which shared links
    link_activations = {}

    # Iterate over partners and their links
    for unit_name, links in partners.items():
        for link in links:
            if link in shared_links:
                if link not in link_activations:
                    link_activations[link] = []
                link_activations[link].append(unit_name)
                
    # Process each shared link
    for link in shared_links:
        if link in link_skills:
            # Fetch link effects at level 10
            effects = link_skills[link].get("level_10", {})

            # Process each stat in the link
            for stat, value in effects.items():
                if isinstance(value, dict) and "condition" in value:
                    # Conditional buff found, ask user via the popup
                    condition = value["condition"]
                    condition_met = False
                    if condition == "On Superattack":
                        if ki >= 12:
                            condition_met = True
                            if print_output:
                                print(f"ki used: {ki}, so condition met")
                        else:
                            if print_output:
                                print(f"ki used: {ki}, so condition not met")

                    if condition == "HP below 50%":
                        if relative_team_hp < 0.5:
                            condition_met = True
                            if print_output:
                                print(f"team_hp: {relative_team_hp}, so condition met")
                        else:
                            if print_output:
                                print(f"team_hp: {relative_team_hp}, so condition not met")

                    if condition_met:
                        # Print character's name with the partner(s)
                        for linkname, units in link_activations.items():
                            if linkname == link:    # Check if the link is the same as the current link
                                partner_names = ", ".join(units)  # Join all partner names
                        if stat == "ConditionalATK":
                            total_atk += value.get("ATK", 0)
                            if print_output:
                                print(f"{Fore.YELLOW}{link} link activated with {partner_names}: {Style.RESET_ALL}{Fore.GREEN} Condition met. Adding {value.get('ATK', 0)} to ATK. total_atk: {total_atk}")
                        elif stat == "ConditionalDEF":
                            total_def += value.get("DEF", 0)
                            if print_output:
                                print(f"{Fore.YELLOW}{link} link activated with {partner_names}: {Style.RESET_ALL}{Fore.GREEN} Condition met. Adding {value.get('DEF', 0)} to DEF. total_def: {total_def}")
                        elif stat == "ConditionalKi":
                            total_ki += value.get("ki", 0)
                            if print_output:
                                print(f"{Fore.YELLOW}{link} link activated with {partner_names}: {Style.RESET_ALL}{Fore.GREEN} Condition met. Adding {value.get('ki', 0)} to KI. total_ki: {total_ki}")
                    else:
                        removed_links.append(link)  # Mark link for removal
                        if print_output:
                            print(f"{Fore.RED}Condition not met for {link}. Skipping link effect.")
                
                elif isinstance(value, (int, float)):
                    # Unconditional buff, apply directly
                    for linkname, units in link_activations.items():
                        if linkname == link:
                            partner_names = ", ".join(units)  # Join all partner names
                    if stat == "ATK":
                        total_atk += value
                        if print_output:
                            print(f"{Fore.YELLOW}{link} link activated with {partner_names}: {Style.RESET_ALL} {Fore.GREEN} Adding {value} to ATK. total_atk: {total_atk}")
                    elif stat == "DEF":
                        total_def += value
                        if print_output:
                            print(f"{Fore.YELLOW}{link} link activated with {partner_names}: {Style.RESET_ALL} {Fore.GREEN} Adding {value} to DEF. total_def: {total_def}")
                    elif stat == "ki":
                        total_ki += value
                        if print_output:
                            print(f"{Fore.YELLOW}{link} link activated with {partner_names}: {Style.RESET_ALL}  {Fore.GREEN} Adding {value} to KI. total_ki: {total_ki}")

# Remove links that did not meet conditions
    for link in removed_links:
        shared_links.remove(link)

    return (1 + total_atk / 100), (1 + total_def / 100), total_ki, shared_links
