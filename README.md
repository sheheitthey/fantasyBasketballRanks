fantasyBasketballRanks
======================

A toolset for analyzing and ranking fantasy basketball stats.

I created this to do fantasy basketball drafts with my own interpretations on
how to rank players/teams while minimizing subjective and irrational decisions
often made during a live draft. That season, I used this on the live draft in
my private league and on two autodrafted public leagues. For most of the
season (before injuries or playoffs), I had mediocre performance in the
private league and pretty strong performance in the public leagues.

The basic analysis for each stat is to compute its standard score (z-score)
within the population. Then a player's total score is the sum of his stat
scores, and a team's stat scores and total score are the sums of those. A few
tweaks included qualifying values only if the player had played enough games,
adding players that didn't have stats because they were to become rookies, and
scaling players by my antipated modification of their minutes.

Not directly used in ranking, but for each stat the toolset also prints the
overall mean, standard deviation, and the number of players who had reached a
"high enough" value to not be a liability. This gave me a sense of comparison
for the actual values (instead of standard scores) for the stats and also
showed me that assists were the rarest stat.
