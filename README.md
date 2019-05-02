Come play [gin ricky](https://heyhowsgame.herokuapp.com). It is an easier and faster version of gin rummy, made up by my friend's uncle named Ricky

# Rules

You and your opponent get dealt 7 cards, and one card is placed face up in the discard pile. You alternate turns, either drawing from the discard or from the top of the deck. Then you discard one of your cards face up onto the discard, and the other person goes. Your goal is to make a *3-meld* and a *4-meld* in your hand; when you do this, you win.

A meld is a group of cards that are either all the same rank or a straight flush (e.g. 6s-7s-8s). An ace can play either high or low (e.g. Ax-2x-3x-4x and Qx-Kx-Ax are both valid melds)

The first person who makes both a 3-meld and a 4-meld gets 0 points. The other person's hand is scored according to the un-melded cards left in their hand. However, if you have two 3-melds in your hand, only one of them is exempt from accruing points

The scoring system:
| Rank  | Points          |
|-------|-----------------|
| Ace   | 1               |
| 2-10  | The card's rank |
| Jack  | 11              |
| Queen | 12              |
| King  | 13              |

More concretely, here is how you'd score each of the main types of losing hands:
- **No melds**: If you finish with no 3- or 4-melds, then sum up the ranks of the cards in your hand. This is simple but painful.
- **One 3-meld**: Sum up the points for the 4 non-melded cards
- **One 4-meld**: Sum up the points for the 3 non-melded cards
- **Two 3-melds, one stray card**: Sum up the stray card plus whichever meld has less points. Example: suppose your hand is *(6s-7s-8s) (3c-3d-3h) (Ah)*. Since the run of spades is more points than trip threes, you'd count the run of spades as your meld, and count the threes towards your hand. The total would be 1+3+3+3=10 points

Generally you'd play a group of games until someone gets 50 or 100 points. This app does not support that functionality yet

# Basic strategy
If you are consistently losing games with >20 points in your hand, then you are playing too aggressively to win. It's okay to shoot for one high-point meld early on if that's what the cards dictate, but as the game goes on you have to dump all of your big cards
