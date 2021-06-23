# GeneticTibalts


Using genetic programming to solve the ratios for a Magic: the Gathering deck.


Magic: The Gathering is a card game where players play as wizards, dueling with magic and summoning creatures to attack their opponents. Decks in MTG are composed of 60 cards and are composed of various spells, creatures, and mana producing lands (which players can only play one of each of their turns). Each card can only show up as 4 copies in a deck.

As bigger spells cost increasingly more mana, this lends the game to have **some** linearity in power level. Although some effects can disrupt this progression of power level, games tend to mostly follow it, as players increasingly get more powerful as they draw lands. Some cards, however, disrupt it greatly.



Tibalt's Trickery is one of those cards.

<img src="https://c1.scryfall.com/file/scryfall-cards/large/front/d/d/dd921e27-3e08-438c-bec2-723226d35175.jpg" height="300">

Trickery breaks powerlevel progression by allowing a player to counter one of his own 0-costed spells, and then take a gamble with the top of his deck. The potential payoff is revealing a 6+ mana costed spell which potentially wins the game on the spot.

Thus a trickery deck is crafted as a balanced of 4 Trickeries, some amount of lands, some amount of 0-costed spells and some amount of big spells to serve as payoff.
I wrote this script to find the ideal balance of lands, 0costs, and payoffs. The format in which this deck was popular contained 2 0-cost cards to choose from, and as such could contain from between 0 and 8 of them. My experiments showed 8 was the clear winner, with some number between 8 and 11 being possible if you could go that high. As for lands and payoffs, as I did not fit for multiple pay  off hits, it varied wildly, with some epochs reaching equilibrium with 20 lands. 
