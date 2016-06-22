
import random as r

names_race = [	"Human",
		"Troll",
		"High Elf",
		"Gray Elf",
		"Dark Elf",
		"Orc",
		"Drakeling",
		"Dwarf",
		"Gnome",
		"Hurthling"	]

names_class = [	"Fighter",
		"Paladin",
		"Ranger",
		"Thief",
		"Assassin",
		"Wizard",
		"Priest",
		"Bard",
		"Monk",
		"Healer",
		"Weaponsmith",
		"Archer",
		"Merchant",
		"Farmer",
		"Mindcrafter",
		"Barbarian",
		"Druid",
		"Necromancer",
		"Elementalist",
		"Beastfighter"	]

names_gender = [ "Male", "Female" ]

def randpc():
	picks = (r.choice(names_gender),
		r.choice(names_race),
		r.choice(names_class))
	return "%s, %s, %s" % picks

