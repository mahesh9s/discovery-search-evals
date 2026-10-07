# Failure analysis: `hybrid` on the dev set

20 of 40 queries fail (NDCG@10 below 0.5, or 0.1 or more behind `keyword_meta`).

| Root cause | Queries | What it means |
|---|---|---|
| `mood_not_in_metadata` | 7 | The person asked for a feeling. Synopses describe plot and credits, so there is nothing for any ranker to match. |
| `name_not_understood` | 5 | An actor's name. The embedding model has no idea who people are, and fusing its guesses in pushes real cast matches down. |
| `title_outranked` | 4 | The exact title exists but a sequel, a lookalike or a common-word match is ranked above it. |
| `vocabulary_gap` | 3 | The catalog describes the film in different words from the ones the person used. |
| `typo` | 1 | A misspelled title. Keyword matching returns an empty page. |

## n03: "the dark knight"

Slice: navigational. NDCG@10 0.70 (baseline 0.85). Root cause: `title_outranked`.

The Dark Knight Rises above The Dark Knight once synopses are indexed: the sequel's synopsis repeats the original's title.

Returned: The Dark Knight Rises (2012) [1]; The Dark Knight (2008) [2]; Detective Knight: Independence (2023) [0]; A Knight's Tale (2001) [0]; Detective Knight: Redemption (2022) [0].

## n05: "spiderman into the spider verse"

Slice: navigational. NDCG@10 0.63 (baseline 1.00). Root cause: `title_outranked`.

Typed 'spiderman' with no hyphen, so the title match is partial and five other Spider-Man films crowd in.

Returned: Spider-Man: Across the Spider-Verse (2023) [1]; Spider-Man (2002) [0]; The Amazing Spider-Man (2012) [0]; Spider-Man: Into the Spider-Verse (2018) [2]; Spider-Man: No Way Home (2021) [0].

## n06: "oceans eleven"

Slice: navigational. NDCG@10 0.84 (baseline 0.95). Root cause: `title_outranked`.

Ocean's Twelve above Ocean's Eleven in the fused list.

Returned: Ocean's Twelve (2004) [1]; Ocean's Eleven (2001) [2]; Ocean's Thirteen (2007) [1]; Ocean's 8 (2018) [1]; Clubland (2007) [0].

## n07: "get out"

Slice: navigational. NDCG@10 0.30 (baseline 1.00). Root cause: `title_outranked`.

'get out' is two common words. The embedding returns Catch and Release and Snow Day; fused, the real title drops to rank 9.

Returned: Crush (2022) [0]; Why Did I Get Married? (2007) [0]; Fall Down Dead (2009) [0]; An American Pickle (2020) [0]; Frozen (2010) [0].

## n08: "intersteller"

Slice: navigational. NDCG@10 0.36 (baseline 0.00). Root cause: `typo`.

'intersteller'. Empty page from keyword search. The embedding gets close (space films) and finds Interstellar at rank 6.

Returned: Solo: A Star Wars Story (2018) [0]; Star Trek Nemesis (2002) [0]; Star Wars: The Rise of Skywalker (2019) [0]; Star Trek (2009) [0]; Zack Snyder's Justice League (2021) [0].

## p01: "saoirse ronan movies"

Slice: person. NDCG@10 0.87 (baseline 1.00). Root cause: `name_not_understood`.

Saoirse Ronan. Embedding results include both Lord of the Rings films.

Returned: On Chesil Beach (2018) [2]; Atonement (2007) [2]; Mary Queen of Scots (2018) [2]; The Seagull (2018) [2]; Lost River (2015) [2].

Missed 6 top-grade answers, including: Brooklyn (2015); City of Ember (2008); Lady Bird (2017).

## p03: "movies with florence pugh"

Slice: person. NDCG@10 0.61 (baseline 1.00). Root cause: `name_not_understood`.

Florence Pugh. Embedding top 5 has none of her films: Funny Games, She Creature, The Purge.

Returned: Puss in Boots: The Last Wish (2022) [2]; Funny Games (2008) [0]; Midsommar (2019) [2]; Don't Worry Darling (2022) [2]; She Creature (2001) [0].

Missed 4 top-grade answers, including: Dune: Part Two (2023); Little Women (2019); Oppenheimer (2023).

## p05: "viola davis"

Slice: person. NDCG@10 0.86 (baseline 1.00). Root cause: `name_not_understood`.

Viola Davis.

Returned: Prisoners (2013) [2]; Ma Rainey's Black Bottom (2020) [2]; The Unforgivable (2021) [2]; Air (2023) [2]; It's Kind of a Funny Story (2010) [2].

Missed 18 top-grade answers, including: Blackhat (2015); Disturbia (2007); Eat Pray Love (2010).

## p07: "amy adams"

Slice: person. NDCG@10 0.55 (baseline 0.94). Root cause: `name_not_understood`.

Amy Adams. Zero of the embedding's top 10 are hers.

Returned: Adam (2009) [0]; Hillbilly Elegy (2020) [2]; Miss Pettigrew Lives for a Day (2008) [2]; Cruel Intentions 2 (2001) [2]; Beautiful Boy (2018) [0].

Missed 25 top-grade answers, including: American Hustle (2013); Arrival (2016); Batman v Superman: Dawn of Justice (2016).

## p08: "mahershala ali"

Slice: person. NDCG@10 0.67 (baseline 0.84). Root cause: `name_not_understood`.

Mahershala Ali. The embedding returns Talaash, Bol and Thalaivaa; the fused list adds the boxing biopic Ali.

Returned: Leave the World Behind (2023) [2]; Hidden Figures (2016) [2]; Bol (2011) [0]; Lemon Tree (2009) [0]; Ali (2001) [0].

Missed 3 top-grade answers, including: Free State of Jones (2016); Spider-Man: Into the Spider-Verse (2018); The Curious Case of Benjamin Button (2008).

## c07: "courtroom drama"

Slice: category. NDCG@10 0.07 (baseline 0.00). Root cause: `vocabulary_gap`.

'courtroom drama'. The catalog's genre label is Legal and only 2 of 5,065 synopses say 'courtroom'. Every system returns generic dramas.

Returned: Scottsboro: An American Tragedy (2000) [1]; Last Ride (2012) [0]; Sweet Country (2018) [0]; Rust and Bone (2012) [0]; Unforgettable (2017) [0].

Missed 13 top-grade answers, including: Conviction (2010); Fracture (2007); High Crimes (2002).

## d02: "soldier relives the same day fighting aliens"

Slice: descriptive. NDCG@10 0.00 (baseline 0.00). Root cause: `vocabulary_gap`.

Edge of Tomorrow's synopsis says 'time loop', the query says 'relives the same day'. Nothing bridges the two.

Returned: Evil Alien Conquerors (2003) [0]; Alien vs. Predator (2004) [0]; The Tomorrow War (2021) [0]; We Were Soldiers (2002) [0]; Kids vs. Aliens (2023) [0].

Missed 1 top-grade answers, including: Edge of Tomorrow (2014).

## d04: "man falls in love with his computer operating system"

Slice: descriptive. NDCG@10 0.00 (baseline 0.00). Root cause: `vocabulary_gap`.

Her's synopsis says 'artificially intelligent virtual assistant', the query says 'computer operating system'.

Returned: I Love You, Man (2009) [0]; Falling (2021) [0]; Operation Mincemeat (2022) [0]; The Notebook (2004) [0]; The Perfect Guy (2015) [0].

Missed 1 top-grade answers, including: Her (2013).

## v01: "feel-good movie about food and cooking"

Slice: vibe. NDCG@10 0.10 (baseline 0.03). Root cause: `mood_not_in_metadata`.

'feel-good' matches I Feel Pretty and Good Luck Chuck. Only the embedding finds Julie & Julia.

Returned: Super Size Me (2004) [0]; Good Luck Chuck (2007) [0]; Food, Inc. (2009) [0]; Mr. Brooks (2007) [0]; Planes: Fire & Rescue (2014) [0].

Missed 7 top-grade answers, including: Chocolat (2000); Last Holiday (2006); No Reservations (2007).

## v02: "something scary but not gory"

Slice: vibe. NDCG@10 0.32 (baseline 0.12). Root cause: `mood_not_in_metadata`.

'scary but not gory'. Keyword returns the Scary Movie parodies. No field says how violent a film is.

Returned: Scary Movie 3 (2003) [0]; Scary Stories to Tell in the Dark (2019) [2]; Scary Movie 2 (2001) [0]; Scary Movie (2000) [0]; Down a Dark Hall (2018) [2].

Missed 30 top-grade answers, including: 10 Cloverfield Lane (2016); 1408 (2007); A Quiet Place (2018).

## v03: "movies that will make me cry"

Slice: vibe. NDCG@10 0.02 (baseline 0.00). Root cause: `mood_not_in_metadata`.

'make me cry' returns Cry Macho and Cry Wolf. Of 28 known tearjerkers, one reaches any system's top 10, at rank 9.

Returned: Out Cold (2001) [0]; Tupac: Resurrection (2003) [0]; X Games: The Movie (2009) [0]; Cry Macho (2021) [0]; Scary Movie 5 (2013) [0].

Missed 28 top-grade answers, including: A Dog's Purpose (2017); A Star Is Born (2018); A Walk to Remember (2002).

## v04: "mind-bending sci-fi with a twist"

Slice: vibe. NDCG@10 0.23 (baseline 0.15). Root cause: `mood_not_in_metadata`.

'mind-bending ... with a twist' returns Cinderella III: A Twist in Time.

Returned: Idiocracy (2006) [0]; Significant Other (2022) [1]; After Earth (2013) [0]; The Darkest Minds (2018) [0]; Eternal Sunshine of the Spotless Mind (2004) [2].

Missed 22 top-grade answers, including: Annihilation (2018); Arrival (2016); Black Box (2020).

## v05: "funny movie to watch with the whole family"

Slice: vibe. NDCG@10 0.38 (baseline 0.00). Root cause: `mood_not_in_metadata`.

'funny ... whole family' returns Funny Games, a home-invasion horror film, from keyword search.

Returned: Funny Games (2008) [0]; Dysfunktional Family (2003) [0]; Instant Family (2018) [1]; Stuck in the Suburbs (2004) [1]; The Fitzgerald Family Christmas (2012) [0].

Missed 41 top-grade answers, including: Alexander and the Terrible, Horrible, No Good, Very Bad Day (2014); Are We There Yet? (2005); Cheaper by the Dozen (2003).

## v07: "inspiring true story about an underdog athlete"

Slice: vibe. NDCG@10 0.46 (baseline 0.18). Root cause: `mood_not_in_metadata`.

Half right: sports biopics surface, but so does DodgeBall: A True Underdog Story.

Returned: The Case for Christ (2017) [0]; Radio (2003) [1]; Facing the Giants (2006) [1]; Glory Road (2006) [2]; DodgeBall: A True Underdog Story (2004) [1].

Missed 30 top-grade answers, including: 12 Mighty Orphans (2021); 42 (2013); American Underdog (2021).

## v08: "dark comedy about rich people behaving badly"

Slice: vibe. NDCG@10 0.13 (baseline 0.00). Root cause: `mood_not_in_metadata`.

'behaving badly' returns Bad Samaritan, Bad Times at the El Royale and The Bad Batch.

Returned: Dear White People (2014) [1]; The Dirt (2019) [0]; Funny People (2009) [0]; The Bad Guys (2022) [0]; Crazy Rich Asians (2018) [1].

Missed 10 top-grade answers, including: American Psycho (2000); Bodies Bodies Bodies (2022); Glass Onion: A Knives Out Mystery (2022).
