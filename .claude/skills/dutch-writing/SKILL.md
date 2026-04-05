---
name: dutch-writing
description: >
  Ensure Dutch prose reads like a native Dutch person wrote it, not like
  AI-translated-from-English text. Detects and fixes Dutch-specific AI
  writing patterns: literal English calques ("De Lijn Knijf" → "De Knijven"),
  archaic vocabulary nobody uses ("lemmet", "desalniettemin"), Anglo-centric
  framing (comparing Dutch institutions to British equivalents), over-formal
  register, Title Case in Dutch headings, em dash journalism patterns,
  overuse of "jou/je/u" (Dutch avoids direct address), and over-explaining
  things Dutch readers already know. Use this skill when writing or editing
  ANY Dutch prose — stories, narratives, reports. Also use when another
  skill (like /story or /humanizer) produces Dutch text that needs a
  native-feel pass. Triggers on: "check the Dutch", "make it sound more
  Dutch", "this reads like a translation", "fix the Dutch",
  "/dutch-writing", or whenever you're writing Dutch text longer than a
  paragraph.
---

# Natuurlijk Nederlands schrijven

Dutch AI text has its own failure modes, distinct from English. The English
humanizer catches generic AI patterns (significance inflation, rule of three,
sycophantic tone). This skill catches the patterns that make Dutch text read
like it was written by someone who thinks in English and translates.

The core test: **would a Dutch person actually say this out loud?** If not,
rewrite it.

## How to use

Apply these checks during writing or as a review pass after drafting. When
used alongside the humanizer skill, run the humanizer first (universal AI
patterns), then this skill for Dutch-specific issues.

## Patterns

### 1. Literal English calques

AI thinks in English and translates literally. The result is grammatically
correct Dutch that no Dutch person would write.

| English construct | AI-Dutch (wrong) | Natural Dutch |
|---|---|---|
| "The Knijf Line" | "De Lijn Knijf" | "De Knijven" / "de familie Knijf" |
| "A Name Like a Blade" | "Een Naam als een Lemmet" | "Een familienaam die 'mes' betekent" |
| "The Line to You" | "De Lijn naar Jou" | "De Lijn" (drop the address) |
| "It makes sense" | "Het maakt zin" | "Het is logisch" / "Dat klopt" |
| "In terms of" | "In termen van" | "Wat betreft" / "Qua" |
| "At the end of the day" | "Aan het einde van de dag" | "Uiteindelijk" |

**Test:** read the sentence aloud — does it sound like a dubbed movie?
Then it's a calque.

**Before:**
> De Lijn Knijf: Een Familie Door Vier Eeuwen Nederlandse Geschiedenis

**After:**
> De Knijven: een familie door vier eeuwen Nederlandse geschiedenis


### 2. Avoiding "jou/je" and "u"

Dutch has an unresolved formal/informal tension between "je/jou" (informal)
and "u" (formal). Rather than choose wrong, Dutch people usually avoid
direct address altogether. AI, trained on English where "you/your" is
everywhere, over-translates it into Dutch.

**Before:**
> De lijn naar jou — veertien generaties van jouw voorouders.

**After:**
> Veertien generaties voorouders.

**Before:**
> In dit verhaal nemen we je mee door vier eeuwen familiegeschiedenis.

**After:**
> Dit verhaal beslaat vier eeuwen familiegeschiedenis.

This doesn't mean "je" is forbidden — it's fine in casual contexts
("als je dat leest" in a chatty aside). But as a structural element
or in titles, Dutch avoids it where English would use "you" freely.
When in doubt, restructure the sentence to not need it.


### 3. Title Case

Dutch capitalizes only the first word of titles/headings, plus proper
nouns. Title Case (capitalizing every major word) is English.

**Before:**
> Een Naam als een Lemmet
> De Laatste Woerdense Knijffs
> De Gouden Eeuw Pannenbakkers

**After:**
> Een naam als een lemmet
> De laatste Woerdense Knijffs
> De Gouden Eeuw-pannenbakkers

"Gouden Eeuw" stays capitalized — it's a proper noun (historical period).
"Pannenbakkers" gets lowercased — common noun.


### 4. Archaic vocabulary

AI reaches for impressive-sounding Dutch words that exist in dictionaries
but nobody uses in modern writing.

| AI loves | Normal Dutch |
|---|---|
| lemmet | mes, kling |
| onontbeerlijk | onmisbaar, nodig |
| desalniettemin | toch, desondanks |
| doch | maar |
| geenszins | helemaal niet |
| nimmer | nooit |
| welhaast | bijna |
| poniaard | dolk, steekwapen |
| aldus | zo |
| voorts | ook, verder |
| gaandeweg | geleidelijk |

**Test:** would you use this word in a WhatsApp message? If not, find a
simpler one. Exceptions: when quoting a historical source, keep the
original language. When describing a historical object or concept,
period-appropriate vocabulary is fine ("poniaard" for a medieval dagger,
"schout" for a pre-1811 official).

**Before:**
> Een Naam als een Lemmet — de achternaam Knijff is het Middelnederlandse
> woord voor een poniaard, een puntig steekwapen.

**After:**
> De achternaam Knijff is het oude woord voor mes — een lang steekwapen.


### 5. Anglo-centric framing

AI explains Dutch concepts by comparing them to British or American
equivalents. For Dutch readers, this is patronizing.

**Before:**
> Hij ontving de Militaire Willems-Orde — de hoogste Nederlandse militaire
> onderscheiding, vergelijkbaar met het Britse Victoria Cross.

**After:**
> Hij ontving de Militaire Willems-Orde.

**Things that don't need explaining to Dutch readers:**
- Militaire Willems-Orde, VOC, WIC, Deltawerken
- Polders, dijken, waterschappen
- De Veluwe, de Betuwe, de Achterhoek, de Randstad
- Burgerlijke Stand, Gereformeerde Kerk, diaconie
- Sinterklaas, Koningsdag, Bevrijdingsdag
- Verzuiling, gedogen, nuchterheid
- How inundation lines worked

**When to explain:** when genuinely obscure even for Dutch readers —
specialized archive terminology, specific guild structures, military
tactics. Even then, weave it into the narrative instead of bolting on
an em-dash explanation.


### 6. AI-Dutch vocabulary

Correct Dutch but used 10x more by AI than by humans. The Dutch
equivalents of English AI's "delve" and "tapestry."

| AI-Dutch | Use instead |
|---|---|
| cruciaal | belangrijk, wezenlijk |
| het landschap (abstract) | de wereld, de situatie |
| een schat aan | veel, een hoop |
| het is belangrijk op te merken dat | (just state the fact) |
| in het huidige landschap | tegenwoordig |
| daarnaast (paragraph opener) | ook, bovendien, or just start |
| echter (overused) | maar, toch |
| tevens | ook |
| derhalve | daarom |
| teneinde | om ... te |
| bewerkstelligen | regelen, zorgen voor |
| faciliteren | mogelijk maken |
| optimaliseren | verbeteren |
| implementeren | invoeren |


### 7. Overly formal register

AI defaults to beleidsnota-Dutch, not book-Dutch.

**Signs:**
- "men" instead of "je/we/de mensen"
- Passive voice where active is natural
- Nominalisations: "het uitvoeren van" instead of just the verb
- "dient te worden" instead of "moet"

**Before:**
> Men kan stellen dat de pannenbakkerij van aanzienlijk belang was voor
> de lokale economie.

**After:**
> De pannenbakkerij was belangrijk voor Woerden.

Match the register to the audience. Family history reads like a book,
not an ambtelijk rapport.


### 8. Em-dash explanatory appositive

"X — de Y van Z" is English journalism. Dutch uses it much less.

**Before:**
> De Petruskerk — de belangrijkste kerk van Woerden — was een laat-gotische
> basiliek. Bernard Costerus — de stadssecretaris — hield een dagboek bij.

**After:**
> De Petruskerk, de belangrijkste kerk van Woerden, was een laat-gotische
> basiliek. Stadssecretaris Bernard Costerus hield een dagboek bij.

Dutch alternatives: commas, parentheses, a separate sentence, or move
the descriptor before the name ("stadssecretaris Costerus").

One em dash per page is fine. Five per page is AI.


### 9. Over-explaining for Dutch readers

AI writes for a global audience. Dutch text for Dutch readers shouldn't
explain what a polder is.

**Before:**
> De Veluwe — een uitgestrekt bos- en heidegebied in de provincie
> Gelderland, het grootste aaneengesloten natuurgebied van Nederland —
> was het nieuwe thuisland van de familie.

**After:**
> De familie vestigde zich op de Veluwe.

**Rule:** if it's in de Bosatlas or on het Journaal, don't explain it.


### 10. Missing Dutch naturalness

Dutch has patterns AI underuses because they lack English equivalents.

**Diminutives:** Dutch uses them constantly — for smallness, affection,
casualness. AI barely uses them.
- een huis*je* langs de Rijn
- een bier*tje* na het werk

**"Er" constructions:**
- "Er woonden twintig families" (not "Twintig families woonden daar")
- "Er was geen werk meer"

**Modal particles:** "wel", "toch", "maar", "even", "eigenlijk",
"gewoon" add nuance AI skips.
- "Het was toch een mooi gezicht"
- "Dat is eigenlijk best bijzonder"
- "Het ging gewoon niet meer"

**Sentence-initial variation:** Dutch often fronts adverbs or
prepositional phrases: "In 1672 viel Frankrijk aan" — not always
subject-first like English.

Don't force these, but their total absence in a multi-page Dutch text
is a tell.


## Quick checklist

- [ ] Title Case in headings → sentence case
- [ ] "De Lijn X" or "De X Lijn" → "de familie X" or "de X-en"
- [ ] "jou/je/u" used where Dutch would avoid direct address
- [ ] More than 2 em dashes per page
- [ ] Words from the archaic vocabulary list
- [ ] Explaining Dutch concepts to Dutch readers
- [ ] Comparing Dutch things to British/American equivalents
- [ ] "Men" or excessive passive voice
- [ ] AI-Dutch vocabulary (cruciaal, het landschap, een schat aan)
- [ ] Zero diminutives in multi-page text
- [ ] Zero modal particles (toch, eigenlijk, gewoon)
- [ ] Every sentence starting with the subject
- [ ] "Daarnaast" as paragraph opener more than once
