import os
from os import path
import csv
import re
from statistics import stdev
import spacy
import json
import sys
import shutil
from operator import itemgetter


#Fetches the whole_text from the PHP POST method.
whole_text = sys.argv[1].replace("\?", "?").replace('\"', '"').replace("\;", ";").replace("\(", "(").replace("\)", ")").replace("\&", "&").replace("\+", "+").replace("\*", "*").replace("\[", "[").replace("\]", "]").replace("\{", "{").replace("\}", "}").replace("\$", "$").replace("\=", "=").replace("\!", "!").replace("\^", "^").replace("\<", "<").replace("\>", ">").replace("\|", "|").replace("\:", ":").replace("\-", "-").replace("\/", "/")

#The English accent (British vs US-English) will determine which heteronyms list is used for the substitution of the Speech Synthesis Markup Language (SSML) "phoneme" tags for their corresponding
#heteronyms. This will have an impact on which heteronums get their pronounciation altered (such as "address", which is pronounced the same in British English whether it is a noun or a verb,
#but is pronounced differently for these two parts of speech in American English). "English_Phonetics" defaults to American_English if the user didn't select a English accent value.
if len(sys.argv)>2:
    English_Phonetics = sys.argv[2]
else:
    English_Phonetics = "American_English"

cwd = os.getcwd()

#The order is of heteronyms in the lists is important here. For example: 'bows' needs to be substituted before 'bow', in order to avoid mixups.
#Having 'bow' before 'bows' in the lists would lead to 'bows' being converted to 'bough' and 'bow' instead of 'boughs' and 'bose',
#as 'bow' is found in 'bows'.

heteronyms_list_American_English = ["Absent", "Abstract", "Abuse", "Acuminate", "Addict", "Adduct", "Adept", "Adulterate", "Advert", "Advocate", "Affect", "Affiliate", "Agglomerate", "Agglutinate", "Aggregate", "Aliment", "Allied", "Alloy", "Ally", "Alternate", "Analyses", "Animate", "Annex", "Appropriate", "Approximate", "Arithmetic", "Articulate", "Aspirate", "Associate", "Attribute", "Augment", "August", "Axes", "Bases", "Blessed", "Bows", "Bow", "Buffet", "Certificate", "Chassis", "Close", "Coagulate", "Coax", "Collect", "Combat", "Combine", "Commune", "Compact", "Complex", "Compound", "Compress", "Concert", "Concrete", "Conduct", "Confect", "Confines", "Conflict", "Conglomerate", "Congress", "Conjugate", "Conscript", "Conserve", "Console", "Consociate", "Consort", "Consummate", "Construct", "Content", "Contest", "Contract", "Contrast", "Converse", "Convert", "Convict", "Coordinate", "Co-ordinate", "Crooked", "Decrease", "Defect", "Degenerate", "Delegate", "Deliberate", "Derogate", "Desert", "Desolate", "Deviate", "Diagnoses", "Diffuse", "Digest", "Dingy", "Discard", "Discharge", "Discord", "Discount", "Do", "Does", "Dogged", "Dove", "Duplicate", "Egress", "Ejaculate", "Elaborate", "Ellipses", "Entrance", "Envelop", "Escort", "Essay", "Estimate", "Excuse",  "Exploit", "Extract", "Ferment", "Frequent", "Graduate", "Hinder", "House", "Implant", "Import", "Impress", "Imprint", "Incense", "Incline", "Incorporate", "Increase", "Indent", "Initiate", "Insert", "Inset", "Instinct", "Insult", "Intercept", "Intermediate", "Intern", "Intimate", "Invite", "Isolate", "Jagged", "Lead", "Learned", "Legitimate", "Lied", "Live", "Lower", "Lupine", "Merchandise", "Minute", "Misconduct", "Misread", "Mobile", "Moderate", "Moped", "Mouse", "Mouth", "Mow", "Multiply", "Number", "Object", "Obligate", "Overage", "Overall", "Overhead", "Overlook", "Overrun", "Pedal", "Perfect", "Permit", "Pervert", "Polish", "Postulate", "Precedent", "Precipitate", "Predicate", "Premise", "Present", "Proceeds", "Produce", "Progress", "Project", "Proofread", "Protest", "Pussy", "Putting", "Raven", "Read", "Rebel", "Recall", "Recap", "Recess",  "Recoil", "Recollect", "Record", "Redress", "Refill", "Refit", "Reflex", "Refund", "Refuse", "Regenerate", "Regress", "Rehash", "Reject", "Relapse", "Relay", "Remake", "Repatriate", "Repent", "Replay", "Reprint", "Rerun", "Retake", "Retard", "Rewind", "Segment", "Separate", "Skied", "Sow", "Stabile", "Stipulate", "Subject", "Supply", "Supposed", "Survey", "Suspect", "Syndicate", "Tarry", "Tear", "Torment", "Transect", "Transplant", "Transport", "Upset", "Use", "Used", "Wicked", "Wind", "Wound"]

heteronyms_list_British_English = ["Absent", "Abstract", "Abuse", "Accent", "Acuminate", "Addict", "Adduct", "Adept", "Adulterate", "Advert", "Advocate", "Affect", "Affiliate", "Agglomerate", "Agglutinate", "Aggregate", "Aliment", "Allied", "Alloy", "Ally", "Alternate", "Analyses", "Animate", "Annex", "Appropriate", "Approximate", "Arithmetic", "Articulate", "Aspirate", "Associate", "Attribute", "Augment", "August", "Axes", "Bases", "Bows", "Blessed", "Bow", "Buffet", "Certificate", "Chassis", "Close", "Coagulate", "Coax", "Collect", "Combat", "Combine", "Commune", "Compact", "Compound", "Compress", "Concert", "Conduct", "Confect", "Confines", "Conflict", "Conglomerate", "Congress", "Conjugate", "Conscript", "Console", "Consociate", "Consort", "Consummate", "Construct", "Content", "Contest", "Contract", "Contrast", "Converse", "Convert", "Convict", "Coordinate", "Co-ordinate", "Crooked", "Decrease", "Defect", "Degenerate", "Deliberate", "Derogate", "Desert", "Desolate", "Deviate", "Diagnoses", "Diffuse", "Digest", "Dingy", "Discard", "Discharge", "Discord", "Discount", "Do", "Does", "Dogged", "Dove", "Duplicate", "Egress", "Ejaculate", "Elaborate", "Ellipses", "Entrance", "Envelop", "Escort", "Essay", "Estimate", "Excise", "Excuse", "Exploit", "Extract", "Ferment", "Frequent", "Graduate", "Hinder", "House", "Implant", "Import", "Impress", "Imprint", "Incense", "Incline", "Incorporate", "Increase", "Indent", "Initiate", "Insert", "Inset", "Instinct", "Insult", "Intercept", "Intermediate", "Intern", "Intimate", "Invite", "Involute", "Isolate", "Jagged", "Lead", "Learned", "Legitimate", "Lied", "Live", "Lower", "Lupine", "Merchandise", "Minute", "Misconduct", "Misread", "Mobile", "Moderate", "Moped", "Mouse", "Mouth", "Mow", "Multiply", "Number", "Object", "Overage", "Overall", "Overhead", "Overlook", "Overrun", "Pedal", "Perfect", "Permit", "Pervert", "Polish", "Postulate", "Precedent", "Precipitate", "Predicate", "Premise", "Present", "Proceeds", "Produce", "Progress", "Project", "Proofread", "Prospect", "Protest", "Pussy", "Putting", "Raven", "Read", "Rebel", "Recall", "Recap", "Recess", "Recitative", "Recoil", "Recollect", "Record", "Refill", "Refit", "Reflex", "Refund", "Refuse", "Regenerate", "Regress", "Rehash", "Reject", "Relapse", "Relay", "Remake", "Repatriate", "Repent", "Replay", "Reprint", "Rerun", "Retake", "Retard", "Rewind", "Segment", "Separate", "Skied", "Sow", "Stipulate", "Subject", "Supply", "Supposed", "Survey", "Suspect", "Syndicate", "Tarry", "Tear", "Torment", "Transect", "Transfer", "Transplant", "Transport", "Upset", "Use", "Used", "Wicked", "Wind", "Wound"]

onomatopoeias = ["[^\w]Achoo[^\w]", "[^\w]Arg[h]+[^\w]", "[^\w]Br[r]+ng[^\w]", "[^\w]BR[R]+[^\w]", "[^\w]Br[r]+[^\w]", "[^\w]Bz[z]+[^\w]", "[^\w]Ca-ching[^\w]", "[^\w]Chaching[^\w]", "[^\w]Ka-ching[^\w]", "[^\w]Kerching[^\w]", "[^\w]Ca-chunk[^\w]", "[^\w]Ka-chunk[^\w]", "[^\w]G-R[-R]+[^\w]", "[^\w]G-r[-r]+[^\w]", "[^\w]GR[R]+[^\w]", "[^\w]Gr[r]+[^\w]", "[^\w]Pizzaz[^\w]", "[^\w]Ps[s]+t[^\w]", "[^\w]Sh[h]+[^\w]", "[^\w]T[s]+k[^\w]", "[^\w]Ug[h]+[^\w]", "[^\w]Yip pee[^\w]", "[^\w]Yippee[^\w]", "[^\w]Zz[z]+[^\w]", "[^\w]Pshaw[^\w]"]
modified_onomatopoeias = ['<phoneme alphabet="ipa" ph="????t????u??">Achoo</phoneme>', '<phoneme alphabet="ipa" ph="????x">Argh</phoneme>', '<phoneme alphabet="ipa" ph="??bri??">Ring</phoneme>', '<phoneme alphabet="ipa" ph="b??r">Shiver</phoneme>', '<phoneme alphabet="ipa" ph="b??r">Shiver</phoneme>', '<phoneme alphabet="ipa" ph="b??z">Buzz</phoneme>', '<phoneme alphabet="ipa" ph="t??????t??????">Ca-ching</phoneme>', '<phoneme alphabet="ipa" ph="t??????t??????">Chaching</phoneme>', '<phoneme alphabet="ipa" ph="t??????t??????">Ka-ching</phoneme>', '<phoneme alphabet="ipa" ph="t??????t??????">Kerching</phoneme>', '<phoneme alphabet="ipa" ph="??k??ch????k">Ca-chunk</phoneme>', '<phoneme alphabet="ipa" ph="??k??ch????k">Ka-chunk</phoneme>', '<phoneme alphabet="ipa" ph="??g??r">Growl</phoneme>', '<phoneme alphabet="ipa" ph="??g??r">Growl</phoneme>', '<phoneme alphabet="ipa" ph="??g??r">Growl</phoneme>', '<phoneme alphabet="ipa" ph="??g??r">Growl</phoneme>', '<phoneme alphabet="ipa" ph="p??z??z">Pizzaz</phoneme>', '<phoneme alphabet="ipa" ph="pst">Hist</phoneme>', '<phoneme alphabet="ipa" ph="??">Shush</phoneme>', '<phoneme alphabet="ipa" ph="t??sk">Tisk</phoneme>', '<phoneme alphabet="ipa" ph="????x">Ugh</phoneme>', '<phoneme alphabet="ipa" ph="j??pi??">Yip pee</phoneme>', '<phoneme alphabet="ipa" ph="j??pi??">Yippee</phoneme>', '<phoneme alphabet="ipa" ph="zi??z">Snore</phoneme>', '<phoneme alphabet="ipa" ph="????">Pshaw</phoneme>']

hyphens = [' --', ' ???', '-- ', '??? ' , ' -- ', ' ??? ', '--', '???']

#Since in some cases I am adding a comma on both sides of the phrase, I thus include [^\w] on both sides of the phrase, in the event that there is aldready a comma in these locations. I know [^\w] is not strictly needed on the left side, and that in theory a space could preclude inclusion of words containing such suffixes, but better safe than sorry in the event that there is a comma right next to the word (ex: ",admittedly") and where I want to add a comma on either side of the phrase.
linking_words_middle_of_sentence_no_comma = ["[^\w]admittedly[^\w]", "[^\w]as a result of[^\w]", "[^\w]as a result[^\w]", "[^\w]but[^\w]", ", but one[^\w]", "[^\w]by the way[^\w]", "[^\w]despite the[^\w]", "[^\w]for example[^\w]", "[^\w]for instance[^\w]", "[^\w]hence[^\w]", "[^\w]in addition[^\w]", "[^\w]in spite of[^\w]", "[^\w]in the same way[^\w]", "[^\w]including[^\w]", "[^\w]indeed[^\w]", "[^\w]moreover[^\w]", "[^\w]namely[^\w]", "[^\w]nor[^\w]", "[^\w]on the contrary[^\w]", "[^\w]on the one hand[^\w]", "[^\w]on the other hand[^\w]", "[^\w]as a consequence[^\w]", "[^\w]which indeed[^\w]"]
linking_words_middle_of_sentence_with_comma = [", admittedly, ", ", as a result of ", ", as a result, ", ", but ", " but one ", ", by the way, ", ", despite the ", ", for example, ", ", for instance, ", ", hence ", ", in addition ", ", in spite of ", ", in the same way, ", ", including ", ", indeed, ", ", moreover, ", ", namely ", ", nor ", ", on the contrary, ", ", on the one hand, ", ", on the other hand, ", "as a consequence, ", ", which indeed "]

but_middle_of_sentence_comma_inside = ["[^\w]all, but[^\w]", "[^\w]anything, but[^\w]", "[^\w]can.t, but[^\w]", "[^\w]cannot, but[^\w]", "[^\w]everything, but[^\w]", "[^\w]is, but[^\w]", "[^\w]last, but not least[^\w]", "[^\w]none, but[^\w]", "[^\w]nothing, but[^\w]", "[^\w]sad, but true[^\w]", "[^\w]slow, but sure[^\w]", "[^\w]slowly, but surely[^\w]", "[^\w]was, but[^\w]"]
but_middle_of_sentence_no_comma = [" all but ", " anything but ", " can.t but ", " cannot but ", " everything but ", " is but ", " last but not least, ", " none but ", " nothing but ", " sad but true ", " slow but sure ", " slowly but surely ", " was but "]

linking_words_start_of_sentence_no_comma = ["Additionally ", "Admittedly ", "As a consequence ", "As a result ", "Besides ", "But ", "By the way ", "Consequently ", "Conversely ", "Firstly ", "For example ", "For instance ", "Furthermore ", "Hence ", "Importantly ", "In addition ", "In conclusion ", "In spite of this ", "In spite of that ", "In the same way ", "Indeed ", "Moreover ", "Namely ", "Nevertheless ", "Nonetheless ", "On the contrary ", "On the one hand ", "On the other hand ", "Secondly ", "Similarly ", "Specifically ", "Subsequently ", "Therefore ", "Thus "]
linking_words_start_of_sentence_with_comma = ["Additionally, ", "Admittedly, ", "As a consequence, ", "As a result, ", "Besides, ", "But, ", "By the way, ", "Consequently, ", "Conversely, ", "Firstly, ", "For example, ", "For instance, ", "Furthermore, ", "Hence, ", "Importantly, ", "In addition, ", "In conclusion, ", "In spite of this, ", "In spite of that, ", "In the same way, ", "Indeed, ", "Moreover, ", "Namely, ", "Nevertheless, ", "Nonetheless, ", "On the contrary, ", "On the one hand, ", "On the other hand, ", "Secondly, ", "Similarly, ", "Specifically, ", "Subsequently, ", "Therefore, ", "Thus, "]

yet_comma_inside_capitalized = ["And, yet", "Anything, yet", "As of, yet", "As, yet", "Better, yet", "But, yet", "Can[.]t, yet", "Cannot, yet", "From, yet", "He, yet", "I, yet", "Just, yet", "May, yet", "Might, yet", "Never, yet", "Not just, yet", "Not, yet", "Nothing, yet", "Of, yet", "She, yet", "They, yet", "We, yet", "Worse, yet"]
yet_no_comma_capitalized = ["And yet, ", "Anything yet", "As of yet, ", "As yet, ", "Better yet, ", "But yet", "Can[.]t yet", "Cannot yet", "From yet", "He yet", "I yet", "Just yet", "May yet", "Might yet", "Never yet", "Not just yet", "Not yet", "Nothing yet", "Of yet", "She yet", "They yet", "We yet", "Worse yet"]

#I do not put [^\w] on the right side of 'yet', only instances of ' yet ' have been replaced by ', yet ' to begin with (the same logic applies for the other phrases such as 'which'). I do not put a space on the right side of 'yet', as I want to include results already having a comma in that position. This is important, as I am removing superfluous inside commas from all phrases, whether or not they have a comma on the right side. I know [^\w] is not strictly needed on the left side, and that in theory a space could preclude inclusion of words containing such suffixes, but better safe than sorry in the event that there is a comma right next to the word (ex: ",anything, yet").
yet_comma_inside_lowercase = ["[^\w]anything, yet", "[^\w]are, yet", "[^\w]aren[.]t, yet", "[^\w]arrived, yet", "[^\w]as of, yet", "[^\w]as, yet", "[^\w]better, yet", "[^\w]but, yet", "[^\w]can[.]t, yet", "[^\w]cannot, yet", "[^\w]come, yet", "[^\w]did, yet", "[^\w]didn[.]t, yet", "[^\w]doesn[.]t, yet", "[^\w]don[.]t, yet", "[^\w]from, yet", "[^\w]had, yet", "[^\w]hadn[.]t, yet", "[^\w]has, yet", "[^\w]hasn[.]t, yet", "[^\w]he, yet", "[^\w]is, yet", "[^\w]just, yet", "[^\w]may, yet", "[^\w]might, yet", "[^\w]never, yet", "[^\w]not just, yet", "[^\w]not, yet", "[^\w]nothing, yet", "[^\w]of, yet", "[^\w]over, yet", "[^\w]quite, yet", "[^\w]seemed, yet", "[^\w]she, yet", "[^\w]they, yet", "[^\w]was, yet", "[^\w]wasn[.]t, yet", "[^\w]we, yet", "[^\w]were, yet", "[^\w]weren[.]t, yet", "[^\w]worse, yet", "[^\w]and, yet"]
yet_no_comma_lowercase = [" anything yet", " are yet", " aren[.]t yet", " arrived yet", " as of yet", " as yet", " better yet, ", " but yet", " can[.]t yet", " cannot yet", " come yet", " did yet", " didn[.]t yet", " doesn[.]t yet", " don[.]t yet", " from yet", " had yet", " hadn[.]t yet", " has yet", " hasn[.]t yet", " he yet", " is yet", " just yet", " may yet", " might yet", " never yet", " not just yet", " not yet", " nothing yet", " of yet", " over yet", " quite yet", " seemed yet", " she yet", " they yet", " was yet", " wasn[.]t yet", " we yet", " were yet", " weren[.]t yet", " worse yet", ", and yet"]

#I have the 'or' phrases capitalized, since I add a comma after 'believe it or not', 'sooner or later' and after 'for better or for worse', which could be at the beginning of the sentence (I do the substitutions for the capitalized and lower case versions of the phrases).
or_comma_inside = ["A thing, or two", "All, or none", "All, or nothing", "Believe it, or not", "Better, or for worse", "Better, or worse", "Black, or white", "Coming, or going", "Common, or garden", "Covered, or hedge", "Dead, or alive", "Deficit, or surplus", "Dick, or Harry", "Do, or die", "Double, or nothing", "Eight, or nine", "Either, or", "Feast, or famine", "Fight, or flight", "Fill, or kill", "Fish, or cut bait", "Five, or six", "For better, or for worse", "Four, or five", "Free, or die", "Friend, or foe", "Give, or take", "Head, or tail", "Heads, or tails", "Hell, or high water", "Hit, or miss", "Hook, or by crook", "Hook, or crook", "Kill, or cure", "Life, or death", "Like it, or lump it", "Like it, or not", "Little, or no", "Little, or none", "Love, or money", "Make, or break", "May, or may not", "Means, or foul", "More, or less", "Neck, or nothing", "Nine, or ten", "On, or about", "Once, or twice", "One, or another", "One, or more", "One, or other", "One, or the other", "One, or two", "One way, or another", "One way, or the other", "Out, or keeping", "Piss, or get off the pot", "Plus, or minus", "Put up, or shut up", "Rain, or shine", "Rhyme, or reason", "Sale, or return", "Seven, or eight", "Shape, or form", "Shape up, or ship out", "Shit, or get off the pot", "Sink, or swim", "Sinks, or swim", "Six, or seven", "Somehow, or other", "Something, or other", "Sooner, or later", "Sunk, or swim", "Take it, or leave it", "Thing, or two", "Three, or four", "Three, or more", "Trick, or treat", "Trick, or treater", "Trick, or treating", "Truth, or consequences", "Truth, or dare", "Two, or more", "Two, or three", "Whether, or no", "Win, or lose"]
or_no_comma = ["A thing or two", "All or none", "All or nothing", "Believe it or not, ", "Better or for worse", "Better or worse", "Black or white", "Coming or going", "Common or garden", "Covered or hedge", "Dead or alive", "Deficit or surplus", "Dick or Harry", "Do or die", "Double or nothing", "Eight or nine", "Either or", "Feast or famine", "Fight or flight", "Fill or kill", "Fish or cut bait", "Five or six", "For better or for worse, ", "Four or five", "Free or die", "Friend or foe", "Give or take", "Head or tail", "Heads or tails", "Hell or high water", "Hit or miss", "Hook or by crook", "Hook or crook", "Kill or cure", "Life or death", "Like it or lump it", "Like it or not", "Little or no", "Little or none", "Love or money", "Make or break", "May or may not", "Means or foul", "More or less", "Neck or nothing", "Nine or ten", "On or about", "Once or twice", "One or another", "One or more", "One or other", "One or the other", "One or two", "One way or another", "One way or the other", "Out or keeping", "Piss or get off the pot", "Plus or minus", "Put up or shut up", "Rain or shine", "Rhyme or reason", "Sale or return", "Seven or eight", "Shape or form", "Shape up or ship out", "Shit or get off the pot", "Sink or swim", "Sinks or swim", "Six or seven", "Somehow or other", "Something or other", "Sooner or later, ", "Sunk or swim", "Take it or leave it", "Thing or two", "Three or four", "Three or more", "Trick or treat", "Trick or treater", "Trick or treating", "Truth or consequences", "Truth or dare", "Two or more", "Two or three", "Whether or no", "Win or lose"]

#Since there are so many phrases for or, and because some of them might be at the beginning of a sentence, I didn't bother including [^\w] on either side of the phrases
and_comma_inside = ["A, and B", "Adam, and Eve", ", and a half", ", and a third", ", and eighty", ", and fifty", ", and five", ", and forty", ", and ninety", ", and ninety five", ", and ninety nine", ", and seventy", ", and sixty", ", and ten", ", and thirty", ", and three quarters", ", and twenty", "B, and B", "Bonnie, and Clyde", "East, and West", "Herb, and Al", "Jekyll, and Hyde", "Netflix, and chill", "North, and South", "Sam, and Dave", "Siegfried, and Roy", "Stars, and Stripes", "Summer, and Winter", "a boon, and a bane", "a day late, and a dollar short", "about, and scatter", "above, and beyond", "acres, and a mule", "act, and deed", "again, and again", "aid, and abet", "airs, and graces", "alarms, and excursions", "alarums, and excursions", "alive, and kicking", "all, and end", "all, and some", "all, and sundry", "all day, and every", "all gas, and gaiters", "all hat, and no cattle", "alpha, and omega", "apples, and oranges", "arm, and a leg", "armed, and dangerous", "around, and around", "art, and part of", "arts, and crafts", "assholes, and elbows", "at sixes, and sevens", "back, and edge", "back, and fill", "back, and forth", "back, and sides", "backward, and forward", "backwards, and forwards", "bait, and switch", "ball, and chain", "ball, and run", "balls, and strikes", "bam, and scram", "banana, and split", "bark, and no bite", "beck, and call", "bed, and board", "bed, and breakfast", "bee, and buzz", "been, and done", "beer, and skittles", "before, and after", "bells, and buckets", "bells, and whistles", "belt, and braces", "bib, and tucker", "big, and bold", "binge, and purge", "birds, and the bees", "bitch, and moan", "bits, and bobs", "bits, and pieces", "bitter, and twisted", "black, and blue", "black, and tan", "black, and white", "blink, and you", "block, and tackle", "blood, and guts", "blood, and iron", "blood, and thunder", "blue, and white", "blues, and twos", "bob, and weave", "body, and soul", "boots, and all", "born, and bred", "born, and raised", "bottle, and glass", "bound, and determined", "bow, and scrape", "boys, and girls", "boys, and their toys", "brains, and brawn", "brawn, and no brain", "bread, and butter", "bread, and water", "break down, and cry", "breaking, and entering", "brick, and mortar", "bricks, and mortar", "bright, and breezy", "bright-eyed, and bushy-tailed", "bruised, and battered", "buckle, and tongue", "bull, and cow", "burning, and no ship", "by, and by", "by, and large", "bye, and good", "cake, and eat", "cake, and have it", "cakes, and ale", "cap, and bells", "carrot, and stick", "carrot, and the stick", "cash, and carry", "cat, and dog", "cat, and mouse", "cats, and dogs", "cause, and effect", "chalk, and cheese", "chapter, and verse", "checks, and balances", "chicken, and egg", "children, and drunken", "children, and fools", "chili, and beans", "chip, and dip", "chop, and charge", "cloak, and dagger", "close, and personal", "close down, and shut down", "coach, and horses", "coat, and no knickers", "coat, and tie", "cock, and bull", "coffee, and Danish", "cold, and starve", "come, and get it", "come, and go", "come, and gone", "come back, and see us", "coming, and going", "comings, and goings", "control, and status", "cook, and bottlewasher", "copy, and paste", "crash, and burn", "cry, and no wool", "cut, and dried", "cut, and run", "cut, and thrust", "dark, and handsome", "day, and age", "day, and night", "days, and holidays", "dead, and buried", "dead, and gone", "deaf, and dumb", "death, and taxes", "desert, and reward", "devil, and deep blue sea", "devil, and the deep blue sea", "dine, and dash", "divide, and conquer", "divide, and govern", "divide, and rule", "do's, and don'ts", "dog, and bone", "dog, and pony", "dog, and wolf", "dogs, and cats", "dollars, and cents", "done, and done", "done, and dusted", "doom, and gloom", "dos, and don'ts", "dot the I's, and cross the T's", "dot the i's, and cross the t's", "down, and die", "down, and dirty", "down, and out", "down, and outer", "draw, and quarter", "drawn, and quartered", "dribs, and drabs", "drink, and be merry", "drop, and a sudden", "drunk, and disorderly", "dry up, and blow away", "duck, and cover", "duck, and dive", "ducking, and diving", "ducks, and drakes", "dust, and ashes", "each, and every", "east, and west", "eat, and run", "ebb, and flow", "effing, and blinding", "elders, and betters", "enough, and some", "enough, and to spare", "errors, and omissions", "ever, and a day", "ever, and again", "everybody, and his", "everybody, and his brother", "everybody, and his cousin", "everybody, and their", "everyone, and their", "everything, and the", "eyes, and ears", "fair, and impartial", "fair, and square", "fair field, and no favour", "far, and away", "far, and near", "far, and wide", "fast, and furious", "fast, and loose", "faster, and faster", "fat, and happy", "fat, and sassy", "fear, and loathing", "fend, and prove", "fetch, and carry", "fever, and run", "few, and far between", "fights, and run", "fine, and dandy", "fingers, and thumbs", "fire, and brimstone", "fire, and water", "first, and foremost", "first, and last", "fit, and trim", "fits, and starts", "five, and dime", "five, and ten", "flesh, and blood", "flora, and fauna", "flotsam, and jetsam", "fool, and his money", "footloose, and fancy", "fore, and aft", "forever, and ever", "forgive, and forget", "form, and substance", "forward, and backward", "forwards, and backwards", "free, and clear", "free, and easy", "fresh, and sweet", "frog, and toad", "front, and center", "fun, and games", "fur, and feather", "fuss, and feathers", "gall, and wormwood", "give, and take", "gloom, and doom", "go, and chase", "go, and do", "gone, and done", "good, and all", "good, and proper", "good, and quickly", "good, and ready", "good news, and bad news", "goods, and chattels", "grab, and go", "great, and small", "great, and the good", "grin, and bear it", "hair, and hide", "hale, and hearty", "hammer, and sickle", "hammer, and tongs", "hand, and foot", "hand, and glove", "hands, and knees", "hands, and the cook", "hard, and fast", "haul off, and do", "hawk, and buzzard", "hawks, and doves", "head, and shoulders", "heart, and soul", "hearth, and home", "hearts, and flowers", "hearts, and minds", "heaven, and earth", "hell, and back", "hell, and gone", "hell, and half", "hell, and high", "hellfire, and damnation", "hem, and haw", "here, and now", "here, and there", "hide, and seek", "high, and dry", "high, and low", "high, and mighty", "highways, and byways", "hill, and down", "hire, and fire", "hit, and miss", "hit, and run", "hither, and tither", "hole, and corner", "home, and dry", "home, and hosted", "honest, and above", "hoops, and a holler", "hoot, and a half", "horns, and rattles", "horse, and buggy", "horse, and carriage", "horse, and rabbit", "hot, and bothered", "hot, and cold", "hot, and heavy", "house, and home", "howdy, and a half", "hue, and a cry", "hue, and cry", "huff, and puff", "hugs, and kisses", "hum, and haw", "hundred, and ten", "hurry up, and wait", "hustle, and bustle", "ifs, and buts", "in, and of itself", "in, and out", "in, and week", "information, and communication technology", "ins, and outs", "inside, and out", "intents, and purposes", "jigs, and the reels", "jot, and tittle", "juice, and cookies", "kicking, and screaming", "kicks, and for giggles", "kicks, and for laughs", "kiss, and cry", "kiss, and tell", "kit, and caboodle", "kith, and kin", "knife, and fork", "ladies, and gentlemen", "lares, and penates", "large, and in charge", "large as life, and twice as ugly", "lark, and on a lark", "laugh, and grow", "law, and order", "lean, and mean", "leaps, and bounds", "left, and right", "length, and breadth", "less, and less", "lick, and a promise", "life, and death", "life, and limb", "life, and soul", "line, and sinker", "little, and care", "live, and breathe", "live, and let", "live, and well", "lives, and breathes", "living, and breathing", "lo, and behold", "lo, and beyond", "loaves, and fishes", "lock, and key", "long, and hard", "long, and life", "long, and prosper", "long, and short", "long, and the short", "look, and feel", "lord, and master", "lost, and found", "lost, and gone", "loud, and clear", "love, and care", "love, and hate", "love, and war", "low, and sing", "make do, and mend", "man, and boy", "man, and wife", "many, and many", "me, and my", "me, and you", "meat, and drink", "meat, and no potatoes", "meet, and greet", "men, and true", "men, and women", "might, and main", "miles, and miles", "milk, and honey", "milk, and water", "million, and one", "mix, and match", "mix, and mingle", "mom, and apple", "money, and run", "moon, and back", "moon, and the milkman", "moon, and the stars", "moonlight, and roses", "mops, and brooms", "more, and more", "mouth, and trousers", "mover, and a shaker", "mover, and shaker", "movers, and shakers", "myself, and I", "name, and address", "name, and shame", "near, and dear", "near, and far", "nearest, and dearest", "neat, and tidy", "neck, and crop", "neck, and neck", "nerve, and muscle", "nice, and peaceful", "nickel, and dime", "night, and day", "nip, and tuck", "nod, and a wink", "nook, and cranny", "nooks, and crannies", "north, and south", "nothing, and care", "now, and again", "now, and anon", "now, and then", "nudge, and a wink", "null, and void", "nuts, and bolts", "oak, and iron", "odd, and curious", "odds, and ends", "odds, and sods", "off, and on", "off, and running", "oil, and water", "on, and about", "on, and off", "once, and again", "once, and for", "once, and for all", "once, and future", "one, and a", "one, and all", "one, and cheese", "one, and flesh", "one, and half", "one, and only", "one, and the same", "onward, and upward", "onwards, and upwards", "open, and above", "open, and shut", "out, and about", "out, and out", "over, and about", "over, and above", "over, and done", "over, and out", "over, and over", "pain, and suffering", "part, and parcel", "party, and play", "peace, and quiet", "peaches, and cream", "pen, and ink", "people, and true", "pick, and choose", "pick, and mix", "pinch, and a punch", "pinch, and scrape", "pink it, and shrink it", "pins, and needles", "pipe, and smoke", "piss, and moan", "piss, and vinegar", "piss, and wind", "pitch in, and help", "pitchforks, and hammer", "pith, and moment", "plain, and simple", "plug, and play", "pomp, and circumstance", "postage, and handling", "present, and correct", "pride, and joy", "prim, and proper", "pros, and cons", "prunes, and prisms", "pudding, and tame", "puff, and blow", "puff, and pant", "pure, and simple", "purely, and simply", "quick, and dirty", "quick, the dead", "r, and r", "rack, and ruin", "rain cats, and dogs", "rainbows, and unicorns", "rank, and file", "rant, and rave", "read it, and weep", "read.em, and weep", "ready, and willing", "real, and for true", "really, and truly", "rest, and relax", "right, and center", "right, and centre", "right, and left", "rinse, and repeat", "rise, and shine", "rises, and sets", "rock, and roll", "room, and board", "root, and branch", "rough, and ready", "rough, and tumble", "round, and round", "sackcloth, and ashes", "sadder, and wiser", "safe, and sound", "said, and done", "salt, and pepper", "score, and seven", "score, and ten", "scot, and lot", "scotch, and notch", "scratch, and find", "scrimp, and save", "sealed, and delivered", "search, and destroy", "shilling, and found", "shirts, and skins", "shock, and awe", "short, and curlies", "short, and sweet", "short, and the long", "shot, and powder", "show, and tell", "shreds, and patches", "shrink it, and pink it", "shut up, and take", "sick, and tired", "side, and down", "signed, and sealed", "sit back, and enjoy", "sit back, and let", "sit up, and take", "six, and two threes", "sizzle, and no steak", "skin, and bone", "slash, and burn", "sling, and arrows", "slings, and arrows", "slower, and slower", "slowly, and surely", "smoke, and mirrors", "snakes, and ladders", "so, and so", "softly, and carry", "song, and dance", "spic, and span", "spick, and span", "spit, and image", "spit, and polish", "spit, and sawdust", "stage, and off", "stand, and deliver", "stand up, and be", "stars, and stripes", "sticks, and stones", "still, and all", "stop, and smell", "straight, and narrow", "strikes, and you", "stuff, and nonsense", "such, and such", "suck it, and see", "sugar, and spice", "sum, and substance", "summer, and winter", "sunshine, and rainbows", "supply, and demand", "surf, and turf", "sweat, and tears", "sweet, and sour", "sweetness, and light", "swift, and sure", "swing, and a miss", "swings, and roundabouts", "sword, and sandal", "sword, and sorcery", "tag, and rag", "tail, and run", "talk, and no action", "talk, and no trousers", "tar, and feather", "tarred, and feathered", "tax, and spend", "tea, and sympathy", "team, and the dog", "them, and leave", "them, and us", "then, and there", "there, and back", "there, and then", "thick, and fast", "thick, and thin", "this, and that", "thoughts, and prayers", "thousand, and one", "thread, and thrum", "thrills, and spills", "through, and through", "thrust, and parry", "thus, and so", "thus, and such", "thus, and thus", "time, and a place", "time, and again", "time, and material", "time, and place", "time, and tide", "time, and time", "tired, and emotional", "tither, and yon", "to, and fro", "today, and gone", "toing, and froing", "tooth, and claw", "tooth, and nail", "top, and tail", "toss, and turn", "tossing, and turning", "touch, and go", "town, and gown", "track, and field", "tree, and leave", "trial, and error", "trials, and tribulations", "tried, and tested", "tried, and true", "tried, and trusted", "trouble, and strife", "turn, and turn", "tweedledee, and tweedledum", "tweedledum, and tweedledee", "two, and two", "um, and aah", "um, and ah", "underpromise, and overdeliver", "up, and about", "up, and around", "up, and at", "up, and away", "up, and comer", "up, and coming", "up, and did", "up, and die", "up, and doing", "up, and down", "up, and go", "up, and leave", "up, and nowhere", "up, and running", "up, and salted", "up, and up", "ups, and downs", "us, and them", "various, and sundry", "vim, and vigor", "vim, and vigour", "waifs, and strays", "wait, and see", "wake up, and smell", "walk, and chew", "walk, and talk", "warm, and fuzzy", "warp, and woof", "warts, and all", "wash, and wear", "wax, and wane", "way, and that", "ways, and means", "weal, and woe", "wear, and tear", "weighed, and found", "weird, and wonderful", "well, and good", "well, and truly", "wheel, and deal", "wheeling, and dealing", "whips, and jingles", "whistle, and flute", "whoop, and a holler", "whys, and wherefores", "wild, and woolly", "will, and testament", "willing, and able", "wind, and water", "wine, and dine", "wing, and a prayer", "wise, and dollar", "wise, and pound", "women, and children", "wool, and no shoddy", "work, and no play", "world, and his", "wormwood, and gall", "wrack, and ruin", "you and me"]
and_no_comma = ["A and B", "Adam and Eve", " and a half", " and a third", " and eighty", " and fifty", " and five", " and forty", " and ninety", " and ninety five", " and ninety nine", " and seventy", " and sixty", " and ten", " and thirty", " and three quarters", " and twenty", "B and B", "Bonnie and Clyde", "East and West", "Herb and Al", "Jekyll and Hyde", "Netflix and chill", "North and South", "Sam and Dave", "Siegfried and Roy", "Stars and Stripes", "Summer and Winter", "a boon and a bane", "a day late and a dollar short", "about and scatter", "above and beyond", "acres and a mule", "act and deed", "again and again", "aid and abet", "airs and graces", "alarms and excursions", "alarums and excursions", "alive and kicking", "all and end", "all and some", "all and sundry", "all day and every", "all gas and gaiters", "all hat and no cattle", "alpha and omega", "apples and oranges", "arm and a leg", "armed and dangerous", "around and around", "art and part of", "arts and crafts", "assholes and elbows", "at sixes and sevens", "back and edge", "back and fill", "back and forth", "back and sides", "backward and forward", "backwards and forwards", "bait and switch", "ball and chain", "ball and run", "balls and strikes", "bam and scram", "banana and split", "bark and no bite", "beck and call", "bed and board", "bed and breakfast", "bee and buzz", "been and done", "beer and skittles", "before and after", "bells and buckets", "bells and whistles", "belt and braces", "bib and tucker", "big and bold", "binge and purge", "birds and the bees", "bitch and moan", "bits and bobs", "bits and pieces", "bitter and twisted", "black and blue", "black and tan", "black and white", "blink and you", "block and tackle", "blood and guts", "blood and iron", "blood and thunder", "blue and white", "blues and twos", "bob and weave", "body and soul", "boots and all", "born and bred", "born and raised", "bottle and glass", "bound and determined", "bow and scrape", "boys and girls", "boys and their toys", "brains and brawn", "brawn and no brain", "bread and butter", "bread and water", "break down and cry", "breaking and entering", "brick and mortar", "bricks and mortar", "bright and breezy", "bright-eyed and bushy-tailed", "bruised and battered", "buckle and tongue", "bull and cow", "burning and no ship", "by and by", "by and large", "bye and good", "cake and eat", "cake and have it", "cakes and ale", "cap and bells", "carrot and stick", "carrot and the stick", "cash and carry", "cat and dog", "cat and mouse", "cats and dogs", "cause and effect", "chalk and cheese", "chapter and verse", "checks and balances", "chicken and egg", "children and drunken", "children and fools", "chili and beans", "chip and dip", "chop and charge", "cloak and dagger", "close and personal", "close down and shut down", "coach and horses", "coat and no knickers", "coat and tie", "cock and bull", "coffee and Danish", "cold and starve", "come and get it", "come and go", "come and gone", "come back and see us", "coming and going", "comings and goings", "control and status", "cook and bottlewasher", "copy and paste", "crash and burn", "cry and no wool", "cut and dried", "cut and run", "cut and thrust", "dark and handsome", "day and age", "day and night", "days and holidays", "dead and buried", "dead and gone", "deaf and dumb", "death and taxes", "desert and reward", "devil and deep blue sea", "devil and the deep blue sea", "dine and dash", "divide and conquer", "divide and govern", "divide and rule", "do's and don'ts", "dog and bone", "dog and pony", "dog and wolf", "dogs and cats", "dollars and cents", "done and done", "done and dusted", "doom and gloom", "dos and don'ts", "dot the I's and cross the T's", "dot the i's and cross the t's", "down and die", "down and dirty", "down and out", "down and outer", "draw and quarter", "drawn and quartered", "dribs and drabs", "drink and be merry", "drop and a sudden", "drunk and disorderly", "dry up and blow away", "duck and cover", "duck and dive", "ducking and diving", "ducks and drakes", "dust and ashes", "each and every", "east and west", "eat and run", "ebb and flow", "effing and blinding", "elders and betters", "enough and some", "enough and to spare", "errors and omissions", "ever and a day", "ever and again", "everybody and his", "everybody and his brother", "everybody and his cousin", "everybody and their", "everyone and their", "everything and the", "eyes and ears", "fair and impartial", "fair and square", "fair field and no favour", "far and away", "far and near", "far and wide", "fast and furious", "fast and loose", "faster and faster", "fat and happy", "fat and sassy", "fear and loathing", "fend and prove", "fetch and carry", "fever and run", "few and far between", "fights and run", "fine and dandy", "fingers and thumbs", "fire and brimstone", "fire and water", "first and foremost", "first and last", "fit and trim", "fits and starts", "five and dime", "five and ten", "flesh and blood", "flora and fauna", "flotsam and jetsam", "fool and his money", "footloose and fancy", "fore and aft", "forever and ever", "forgive and forget", "form and substance", "forward and backward", "forwards and backwards", "free and clear", "free and easy", "fresh and sweet", "frog and toad", "front and center", "fun and games", "fur and feather", "fuss and feathers", "gall and wormwood", "give and take", "gloom and doom", "go and chase", "go and do", "gone and done", "good and all", "good and proper", "good and quickly", "good and ready", "good news and bad news", "goods and chattels", "grab and go", "great and small", "great and the good", "grin and bear it", "hair and hide", "hale and hearty", "hammer and sickle", "hammer and tongs", "hand and foot", "hand and glove", "hands and knees", "hands and the cook", "hard and fast", "haul off and do", "hawk and buzzard", "hawks and doves", "head and shoulders", "heart and soul", "hearth and home", "hearts and flowers", "hearts and minds", "heaven and earth", "hell and back", "hell and gone", "hell and half", "hell and high", "hellfire and damnation", "hem and haw", "here and now", "here and there", "hide and seek", "high and dry", "high and low", "high and mighty", "highways and byways", "hill and down", "hire and fire", "hit and miss", "hit and run", "hither and tither", "hole and corner", "home and dry", "home and hosted", "honest and above", "hoops and a holler", "hoot and a half", "horns and rattles", "horse and buggy", "horse and carriage", "horse and rabbit", "hot and bothered", "hot and cold", "hot and heavy", "house and home", "howdy and a half", "hue and a cry", "hue and cry", "huff and puff", "hugs and kisses", "hum and haw", "hundred and ten", "hurry up and wait", "hustle and bustle", "ifs and buts", "in and of itself", "in and out", "in and week", "information and communication technology", "ins and outs", "inside and out", "intents and purposes", "jigs and the reels", "jot and tittle", "juice and cookies", "kicking and screaming", "kicks and for giggles", "kicks and for laughs", "kiss and cry", "kiss and tell", "kit and caboodle", "kith and kin", "knife and fork", "ladies and gentlemen", "lares and penates", "large and in charge", "large as life and twice as ugly", "lark and on a lark", "laugh and grow", "law and order", "lean and mean", "leaps and bounds", "left and right", "length and breadth", "less and less", "lick and a promise", "life and death", "life and limb", "life and soul", "line and sinker", "little and care", "live and breathe", "live and let", "live and well", "lives and breathes", "living and breathing", "lo and behold", "lo and beyond", "loaves and fishes", "lock and key", "long and hard", "long and life", "long and prosper", "long and short", "long and the short", "look and feel", "lord and master", "lost and found", "lost and gone", "loud and clear", "love and care", "love and hate", "love and war", "low and sing", "make do and mend", "man and boy", "man and wife", "many and many", "me and my", "me and you", "meat and drink", "meat and no potatoes", "meet and greet", "men and true", "men and women", "might and main", "miles and miles", "milk and honey", "milk and water", "million and one", "mix and match", "mix and mingle", "mom and apple", "money and run", "moon and back", "moon and the milkman", "moon and the stars", "moonlight and roses", "mops and brooms", "more and more", "mouth and trousers", "mover and a shaker", "mover and shaker", "movers and shakers", "myself and I", "name and address", "name and shame", "near and dear", "near and far", "nearest and dearest", "neat and tidy", "neck and crop", "neck and neck", "nerve and muscle", "nice and peaceful", "nickel and dime", "night and day", "nip and tuck", "nod and a wink", "nook and cranny", "nooks and crannies", "north and south", "nothing and care", "now and again", "now and anon", "now and then", "nudge and a wink", "null and void", "nuts and bolts", "oak and iron", "odd and curious", "odds and ends", "odds and sods", "off and on", "off and running", "oil and water", "on and about", "on and off", "once and again", "once and for", "once and for all", "once and future", "one and a", "one and all", "one and cheese", "one and flesh", "one and half", "one and only", "one and the same", "onward and upward", "onwards and upwards", "open and above", "open and shut", "out and about", "out and out", "over and about", "over and above", "over and done", "over and out", "over and over", "pain and suffering", "part and parcel", "party and play", "peace and quiet", "peaches and cream", "pen and ink", "people and true", "pick and choose", "pick and mix", "pinch and a punch", "pinch and scrape", "pink it and shrink it", "pins and needles", "pipe and smoke", "piss and moan", "piss and vinegar", "piss and wind", "pitch in and help", "pitchforks and hammer", "pith and moment", "plain and simple", "plug and play", "pomp and circumstance", "postage and handling", "present and correct", "pride and joy", "prim and proper", "pros and cons", "prunes and prisms", "pudding and tame", "puff and blow", "puff and pant", "pure and simple", "purely and simply", "quick and dirty", "quick and the dead", "r and r", "rack and ruin", "rain cats and dogs", "rainbows and unicorns", "rank and file", "rant and rave", "read it and weep", "read.em and weep", "ready and willing", "real and for true", "really and truly", "rest and relax", "right and center", "right and centre", "right and left", "rinse and repeat", "rise and shine", "rises and sets", "rock and roll", "room and board", "root and branch", "rough and ready", "rough and tumble", "round and round", "sackcloth and ashes", "sadder and wiser", "safe and sound", "said and done", "salt and pepper", "score and seven", "score and ten", "scot and lot", "scotch and notch", "scratch and find", "scrimp and save", "sealed and delivered", "search and destroy", "shilling and found", "shirts and skins", "shock and awe", "short and curlies", "short and sweet", "short and the long", "shot and powder", "show and tell", "shreds and patches", "shrink it and pink it", "shut up and take", "sick and tired", "side and down", "signed and sealed", "sit back and enjoy", "sit back and let", "sit up and take", "six and two threes", "sizzle and no steak", "skin and bone", "slash and burn", "sling and arrows", "slings and arrows", "slower and slower", "slowly and surely", "smoke and mirrors", "snakes and ladders", "so and so", "softly and carry", "song and dance", "spic and span", "spick and span", "spit and image", "spit and polish", "spit and sawdust", "stage and off", "stand and deliver", "stand up and be", "stars and stripes", "sticks and stones", "still and all", "stop and smell", "straight and narrow", "strikes and you", "stuff and nonsense", "such and such", "suck it and see", "sugar and spice", "sum and substance", "summer and winter", "sunshine and rainbows", "supply and demand", "surf and turf", "sweat and tears", "sweet and sour", "sweetness and light", "swift and sure", "swing and a miss", "swings and roundabouts", "sword and sandal", "sword and sorcery", "tag and rag", "tail and run", "talk and no action", "talk and no trousers", "tar and feather", "tarred and feathered", "tax and spend", "tea and sympathy", "team and the dog", "them and leave", "them and us", "then and there", "there and back", "there and then", "thick and fast", "thick and thin", "this and that", "thoughts and prayers", "thousand and one", "thread and thrum", "thrills and spills", "through and through", "thrust and parry", "thus and so", "thus and such", "thus and thus", "time and a place", "time and again", "time and material", "time and place", "time and tide", "time and time", "tired and emotional", "tither and yon", "to and fro", "today and gone", "toing and froing", "tooth and claw", "tooth and nail", "top and tail", "toss and turn", "tossing and turning", "touch and go", "town and gown", "track and field", "tree and leave", "trial and error", "trials and tribulations", "tried and tested", "tried and true", "tried and trusted", "trouble and strife", "turn and turn", "tweedledee and tweedledum", "tweedledum and tweedledee", "two and two", "um and aah", "um and ah", "underpromise and overdeliver", "up and about", "up and around", "up and at", "up and away", "up and comer", "up and coming", "up and did", "up and die", "up and doing", "up and down", "up and go", "up and leave", "up and nowhere", "up and running", "up and salted", "up and up", "ups and downs", "us and them", "various and sundry", "vim and vigor", "vim and vigour", "waifs and strays", "wait and see", "wake up and smell", "walk and chew", "walk and talk", "warm and fuzzy", "warp and woof", "warts and all", "wash and wear", "wax and wane", "way and that", "ways and means", "weal and woe", "wear and tear", "weighed and found", "weird and wonderful", "well and good", "well and truly", "wheel and deal", "wheeling and dealing", "whips and jingles", "whistle and flute", "whoop and a holler", "whys and wherefores", "wild and woolly", "will and testament", "willing and able", "wind and water", "wine and dine", "wing and a prayer", "wise and dollar", "wise and pound", "women and children", "wool and no shoddy", "work and no play", "world and his", "wormwood and gall", "wrack and ruin", "you and me"]

which_comma_inside = ["[^\w]against, which", "[^\w]and, which", "[^\w]any, which", "[^\w]at, which", "[^\w]by, which", "[^\w]ever, which", "[^\w]every, which", "[^\w]for, which", "[^\w]from, which", "[^\w]in, which", "[^\w]into, which", "[^\w]knew, which", "[^\w]know, which", "[^\w]know, which is which", "[^\w]manner, which", "[^\w]matter, which", "[^\w]near, which", "[^\w]of, which", "[^\w]on, which", "[^\w]one, which", "[^\w]see, which", "[^\w]something, which", "[^\w]tell, which is which", "[^\w]that, which", "[^\w]through, which", "[^\w]to, which", "[^\w]towards, which", "[^\w]upon, which", "[^\w]way, which", "[^\w]which, is which", "[^\w]with, which", "[^\w]above, which", "[^\w]after, which", "[^\w]before, which", "[^\w]behind, which", "[^\w]below, which", "[^\w]besides, which", "[^\w]during, which", "[^\w]in front of, which", "[^\w]over, which", "[^\w]those, which", "[^\w]under, which"]
which_no_comma = [", against which", ", and which", " any which", ", at which", ", by which", " ever which", " every which", ", for which", ", from which", ", in which", ", into which", " knew which", " know which", " know which is which", " manner which", " matter which", ", near which", ", of which", ", on which", " one which", " see which", " something which", " tell which is which", ", that which", ", through which", ", to which", ", towards which", ", upon which", " way which", " which is which", ", with which", ", above which", ", after which", ", before which", ", behind which", ", below which", ", besides which", ", during which", ", in front of which", ", over which", ", those which", ", under which"]

that_comma_inside = ["[^\w]'bout, that", "[^\w]about, that", "[^\w]above, that", "[^\w]after, that", "[^\w]all, that", "[^\w]along, that", "[^\w]and, that", "[^\w]around, that", "[^\w]as, that", "[^\w]at, that", "[^\w]be, that", "[^\w]because, that", "[^\w]before, that", "[^\w]behind, that", "[^\w]besides, that", "[^\w]beyond, that", "[^\w]but, that", "[^\w]by, that", "[^\w]did, that", "[^\w]do, that", "[^\w]does, that", "[^\w]done, that", "[^\w]during, that", "[^\w]even, that", "[^\w]except, that", "[^\w]fancy, that", "[^\w]for, that", "[^\w]from, that", "[^\w]fuck, that", "[^\w]he, that", "[^\w]how, that", "[^\w]if, that", "[^\w]in, that", "[^\w]is, that", "[^\w]isn[.]t, that", "[^\w]just, that", "[^\w]knew, that", "[^\w]know, that", "[^\w]leave, that", "[^\w]left, that", "[^\w]let, that", "[^\w]may, that", "[^\w]me, that", "[^\w]might, that", "[^\w]much, that", "[^\w] near, that", "[^\w]not, that", "[^\w]now, that", "[^\w]of, that", "[^\w]on, that", "[^\w]one, that", "[^\w]only, that", "[^\w]or, that", "[^\w]over, that", "[^\w]said, that", "[^\w]save, that", "[^\w]say, that", "[^\w]says, that", "[^\w]she, that", "[^\w], that", "[^\w]so, that", "[^\w]than, that", "[^\w]that settles, that", "[^\w]that's, that", "[^\w]then, that", "[^\w]they, that", "[^\w]those, that", "[^\w]to, that", "[^\w]under, that", "[^\w], that", "[^\w]upon, that", "[^\w]was, that", "[^\w]what, that", "[^\w]when, that", "[^\w]where, that", "[^\w]while, that", "[^\w]why, that", "[^\w]with, that", "[^\w]write, that", "[^\w]writes, that", "[^\w]wrote, that", "[^\w]believe, that", "[^\w]believing, that", "[^\w]came, that", "[^\w]case, that", "[^\w]come, that", "[^\w]didn[.]t, that", "[^\w]get, that", "[^\w]given, that", "[^\w]go, that", "[^\w]got, that", "[^\w]head, that", "[^\w]headed, that", "[^\w]heading, that", "[^\w]hear, that", "[^\w]heard, that", "[^\w]hearing, that", "[^\w]here[.]s, that", "[^\w]imagine, that", "[^\w]imagined, that", "[^\w]it[.]s, that", "[^\w]knowing, that", "[^\w]lie, that", "[^\w]lied, that", "[^\w]lies, that", "[^\w]like, that", "[^\w]make, that", "[^\w]mean, that", "[^\w]meant, that", "[^\w]mind, that", "[^\w]provided, that", "[^\w]roger, that", "[^\w]run, that", "[^\w]saw, that", "[^\w]scratch, that", "[^\w]see, that", "[^\w]seeing, that", "[^\w]take, that", "[^\w]tell, that", "[^\w]there[.]s, that", "[^\w]think, that", "[^\w]thought, that", "[^\w]told, that", "[^\w]unlike, that", "[^\w]wasn[.]t, that", "[^\w]went, that", "[^\w]what[.]s, that", "[^\w]will, that", "[^\w]would, that"]
that_no_comma = [" 'bout that", " about that", " above that", " after that", " all that", " along that", ", and that", " around that", " as that", " at that", " be that", " because that", " before that", " behind that", " besides that", " beyond that", " but that", " by that", " did that", " do that", " does that", " done that", " during that", " even that", " except that", " fancy that", " for that", " from that", " fuck that", " he that", " how that", " if that", " in that", " is that", " isn[.]t that", " just that", " knew that", " know that", " leave that", " left that", " let that", " may that", " me that", " might that", " much that", " near that", " not that", " now that", " of that", " on that", " one that", " only that", " or that", " over that", " said that", " save that", " say that", " says that", " she that", ", since that", " so that", " than that", " that settles that", " that's that", ", then that", " they that", " those that", " to that", " under that", ", until that", " upon that", " was that", " what that", " when that", " where that", " while that", " why that", " with that", " write that", " writes that", " wrote that", " believe that", " believing that", " came that", " case that", " come that", " didn[.]t that", " get that", " given that", " go that", " got that", " head that", " headed that", " heading that", " hear that", " heard that", " hearing that", " here[.]s that", " imagine that", " imagined that", " it[.]s that", " knowing that", " lie that", " lied that", " lies that", " like that", " make that", " mean that", " meant that", " mind that", " provided that", " roger that", " run that", " saw that", " scratch that", " see that", " seeing that", " take that", " tell that", " there[.]s that", " think that", " thought that", " told that", " unlike that", " wasn[.]t that", " went that", " what[.]s that", " will that", " would that"]

with open('/opt/lampp/htdocs/SpeakTheBeats/SpeakTheScript/EnglishDictionary.txt', 'r') as dictionary:
    dictionary_words = set(word.strip().lower() for word in dictionary)

text_chunks = [[]]
index = 0

whole_text = whole_text.replace('\ufeff', '').replace('_', '"').replace('<i>', '"').replace('</i>', '"')
initial_phoneme_tag_count = whole_text.count("<phoneme alphabet=")

#Replaces onomatopoeias with words that are more easily amenable to TTS (ex: '[^\w]Sh[h]+[^\w]' => 'Shush').
#I used [^\w] on either side of the patterns to exclude words such as 'Shirt'
#Including match[0] and match[-1] avoids losing the the characters on either side of the onomatopoeias following substitution.
#match_counts allows to convert every identical word matching a re pattern, and there can be several
#hits for a single re pattern (ex: Sh!, shh! for '[^\w]Sh[h]+[^\w]')
for pattern in onomatopoeias:
    pattern_matches = re.findall(pattern, whole_text)
    if pattern_matches != []:
        pattern_list_index = onomatopoeias.index(pattern)
        for match in pattern_matches:
            match_count = whole_text.count(match)
            for _ in range(match_count):
                whole_text = whole_text.replace(match, match[0] + modified_onomatopoeias[pattern_list_index] + match[-1], match_count)
for pattern in onomatopoeias:
    pattern_matches = re.findall(pattern.lower(), whole_text)
    if pattern_matches != []:
        pattern_list_index = onomatopoeias.index(pattern)
        for match in pattern_matches:
            match_count = whole_text.count(match)
            for _ in range(match_count):
                whole_text = whole_text.replace(match, match[0] + modified_onomatopoeias[pattern_list_index].lower() + match[-1], match_count)

for hyphen in hyphens:
    pattern = re.compile(hyphen)
    whole_text = re.sub(pattern, ', ', whole_text)

terminating_punctuation = "[!?.]"
sentences = [sentence.strip() for sentence in re.split(terminating_punctuation, whole_text)]
potentially_mispronounced_words = set()
set_sentences_many_commas = set()
commas_semicolons_per_word_for_every_sentence = []
sentences_word_counts = []

sentence_start_index = 0
for i in range(len(sentences)):
    #Making a list of all words in sentence (not space characters).
    sentence_words = re.split('\s|"|\'|:|;|,|\n|???|???', sentences[i])
    sentence_words = [w for w in sentence_words if w != '']
    sentences_word_counts.append(len(sentence_words))
    comma_semicolon_count = sentences[i].count(',') + sentences[i].count(';')

    if len(sentence_words) > 0:
        commas_semicolons_per_word_for_every_sentence.append(comma_semicolon_count/sentences_word_counts[i])

commas_semicolons_whole_text_before_modifications = whole_text.count(',') + whole_text.count(';')

if sum(commas_semicolons_per_word_for_every_sentence) and len(commas_semicolons_per_word_for_every_sentence) and len(sentences) > 0:
    average_commas_semicolons_per_word_for_whole_text = sum(commas_semicolons_per_word_for_every_sentence)/len(commas_semicolons_per_word_for_every_sentence)
    standard_deviation = stdev(commas_semicolons_per_word_for_every_sentence)
    comma_semicolons_threshold = average_commas_semicolons_per_word_for_whole_text + standard_deviation
else:
    comma_semicolons_threshold = 0.2

#Here I define a cap for the threshold (average comma+semicolon/word count + standard deviation), because it wouldn't be desirable to add so many commas to a text already having a lot of commas.
if comma_semicolons_threshold > 0.2:
    comma_semicolons_threshold = 0.2

terminating_punctuation = "[!?.]"
sentences = [sentence.strip() for sentence in re.split(terminating_punctuation, whole_text)]
for i in range(len(sentences)):

    #Making a list of all words in sentence this is the second split, where the separators are included in the list of results (through the inclusion of
    #the regex expressions in parentheses). This is an important distinction, because the amended sentences[i] will be reconstituted with a join, after
    #substitution of a word containing digits and letters for a version of the word having a spacer (ex: L500 => L 500)
    sentence_words_second_split = re.split('(\s|"|\'|:|;|,|\n|???|???|???|???|-)', sentences[i])
    sentence_words_second_split = [w for w in sentence_words_second_split if w != '']
    for word in sentence_words_second_split:

        #In the event that a number is directly preceded or followed by a non-digit character other than a comma or a period, it wouldn't be
        #read properly by TTS. The code below allows to add a space between these characters and the digits.
        if (re.search('[\d]', word) != None and re.search('[^\d^.^,]', word) != None):
            #Need to preserve 1st, 2nd, 3rd, 4th and so on for it to read well, all other units can be read at a space interval from the digit.
            #Finds all digits in word separated by letters or beginning or end of word. If there is only one digit, the code will split the
            #words from the digit, so that it may be more easily readable by TTS.
            if 'st' not in word and 'nd' not in word and 'rd' not in word and 'th' not in word:
                word_digits = re.findall('\d+', word)
                digits_index_start = word.index(word_digits[0])
                digits_length = len(word_digits[0])
                if len(word_digits) > 1:
                    pass
                else:
                    if ((digits_index_start > 0) and (digits_index_start + digits_length < len(word))):
                        new_word_with_space = word[:digits_index_start] + ' ' + word[digits_index_start:(digits_index_start+digits_length)] + ' ' + word[(digits_index_start+digits_length):]
                    else:
                        if digits_index_start == 0:
                            new_word_with_space = word[digits_index_start:(digits_index_start+digits_length)] + ' ' + word[(digits_index_start+digits_length):]
                        elif digits_index_start > 0:
                            new_word_with_space = word[:digits_index_start] + ' ' + word[digits_index_start:]
                    sentence_words_second_split[sentence_words_second_split.index(word)] = new_word_with_space

    old_sentence = sentences[i]
    sentences[i] = ''.join(sentence_words_second_split)
    whole_text = whole_text.replace(old_sentence, sentences[i])

    for word in sentence_words_second_split:
        #Building a set of potentially mispronounced capitalized words and words having 3 or more of the same letter in succession, or words not exclusively comprised of letters or numbers.
        if (word[0].isupper() and word.isalpha() and word.lower() not in dictionary_words and ' ' + word not in modified_onomatopoeias):
            potentially_mispronounced_words.add(word)
        for char_index in range(len(word)-2):
            if ((word.isalpha() and (word[char_index] == word[char_index+1] and word[char_index+1] == word[char_index+2])) or (word.isnumeric() == False and word.isalpha() == False and word[-2:] not in ['st', 'nd', 'rd', 'th'] and word != "********************")):
                potentially_mispronounced_words.add(word)

    comma_semicolon_count = sentences[i].count(',') + sentences[i].count(';')
    #Only perform the substitutions below in the sentences that have a comma/word count ratio below comma_semicolons_threshold, which can be up to 0.2.
    if (sentences_word_counts[i] > 0 and comma_semicolon_count/sentences_word_counts[i] < comma_semicolons_threshold):

        for phrase_index in range(len(linking_words_middle_of_sentence_no_comma)):
            pattern = re.compile(linking_words_middle_of_sentence_no_comma[phrase_index])
            if pattern.search(sentences[i]) != None:
                old_sentence = sentences[i]
                sentences[i] = re.sub(pattern, linking_words_middle_of_sentence_with_comma[phrase_index], sentences[i])
                whole_text = whole_text.replace(old_sentence, sentences[i])
        if (sentences_word_counts[i] > 10 and (comma_semicolon_count/sentences_word_counts[i] > comma_semicolons_threshold)):
            set_sentences_many_commas.add(i)
#Since these substitutions are for phrases containing several words, they can be done throughout the "whole_text",
#at the end of a 'for i in range(len(sentences))' loop.
for phrase_index in range(len(but_middle_of_sentence_comma_inside)):
    pattern = re.compile(but_middle_of_sentence_comma_inside[phrase_index])
    whole_text = re.sub(pattern, but_middle_of_sentence_no_comma[phrase_index], whole_text)

terminating_punctuation = "[!?.]"
sentences = [sentence.strip() for sentence in re.split(terminating_punctuation, whole_text)]
for i in range(len(sentences)):
    comma_semicolon_count = sentences[i].count(',') + sentences[i].count(';')
    #Only perform the substitutions below in the sentences that have a comma/word count ratio below comma_semicolons_threshold, which can be up to 0.2.
    if (sentences_word_counts[i] > 0 and comma_semicolon_count/sentences_word_counts[i] < comma_semicolons_threshold):
        #Making a list of all words in sentence this is the second split, where the separators are included in the list of results (through the inclusion of
        #the regex expressions in parentheses). This is an important distinction, because the amended sentences[i] will be reconstituted with a join, after
        #substitution of a word containing digits and letters for a version of the word having a spacer (ex: L500 => L 500)
        sentence_words_second_split = re.split('(\s|"|\'|:|;|,|\n|???|???|???|???|-)', sentences[i])
        sentence_words_second_split = [w for w in sentence_words_second_split if w != '']
        #When looking up if the sentence_first_word is in linking_words_start_of_sentence_no_comma, a space is added after sentence_first_word, because
        #the linking words in the list have a space after them. Due to the presence of Byte Order Marks ('\ufeff'), a string replace method is added to remove BOMs.
        #The index of the first colon or comma in the sentence will be compared to those of instances of linking_words_start_of_sentence_no_comma' at the start of the sentence.
        #Commas will be added after the linking_word if there is more than 20 characters between the first comma or semicolon and the index after the linking_word.
        sentence_first_word = sentence_words_second_split[0]
        if sentence_first_word in linking_words_start_of_sentence_no_comma:
            index_first_comma_semicolon = re.search(',|;', sentences[i]).start()
            phrase_index = linking_words_start_of_sentence_no_comma.index(sentence_first_word + ' ')
            linking_word_threshold = len(sentence_first_word) + 20
            if linking_word_threshold < index_first_comma_semicolon:
                old_sentence = sentences[i]
                sentences[i] = re.sub(sentence_first_word, linking_words_start_of_sentence_with_comma[phrase_index], sentences[i])
                whole_text = whole_text.replace(old_sentence, sentences[i])

        #The indices of the colons and commas will be compared to those of instances of 'yet'. Should instances of 'yet'
        #be within 20 characters (about 3.5 words+spaces) of a comma or a semicolon, no substitution will take place to introduce further commas.
        commas_semicolons_matches = re.finditer(',|;', sentences[i])
        commas_semicolons_indices_list = [m.start() for m in commas_semicolons_matches]
        #This can get confusing, as I refer to element indexes of lists of indexes. Read the variable titles carefully. Also, I include [\s]? (1 whitespace character,
        #including carriage returns, on either side of the 'yet' keyword) to include matches for 'yet' which might occur at the very beginning (without a space to the left)
        #or the very end of a line (without a space to the right).
        yet_matches = re.finditer('[\s]yet[\s]', sentences[i])
        yet_indices_list = [m.start() for m in yet_matches]
        for yet_index in yet_indices_list:
            index_difference_list = []
            for punct_index in commas_semicolons_indices_list:
                index_difference_list.append(abs(yet_index-punct_index))
            if (all(difference >= 20 for difference in index_difference_list) and (len(sentences[i]) - yet_index > 20)):
                #print('\n\nThe "yet" at index ' + str(yet_index) + ' was over about 3.5 words+spaces of either a comma or a semicolon in sentence and will get a comma.\n\n')
                if yet_indices_list.index(yet_index) < len(yet_indices_list)-1:
                    next_yet_index = yet_indices_list[yet_indices_list.index(yet_index)+1]
                    new_sentence = re.sub('[\s]yet', ', yet', sentences[i][yet_index: next_yet_index])
                    old_sentence = sentences[i]
                    sentences[i] = sentences[i][:yet_index] + new_sentence + sentences[i][next_yet_index:]
                    whole_text = whole_text.replace(old_sentence, sentences[i])
                else:
                    new_sentence = re.sub('[\s]yet', ', yet', sentences[i][yet_index:])
                    old_sentence = sentences[i]
                    sentences[i] = sentences[i][:yet_index] + new_sentence
                    whole_text = whole_text.replace(old_sentence, sentences[i])
        if (sentences_word_counts[i] > 10 and (comma_semicolon_count/sentences_word_counts[i] > comma_semicolons_threshold)):
            set_sentences_many_commas.add(i)
#Since these substitutions are for phrases containing several words, they can be done throughout the "whole_text",
#at the end of a 'for i in range(len(sentences))' loop.
for phrase_index in range(len(yet_comma_inside_capitalized)):
    pattern = re.compile(yet_comma_inside_capitalized[phrase_index])
    whole_text = re.sub(pattern, yet_no_comma_capitalized[phrase_index], whole_text)
for phrase_index in range(len(yet_comma_inside_lowercase)):
    pattern = re.compile(yet_comma_inside_lowercase[phrase_index])
    whole_text = re.sub(pattern, yet_no_comma_lowercase[phrase_index], whole_text)

terminating_punctuation = "[!?.]"
sentences = [sentence.strip() for sentence in re.split(terminating_punctuation, whole_text)]
for i in range(len(sentences)):
    comma_semicolon_count = sentences[i].count(',') + sentences[i].count(';')
    #Only perform the substitutions below in the sentences that have a comma/word count ratio below comma_semicolons_threshold, which can be up to 0.2.
    if (sentences_word_counts[i] > 0 and comma_semicolon_count/sentences_word_counts[i] < comma_semicolons_threshold):

        #The indices of the colons and commas will be compared to those of instances of 'or'. Should instances of 'or'
        #be within 20 characters (about 3.5 words+spaces) of a comma or a semicolon, no substitution will take place to introduce further commas.
        commas_semicolons_matches = re.finditer(',|;', sentences[i])
        commas_semicolons_indices_list = [m.start() for m in commas_semicolons_matches]
        #This can get confusing, as I refer to element indexes of lists of indexes. Read the variable titles carefully.
        or_matches = re.finditer('[\s]or[\s]', sentences[i])
        or_indices_list = [m.start() for m in or_matches]
        for or_index in or_indices_list:
            index_difference_list = []
            for punct_index in commas_semicolons_indices_list:
                index_difference_list.append(abs(or_index-punct_index))
            if (all(difference >= 20 for difference in index_difference_list) and (len(sentences[i]) - or_index > 20)):
                #print('\n\nThe "or" at index ' + str(or_index) + ' was over about 3.5 words+spaces of either a comma or a semicolon in sentence and will get a comma.\n\n')
                if or_indices_list.index(or_index) < len(or_indices_list)-1:
                    next_or_index = or_indices_list[or_indices_list.index(or_index)+1]
                    new_sentence = re.sub('[\s]or', ', or', sentences[i][or_index: next_or_index])
                    old_sentence = sentences[i]
                    sentences[i] = sentences[i][:or_index] + new_sentence + sentences[i][next_or_index:]
                    whole_text = whole_text.replace(old_sentence, sentences[i])
                else:
                    new_sentence = re.sub('[\s]or', ', or', sentences[i][or_index:])
                    old_sentence = sentences[i]
                    sentences[i] = sentences[i][:or_index] + new_sentence
                    whole_text = whole_text.replace(old_sentence, sentences[i])
        if (sentences_word_counts[i] > 10 and (comma_semicolon_count/sentences_word_counts[i] > comma_semicolons_threshold)):
            set_sentences_many_commas.add(i)
#Since these substitutions are for phrases containing several words, they can be done throughout the "whole_text",
#at the end of a 'for i in range(len(sentences))' loop.
for phrase_index in range(len(or_comma_inside)):
    pattern = re.compile(or_comma_inside[phrase_index])
    whole_text = re.sub(pattern, or_no_comma[phrase_index], whole_text)
for phrase_index in range(len(or_comma_inside)):
    pattern = re.compile(or_comma_inside[phrase_index].lower())
    whole_text = re.sub(pattern, or_no_comma[phrase_index].lower(), whole_text)

terminating_punctuation = "[!?.]"
sentences = [sentence.strip() for sentence in re.split(terminating_punctuation, whole_text)]
for i in range(len(sentences)):
    comma_semicolon_count = sentences[i].count(',') + sentences[i].count(';')
    #Only perform the substitutions below in the sentences that have a comma/word count ratio below comma_semicolons_threshold, which can be up to 0.2.
    if (sentences_word_counts[i] > 0 and comma_semicolon_count/sentences_word_counts[i] < comma_semicolons_threshold):

        #The indices of the colons and commas will be compared to those of instances of 'and'. Should instances of 'and'
        #be within 20 characters (about 3.5 words+spaces) of a comma or a semicolon, no substitution will take place to introduce further commas.
        commas_semicolons_matches = re.finditer(',|;', sentences[i])
        commas_semicolons_indices_list = [m.start() for m in commas_semicolons_matches]
        #This can get confusing, as I refer to element indexes of lists of indexes. Read the variable titles carefully.
        and_matches = re.finditer('[\s]and[\s]', sentences[i])
        and_indices_list = [m.start() for m in and_matches]
        for and_index in and_indices_list:
            index_difference_list = []
            for punct_index in commas_semicolons_indices_list:
                index_difference_list.append(abs(and_index-punct_index))
            if (all(difference >= 20 for difference in index_difference_list) and (len(sentences[i]) - and_index > 20) and (and_index > 20)):
                #print('\n\nThe "and" at index ' + str(and_index) + ' was over 20 characters (about 3.5 words+spaces) of either a comma or a semicolon in sentence and will get a comma.\n\n')
                if and_indices_list.index(and_index) < len(and_indices_list)-1:
                    next_and_index = and_indices_list[and_indices_list.index(and_index)+1]
                    new_sentence = re.sub('[\s]and', ', and', sentences[i][and_index: next_and_index])
                    old_sentence = sentences[i]
                    sentences[i] = sentences[i][:and_index] + new_sentence + sentences[i][next_and_index:]
                    whole_text = whole_text.replace(old_sentence, sentences[i])
                else:
                    new_sentence = re.sub('[\s]and', ', and', sentences[i][and_index:])
                    old_sentence = sentences[i]
                    sentences[i] = sentences[i][:and_index] + new_sentence
                    whole_text = whole_text.replace(old_sentence, sentences[i])
        if (sentences_word_counts[i] > 10 and (comma_semicolon_count/sentences_word_counts[i] > comma_semicolons_threshold)):
            set_sentences_many_commas.add(i)
#Since these substitutions are for phrases containing several words, they can be done throughout the "whole_text",
#at the end of a 'for i in range(len(sentences))' loop.
for phrase_index in range(len(and_comma_inside)):
    pattern = re.compile(and_comma_inside[phrase_index])
    whole_text = re.sub(pattern, and_no_comma[phrase_index], whole_text)

terminating_punctuation = "[!?.]"
sentences = [sentence.strip() for sentence in re.split(terminating_punctuation, whole_text)]
for i in range(len(sentences)):
    comma_semicolon_count = sentences[i].count(',') + sentences[i].count(';')
    #Only perform the substitutions below in the sentences that have a comma/word count ratio below comma_semicolons_threshold, which can be up to 0.2.
    if (sentences_word_counts[i] > 0 and comma_semicolon_count/sentences_word_counts[i] < comma_semicolons_threshold):

        #The indices of the colons and commas will be compared to those of instances of 'which'. Should instances of 'which'
        #be within 20 characters (about 3.5 words+spaces) of a comma or a semicolon, no substitution will take place to introduce further commas.
        commas_semicolons_matches = re.finditer(',|;', sentences[i])
        commas_semicolons_indices_list = [m.start() for m in commas_semicolons_matches]
        #This can get confusing, as I refer to element indexes of lists of indexes. Read the variable titles carefully.
        which_matches = re.finditer('[\s]which[\s]', sentences[i])
        which_indices_list = [m.start() for m in which_matches]
        for which_index in which_indices_list:
            index_difference_list = []
            for punct_index in commas_semicolons_indices_list:
                index_difference_list.append(abs(which_index-punct_index))
            if (all(difference >= 20 for difference in index_difference_list) and (len(sentences[i]) - which_index > 20) and (which_index > 20)):
                #print('\n\nThe "which" at index ' + str(which_index) + ' was over about 3.5 words+spaces of either a comma or a semicolon in sentence and will get a comma.\n\n')
                if which_indices_list.index(which_index) < len(which_indices_list)-1:
                    next_which_index = which_indices_list[which_indices_list.index(which_index)+1]
                    new_sentence = re.sub('[\s]which', ', which', sentences[i][which_index: next_which_index])
                    old_sentence = sentences[i]
                    sentences[i] = sentences[i][:which_index] + new_sentence + sentences[i][next_which_index:]
                    whole_text = whole_text.replace(old_sentence, sentences[i])
                else:
                    new_sentence = re.sub('[\s]which', ', which', sentences[i][which_index:])
                    old_sentence = sentences[i]
                    sentences[i] = sentences[i][:which_index] + new_sentence
                    whole_text = whole_text.replace(old_sentence, sentences[i])

        if (sentences_word_counts[i] > 10 and (comma_semicolon_count/sentences_word_counts[i] > comma_semicolons_threshold)):
            set_sentences_many_commas.add(i)
#Since these substitutions are for phrases containing several words, they can be done throughout the "whole_text",
#at the end of a 'for i in range(len(sentences))' loop.
for phrase_index in range(len(which_comma_inside)):
    pattern = re.compile(which_comma_inside[phrase_index])
    whole_text = re.sub(pattern, which_no_comma[phrase_index], whole_text)

terminating_punctuation = "[!?.]"
sentences = [sentence.strip() for sentence in re.split(terminating_punctuation, whole_text)]
for i in range(len(sentences)):
    comma_semicolon_count = sentences[i].count(',') + sentences[i].count(';')
    #Only perform the substitutions below in the sentences that have a comma/word count ratio below comma_semicolons_threshold, which can be up to 0.2.
    if (sentences_word_counts[i] > 0 and comma_semicolon_count/sentences_word_counts[i] < comma_semicolons_threshold):

        #The indices of the colons and commas will be compared to those of instances of 'that'. Should instances of 'that'
        #be within 20 characters (about 3.5 words+spaces) of a comma or a semicolon, no substitution will take place to introduce further commas.
        commas_semicolons_matches = re.finditer(',|;', sentences[i])
        commas_semicolons_indices_list = [m.start() for m in commas_semicolons_matches]
        #This can get confusing, as I refer to element indexes of lists of indexes. Read the variable titles carefully.
        that_matches = re.finditer('[\s]that[\s]', sentences[i])

        that_indices_list = [m.start() for m in that_matches]
        for that_index in that_indices_list:
            index_difference_list = []
            for punct_index in commas_semicolons_indices_list:
                index_difference_list.append(abs(that_index-punct_index))
            if (all(difference >= 20 for difference in index_difference_list) and (len(sentences[i]) - that_index > 20) and (that_index > 20)):
                #print('\n\nThe "that" at index ' + str(that_index) + ' was over about 3.5 words+spaces of either a comma or a semicolon in sentence and will get a comma.\n\n')
                if that_indices_list.index(that_index) < len(that_indices_list)-1:
                    next_that_index = that_indices_list[that_indices_list.index(that_index)+1]
                    new_sentence = re.sub('[\s]that', ', that', sentences[i][that_index: next_that_index])
                    old_sentence = sentences[i]
                    sentences[i] = sentences[i][:that_index] + new_sentence + sentences[i][next_that_index:]
                    whole_text = whole_text.replace(old_sentence, sentences[i])
                else:
                    new_sentence = re.sub('[\s]that', ', that', sentences[i][that_index:])
                    old_sentence = sentences[i]
                    sentences[i] = sentences[i][:that_index] + new_sentence
                    whole_text = whole_text.replace(old_sentence, sentences[i])
        if sum(commas_semicolons_per_word_for_every_sentence) and len(commas_semicolons_per_word_for_every_sentence) and len(sentences) > 0:
            if (sentences_word_counts[i] > 10 and (comma_semicolon_count/sentences_word_counts[i] > (average_commas_semicolons_per_word_for_whole_text + standard_deviation))):
                set_sentences_many_commas.add(i)
#Since these substitutions are for phrases containing several words, they can be done throughout the "whole_text",
#at the end of a 'for i in range(len(sentences))' loop.
for phrase_index in range(len(that_comma_inside)):
    pattern = re.compile(that_comma_inside[phrase_index])
    whole_text = re.sub(pattern, that_no_comma[phrase_index], whole_text)

whole_text = whole_text.replace(',,,', ',').replace(',,',',').replace(', ,', ',').replace(':,', ':').replace(';,', ';').replace(",',", ",'").replace(',",', ',"')

#All of the data will be outputed in a single dictionary (entireData_dictionaries), whose sole key is mapped to a value consisting of a list of the
#four dictionaries below (along with lists/strings). The title of the individual dictionaries give insight as to the structure of the dictionaries: KeyNames_ValueName1ValueName2ValueName3.
sentencesFewCommas_sentenceIndex = {}
sentencesManyCommas_sentenceIndex = {}
percent_increase_in_commas = {}
potentiallyMispronouncedWords_wordCounts = {}
entireData_dictionaries = {}

#A list of heteronyms in the text will be assembled (using either "heteronyms_list_American_English" or "heteronyms_list_American_English" based on the
#TTS voice you are using (they don't have the exact same list of heteronyms)) Every element of the list will contain the start index of the heteronym
#within the whole_text and the heteronym itself.
if English_Phonetics == "American_English":
    list_of_heteronyms_in_text = []
    for heteronym in heteronyms_list_American_English:
        heteronym_matches = re.finditer("\W" + heteronym + "\W", whole_text)
        list_of_heteronyms_in_text += [[match.start(),heteronym] for match in heteronym_matches]

        heteronym_whole_text = whole_text
        heteronym_matches = re.finditer("\W" + heteronym.lower() + "\W", whole_text)
        list_of_heteronyms_in_text += [[match.start(), heteronym] for match in heteronym_matches]
else:
    list_of_heteronyms_in_text = []
    for heteronym in heteronyms_list_British_English:
        heteronym_matches = re.finditer("\W" + heteronym + "\W", whole_text)
        list_of_heteronyms_in_text += [[match.start(),heteronym] for match in heteronym_matches]

        heteronym_whole_text = whole_text
        heteronym_matches = re.finditer("\W" + heteronym.lower() + "\W", whole_text)
        list_of_heteronyms_in_text += [[match.start(), heteronym] for match in heteronym_matches]

list_of_heteronyms_in_text = sorted(list_of_heteronyms_in_text, key=itemgetter(0))

sentences = [sentence.strip() for sentence in re.split('(!?\.)', whole_text)]
sentence_start_index = 0
set_of_sentence_indices_with_heteronyms = set()
for i in range(len(sentences)):
    #Populating the dictionaries of sentences with few commas and sentences with many commas (this needs to be
    #done before the heteronym substitutions, as the added phoneme tags would lengthen the sentences).
    comma_semicolon_count = sentences[i].count(',') + sentences[i].count(';')
    ##Flag long sentences with less than 2 commas/semicolons (average of 4.7 characters per word in English and sentences shouldn't be longer than 35 words), after having added some commas.
    if ((len(sentences[i].strip()) > 165) and ((sentences[i].count(';') + sentences[i].count(':') + sentences[i].count(',')) < 2)):
        sentencesFewCommas_sentenceIndex[sentences[i] + sentences[i+1]] = i
    if i in set_sentences_many_commas:
        sentencesManyCommas_sentenceIndex[sentences[i] + sentences[i+1]] = i

    #Making a set of sentences indices of sentences containing heteronyms. Only sentences of which the heteronym index within
    #the whole_text is in between the bounds of the sentence's start and end indices within the whole_text are included in the set.
    if list_of_heteronyms_in_text != [] and sentences[i] != "":
        sentence_start_index = whole_text.index(sentences[i], sentence_start_index)
        sentence_end_index = sentence_start_index + len(sentences[i])
        for element in list_of_heteronyms_in_text:
            if element[0]>= sentence_start_index and element[0] < sentence_end_index:
                set_of_sentence_indices_with_heteronyms.add(i)

#All of the sentences at the indices in "set_of_sentence_indices_with_heteronyms" will be merged together and submitted as one block to the code below, for maximal efficiency.
#The sentences will then be split again at "===" placeholder introduced between sentences in combined_sentences and will populate the dictionary
#heteronymListIndex_HeteronymModifiedSentenceHeteronymCount with results.
#This will be repeated for every different heteronym in the text. A space is needed in " ===" to ensure that if the final word in a
#sentence is a heteronym, it will be corretly tokenized by spacy (otherwise, it would give "heteronym===").
combined_sentences = ""
for index in set_of_sentence_indices_with_heteronyms:
    combined_sentences += sentences[index] + " ==="

#Only pass perform parsing of 'text' if a heteronym was found in 'combined_sentences_word_list'. This is important, as the parsing step is very computationally onerous, and there
#may be thousands of heteronyms in the text file.
nlp = spacy.load('en_core_web_trf')
doc = nlp(combined_sentences)
combined_sentences_token_list = [[token.text, token.tag_, token.pos_, token.lemma_, token.children] for token in doc]
combined_sentences_word_list = [i[0] for i in combined_sentences_token_list]

#In certain verb heteronyms, the pronounciation differs for different forms of the verb (transitive vs intransitive).
#The function "is_transitive_verb" returns True if the verb depencency labels marking it as transitive, and
#returns False otherwise.
def is_transitive_verb(combined_sentences_token_list):
    indirect_object = False
    direct_object = False
    #combined_sentences_token_list[4] equates to token.children. indirect_object or direct_object will be set to True
    #if the corresponding dependency labels are present in token.children for the instance of the verb.
    for element in combined_sentences_token_list[4]:
        if type(element) == "generator" and (element.dep_ == "iobj" or element.dep_ == "pobj"):
            indirect_object = True
        elif type(element) == "generator" and (element.dep_ == "dobj" or element.dep_ == "dative"):
            direct_object = True
    #Returns False if the verb is intransitive (indirect_object and direct_object are equal to False).
    #Otherwise returns True, indicating that the verb is transitive.
    if not direct_object and not indirect_object:
        return False
    else:
        return True

#There is a function for every heteronym in 'heteronyms_list_American_English' and 'heteronyms_list_British_English'. In each function, the original
#heteronym is substituted for words with less ambiguous pronunciations, depending on their capitalized status and spacy parsing tagging.
def absent(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Absent" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????bs??nt">Absent</phoneme>'
        elif combined_sentences_token_list[i][0] == "absent" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????bs??nt">absent</phoneme>'
        elif combined_sentences_token_list[i][0] == "Absent" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??b??s??nt">Absent</phoneme>'
        elif combined_sentences_token_list[i][0] == "absent" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??b??s??nt">absent</phoneme>'
    return combined_sentences_word_list

#In the (seldomly encountered) specific case of the verb "abstract" as in "to summarize", the heteronym should read ????b??str??kt, but in the code below,
#all verb forms of "abstract" have been assigned with the phoneme ??b??str??kt.
def abstract(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Abstract" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????b??str??kt">Abstract</phoneme>'
        elif combined_sentences_token_list[i][0] == "abstract" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????b??str??kt">abstract</phoneme>'
        elif combined_sentences_token_list[i][0] == "Abstract" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??b??str??kt">Abstract</phoneme>'
        elif combined_sentences_token_list[i][0] == "abstract" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??b??str??kt">abstract</phoneme>'

        elif combined_sentences_token_list[i][0] == "Abstract" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????bstr??kt">Abstract</phoneme>'
        elif combined_sentences_token_list[i][0] == "abstract" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????bstr??kt">abstract</phoneme>'
        elif combined_sentences_token_list[i][0] == "Abstract" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??b??str??kt">Abstract</phoneme>'
        elif combined_sentences_token_list[i][0] == "abstract" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??b??str??kt">abstract</phoneme>'
    return combined_sentences_word_list

def abuse(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Abuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????bjuz">Abuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "abuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????bjuz">abuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Abuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????bjus">Abuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "abuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????bjus">abuse</phoneme>'

        elif combined_sentences_token_list[i][0] == "Abuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????bju??z">Abuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "abuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????bju??z">abuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Abuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????bju??s">Abuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "abuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????bju??s">abuse</phoneme>'
    return combined_sentences_word_list

#Only if the voice is British English, because in American English, it can be pronounced the same (verb vs noun).
def accent(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Accent" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??s??nt">Accent</phoneme>'
        elif combined_sentences_token_list[i][0] == "accent" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??s??nt">accent</phoneme>'
        elif combined_sentences_token_list[i][0] == "Accent" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????ks??nt">Accent</phoneme>'
        elif combined_sentences_token_list[i][0] == "accent" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????ks??nt">accent</phoneme>'
    return combined_sentences_word_list

def acuminate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Acuminate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????kjum????ne??t">Acuminate</phoneme>'
        elif combined_sentences_token_list[i][0] == "acuminate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????kjum????ne??t">acuminate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Acuminate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????kjum??n??t">Acuminate</phoneme>'
        elif combined_sentences_token_list[i][0] == "acuminate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????kjum??n??t">acuminate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Acuminate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????kju??m????ne??t">Acuminate</phoneme>'
        elif combined_sentences_token_list[i][0] == "acuminate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????kju??m????ne??t">acuminate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Acuminate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????kju??m??n??t">Acuminate</phoneme>'
        elif combined_sentences_token_list[i][0] == "acuminate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????kju??m??n??t">acuminate</phoneme>'
    return combined_sentences_word_list

def addict(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Addict" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d??kt">Addict</phoneme>'
        elif combined_sentences_token_list[i][0] == "addict" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d??kt">addict</phoneme>'
        elif combined_sentences_token_list[i][0] == "Addict" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d??kt">Addict</phoneme>'
        elif combined_sentences_token_list[i][0] == "addict" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d??kt">addict</phoneme>'
    return combined_sentences_word_list

def adduct(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Adduct" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d??kt">Adduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "adduct" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d??kt">adduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "Adduct" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d??kt">Adduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "adduct" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d??kt">adduct</phoneme>'
    return combined_sentences_word_list

def adept(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Adept" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d??pt">Adept</phoneme>'
        elif combined_sentences_token_list[i][0] == "adept" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d??pt">adept</phoneme>'
        elif combined_sentences_token_list[i][0] == "Adept" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d????pt">Adept</phoneme>'
        elif combined_sentences_token_list[i][0] == "adept" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d????pt">adept</phoneme>'
        elif combined_sentences_token_list[i][0] == "Adept" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d??pt">Adept</phoneme>'
        elif combined_sentences_token_list[i][0] == "adept" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d??pt">adept</phoneme>'
    return combined_sentences_word_list

def adulterate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Adulterate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d??lt????re??t">Adulterate</phoneme>'
        elif combined_sentences_token_list[i][0] == "adulterate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d??lt????re??t">adulterate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Adulterate" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d??lt??r??t">Adulterate</phoneme>'
        elif combined_sentences_token_list[i][0] == "adulterate" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d??lt??r??t">adulterate</phoneme>'
    return combined_sentences_word_list

def advert(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Advert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??v??rt">Advert</phoneme>'
        elif combined_sentences_token_list[i][0] == "advert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??v??rt">advert</phoneme>'
        elif combined_sentences_token_list[i][0] == "Advert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d??v??rt">Advert</phoneme>'
        elif combined_sentences_token_list[i][0] == "advert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d??v??rt">advert</phoneme>'

        elif combined_sentences_token_list[i][0] == "Advert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??v????t">Advert</phoneme>'
        elif combined_sentences_token_list[i][0] == "advert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??v????t">advert</phoneme>'
        elif combined_sentences_token_list[i][0] == "Advert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????dv????t">Advert</phoneme>'
        elif combined_sentences_token_list[i][0] == "advert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????dv????t">advert</phoneme>'
    return combined_sentences_word_list

def advocate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Advocate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????dv????ke??t">Advocate</phoneme>'
        elif combined_sentences_token_list[i][0] == "advocate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????dv????ke??t">advocate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Advocate" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????dv??k??t">Advocate</phoneme>'
        elif combined_sentences_token_list[i][0] == "advocate" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????dv??k??t">advocate</phoneme>'
    return combined_sentences_word_list

#In both American and British English, the verb "affect" is pronounced ????f??kt. In British English, the noun may be
#pronounced as either ????f??kt or ????f??kt and in American English, the noun is pronounced ????f????kt, so the SSML phoneme
#is only included for the noun in American English.
def affect(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Affect" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????f??kt">Affect</phoneme>'
        elif combined_sentences_token_list[i][0] == "affect" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????f??kt">affect</phoneme>'
        elif combined_sentences_token_list[i][0] == "Affect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????f??kt">Affect</phoneme>'
        elif combined_sentences_token_list[i][0] == "affect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????f??kt">affect</phoneme>'
    return combined_sentences_word_list

def affiliate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Affiliate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????f??li??e??t">Affiliate</phoneme>'
        elif combined_sentences_token_list[i][0] == "affiliate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????f??li??e??t">affiliate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Affiliate" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????f??li??t">Affiliate</phoneme>'
        elif combined_sentences_token_list[i][0] == "affiliate" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????f??li??t">affiliate</phoneme>'
    return combined_sentences_word_list

def affix(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Affix" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????f??ks">Affix</phoneme>'
        elif combined_sentences_token_list[i][0] == "affix" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????f??ks">affix</phoneme>'
        elif combined_sentences_token_list[i][0] == "Affix" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????f????ks">Affix</phoneme>'
        elif combined_sentences_token_list[i][0] == "affix" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????f????ks">affix</phoneme>'

        elif combined_sentences_token_list[i][0] == "Affix" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????f??ks">Affix</phoneme>'
        elif combined_sentences_token_list[i][0] == "affix" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????f??ks">affix</phoneme>'
        elif combined_sentences_token_list[i][0] == "Affix" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????f??ks">Affix</phoneme>'
        elif combined_sentences_token_list[i][0] == "affix" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????f??ks">affix</phoneme>'
    return combined_sentences_word_list

def agglomerate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Agglomerate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????gl??m??r??e??t">Agglomerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "agglomerate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????gl??m??r??e??t">agglomerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Agglomerate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????l??m??r??t">Agglomerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "agglomerate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????l??m??r??t">agglomerate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Agglomerate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????l??m????re??t">Agglomerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "agglomerate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????l??m????re??t">agglomerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Agglomerate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????l??m??r??t">Agglomerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "agglomerate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????l??m??r??t">agglomerate</phoneme>'
    return combined_sentences_word_list

def agglutinate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Agglutinate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????lu??t????ne??t">Agglutinate</phoneme>'
        elif combined_sentences_token_list[i][0] == "agglutinate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????lu??t????ne??t">agglutinate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Agglutinate" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????lu??t??n??t">Agglutinate</phoneme>'
        elif combined_sentences_token_list[i][0] == "agglutinate" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????lu??t??n??t">agglutinate</phoneme>'
    return combined_sentences_word_list


def aggregate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Aggregate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????gr????ge??t">Aggregate</phoneme>'
        elif combined_sentences_token_list[i][0] == "aggregate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????gr????ge??t">aggregate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Aggregate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????gr??g??t">Aggregate</phoneme>'
        elif combined_sentences_token_list[i][0] == "aggregate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????gr??g??t">aggregate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Aggregate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????r??????e??t">Aggregate</phoneme>'
        elif combined_sentences_token_list[i][0] == "aggregate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????r??????e??t">aggregate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Aggregate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????r??????t">Aggregate</phoneme>'
        elif combined_sentences_token_list[i][0] == "aggregate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????r??????t">aggregate</phoneme>'
    return combined_sentences_word_list

def aliment(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Aliment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????l????m??nt">Aliment</phoneme>'
        elif combined_sentences_token_list[i][0] == "aliment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????l????m??nt">aliment</phoneme>'
        elif combined_sentences_token_list[i][0] == "Aliment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????l??m??nt">Aliment</phoneme>'
        elif combined_sentences_token_list[i][0] == "aliment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????l??m??nt">aliment</phoneme>'

        elif combined_sentences_token_list[i][0] == "Aliment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????l????m??nt">Aliment</phoneme>'
        elif combined_sentences_token_list[i][0] == "aliment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????l????m??nt">aliment</phoneme>'
        elif combined_sentences_token_list[i][0] == "Aliment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????l??m??nt">Aliment</phoneme>'
        elif combined_sentences_token_list[i][0] == "aliment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????l??m??nt">aliment</phoneme>'
    return combined_sentences_word_list

def alloy(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Alloy" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????l????">Alloy</phoneme>'
        elif combined_sentences_token_list[i][0] == "alloy" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????l????">alloy</phoneme>'
        elif combined_sentences_token_list[i][0] == "Alloy" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????l????">Alloy</phoneme>'
        elif combined_sentences_token_list[i][0] == "alloy" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????l????">alloy</phoneme>'
    return combined_sentences_word_list

#Spacy tokenizes "Allies" (as in "the Allied forces") as a proper name.
#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def allied(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Allied" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????la??d">Allied</phoneme>'
        elif combined_sentences_token_list[i][0] == "allied" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????la??d">allied</phoneme>'
        elif combined_sentences_token_list[i][0] == "Allied" and combined_sentences_token_list[i][1] in ["NNP", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????la??d">Allied</phoneme>'
        elif combined_sentences_token_list[i][0] == "allied" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????la??d">allied</phoneme>'
    return combined_sentences_word_list

def ally(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Ally" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????la??">Ally</phoneme>'
        elif combined_sentences_token_list[i][0] == "ally" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????la??">ally</phoneme>'
        elif combined_sentences_token_list[i][0] == "Ally" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????la??">Ally</phoneme>'
        elif combined_sentences_token_list[i][0] == "ally" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????la??">ally</phoneme>'
    return combined_sentences_word_list

def alternate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Alternate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????lt??r??ne??t">Alternate</phoneme>'
        elif combined_sentences_token_list[i][0] == "alternate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????lt??r??ne??t">alternate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Alternate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????lt??rn??t">Alternate</phoneme>'
        elif combined_sentences_token_list[i][0] == "alternate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????lt??rn??t">alternate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Alternate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????lt????ne??t">Alternate</phoneme>'
        elif combined_sentences_token_list[i][0] == "alternate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????lt????ne??t">alternate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Alternate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????l??t????n??t">Alternate</phoneme>'
        elif combined_sentences_token_list[i][0] == "alternate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????l??t????n??t">alternate</phoneme>'
    return combined_sentences_word_list

def analyses(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Analyses" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??la??z??z">Analyses</phoneme>'
        elif combined_sentences_token_list[i][0] == "analyses" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??la??z??z">analyses</phoneme>'
        elif combined_sentences_token_list[i][0] == "Analyses" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??l??si??z">Analyses</phoneme>'
        elif combined_sentences_token_list[i][0] == "analyses" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??l??si??z">analyses</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def animate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Animate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n????me??t">Animate</phoneme>'
        elif combined_sentences_token_list[i][0] == "animate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n????me??t">animate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Animate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??m??t">Animate</phoneme>'
        elif combined_sentences_token_list[i][0] == "animate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??m??t">animate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Animate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n????me??t">Animate</phoneme>'
        elif combined_sentences_token_list[i][0] == "animate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n????me??t">animate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Animate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??m??t">Animate</phoneme>'
        elif combined_sentences_token_list[i][0] == "animate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??m??t">animate</phoneme>'
    return combined_sentences_word_list

def annex(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Annex" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??ks">Annex</phoneme>'
        elif combined_sentences_token_list[i][0] == "annex" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??ks">annex</phoneme>'
        elif combined_sentences_token_list[i][0] == "Annex" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n????ks">Annex</phoneme>'
        elif combined_sentences_token_list[i][0] == "annex" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n????ks">annex</phoneme>'

        elif combined_sentences_token_list[i][0] == "Annex" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??ks">Annex</phoneme>'
        elif combined_sentences_token_list[i][0] == "annex" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??ks">annex</phoneme>'
        elif combined_sentences_token_list[i][0] == "Annex" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??ks">Annex</phoneme>'
        elif combined_sentences_token_list[i][0] == "annex" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??ks">annex</phoneme>'
    return combined_sentences_word_list

def appropriate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Appropriate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????pro??pri??e??t">Appropriate</phoneme>'
        elif combined_sentences_token_list[i][0] == "appropriate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????pro??pri??e??t">appropriate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Appropriate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????pro??pri??t">Appropriate</phoneme>'
        elif combined_sentences_token_list[i][0] == "appropriate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????pro??pri??t">appropriate</phoneme>'

        if combined_sentences_token_list[i][0] == "Appropriate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????pr????pr????e??t">Appropriate</phoneme>'
        elif combined_sentences_token_list[i][0] == "appropriate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????pr????pr????e??t">appropriate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Appropriate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????pr????pr????t">Appropriate</phoneme>'
        elif combined_sentences_token_list[i][0] == "appropriate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????pr????pr????t">appropriate</phoneme>'
    return combined_sentences_word_list

def approximate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Approximate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????pr??ks????me??t">Approximate</phoneme>'
        elif combined_sentences_token_list[i][0] == "approximate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????pr??ks????me??t">approximate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Approximate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????pr??ks??m??t">Approximate</phoneme>'
        elif combined_sentences_token_list[i][0] == "approximate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????pr??ks??m??t">approximate</phoneme>'

        if combined_sentences_token_list[i][0] == "Approximate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????pr??ks????me??t">Approximate</phoneme>'
        elif combined_sentences_token_list[i][0] == "approximate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????pr??ks????me??t">approximate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Approximate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????pr??ks??m??t">Approximate</phoneme>'
        elif combined_sentences_token_list[i][0] == "approximate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????pr??ks??m??t">approximate</phoneme>'
    return combined_sentences_word_list

def arithmetic(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Arithmetic" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????r????m??t??k">Arithmetic</phoneme>'
        elif combined_sentences_token_list[i][0] == "arithmetic" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????r????m??t??k">arithmetic</phoneme>'
        elif combined_sentences_token_list[i][0] == "Arithmetic" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????r??????m??t??k">Arithmetic</phoneme>'
        elif combined_sentences_token_list[i][0] == "arithmetic" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????r??????m??t??k">arithmetic</phoneme>'
    return combined_sentences_word_list

def articulate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Articulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??r??t??kj????le??t">Articulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "articulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??r??t??kj????le??t">articulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Articulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??r??t??kj??l??t">Articulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "articulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??r??t??kj??l??t">articulate</phoneme>'

        if combined_sentences_token_list[i][0] == "Articulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????t??kj????le??t">Articulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "articulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????t??kj????le??t">articulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Articulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????t??kj??l??t">Articulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "articulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????t??kj??l??t">articulate</phoneme>'
    return combined_sentences_word_list

def aspirate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Aspirate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????sp????re??t">Aspirate</phoneme>'
        elif combined_sentences_token_list[i][0] == "aspirate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????sp????re??t">aspirate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Aspirate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????sp??r??t">Aspirate</phoneme>'
        elif combined_sentences_token_list[i][0] == "aspirate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????sp??r??t">aspirate</phoneme>'

        if combined_sentences_token_list[i][0] == "Aspirate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????sp????re??t">Aspirate</phoneme>'
        elif combined_sentences_token_list[i][0] == "aspirate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????sp????re??t">aspirate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Aspirate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????sp??r??t">Aspirate</phoneme>'
        elif combined_sentences_token_list[i][0] == "aspirate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????sp??r??t">aspirate</phoneme>'
    return combined_sentences_word_list

def associate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Associate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????so????i??e??t">Associate</phoneme>'
        elif combined_sentences_token_list[i][0] == "associate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????so????i??e??t">associate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Associate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????so????i??t">Associate</phoneme>'
        elif combined_sentences_token_list[i][0] == "associate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????so????i??t">associate</phoneme>'

        if combined_sentences_token_list[i][0] == "Associate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????s??????????e??t">Associate</phoneme>'
        elif combined_sentences_token_list[i][0] == "associate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????s??????????e??t">associate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Associate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????s??????????t">Associate</phoneme>'
        elif combined_sentences_token_list[i][0] == "associate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????s??????????t">associate</phoneme>'
    return combined_sentences_word_list

def attribute(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Attribute" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????tr??bjut">Attribute</phoneme>'
        elif combined_sentences_token_list[i][0] == "attribute" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????tr??bjut">attribute</phoneme>'
        elif combined_sentences_token_list[i][0] == "Attribute" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????tr????bjut">Attribute</phoneme>'
        elif combined_sentences_token_list[i][0] == "attribute" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????tr????bjut">attribute</phoneme>'

        elif combined_sentences_token_list[i][0] == "Attribute" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????tr??bju??t">Attribute</phoneme>'
        elif combined_sentences_token_list[i][0] == "attribute" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????tr??bju??t">attribute</phoneme>'
        elif combined_sentences_token_list[i][0] == "Attribute" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????tr????bju??t">Attribute</phoneme>'
        elif combined_sentences_token_list[i][0] == "attribute" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????tr????bju??t">attribute</phoneme>'
    return combined_sentences_word_list

def augment(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Augment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??g??m??nt">Augment</phoneme>'
        elif combined_sentences_token_list[i][0] == "augment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??g??m??nt">augment</phoneme>'
        elif combined_sentences_token_list[i][0] == "Augment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????g??m??nt">Augment</phoneme>'
        elif combined_sentences_token_list[i][0] == "augment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????g??m??nt">augment</phoneme>'

        elif combined_sentences_token_list[i][0] == "Augment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????????m??nt">Augment</phoneme>'
        elif combined_sentences_token_list[i][0] == "augment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????????m??nt">augment</phoneme>'
        elif combined_sentences_token_list[i][0] == "Augment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????????m??nt">Augment</phoneme>'
        elif combined_sentences_token_list[i][0] == "augment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????????m??nt">augment</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def august(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "August" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????g??st">August</phoneme>'
        elif combined_sentences_token_list[i][0] == "august" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????g??st">august</phoneme>'
        elif combined_sentences_token_list[i][0] == "August" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????g??st">August</phoneme>'
        elif combined_sentences_token_list[i][0] == "august" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????g??st">august</phoneme>'

        elif combined_sentences_token_list[i][0] == "August" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????????st">August</phoneme>'
        elif combined_sentences_token_list[i][0] == "august" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????????st">august</phoneme>'
        elif combined_sentences_token_list[i][0] == "August" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????????st">August</phoneme>'
        elif combined_sentences_token_list[i][0] == "august" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????????st">august</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def axes(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Axes" and English_Phonetics == "American_English" and combined_sentences_token_list[i][3].lower() in ["ax", "axe"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????k??s??z">Axes</phoneme>'
        elif combined_sentences_token_list[i][0] == "axes" and English_Phonetics == "American_English" and combined_sentences_token_list[i][3].lower() in ["ax", "axe"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????k??s??z">axes</phoneme>'
        elif combined_sentences_token_list[i][0] == "Axes" and English_Phonetics == "American_English" and combined_sentences_token_list[i][3].lower() == "axis":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????k??siz">Axes</phoneme>'
        elif combined_sentences_token_list[i][0] == "axes" and English_Phonetics == "American_English" and combined_sentences_token_list[i][3].lower() == "axis":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????k??siz">axes</phoneme>'

        if combined_sentences_token_list[i][0] == "Axes" and English_Phonetics == "British_English" and combined_sentences_token_list[i][3].lower() in ["ax", "axe"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????ks??z">Axes</phoneme>'
        elif combined_sentences_token_list[i][0] == "axes" and English_Phonetics == "British_English" and combined_sentences_token_list[i][3].lower() in ["ax", "axe"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????ks??z">axes</phoneme>'
        elif combined_sentences_token_list[i][0] == "Axes" and English_Phonetics == "British_English" and combined_sentences_token_list[i][3].lower() == "axis":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????ksi??z">Axes</phoneme>'
        elif combined_sentences_token_list[i][0] == "axes" and English_Phonetics == "British_English" and combined_sentences_token_list[i][3].lower() == "axis":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????ksi??z">axes</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def bases(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Bases" and English_Phonetics == "American_English" and combined_sentences_token_list[i][3].lower() == "base":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??be??s??z">Bases</phoneme>'
        elif combined_sentences_token_list[i][0] == "bases" and English_Phonetics == "American_English" and combined_sentences_token_list[i][3].lower() == "base":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??be??s??z">bases</phoneme>'
        elif combined_sentences_token_list[i][0] == "Bases" and English_Phonetics == "American_English" and combined_sentences_token_list[i][3].lower() == "basis":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??be????siz">Bases</phoneme>'
        elif combined_sentences_token_list[i][0] == "bases" and English_Phonetics == "American_English" and combined_sentences_token_list[i][3].lower() == "basis":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??be????siz">bases</phoneme>'

        elif combined_sentences_token_list[i][0] == "Bases" and English_Phonetics == "British_English" and combined_sentences_token_list[i][3].lower() == "base":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??be??s??z">Bases</phoneme>'
        elif combined_sentences_token_list[i][0] == "bases" and English_Phonetics == "British_English" and combined_sentences_token_list[i][3].lower() == "base":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??be??s??z">bases</phoneme>'
        elif combined_sentences_token_list[i][0] == "Bases" and English_Phonetics == "British_English" and combined_sentences_token_list[i][3].lower() == "basis":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??be??si??z">Bases</phoneme>'
        elif combined_sentences_token_list[i][0] == "bases" and English_Phonetics == "British_English" and combined_sentences_token_list[i][3].lower() == "basis":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??be??si??z">bases</phoneme>'
    return combined_sentences_word_list

#As the following nouns may be pronounced "ba??" for a bow gesture or the forward end of a ship and "bo??" or "b????" for a bow-shaped object,
#only the verb (always pronounced "ba??") is included here to avoid misassigning the phonemes.
def bow(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Bow" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ba??">Bow</phoneme>'
        elif combined_sentences_token_list[i][0] == "bow" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ba??">bow</phoneme>'
    return combined_sentences_word_list

def bows(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Bows" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ba??z">Bows</phoneme>'
        elif combined_sentences_token_list[i][0] == "bows" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ba??z">bows</phoneme>'
        elif combined_sentences_token_list[i][0] == "Bows" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??bo??z">Bows</phoneme>'
        elif combined_sentences_token_list[i][0] == "bows" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??bo??z">bows</phoneme>'
    return combined_sentences_word_list

#As there are several pronounciations for the different nouns "buffet", only the verb was included.
def buffet(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Buffet" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??b??f??t">Buffet</phoneme>'
        elif combined_sentences_token_list[i][0] == "buffet" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??b??f??t">buffet</phoneme>'
    return combined_sentences_word_list

def certificate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Certificate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s??r??t??f????ke??t">Certificate</phoneme>'
        elif combined_sentences_token_list[i][0] == "certificate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s??r??t??f????ke??t">certificate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Certificate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s??r??t??f??k??t">Certificate</phoneme>'
        elif combined_sentences_token_list[i][0] == "certificate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s??r??t??f??k??t">certificate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Certificate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s????t??f????ke??t">Certificate</phoneme>'
        elif combined_sentences_token_list[i][0] == "certificate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s????t??f????ke??t">certificate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Certificate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s????t??f??k??t">Certificate</phoneme>'
        elif combined_sentences_token_list[i][0] == "certificate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s????t??f??k??t">certificate</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def chassis(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Chassis" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:3] == "NNS":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????s??iz">Chassis</phoneme>'
        elif combined_sentences_token_list[i][0] == "chassis" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:3] == "NNS":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????s??iz">chassis</phoneme>'
        elif combined_sentences_token_list[i][0] == "Chassis" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????si">Chassis</phoneme>'
        elif combined_sentences_token_list[i][0] == "chassis" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????si">chassis</phoneme>'

        elif combined_sentences_token_list[i][0] == "Chassis" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:3] == "NNS":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????s??z">Chassis</phoneme>'
        elif combined_sentences_token_list[i][0] == "chassis" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:3] == "NNS":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????s??z">chassis</phoneme>'
        elif combined_sentences_token_list[i][0] == "Chassis" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????s??">Chassis</phoneme>'
        elif combined_sentences_token_list[i][0] == "chassis" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????s??">chassis</phoneme>'
    return combined_sentences_word_list

def close(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Close" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="klo??z">Close</phoneme>'
        elif combined_sentences_token_list[i][0] == "close" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="klo??z">close</phoneme>'
        elif combined_sentences_token_list[i][0] == "Close" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="klo??s">Close</phoneme>'
        elif combined_sentences_token_list[i][0] == "close" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="klo??s">close</phoneme>'

        elif combined_sentences_token_list[i][0] == "Close" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kl????z">Close</phoneme>'
        elif combined_sentences_token_list[i][0] == "close" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kl????z">close</phoneme>'
        elif combined_sentences_token_list[i][0] == "Close" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kl????s">Close</phoneme>'
        elif combined_sentences_token_list[i][0] == "close" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kl????s">close</phoneme>'
    return combined_sentences_word_list

def coagulate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Coagulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ko??????gju??le??t">Coagulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "coagulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ko??????gju??le??t">coagulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Coagulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ko??????gjulit">Coagulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "coagulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ko??????gjulit">coagulate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Coagulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??????????j????le??t">Coagulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "coagulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??????????j????le??t">coagulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Coagulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??????????j??l??t">Coagulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "coagulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??????????j??l??t">coagulate</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def coax(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Coax" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ko??ks">Coax</phoneme>'
        elif combined_sentences_token_list[i][0] == "coax" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ko??ks">coax</phoneme>'
        elif combined_sentences_token_list[i][0] == "Coax" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kou????ks">Coax</phoneme>'
        elif combined_sentences_token_list[i][0] == "coax" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kou????ks">coax</phoneme>'

        elif combined_sentences_token_list[i][0] == "Coax" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k????ks">Coax</phoneme>'
        elif combined_sentences_token_list[i][0] == "coax" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k????ks">coax</phoneme>'
        elif combined_sentences_token_list[i][0] == "Coax" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??????ks">Coax</phoneme>'
        elif combined_sentences_token_list[i][0] == "coax" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??????ks">coax</phoneme>'
    return combined_sentences_word_list

#As distinct "collect" nouns can be pronounced differently, only the verb was included
def collect(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Collect" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k????l??kt">Collect</phoneme>'
        elif combined_sentences_token_list[i][0] == "collect" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k????l??kt">collect</phoneme>'
    return combined_sentences_word_list

def combat(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Combat" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??m??b??t">Combat</phoneme>'
        elif combined_sentences_token_list[i][0] == "combat" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??m??b??t">combat</phoneme>'
        elif combined_sentences_token_list[i][0] == "Combat" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??m??b??t">Combat</phoneme>'
        elif combined_sentences_token_list[i][0] == "combat" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??m??b??t">combat</phoneme>'

        elif combined_sentences_token_list[i][0] == "Combat" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??m??b??t">Combat</phoneme>'
        elif combined_sentences_token_list[i][0] == "combat" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??m??b??t">combat</phoneme>'
        elif combined_sentences_token_list[i][0] == "Combat" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??mb??t">Combat</phoneme>'
        elif combined_sentences_token_list[i][0] == "combat" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??mb??t">combat</phoneme>'
    return combined_sentences_word_list

#The verb "combine" is pronounced the same in American and British English, except for the form involving harvesting crops with a combine harvester
#(which is pronounced like the noun in American English). Therefore, only the nouns are included.
def combine(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Combine" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??m??ba??n">Combine</phoneme>'
        elif combined_sentences_token_list[i][0] == "combine" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??m??ba??n">combine</phoneme>'
        elif combined_sentences_token_list[i][0] == "Combine" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??mba??n">Combine</phoneme>'
        elif combined_sentences_token_list[i][0] == "combine" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??mba??n">combine</phoneme>'
    return combined_sentences_word_list

def commune(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Commune" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k????mjun">Commune</phoneme>'
        elif combined_sentences_token_list[i][0] == "commune" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k????mjun">commune</phoneme>'
        elif combined_sentences_token_list[i][0] == "Commune" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??m??jun">Commune</phoneme>'
        elif combined_sentences_token_list[i][0] == "commune" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??m??jun">commune</phoneme>'

        elif combined_sentences_token_list[i][0] == "Commune" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k????mju??n">Commune</phoneme>'
        elif combined_sentences_token_list[i][0] == "commune" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k????mju??n">commune</phoneme>'
        elif combined_sentences_token_list[i][0] == "Commune" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??mju??n">Commune</phoneme>'
        elif combined_sentences_token_list[i][0] == "commune" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??mju??n">commune</phoneme>'
    return combined_sentences_word_list

def compact(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Compact" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??m??p??kt">Compact</phoneme>'
        elif combined_sentences_token_list[i][0] == "compact" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??m??p??kt">compact</phoneme>'
        elif combined_sentences_token_list[i][0] == "Compact" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??mp??kt">Compact</phoneme>'
        elif combined_sentences_token_list[i][0] == "compact" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??mp??kt">compact</phoneme>'
    return combined_sentences_word_list

#Only if the voice is American English, because in British English, it is pronounced the same. Also, only the noun
#is included ("??k??m??pl??ks"), as the adjective may or may not be pronounced the same as the noun.
def complex(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Complex" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??m??pl??ks">Complex</phoneme>'
        elif combined_sentences_token_list[i][0] == "complex" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??m??pl??ks">complex</phoneme>'
    return combined_sentences_word_list

def compound(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Compound" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??m??pa??nd">Compound</phoneme>'
        elif combined_sentences_token_list[i][0] == "compound" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??m??pa??nd">compound</phoneme>'
        elif combined_sentences_token_list[i][0] == "Compound" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??m??pa??nd">Compound</phoneme>'
        elif combined_sentences_token_list[i][0] == "compound" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??m??pa??nd">compound</phoneme>'

        elif combined_sentences_token_list[i][0] == "Compound" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??m??pa??nd">Compound</phoneme>'
        elif combined_sentences_token_list[i][0] == "compound" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??m??pa??nd">compound</phoneme>'
        elif combined_sentences_token_list[i][0] == "Compound" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??mpa??nd">Compound</phoneme>'
        elif combined_sentences_token_list[i][0] == "compound" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??mpa??nd">compound</phoneme>'
    return combined_sentences_word_list

def compress(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Compress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??m??pr??s">Compress</phoneme>'
        elif combined_sentences_token_list[i][0] == "compress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??m??pr??s">compress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Compress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??m??pr??s">Compress</phoneme>'
        elif combined_sentences_token_list[i][0] == "compress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??m??pr??s">compress</phoneme>'

        elif combined_sentences_token_list[i][0] == "Compress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??m??pr??s">Compress</phoneme>'
        elif combined_sentences_token_list[i][0] == "compress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??m??pr??s">compress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Compress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??mpr??s">Compress</phoneme>'
        elif combined_sentences_token_list[i][0] == "compress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??mpr??s">compress</phoneme>'
    return combined_sentences_word_list

def concert(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Concert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??s??rt">Concert</phoneme>'
        elif combined_sentences_token_list[i][0] == "concert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??s??rt">concert</phoneme>'
        elif combined_sentences_token_list[i][0] == "Concert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??ns??rt">Concert</phoneme>'
        elif combined_sentences_token_list[i][0] == "concert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??ns??rt">concert</phoneme>'

        elif combined_sentences_token_list[i][0] == "Concert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??s????t">Concert</phoneme>'
        elif combined_sentences_token_list[i][0] == "concert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??s????t">concert</phoneme>'
        elif combined_sentences_token_list[i][0] == "Concert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??ns????t">Concert</phoneme>'
        elif combined_sentences_token_list[i][0] == "concert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??ns????t">concert</phoneme>'
    return combined_sentences_word_list

#Only in American English, as the noun, verb and adjective are pronounced the same in British English.
#Also, as some distinct "concrete" verbs are pronounced differently, only the noun and adjective are included.
def concrete(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Concrete" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??n??krit">Concrete</phoneme>'
        elif combined_sentences_token_list[i][0] == "concrete" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??n??krit">concrete</phoneme>'
    return combined_sentences_word_list

def conduct(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Conduct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??d??kt">Conduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "conduct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??d??kt">conduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "Conduct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nd??kt">Conduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "conduct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nd??kt">conduct</phoneme>'

        elif combined_sentences_token_list[i][0] == "Conduct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??d??kt">Conduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "conduct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??d??kt">conduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "Conduct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nd??kt">Conduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "conduct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nd??kt">conduct</phoneme>'
    return combined_sentences_word_list

def confect(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Confect" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??f??kt">Confect</phoneme>'
        elif combined_sentences_token_list[i][0] == "confect" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??f??kt">confect</phoneme>'
        elif combined_sentences_token_list[i][0] == "Confect" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nfekt">Confect</phoneme>'
        elif combined_sentences_token_list[i][0] == "confect" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nfekt">confect</phoneme>'
    return combined_sentences_word_list

def confines(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Confines" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??fa??nz">Confines</phoneme>'
        elif combined_sentences_token_list[i][0] == "confines" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??fa??nz">confines</phoneme>'
        elif combined_sentences_token_list[i][0] == "Confines" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nfa??nz">Confines</phoneme>'
        elif combined_sentences_token_list[i][0] == "confines" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nfa??nz">confines</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def conflict(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Conflict" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??fl??kt">Conflict</phoneme>'
        elif combined_sentences_token_list[i][0] == "conflict" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??fl??kt">conflict</phoneme>'
        elif combined_sentences_token_list[i][0] == "Conflict" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??n??fl??kt">Conflict</phoneme>'
        elif combined_sentences_token_list[i][0] == "conflict" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??n??fl??kt">conflict</phoneme>'

        elif combined_sentences_token_list[i][0] == "Conflict" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??fl??kt">Conflict</phoneme>'
        elif combined_sentences_token_list[i][0] == "conflict" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??fl??kt">conflict</phoneme>'
        elif combined_sentences_token_list[i][0] == "Conflict" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nfl??kt">Conflict</phoneme>'
        elif combined_sentences_token_list[i][0] == "conflict" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nfl??kt">conflict</phoneme>'
    return combined_sentences_word_list

def conglomerate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Conglomerate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??gl??m??r??e??t">Conglomerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "conglomerate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??gl??m??r??e??t">conglomerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Conglomerate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??gl??m??r??t">Conglomerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "conglomerate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??gl??m??r??t">conglomerate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Conglomerate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n????l??m????re??t">Conglomerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "conglomerate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n????l??m????re??t">conglomerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Conglomerate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n????l??m??r??t">Conglomerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "conglomerate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n????l??m??r??t">conglomerate</phoneme>'
    return combined_sentences_word_list

def congregate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Congregate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??ngr????ge??t">Congregate</phoneme>'
        elif combined_sentences_token_list[i][0] == "congregate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??ngr????ge??t">congregate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Congregate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??ngr??g??t">Congregate</phoneme>'
        elif combined_sentences_token_list[i][0] == "congregate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??ngr??g??t">congregate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Congregate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??????r??????e??t">Congregate</phoneme>'
        elif combined_sentences_token_list[i][0] == "congregate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??????r??????e??t">congregate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Congregate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??????r??????t">Congregate</phoneme>'
        elif combined_sentences_token_list[i][0] == "congregate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??????r??????t">congregate</phoneme>'
    return combined_sentences_word_list

def congress(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Congress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n????res">Congress</phoneme>'
        elif combined_sentences_token_list[i][0] == "congress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n????res">congress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Congress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??ngr??s">Congress</phoneme>'
        elif combined_sentences_token_list[i][0] == "congress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??ngr??s">congress</phoneme>'

        elif combined_sentences_token_list[i][0] == "Congress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n????res">Congress</phoneme>'
        elif combined_sentences_token_list[i][0] == "congress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n????res">congress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Congress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??????r??s">Congress</phoneme>'
        elif combined_sentences_token_list[i][0] == "congress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??????r??s">congress</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def conjugate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Conjugate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nd??????ge??t">Conjugate</phoneme>'
        elif combined_sentences_token_list[i][0] == "conjugate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nd??????ge??t">conjugate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Conjugate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nd????g??t">Conjugate</phoneme>'
        elif combined_sentences_token_list[i][0] == "conjugate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nd????g??t">conjugate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Conjugate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nd????????e??t">Conjugate</phoneme>'
        elif combined_sentences_token_list[i][0] == "conjugate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nd????????e??t">conjugate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Conjugate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nd????????t">Conjugate</phoneme>'
        elif combined_sentences_token_list[i][0] == "conjugate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nd????????t">conjugate</phoneme>'
    return combined_sentences_word_list

def conscript(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Conscript" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??skr??pt">Conscript</phoneme>'
        elif combined_sentences_token_list[i][0] == "conscript" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??skr??pt">conscript</phoneme>'
        elif combined_sentences_token_list[i][0] == "Conscript" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??n??skr??pt">Conscript</phoneme>'
        elif combined_sentences_token_list[i][0] == "conscript" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??n??skr??pt">conscript</phoneme>'

        elif combined_sentences_token_list[i][0] == "Conscript" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??skr??pt">Conscript</phoneme>'
        elif combined_sentences_token_list[i][0] == "conscript" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??skr??pt">conscript</phoneme>'
        elif combined_sentences_token_list[i][0] == "Conscript" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nskr??pt">Conscript</phoneme>'
        elif combined_sentences_token_list[i][0] == "conscript" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nskr??pt">conscript</phoneme>'
    return combined_sentences_word_list

#Only in American English, as they can be pronounced the same in British English, whereas the noun is usually "??k??n??s??rv" in American English.
#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def conserve(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Conserve" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??s??rv">Conserve</phoneme>'
        elif combined_sentences_token_list[i][0] == "conserve" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??s??rv">conserve</phoneme>'
        elif combined_sentences_token_list[i][0] == "Conserve" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??n??s??rv">Conserve</phoneme>'
        elif combined_sentences_token_list[i][0] == "conserve" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??n??s??rv">conserve</phoneme>'
    return combined_sentences_word_list

def consociate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Consociate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??so????i??e??t">Consociate</phoneme>'
        elif combined_sentences_token_list[i][0] == "consociate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??so????i??e??t">consociate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Consociate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??so????i??t">Consociate</phoneme>'
        elif combined_sentences_token_list[i][0] == "consociate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??so????i??t">consociate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Consociate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??s??????????e??t">Consociate</phoneme>'
        elif combined_sentences_token_list[i][0] == "consociate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??s??????????e??t">consociate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Consociate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??s??????????t">Consociate</phoneme>'
        elif combined_sentences_token_list[i][0] == "consociate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??s??????????t">consociate</phoneme>'
    return combined_sentences_word_list

def console(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Console" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??so??l">Console</phoneme>'
        elif combined_sentences_token_list[i][0] == "console" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??so??l">console</phoneme>'
        elif combined_sentences_token_list[i][0] == "Console" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??n??so??l">Console</phoneme>'
        elif combined_sentences_token_list[i][0] == "console" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??n??so??l">console</phoneme>'

        elif combined_sentences_token_list[i][0] == "Console" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??s????l">Console</phoneme>'
        elif combined_sentences_token_list[i][0] == "console" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??s????l">console</phoneme>'
        elif combined_sentences_token_list[i][0] == "Console" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??ns????l">Console</phoneme>'
        elif combined_sentences_token_list[i][0] == "console" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??ns????l">console</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def consort(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Consort" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??s??rt">Consort</phoneme>'
        elif combined_sentences_token_list[i][0] == "consort" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??s??rt">consort</phoneme>'
        elif combined_sentences_token_list[i][0] == "Consort" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??n??s??rt">Consort</phoneme>'
        elif combined_sentences_token_list[i][0] == "consort" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??n??s??rt">consort</phoneme>'

        elif combined_sentences_token_list[i][0] == "Consort" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??s????t">Consort</phoneme>'
        elif combined_sentences_token_list[i][0] == "consort" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??s????t">consort</phoneme>'
        elif combined_sentences_token_list[i][0] == "Consort" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??ns????t">Consort</phoneme>'
        elif combined_sentences_token_list[i][0] == "consort" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??ns????t">consort</phoneme>'
    return combined_sentences_word_list

def construct(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Construct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??str??kt">Construct</phoneme>'
        elif combined_sentences_token_list[i][0] == "construct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??str??kt">construct</phoneme>'
        elif combined_sentences_token_list[i][0] == "Construct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??n??str??kt">Construct</phoneme>'
        elif combined_sentences_token_list[i][0] == "construct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??n??str??kt">construct</phoneme>'

        elif combined_sentences_token_list[i][0] == "Construct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??str??kt">Construct</phoneme>'
        elif combined_sentences_token_list[i][0] == "construct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??str??kt">construct</phoneme>'
        elif combined_sentences_token_list[i][0] == "Construct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nstr??kt">Construct</phoneme>'
        elif combined_sentences_token_list[i][0] == "construct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nstr??kt">construct</phoneme>'
    return combined_sentences_word_list

def consummate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Consummate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??ns????me??t">Consummate</phoneme>'
        elif combined_sentences_token_list[i][0] == "consummate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??ns????me??t">consummate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Consummate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??s??m??t">Consummate</phoneme>'
        elif combined_sentences_token_list[i][0] == "consummate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??s??m??t">consummate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Consummate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??ns????me??t">Consummate</phoneme>'
        elif combined_sentences_token_list[i][0] == "consummate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??ns????me??t">consummate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Consummate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??s??m??t">Consummate</phoneme>'
        elif combined_sentences_token_list[i][0] == "consummate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??s??m??t">consummate</phoneme>'
    return combined_sentences_word_list

#As there are several different ways to pronounce the distinct nouns "content", only the adjective and verb are included
def content(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Content" and combined_sentences_token_list[i][1][:2] in ["JJ", "VB"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??t??nt">Content</phoneme>'
        elif combined_sentences_token_list[i][0] == "content" and combined_sentences_token_list[i][1][:2] in ["JJ", "VB"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??t??nt">content</phoneme>'
    return combined_sentences_word_list

def contest(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Contest" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??t??st">Contest</phoneme>'
        elif combined_sentences_token_list[i][0] == "contest" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??t??st">contest</phoneme>'
        elif combined_sentences_token_list[i][0] == "Contest" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??n??t??st">Contest</phoneme>'
        elif combined_sentences_token_list[i][0] == "contest" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??n??t??st">contest</phoneme>'

        elif combined_sentences_token_list[i][0] == "Contest" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??t??st">Contest</phoneme>'
        elif combined_sentences_token_list[i][0] == "contest" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??t??st">contest</phoneme>'
        elif combined_sentences_token_list[i][0] == "Contest" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nt??st">Contest</phoneme>'
        elif combined_sentences_token_list[i][0] == "contest" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nt??st">contest</phoneme>'
    return combined_sentences_word_list

#In American English, different versions of the verb "contract" have distinct pronounciations, while that is not the case in British English.
#Consequently, only the noun and adjective are included for American English.
def contract(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Contract" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??ntr??kt">Contract</phoneme>'
        elif combined_sentences_token_list[i][0] == "contract" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??ntr??kt">contract</phoneme>'

        elif combined_sentences_token_list[i][0] == "Contract" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??tr??kt">Contract</phoneme>'
        elif combined_sentences_token_list[i][0] == "contract" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??tr??kt">contract</phoneme>'
        elif combined_sentences_token_list[i][0] == "Contract" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??ntr??kt">Contract</phoneme>'
        elif combined_sentences_token_list[i][0] == "contract" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??ntr??kt">contract</phoneme>'
    return combined_sentences_word_list

def contrast(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Contrast" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??tr??st">Contrast</phoneme>'
        elif combined_sentences_token_list[i][0] == "contrast" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??tr??st">contrast</phoneme>'
        elif combined_sentences_token_list[i][0] == "Contrast" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??n??tr??st">Contrast</phoneme>'
        elif combined_sentences_token_list[i][0] == "contrast" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??n??tr??st">contrast</phoneme>'

        elif combined_sentences_token_list[i][0] == "Contrast" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??tr????st">Contrast</phoneme>'
        elif combined_sentences_token_list[i][0] == "contrast" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??tr????st">contrast</phoneme>'
        elif combined_sentences_token_list[i][0] == "Contrast" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??ntr????st">Contrast</phoneme>'
        elif combined_sentences_token_list[i][0] == "contrast" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??ntr????st">contrast</phoneme>'
    return combined_sentences_word_list

def converse(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Converse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??v??rs">Converse</phoneme>'
        elif combined_sentences_token_list[i][0] == "converse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??v??rs">converse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Converse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??n??v??rs">Converse</phoneme>'
        elif combined_sentences_token_list[i][0] == "converse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??n??v??rs">converse</phoneme>'

        elif combined_sentences_token_list[i][0] == "Converse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??v????s">Converse</phoneme>'
        elif combined_sentences_token_list[i][0] == "converse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??v????s">converse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Converse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nv????s">Converse</phoneme>'
        elif combined_sentences_token_list[i][0] == "converse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nv????s">converse</phoneme>'
    return combined_sentences_word_list

def convert(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Convert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??v??rt">Convert</phoneme>'
        elif combined_sentences_token_list[i][0] == "convert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??v??rt">convert</phoneme>'
        elif combined_sentences_token_list[i][0] == "Convert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??n??v??rt">Convert</phoneme>'
        elif combined_sentences_token_list[i][0] == "convert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??n??v??rt">convert</phoneme>'

        elif combined_sentences_token_list[i][0] == "Convert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??v????t">Convert</phoneme>'
        elif combined_sentences_token_list[i][0] == "convert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??v????t">convert</phoneme>'
        elif combined_sentences_token_list[i][0] == "Convert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nv????t">Convert</phoneme>'
        elif combined_sentences_token_list[i][0] == "convert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nv????t">convert</phoneme>'
    return combined_sentences_word_list

def convict(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Convict" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??n??v??kt">Convict</phoneme>'
        elif combined_sentences_token_list[i][0] == "convict" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??n??v??kt">convict</phoneme>'
        elif combined_sentences_token_list[i][0] == "Convict" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["VB", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??v??kt">Convict</phoneme>'
        elif combined_sentences_token_list[i][0] == "convict" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["VB", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??v??kt">convict</phoneme>'

        elif combined_sentences_token_list[i][0] == "Convict" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nv??kt">Convict</phoneme>'
        elif combined_sentences_token_list[i][0] == "convict" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??nv??kt">convict</phoneme>'
        elif combined_sentences_token_list[i][0] == "Convict" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["VB", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??v??kt">Convict</phoneme>'
        elif combined_sentences_token_list[i][0] == "convict" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["VB", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??n??v??kt">convict</phoneme>'
    return combined_sentences_word_list

def coordinate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Coordinate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ko??????rd??n??e??t">Coordinate</phoneme>'
        elif combined_sentences_token_list[i][0] == "coordinate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ko??????rd??n??e??t">coordinate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Coordinate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ko??????rd??n??t">Coordinate</phoneme>'
        elif combined_sentences_token_list[i][0] == "coordinate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ko??????rd??n??t">coordinate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Coordinate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??????????d????ne??t">Coordinate</phoneme>'
        elif combined_sentences_token_list[i][0] == "coordinate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??????????d????ne??t">coordinate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Coordinate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??????????d??n??t">Coordinate</phoneme>'
        elif combined_sentences_token_list[i][0] == "coordinate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="k??????????d??n??t">coordinate</phoneme>'
    return combined_sentences_word_list

#As distinct adjectives "crooked" are pronounced differently in American English, the adjectives are only included for British English
def crooked(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Crooked" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??kr??kt">Crooked</phoneme>'
        elif combined_sentences_token_list[i][0] == "crooked" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??kr??kt">crooked</phoneme>'
        elif combined_sentences_token_list[i][0] == "Crooked" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kr??k??d">Crooked</phoneme>'
        elif combined_sentences_token_list[i][0] == "crooked" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kr??k??d">crooked</phoneme>'
    return combined_sentences_word_list

def decrease(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Decrease" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????kris">Decrease</phoneme>'
        elif combined_sentences_token_list[i][0] == "decrease" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????kris">decrease</phoneme>'
        elif combined_sentences_token_list[i][0] == "Decrease" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??di??kris">Decrease</phoneme>'
        elif combined_sentences_token_list[i][0] == "decrease" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??di??kris">decrease</phoneme>'

        elif combined_sentences_token_list[i][0] == "Decrease" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????kri??s">Decrease</phoneme>'
        elif combined_sentences_token_list[i][0] == "decrease" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????kri??s">decrease</phoneme>'
        elif combined_sentences_token_list[i][0] == "Decrease" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??di??kri??s">Decrease</phoneme>'
        elif combined_sentences_token_list[i][0] == "decrease" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??di??kri??s">decrease</phoneme>'
    return combined_sentences_word_list

def defect(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Defect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????f??kt">Defect</phoneme>'
        elif combined_sentences_token_list[i][0] == "defect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????f??kt">defect</phoneme>'
        elif combined_sentences_token_list[i][0] == "Defect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??di??f??kt">Defect</phoneme>'
        elif combined_sentences_token_list[i][0] == "defect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??di??f??kt">defect</phoneme>'

        elif combined_sentences_token_list[i][0] == "Defect" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????f??kt">Defect</phoneme>'
        elif combined_sentences_token_list[i][0] == "defect" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????f??kt">defect</phoneme>'
        elif combined_sentences_token_list[i][0] == "Defect" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??di??f??kt">Defect</phoneme>'
        elif combined_sentences_token_list[i][0] == "defect" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??di??f??kt">defect</phoneme>'
    return combined_sentences_word_list

def degenerate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Degenerate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="di??d????n??r??e??t">Degenerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "degenerate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="di??d????n??r??e??t">degenerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Degenerate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="di??d????n??r??t">Degenerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "degenerate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="di??d????n??r??t">degenerate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Degenerate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????d????n????re??t">Degenerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "degenerate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????d????n????re??t">degenerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Degenerate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????d????n??r??t">Degenerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "degenerate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????d????n??r??t">degenerate</phoneme>'
    return combined_sentences_word_list

#Only for American English, as the noun and verb are pronounced the same in British English.
def delegate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Delegate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??l????ge??t">Delegate</phoneme>'
        elif combined_sentences_token_list[i][0] == "delegate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??l????ge??t">delegate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Delegate" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??l??g??t">Delegate</phoneme>'
        elif combined_sentences_token_list[i][0] == "delegate" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??l??g??t">delegate</phoneme>'
    return combined_sentences_word_list

def deliberate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Deliberate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????l??b??r??e??t">Deliberate</phoneme>'
        elif combined_sentences_token_list[i][0] == "deliberate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????l??b??r??e??t">deliberate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Deliberate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????l??b??r??t">Deliberate</phoneme>'
        elif combined_sentences_token_list[i][0] == "deliberate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????l??b??r??t">deliberate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Deliberate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????l??b????re??t">Deliberate</phoneme>'
        elif combined_sentences_token_list[i][0] == "deliberate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????l??b????re??t">deliberate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Deliberate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????l??b??r??t">Deliberate</phoneme>'
        elif combined_sentences_token_list[i][0] == "deliberate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????l??b??r??t">deliberate</phoneme>'
    return combined_sentences_word_list

def derogate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Derogate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??der??????eit">Derogate</phoneme>'
        elif combined_sentences_token_list[i][0] == "derogate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??der??????eit">derogate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Derogate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??der??????t">Derogate</phoneme>'
        elif combined_sentences_token_list[i][0] == "derogate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??der??????t">derogate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Derogate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??r??????e??t">Derogate</phoneme>'
        elif combined_sentences_token_list[i][0] == "derogate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??r??????e??t">derogate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Derogate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??r??????t">Derogate</phoneme>'
        elif combined_sentences_token_list[i][0] == "derogate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??r??????t">derogate</phoneme>'
    return combined_sentences_word_list

def desert(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Desert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????z??rt">Desert</phoneme>'
        elif combined_sentences_token_list[i][0] == "desert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????z??rt">desert</phoneme>'
        elif combined_sentences_token_list[i][0] == "Desert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??z??rt">Desert</phoneme>'
        elif combined_sentences_token_list[i][0] == "desert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??z??rt">desert</phoneme>'

        elif combined_sentences_token_list[i][0] == "Desert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????z????t">Desert</phoneme>'
        elif combined_sentences_token_list[i][0] == "desert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????z????t">desert</phoneme>'
        elif combined_sentences_token_list[i][0] == "Desert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??z??t">Desert</phoneme>'
        elif combined_sentences_token_list[i][0] == "desert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??z??t">desert</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def desolate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Desolate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??s????le??t">Desolate</phoneme>'
        elif combined_sentences_token_list[i][0] == "desolate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??s????le??t">desolate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Desolate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??s??l??t">Desolate</phoneme>'
        elif combined_sentences_token_list[i][0] == "desolate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??s??l??t">desolate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Desolate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??s????le??t">Desolate</phoneme>'
        elif combined_sentences_token_list[i][0] == "desolate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??s????le??t">desolate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Desolate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??s??l??t">Desolate</phoneme>'
        elif combined_sentences_token_list[i][0] == "desolate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??s??l??t">desolate</phoneme>'
    return combined_sentences_word_list

def deviate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Deviate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??divi??e??t">Deviate</phoneme>'
        elif combined_sentences_token_list[i][0] == "deviate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??divi??e??t">deviate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Deviate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="divi??t">Deviate</phoneme>'
        elif combined_sentences_token_list[i][0] == "deviate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="divi??t">deviate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Deviate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??di??v????e??t">Deviate</phoneme>'
        elif combined_sentences_token_list[i][0] == "deviate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??di??v????e??t">deviate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Deviate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??di??v????t">Deviate</phoneme>'
        elif combined_sentences_token_list[i][0] == "deviate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??di??v????t">deviate</phoneme>'
    return combined_sentences_word_list

def diagnoses(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Diagnoses" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="da????????n????siz">Diagnoses</phoneme>'
        elif combined_sentences_token_list[i][0] == "diagnoses" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="da????????n????siz">diagnoses</phoneme>'
        elif combined_sentences_token_list[i][0] == "Diagnoses" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="da????????n????s??z">Diagnoses</phoneme>'
        elif combined_sentences_token_list[i][0] == "diagnoses" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="da????????n????s??z">diagnoses</phoneme>'
    return combined_sentences_word_list

def diffuse(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Diffuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????fjuz">Diffuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "diffuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????fjuz">diffuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Diffuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????fjus">Diffuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "diffuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????fjus">diffuse</phoneme>'

        elif combined_sentences_token_list[i][0] == "Diffuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????fju??z">Diffuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "diffuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????fju??z">diffuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Diffuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????fju??s">Diffuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "diffuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????fju??s">diffuse</phoneme>'
    return combined_sentences_word_list

def digest(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Digest" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????d????st">Digest</phoneme>'
        elif combined_sentences_token_list[i][0] == "digest" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????d????st">digest</phoneme>'
        elif combined_sentences_token_list[i][0] == "Digest" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??da????d????st">Digest</phoneme>'
        elif combined_sentences_token_list[i][0] == "digest" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??da????d????st">digest</phoneme>'

        elif combined_sentences_token_list[i][0] == "Digest" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????d????st">Digest</phoneme>'
        elif combined_sentences_token_list[i][0] == "digest" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????d????st">digest</phoneme>'
        elif combined_sentences_token_list[i][0] == "Digest" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????d????st">Digest</phoneme>'
        elif combined_sentences_token_list[i][0] == "digest" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????d????st">digest</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def dingy(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Dingy" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d????i">Dingy</phoneme>'
        elif combined_sentences_token_list[i][0] == "dingy" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d????i">dingy</phoneme>'
        elif combined_sentences_token_list[i][0] == "Dingy" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??nd??i">Dingy</phoneme>'
        elif combined_sentences_token_list[i][0] == "dingy" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??nd??i">dingy</phoneme>'

        elif combined_sentences_token_list[i][0] == "Dingy" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??????">Dingy</phoneme>'
        elif combined_sentences_token_list[i][0] == "dingy" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??????">dingy</phoneme>'
        elif combined_sentences_token_list[i][0] == "Dingy" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??nd????">Dingy</phoneme>'
        elif combined_sentences_token_list[i][0] == "dingy" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??nd????">dingy</phoneme>'
    return combined_sentences_word_list

def discard(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Discard" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d??s??k??rd">Discard</phoneme>'
        elif combined_sentences_token_list[i][0] == "discard" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d??s??k??rd">discard</phoneme>'
        elif combined_sentences_token_list[i][0] == "Discard" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??s??k??rd">Discard</phoneme>'
        elif combined_sentences_token_list[i][0] == "discard" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??s??k??rd">discard</phoneme>'

        elif combined_sentences_token_list[i][0] == "Discard" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d??s??k????d">Discard</phoneme>'
        elif combined_sentences_token_list[i][0] == "discard" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d??s??k????d">discard</phoneme>'
        elif combined_sentences_token_list[i][0] == "Discard" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??sk????d">Discard</phoneme>'
        elif combined_sentences_token_list[i][0] == "discard" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??sk????d">discard</phoneme>'
    return combined_sentences_word_list

def discharge(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Discharge" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d??s??t????rd??">Discharge</phoneme>'
        elif combined_sentences_token_list[i][0] == "discharge" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d??s??t????rd??">discharge</phoneme>'
        elif combined_sentences_token_list[i][0] == "Discharge" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??s??t????rd??">Discharge</phoneme>'
        elif combined_sentences_token_list[i][0] == "discharge" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??s??t????rd??">discharge</phoneme>'

        elif combined_sentences_token_list[i][0] == "Discharge" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d??s??t??????d??">Discharge</phoneme>'
        elif combined_sentences_token_list[i][0] == "discharge" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d??s??t??????d??">discharge</phoneme>'
        elif combined_sentences_token_list[i][0] == "Discharge" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??st??????d??">Discharge</phoneme>'
        elif combined_sentences_token_list[i][0] == "discharge" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??st??????d??">discharge</phoneme>'
    return combined_sentences_word_list

def discord(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Discord" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d??s??k??rd">Discord</phoneme>'
        elif combined_sentences_token_list[i][0] == "discord" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d??s??k??rd">discord</phoneme>'
        elif combined_sentences_token_list[i][0] == "Discord" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??s??k??rd">Discord</phoneme>'
        elif combined_sentences_token_list[i][0] == "discord" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??s??k??rd">discord</phoneme>'

        elif combined_sentences_token_list[i][0] == "Discord" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d??s??k????d">Discord</phoneme>'
        elif combined_sentences_token_list[i][0] == "discord" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d??s??k????d">discord</phoneme>'
        elif combined_sentences_token_list[i][0] == "Discord" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??sk????d">Discord</phoneme>'
        elif combined_sentences_token_list[i][0] == "discord" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??sk????d">discord</phoneme>'
    return combined_sentences_word_list

def discount(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Discount" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d??s??ka??nt">Discount</phoneme>'
        elif combined_sentences_token_list[i][0] == "discount" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d??s??ka??nt">discount</phoneme>'
        elif combined_sentences_token_list[i][0] == "Discount" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??s??ka??nt">Discount</phoneme>'
        elif combined_sentences_token_list[i][0] == "discount" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??s??ka??nt">discount</phoneme>'

        elif combined_sentences_token_list[i][0] == "Discount" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d??s??ka??nt">Discount</phoneme>'
        elif combined_sentences_token_list[i][0] == "discount" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d??s??ka??nt">discount</phoneme>'
        elif combined_sentences_token_list[i][0] == "Discount" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d??s??ka??nt">Discount</phoneme>'
        elif combined_sentences_token_list[i][0] == "discount" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d??s??ka??nt">discount</phoneme>'
    return combined_sentences_word_list

#As the nound "do" can refer to the musical note or the short form of hairdo, only the verb was included. Also, as Spacy tokenizes "don't" as "do" and "n't",
#the phonemes are only substituted if the next element in the "combined_sentences_token_list" list isn't "n't".
def do(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Do" and English_Phonetics == "American_English" and combined_sentences_token_list[i+1][0] != "n???t" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="du">Do</phoneme>'
        elif combined_sentences_token_list[i][0] == "do" and English_Phonetics == "American_English" and combined_sentences_token_list[i+1][0] != "n???t" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="du">do</phoneme>'

        elif combined_sentences_token_list[i][0] == "Do" and English_Phonetics == "British_English" and combined_sentences_token_list[i+1][0] != "n???t" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="du??">Do</phoneme>'
        elif combined_sentences_token_list[i][0] == "do" and English_Phonetics == "British_English" and combined_sentences_token_list[i+1][0] != "n???t" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="du??">do</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately (it seems to always give the verb).
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def does(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Does" and combined_sentences_token_list[i][1][:2] == "VB" and combined_sentences_token_list[i+1][0] != "n???t" :
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??z??">Does</phoneme>'
        elif combined_sentences_token_list[i][0] == "does" and combined_sentences_token_list[i][1][:2] == "VB" and combined_sentences_token_list[i+1][0] != "n???t" :
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??z??">does</phoneme>'
        elif combined_sentences_token_list[i][0] == "Does" and combined_sentences_token_list[i][1][:2] == "NN" and combined_sentences_token_list[i+1][0] != "n???t":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??do??z">Does</phoneme>'
        elif combined_sentences_token_list[i][0] == "does" and combined_sentences_token_list[i][1][:2] == "NN" and combined_sentences_token_list[i+1][0] != "n???t":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??do??z">does</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def dogged(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Dogged" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??gd">Dogged</phoneme>'
        elif combined_sentences_token_list[i][0] == "dogged" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??gd">dogged</phoneme>'
        elif combined_sentences_token_list[i][0] == "Dogged" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??g??d">Dogged</phoneme>'
        elif combined_sentences_token_list[i][0] == "dogged" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??g??d">dogged</phoneme>'

        elif combined_sentences_token_list[i][0] == "Dogged" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d????d">Dogged</phoneme>'
        elif combined_sentences_token_list[i][0] == "dogged" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d????d">dogged</phoneme>'
        elif combined_sentences_token_list[i][0] == "Dogged" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??????d">Dogged</phoneme>'
        elif combined_sentences_token_list[i][0] == "dogged" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d??????d">dogged</phoneme>'
    return combined_sentences_word_list

def dove(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Dove" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="do??v">Dove</phoneme>'
        elif combined_sentences_token_list[i][0] == "dove" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="do??v">dove</phoneme>'
        elif combined_sentences_token_list[i][0] == "Dove" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d??v">Dove</phoneme>'
        elif combined_sentences_token_list[i][0] == "dove" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d??v">dove</phoneme>'

        elif combined_sentences_token_list[i][0] == "Dove" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????v">Dove</phoneme>'
        elif combined_sentences_token_list[i][0] == "dove" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d????v">dove</phoneme>'
        elif combined_sentences_token_list[i][0] == "Dove" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d??v">Dove</phoneme>'
        elif combined_sentences_token_list[i][0] == "dove" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="d??v">dove</phoneme>'
    return combined_sentences_word_list

def duplicate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Duplicate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??dupl????ke??t">Duplicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "duplicate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??dupl????ke??t">duplicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Duplicate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??djupl??k??t">Duplicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "duplicate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??djupl??k??t">duplicate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Duplicate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??dju??pl????ke??t">Duplicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "duplicate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??dju??pl????ke??t">duplicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Duplicate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??dju??pl??k??t">Duplicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "duplicate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??dju??pl??k??t">duplicate</phoneme>'
    return combined_sentences_word_list

def egress(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Egress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????res">Egress</phoneme>'
        elif combined_sentences_token_list[i][0] == "egress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????res">egress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Egress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??i??res">Egress</phoneme>'
        elif combined_sentences_token_list[i][0] == "egress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??i??res">egress</phoneme>'

        elif combined_sentences_token_list[i][0] == "Egress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????r??s">Egress</phoneme>'
        elif combined_sentences_token_list[i][0] == "egress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????r??s">egress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Egress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??i????r??s">Egress</phoneme>'
        elif combined_sentences_token_list[i][0] == "egress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??i????r??s">egress</phoneme>'
    return combined_sentences_word_list

def ejaculate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Ejaculate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d????kj????leit">Ejaculate</phoneme>'
        elif combined_sentences_token_list[i][0] == "ejaculate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d????kj????leit">ejaculate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Ejaculate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d????kj??l??t">Ejaculate</phoneme>'
        elif combined_sentences_token_list[i][0] == "ejaculate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d????kj??l??t">ejaculate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Ejaculate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d????kj????le??t">Ejaculate</phoneme>'
        elif combined_sentences_token_list[i][0] == "ejaculate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d????kj????le??t">ejaculate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Ejaculate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d????kj??l??t">Ejaculate</phoneme>'
        elif combined_sentences_token_list[i][0] == "ejaculate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????d????kj??l??t">ejaculate</phoneme>'
    return combined_sentences_word_list

def elaborate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Elaborate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????l??b????re??t">Elaborate</phoneme>'
        elif combined_sentences_token_list[i][0] == "elaborate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????l??b????re??t">elaborate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Elaborate" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????l??b??r??t">Elaborate</phoneme>'
        elif combined_sentences_token_list[i][0] == "elaborate" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????l??b??r??t">elaborate</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def ellipses(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Ellipses" and combined_sentences_token_list[i][3].lower() == "ellipse":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????l??ps??z">Ellipses</phoneme>'
        elif combined_sentences_token_list[i][0] == "ellipses" and combined_sentences_token_list[i][3].lower() == "ellipse":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????l??ps??z">ellipses</phoneme>'
        elif combined_sentences_token_list[i][0] == "Ellipses" and combined_sentences_token_list[i][3].lower() == "ellipsis":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????l??psi??z">Ellipses</phoneme>'
        elif combined_sentences_token_list[i][0] == "ellipses" and combined_sentences_token_list[i][3].lower() == "ellipsis":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????l??psi??z">ellipses</phoneme>'
    return combined_sentences_word_list

def entrance(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Entrance" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??tr??ns">Entrance</phoneme>'
        elif combined_sentences_token_list[i][0] == "entrance" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??tr??ns">entrance</phoneme>'
        elif combined_sentences_token_list[i][0] == "Entrance" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????ntr??ns">Entrance</phoneme>'
        elif combined_sentences_token_list[i][0] == "entrance" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????ntr??ns">entrance</phoneme>'

        elif combined_sentences_token_list[i][0] == "Entrance" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??tr????ns">Entrance</phoneme>'
        elif combined_sentences_token_list[i][0] == "entrance" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??tr????ns">entrance</phoneme>'
        elif combined_sentences_token_list[i][0] == "Entrance" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????ntr??ns">Entrance</phoneme>'
        elif combined_sentences_token_list[i][0] == "entrance" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????ntr??ns">entrance</phoneme>'
    return combined_sentences_word_list

def envelop(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Envelop" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="en??vel??p">Envelop</phoneme>'
        elif combined_sentences_token_list[i][0] == "envelop" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="en??vel??p">envelop</phoneme>'
        elif combined_sentences_token_list[i][0] == "Envelop" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??env??l??p">Envelop</phoneme>'
        elif combined_sentences_token_list[i][0] == "envelop" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??env??l??p">envelop</phoneme>'

        elif combined_sentences_token_list[i][0] == "Envelop" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??v??l??p">Envelop</phoneme>'
        elif combined_sentences_token_list[i][0] == "envelop" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??v??l??p">envelop</phoneme>'
        elif combined_sentences_token_list[i][0] == "Envelop" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nv??l??p">Envelop</phoneme>'
        elif combined_sentences_token_list[i][0] == "envelop" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nv??l??p">envelop</phoneme>'
    return combined_sentences_word_list

def escort(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Escort" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="i??sk??rt">Escort</phoneme>'
        elif combined_sentences_token_list[i][0] == "escort" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="i??sk??rt">escort</phoneme>'
        elif combined_sentences_token_list[i][0] == "Escort" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??esk??rt">Escort</phoneme>'
        elif combined_sentences_token_list[i][0] == "escort" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??esk??rt">escort</phoneme>'

        elif combined_sentences_token_list[i][0] == "Escort" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??k????t">Escort</phoneme>'
        elif combined_sentences_token_list[i][0] == "escort" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??k????t">escort</phoneme>'
        elif combined_sentences_token_list[i][0] == "Escort" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????sk????t">Escort</phoneme>'
        elif combined_sentences_token_list[i][0] == "escort" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????sk????t">escort</phoneme>'
    return combined_sentences_word_list

def essay(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Essay" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????se??">Essay</phoneme>'
        elif combined_sentences_token_list[i][0] == "essay" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????se??">essay</phoneme>'
        elif combined_sentences_token_list[i][0] == "Essay" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????se??">Essay</phoneme>'
        elif combined_sentences_token_list[i][0] == "essay" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????se??">essay</phoneme>'
    return combined_sentences_word_list

def estimate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Estimate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????st????me??t">Estimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "estimate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????st????me??t">estimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Estimate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????st??m??t">Estimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "estimate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????st??m??t">estimate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Estimate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????st????me??t">Estimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "estimate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????st????me??t">estimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Estimate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????st??m??t">Estimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "estimate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????st??m??t">estimate</phoneme>'
    return combined_sentences_word_list

#Only for Brisith English, as the noun and verb are pronounced the same in American English.
def excise(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Excise" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??sa??z">Excise</phoneme>'
        elif combined_sentences_token_list[i][0] == "excise" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??sa??z">excise</phoneme>'
        elif combined_sentences_token_list[i][0] == "Excise" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????ksa??z">Excise</phoneme>'
        elif combined_sentences_token_list[i][0] == "excise" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????ksa??z">excise</phoneme>'
    return combined_sentences_word_list

def excuse(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Excuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??skjuz">Excuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "excuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??skjuz">excuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Excuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??skjus">Excuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "excuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??skjus">excuse</phoneme>'

        elif combined_sentences_token_list[i][0] == "Excuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??skju??z">Excuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "excuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??skju??z">excuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Excuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??skju??s">Excuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "excuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??skju??s">excuse</phoneme>'
    return combined_sentences_word_list

def exploit(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Exploit" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??spl????t">Exploit</phoneme>'
        elif combined_sentences_token_list[i][0] == "exploit" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??spl????t">exploit</phoneme>'
        elif combined_sentences_token_list[i][0] == "Exploit" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????ks??pl????t">Exploit</phoneme>'
        elif combined_sentences_token_list[i][0] == "exploit" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????ks??pl????t">exploit</phoneme>'

        elif combined_sentences_token_list[i][0] == "Exploit" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??spl????t">Exploit</phoneme>'
        elif combined_sentences_token_list[i][0] == "exploit" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??spl????t">exploit</phoneme>'
        elif combined_sentences_token_list[i][0] == "Exploit" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????kspl????t">Exploit</phoneme>'
        elif combined_sentences_token_list[i][0] == "exploit" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????kspl????t">exploit</phoneme>'
    return combined_sentences_word_list

def extract(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Extract" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??str??kt">Extract</phoneme>'
        elif combined_sentences_token_list[i][0] == "extract" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??str??kt">extract</phoneme>'
        elif combined_sentences_token_list[i][0] == "Extract" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????ks??tr??kt">Extract</phoneme>'
        elif combined_sentences_token_list[i][0] == "extract" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????ks??tr??kt">extract</phoneme>'

        elif combined_sentences_token_list[i][0] == "Extract" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??str??kt">Extract</phoneme>'
        elif combined_sentences_token_list[i][0] == "extract" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??k??str??kt">extract</phoneme>'
        elif combined_sentences_token_list[i][0] == "Extract" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????kstr??kt">Extract</phoneme>'
        elif combined_sentences_token_list[i][0] == "extract" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????kstr??kt">extract</phoneme>'
    return combined_sentences_word_list

def ferment(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Ferment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="f??r??m??nt">Ferment</phoneme>'
        elif combined_sentences_token_list[i][0] == "ferment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="f??r??m??nt">ferment</phoneme>'
        elif combined_sentences_token_list[i][0] == "Ferment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??f??r??m??nt">Ferment</phoneme>'
        elif combined_sentences_token_list[i][0] == "ferment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??f??r??m??nt">ferment</phoneme>'

        elif combined_sentences_token_list[i][0] == "Ferment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="f????m??nt">Ferment</phoneme>'
        elif combined_sentences_token_list[i][0] == "ferment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="f????m??nt">ferment</phoneme>'
        elif combined_sentences_token_list[i][0] == "Ferment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??f????m??nt">Ferment</phoneme>'
        elif combined_sentences_token_list[i][0] == "ferment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??f????m??nt">ferment</phoneme>'
    return combined_sentences_word_list

def frequent(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Frequent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="fri??kw??nt">Frequent</phoneme>'
        elif combined_sentences_token_list[i][0] == "frequent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="fri??kw??nt">frequent</phoneme>'
        elif combined_sentences_token_list[i][0] == "Frequent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??frikw??nt">Frequent</phoneme>'
        elif combined_sentences_token_list[i][0] == "frequent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??frikw??nt">frequent</phoneme>'

        elif combined_sentences_token_list[i][0] == "Frequent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="fr????kw??nt">Frequent</phoneme>'
        elif combined_sentences_token_list[i][0] == "frequent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="fr????kw??nt">frequent</phoneme>'
        elif combined_sentences_token_list[i][0] == "Frequent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??fri??kw??nt">Frequent</phoneme>'
        elif combined_sentences_token_list[i][0] == "frequent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??fri??kw??nt">frequent</phoneme>'
    return combined_sentences_word_list

def graduate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Graduate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??gr??d??u??e??t">Graduate</phoneme>'
        elif combined_sentences_token_list[i][0] == "graduate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??gr??d??u??e??t">graduate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Graduate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??gr??d??u??t">Graduate</phoneme>'
        elif combined_sentences_token_list[i][0] == "graduate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??gr??d??u??t">graduate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Graduate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????r??dj????e??t">Graduate</phoneme>'
        elif combined_sentences_token_list[i][0] == "graduate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????r??dj????e??t">graduate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Graduate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????r??dj????t">Graduate</phoneme>'
        elif combined_sentences_token_list[i][0] == "graduate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????r??dj????t">graduate</phoneme>'
    return combined_sentences_word_list

def hinder(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Hinder" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??h??nd??r">Hinder</phoneme>'
        elif combined_sentences_token_list[i][0] == "hinder" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??h??nd??r">hinder</phoneme>'
        elif combined_sentences_token_list[i][0] == "Hinder" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ha??nd??r">Hinder</phoneme>'
        elif combined_sentences_token_list[i][0] == "hinder" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ha??nd??r">hinder</phoneme>'

        elif combined_sentences_token_list[i][0] == "Hinder" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??h??nd??">Hinder</phoneme>'
        elif combined_sentences_token_list[i][0] == "hinder" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??h??nd??">hinder</phoneme>'
        elif combined_sentences_token_list[i][0] == "Hinder" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ha??nd??">Hinder</phoneme>'
        elif combined_sentences_token_list[i][0] == "hinder" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ha??nd??">hinder</phoneme>'
    return combined_sentences_word_list

def house(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "House" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ha??z">House</phoneme>'
        elif combined_sentences_token_list[i][0] == "house" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ha??z">house</phoneme>'
        elif combined_sentences_token_list[i][0] == "House" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ha??s">House</phoneme>'
        elif combined_sentences_token_list[i][0] == "house" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ha??s">house</phoneme>'
    return combined_sentences_word_list

def implant(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Implant" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??pl??nt">Implant</phoneme>'
        elif combined_sentences_token_list[i][0] == "implant" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??pl??nt">implant</phoneme>'
        elif combined_sentences_token_list[i][0] == "Implant" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????m??pl??nt">Implant</phoneme>'
        elif combined_sentences_token_list[i][0] == "implant" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????m??pl??nt">implant</phoneme>'

        elif combined_sentences_token_list[i][0] == "Implant" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??pl????nt">Implant</phoneme>'
        elif combined_sentences_token_list[i][0] == "implant" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??pl????nt">implant</phoneme>'
        elif combined_sentences_token_list[i][0] == "Implant" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????m??pl????nt">Implant</phoneme>'
        elif combined_sentences_token_list[i][0] == "implant" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????m??pl????nt">implant</phoneme>'
    return combined_sentences_word_list

def import_heteronym(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Import" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??p??rt">Import</phoneme>'
        elif combined_sentences_token_list[i][0] == "import" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??p??rt">import</phoneme>'
        elif combined_sentences_token_list[i][0] == "Import" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????m??p??rt">Import</phoneme>'
        elif combined_sentences_token_list[i][0] == "import" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????m??p??rt">import</phoneme>'

        elif combined_sentences_token_list[i][0] == "Import" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??p????t">Import</phoneme>'
        elif combined_sentences_token_list[i][0] == "import" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??p????t">import</phoneme>'
        elif combined_sentences_token_list[i][0] == "Import" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????mp????t">Import</phoneme>'
        elif combined_sentences_token_list[i][0] == "import" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????mp????t">import</phoneme>'
    return combined_sentences_word_list

def impress(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Impress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??pr??s">Impress</phoneme>'
        elif combined_sentences_token_list[i][0] == "impress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??pr??s">impress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Impress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????m??pr??s">Impress</phoneme>'
        elif combined_sentences_token_list[i][0] == "impress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????m??pr??s">impress</phoneme>'

        elif combined_sentences_token_list[i][0] == "Impress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??pr??s">Impress</phoneme>'
        elif combined_sentences_token_list[i][0] == "impress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??pr??s">impress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Impress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????mpr??s">Impress</phoneme>'
        elif combined_sentences_token_list[i][0] == "impress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????mpr??s">impress</phoneme>'
    return combined_sentences_word_list

def imprint(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Imprint" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??pr??nt">Imprint</phoneme>'
        elif combined_sentences_token_list[i][0] == "imprint" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??pr??nt">imprint</phoneme>'
        elif combined_sentences_token_list[i][0] == "Imprint" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????m??pr??nt">Imprint</phoneme>'
        elif combined_sentences_token_list[i][0] == "imprint" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????m??pr??nt">imprint</phoneme>'

        elif combined_sentences_token_list[i][0] == "Imprint" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??pr??nt">Imprint</phoneme>'
        elif combined_sentences_token_list[i][0] == "imprint" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??pr??nt">imprint</phoneme>'
        elif combined_sentences_token_list[i][0] == "Imprint" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????mpr??nt">Imprint</phoneme>'
        elif combined_sentences_token_list[i][0] == "imprint" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????mpr??nt">imprint</phoneme>'
    return combined_sentences_word_list

#As distict transitive "incense" verb forms are pronounced differently, only the noun is included.
#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def incense(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Incense" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??s??ns">Incense</phoneme>'
        elif combined_sentences_token_list[i][0] == "incense" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??s??ns">incense</phoneme>'

        elif combined_sentences_token_list[i][0] == "Incense" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????ns??ns">Incense</phoneme>'
        elif combined_sentences_token_list[i][0] == "incense" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????ns??ns">incense</phoneme>'
    return combined_sentences_word_list

def incline(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Incline" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??kla??n">Incline</phoneme>'
        elif combined_sentences_token_list[i][0] == "incline" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??kla??n">incline</phoneme>'
        elif combined_sentences_token_list[i][0] == "Incline" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??kla??n">Incline</phoneme>'
        elif combined_sentences_token_list[i][0] == "incline" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??kla??n">incline</phoneme>'

        elif combined_sentences_token_list[i][0] == "Incline" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??kla??n">Incline</phoneme>'
        elif combined_sentences_token_list[i][0] == "incline" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??kla??n">incline</phoneme>'
        elif combined_sentences_token_list[i][0] == "Incline" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nkla??n">Incline</phoneme>'
        elif combined_sentences_token_list[i][0] == "incline" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nkla??n">incline</phoneme>'
    return combined_sentences_word_list

def incorporate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Incorporate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??k??rp????re??t">Incorporate</phoneme>'
        elif combined_sentences_token_list[i][0] == "incorporate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??k??rp????re??t">incorporate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Incorporate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??k??rp??r??t">Incorporate</phoneme>'
        elif combined_sentences_token_list[i][0] == "incorporate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??k??rp??r??t">incorporate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Incorporate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??k????p????re??t">Incorporate</phoneme>'
        elif combined_sentences_token_list[i][0] == "incorporate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??k????p????re??t">incorporate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Incorporate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??k????p??r??t">Incorporate</phoneme>'
        elif combined_sentences_token_list[i][0] == "incorporate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??k????p??r??t">incorporate</phoneme>'
    return combined_sentences_word_list

def increase(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Increase" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??kris">Increase</phoneme>'
        elif combined_sentences_token_list[i][0] == "increase" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??kris">increase</phoneme>'
        elif combined_sentences_token_list[i][0] == "Increase" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nkris">Increase</phoneme>'
        elif combined_sentences_token_list[i][0] == "increase" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nkris">increase</phoneme>'

        elif combined_sentences_token_list[i][0] == "Increase" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??kri??s">Increase</phoneme>'
        elif combined_sentences_token_list[i][0] == "increase" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??kri??s">increase</phoneme>'
        elif combined_sentences_token_list[i][0] == "Increase" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nkri??s">Increase</phoneme>'
        elif combined_sentences_token_list[i][0] == "increase" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nkri??s">increase</phoneme>'
    return combined_sentences_word_list

def indent(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Indent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??d??nt">Indent</phoneme>'
        elif combined_sentences_token_list[i][0] == "indent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??d??nt">indent</phoneme>'
        elif combined_sentences_token_list[i][0] == "Indent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??d??nt">Indent</phoneme>'
        elif combined_sentences_token_list[i][0] == "indent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??d??nt">indent</phoneme>'

        elif combined_sentences_token_list[i][0] == "Indent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??d??nt">Indent</phoneme>'
        elif combined_sentences_token_list[i][0] == "indent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??d??nt">indent</phoneme>'
        elif combined_sentences_token_list[i][0] == "Indent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??d??nt">Indent</phoneme>'
        elif combined_sentences_token_list[i][0] == "indent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??d??nt">indent</phoneme>'
    return combined_sentences_word_list

def initiate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Initiate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n????i??e??t">Initiate</phoneme>'
        elif combined_sentences_token_list[i][0] == "initiate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n????i??e??t">initiate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Initiate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n????i??t">Initiate</phoneme>'
        elif combined_sentences_token_list[i][0] == "initiate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n????i??t">initiate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Initiate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n????????e??t">Initiate</phoneme>'
        elif combined_sentences_token_list[i][0] == "initiate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n????????e??t">initiate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Initiate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n????????t">Initiate</phoneme>'
        elif combined_sentences_token_list[i][0] == "initiate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n????????t">initiate</phoneme>'
    return combined_sentences_word_list

def insert(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Insert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??s??rt">Insert</phoneme>'
        elif combined_sentences_token_list[i][0] == "insert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??s??rt">insert</phoneme>'
        elif combined_sentences_token_list[i][0] == "Insert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??s??rt">Insert</phoneme>'
        elif combined_sentences_token_list[i][0] == "insert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??s??rt">insert</phoneme>'

        elif combined_sentences_token_list[i][0] == "Insert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??s????t">Insert</phoneme>'
        elif combined_sentences_token_list[i][0] == "insert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??s????t">insert</phoneme>'
        elif combined_sentences_token_list[i][0] == "Insert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????ns????t">Insert</phoneme>'
        elif combined_sentences_token_list[i][0] == "insert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????ns????t">insert</phoneme>'
    return combined_sentences_word_list

def inset(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Inset" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??s??t">Inset</phoneme>'
        elif combined_sentences_token_list[i][0] == "inset" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??s??t">inset</phoneme>'
        elif combined_sentences_token_list[i][0] == "Inset" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??s??t">Inset</phoneme>'
        elif combined_sentences_token_list[i][0] == "inset" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??s??t">inset</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def instinct(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Instinct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??st????kt">Instinct</phoneme>'
        elif combined_sentences_token_list[i][0] == "instinct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??st????kt">instinct</phoneme>'
        elif combined_sentences_token_list[i][0] == "Instinct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??st????kt">Instinct</phoneme>'
        elif combined_sentences_token_list[i][0] == "instinct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??st????kt">instinct</phoneme>'

        elif combined_sentences_token_list[i][0] == "Instinct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??st????kt">Instinct</phoneme>'
        elif combined_sentences_token_list[i][0] == "instinct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??st????kt">instinct</phoneme>'
        elif combined_sentences_token_list[i][0] == "Instinct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nst????kt">Instinct</phoneme>'
        elif combined_sentences_token_list[i][0] == "instinct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nst????kt">instinct</phoneme>'
    return combined_sentences_word_list

def insult(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Insult" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??s??lt">Insult</phoneme>'
        elif combined_sentences_token_list[i][0] == "insult" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??s??lt">insult</phoneme>'
        elif combined_sentences_token_list[i][0] == "Insult" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??s??lt">Insult</phoneme>'
        elif combined_sentences_token_list[i][0] == "insult" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??s??lt">insult</phoneme>'

        elif combined_sentences_token_list[i][0] == "Insult" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??s??lt">Insult</phoneme>'
        elif combined_sentences_token_list[i][0] == "insult" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??s??lt">insult</phoneme>'
        elif combined_sentences_token_list[i][0] == "Insult" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????ns??lt">Insult</phoneme>'
        elif combined_sentences_token_list[i][0] == "insult" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????ns??lt">insult</phoneme>'
    return combined_sentences_word_list

def intercept(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Intercept" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt??r??s??pt">Intercept</phoneme>'
        elif combined_sentences_token_list[i][0] == "intercept" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt??r??s??pt">intercept</phoneme>'
        elif combined_sentences_token_list[i][0] == "Intercept" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt??r??s??pt">Intercept</phoneme>'
        elif combined_sentences_token_list[i][0] == "intercept" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt??r??s??pt">intercept</phoneme>'

        elif combined_sentences_token_list[i][0] == "Intercept" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt????s??pt">Intercept</phoneme>'
        elif combined_sentences_token_list[i][0] == "intercept" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt????s??pt">intercept</phoneme>'
        elif combined_sentences_token_list[i][0] == "Intercept" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt????s??pt">Intercept</phoneme>'
        elif combined_sentences_token_list[i][0] == "intercept" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt????s??pt">intercept</phoneme>'
    return combined_sentences_word_list

def intermediate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Intermediate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt??r??midi??e??t">Intermediate</phoneme>'
        elif combined_sentences_token_list[i][0] == "intermediate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt??r??midi??e??t">intermediate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Intermediate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt??r??midi??t">Intermediate</phoneme>'
        elif combined_sentences_token_list[i][0] == "intermediate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt??r??midi??t">intermediate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Intermediate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt????mi??d????e??t">Intermediate</phoneme>'
        elif combined_sentences_token_list[i][0] == "intermediate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt????mi??d????e??t">intermediate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Intermediate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt????mi??d????t">Intermediate</phoneme>'
        elif combined_sentences_token_list[i][0] == "intermediate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt????mi??d????t">intermediate</phoneme>'
    return combined_sentences_word_list

#As the transitive and intransitive versions of the verb "intern" are pronounced differently, a function is used to determine whether
#the verb is transitive or not. However, Spacy does not yet allow to accurately distinguish between transitive and intransitive verbs.
#If the verb "intern" is labelled as a transitive verb by Spacy (To detain or to confine people or material during a conflict, for instance),
#it is replaced by the phoneme "<phoneme alphabet="ipa" ph="??n??t??rn">Intern</phoneme>". #If the verb "intern" is labelled as an intransitive verb by Spacy (to be employed as an intern), it is replaced with the phoneme
#"<phoneme alphabet="ipa" ph="????n??t??rn">Intern</phoneme>"
def intern(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Intern" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            if is_transitive_verb(combined_sentences_token_list) == True:
                combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??t??rn">Intern</phoneme>'
            else:
                combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??t??rn">Intern</phoneme>'
        elif combined_sentences_token_list[i][0] == "intern" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            if is_transitive_verb(combined_sentences_token_list) == True:
                combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??t??rn">Intern</phoneme>'
            else:
                combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??t??rn">Intern</phoneme>'
        elif combined_sentences_token_list[i][0] == "Intern" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??t??rn">Intern</phoneme>'
        elif combined_sentences_token_list[i][0] == "intern" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??t??rn">intern</phoneme>'

        elif combined_sentences_token_list[i][0] == "Intern" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            if is_transitive_verb(combined_sentences_token_list) == True:
                combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??t????n">Intern</phoneme>'
            else:
                combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt????n">Intern</phoneme>'
        elif combined_sentences_token_list[i][0] == "intern" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            if is_transitive_verb(combined_sentences_token_list) == True:
                combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??t????n">Intern</phoneme>'
            else:
                combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt????n">Intern</phoneme>'
        elif combined_sentences_token_list[i][0] == "Intern" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt????n">Intern</phoneme>'
        elif combined_sentences_token_list[i][0] == "intern" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt????n">intern</phoneme>'
    return combined_sentences_word_list

def intimate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Intimate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt????me??t">Intimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "intimate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt????me??t">intimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Intimate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt??m??t">Intimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "intimate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt??m??t">intimate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Intimate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt????me??t">Intimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "intimate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt????me??t">intimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Intimate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt??m??t">Intimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "intimate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nt??m??t">intimate</phoneme>'
    return combined_sentences_word_list

def invite(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Invite" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??va??t">Invite</phoneme>'
        elif combined_sentences_token_list[i][0] == "invite" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??va??t">invite</phoneme>'
        elif combined_sentences_token_list[i][0] == "Invite" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??va??t">Invite</phoneme>'
        elif combined_sentences_token_list[i][0] == "invite" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????n??va??t">invite</phoneme>'

        elif combined_sentences_token_list[i][0] == "Invite" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??va??t">Invite</phoneme>'
        elif combined_sentences_token_list[i][0] == "invite" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??va??t">invite</phoneme>'
        elif combined_sentences_token_list[i][0] == "Invite" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nva??t">Invite</phoneme>'
        elif combined_sentences_token_list[i][0] == "invite" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nva??t">invite</phoneme>'
    return combined_sentences_word_list

#Only for British English, as the noun, verb and adjective may be pronounced the same in American English
def involute(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Involute" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nv????lu??t">Involute</phoneme>'
        elif combined_sentences_token_list[i][0] == "involute" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nv????lu??t">involute</phoneme>'
        elif combined_sentences_token_list[i][0] == "Involute" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nv????lu??t">Involute</phoneme>'
        elif combined_sentences_token_list[i][0] == "involute" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????nv????lu??t">involute</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def isolate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Isolate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ais????leit">Isolate</phoneme>'
        elif combined_sentences_token_list[i][0] == "isolate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ais????leit">isolate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Isolate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ais??l??t">Isolate</phoneme>'
        elif combined_sentences_token_list[i][0] == "isolate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ais??l??t">isolate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Isolate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??a??s????le??t">Isolate</phoneme>'
        elif combined_sentences_token_list[i][0] == "isolate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??a??s????le??t">isolate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Isolate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??a??s??l??t">Isolate</phoneme>'
        elif combined_sentences_token_list[i][0] == "isolate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??a??s??l??t">isolate</phoneme>'
    return combined_sentences_word_list

def jagged(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Jagged" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d????gd">Jagged</phoneme>'
        elif combined_sentences_token_list[i][0] == "jagged" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d????gd">jagged</phoneme>'
        elif combined_sentences_token_list[i][0] == "Jagged" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d????g??d">Jagged</phoneme>'
        elif combined_sentences_token_list[i][0] == "jagged" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??d????g??d">jagged</phoneme>'
    return combined_sentences_word_list

#As the noun "lead" can designate the chemical element or the first place, and as some transitive "lead" verbs forms
#are pronounced differently, only the intransitive verb and adjective are included.
def lead(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Lead" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB" and is_transitive_verb(combined_sentences_token_list) == False:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="lid">Lead</phoneme>'
        elif combined_sentences_token_list[i][0] == "lead" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB" and is_transitive_verb(combined_sentences_token_list) == False:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="lid">lead</phoneme>'
        elif combined_sentences_token_list[i][0] == "Lead" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="lid">Lead</phoneme>'
        elif combined_sentences_token_list[i][0] == "lead" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="lid">lead</phoneme>'

        elif combined_sentences_token_list[i][0] == "Lead" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB" and is_transitive_verb(combined_sentences_token_list) == False:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="li??d">Lead</phoneme>'
        elif combined_sentences_token_list[i][0] == "lead" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB" and is_transitive_verb(combined_sentences_token_list) == False:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="li??d">lead</phoneme>'
        elif combined_sentences_token_list[i][0] == "Lead" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="li??d">Lead</phoneme>'
        elif combined_sentences_token_list[i][0] == "lead" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="li??d">lead</phoneme>'
    return combined_sentences_word_list

#As some "learned" adjective forms are pronounced differently in American English, the adjective is
#only covered in British English, where all adjective forms are pronounced the same.
#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def learned(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Learned" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??l????rnd">Learned</phoneme>'
        elif combined_sentences_token_list[i][0] == "learned" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??l????rnd">learned</phoneme>'
        elif combined_sentences_token_list[i][0] == "Learned" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??l????n??d">Learned</phoneme>'
        elif combined_sentences_token_list[i][0] == "learned" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??l????n??d">learned</phoneme>'
    return combined_sentences_word_list

def legitimate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Legitimate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="l????d????t????me??t">Legitimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "legitimate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="l????d????t????me??t">legitimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Legitimate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="l????d????t??m??t">Legitimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "legitimate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="l????d????t??m??t">legitimate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Legitimate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="l????d????t????me??t">Legitimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "legitimate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="l????d????t????me??t">legitimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Legitimate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="l????d????t??m??t">Legitimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "legitimate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="l????d????t??m??t">legitimate</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def lied(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Lied" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="laid">Lied</phoneme>'
        elif combined_sentences_token_list[i][0] == "lied" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="laid">lied</phoneme>'
        elif combined_sentences_token_list[i][0] == "Lied" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="lid">Lied</phoneme>'
        elif combined_sentences_token_list[i][0] == "lied" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="lid">lied</phoneme>'

        elif combined_sentences_token_list[i][0] == "Lied" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="laid">Lied</phoneme>'
        elif combined_sentences_token_list[i][0] == "lied" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="laid">lied</phoneme>'
        elif combined_sentences_token_list[i][0] == "Lied" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="li??d">Lied</phoneme>'
        elif combined_sentences_token_list[i][0] == "lied" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="li??d">lied</phoneme>'
    return combined_sentences_word_list

def live(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Live" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="l??v">Live</phoneme>'
        elif combined_sentences_token_list[i][0] == "live" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="l??v">live</phoneme>'
        elif combined_sentences_token_list[i][0] == "Live" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="la??v">Live</phoneme>'
        elif combined_sentences_token_list[i][0] == "live" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="la??v">live</phoneme>'
    return combined_sentences_word_list

#As different forms of the noun and intransitive verb "lower" can be pronounced in different ways, only the adjectives and transitive verbs are included.
#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def lower(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Lower" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB" and is_transitive_verb(combined_sentences_token_list) == True:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??lo????r">Lower</phoneme>'
        elif combined_sentences_token_list[i][0] == "lower" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB" and is_transitive_verb(combined_sentences_token_list) == True:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??lo????r">lower</phoneme>'
        elif combined_sentences_token_list[i][0] == "Lower" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??lo????r">Lower</phoneme>'
        elif combined_sentences_token_list[i][0] == "lower" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??lo????r">lower</phoneme>'

        elif combined_sentences_token_list[i][0] == "Lower" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB" and is_transitive_verb(combined_sentences_token_list) == True:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??l??????">Lower</phoneme>'
        elif combined_sentences_token_list[i][0] == "lower" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB" and is_transitive_verb(combined_sentences_token_list) == True:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??l??????">lower</phoneme>'
        elif combined_sentences_token_list[i][0] == "Lower" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??l??????">Lower</phoneme>'
        elif combined_sentences_token_list[i][0] == "lower" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??l??????">lower</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def lupine(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Lupine" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??lu??pa??n">Lupine</phoneme>'
        elif combined_sentences_token_list[i][0] == "lupine" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??lu??pa??n">lupine</phoneme>'
        elif combined_sentences_token_list[i][0] == "Lupine" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??lup??n">Lupine</phoneme>'
        elif combined_sentences_token_list[i][0] == "lupine" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??lup??n">lupine</phoneme>'

        elif combined_sentences_token_list[i][0] == "Lupine" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??lu??pa??n">Lupine</phoneme>'
        elif combined_sentences_token_list[i][0] == "lupine" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??lu??pa??n">lupine</phoneme>'
        elif combined_sentences_token_list[i][0] == "Lupine" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??lup??n">Lupine</phoneme>'
        elif combined_sentences_token_list[i][0] == "lupine" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??lup??n">lupine</phoneme>'
    return combined_sentences_word_list

def merchandise(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Merchandise" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??rt????n??da??z">Merchandise</phoneme>'
        elif combined_sentences_token_list[i][0] == "merchandise" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??rt????n??da??z">merchandise</phoneme>'
        elif combined_sentences_token_list[i][0] == "Merchandise" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??rt????n??da??s">Merchandise</phoneme>'
        elif combined_sentences_token_list[i][0] == "merchandise" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??rt????n??da??s">merchandise</phoneme>'

        elif combined_sentences_token_list[i][0] == "Merchandise" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m????t????n??da??z">Merchandise</phoneme>'
        elif combined_sentences_token_list[i][0] == "merchandise" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m????t????n??da??z">merchandise</phoneme>'
        elif combined_sentences_token_list[i][0] == "Merchandise" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m????t????n??da??s">Merchandise</phoneme>'
        elif combined_sentences_token_list[i][0] == "merchandise" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m????t????n??da??s">merchandise</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def minute(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Minute" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ma????njut">Minute</phoneme>'
        elif combined_sentences_token_list[i][0] == "minute" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ma????njut">minute</phoneme>'
        elif combined_sentences_token_list[i][0] == "Minute" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??n??t">Minute</phoneme>'
        elif combined_sentences_token_list[i][0] == "minute" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??n??t">minute</phoneme>'

        elif combined_sentences_token_list[i][0] == "Minute" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ma????nju??t">Minute</phoneme>'
        elif combined_sentences_token_list[i][0] == "minute" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ma????nju??t">minute</phoneme>'
        elif combined_sentences_token_list[i][0] == "Minute" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??n??t">Minute</phoneme>'
        elif combined_sentences_token_list[i][0] == "minute" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??n??t">minute</phoneme>'
    return combined_sentences_word_list

def misconduct(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Misconduct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??sk??n??d??kt">Misconduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "misconduct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??sk??n??d??kt">misconduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "Misconduct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="m??s??k??nd??kt">Misconduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "misconduct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="m??s??k??nd??kt">misconduct</phoneme>'

        elif combined_sentences_token_list[i][0] == "Misconduct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??sk??n??d??kt">Misconduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "misconduct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??sk??n??d??kt">misconduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "Misconduct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="m??s??k??nd??kt">Misconduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "misconduct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="m??s??k??nd??kt">misconduct</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def misread(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Misread" and combined_sentences_token_list[i][1] in ["VB", "VBP", "VBZ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??s??ri??d">Misread</phoneme>'
        elif combined_sentences_token_list[i][0] == "misread" and combined_sentences_token_list[i][1] in ["VB", "VBP", "VBZ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??s??ri??d">misread</phoneme>'
        elif combined_sentences_token_list[i][0] == "Misread" and combined_sentences_token_list[i][1] not in ["VB", "VBP", "VBZ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??s??r??d">Misread</phoneme>'
        elif combined_sentences_token_list[i][0] == "misread" and combined_sentences_token_list[i][1] not in ["VB", "VBP", "VBZ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??s??r??d">misread</phoneme>'
    return combined_sentences_word_list

#As the two noun forms of "mobile" ("mobile" as in cell phone, "mobile" as in an abstract sculpture) are pronounced differently in American English, only the
#adjectives and the proper noun are included (the regular nouns are included in British English).
def mobile(combined_sentences_word_list, combined_sentences_token_list):
    global English_Phonetics
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Mobile" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:3] == "NNP":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??mo????bil">Mobile</phoneme>'
        elif combined_sentences_token_list[i][0] == "Mobile" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??mo????ba??l">Mobile</phoneme>'
        elif combined_sentences_token_list[i][0] == "mobile" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??mo????ba??l">mobile</phoneme>'

        elif combined_sentences_token_list[i][0] == "Mobile" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:3] == "NNP":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m????bi??l">Mobile</phoneme>'
        elif combined_sentences_token_list[i][0] == "Mobile" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m????ba??l">Mobile</phoneme>'
        elif combined_sentences_token_list[i][0] == "mobile" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m????ba??l">mobile</phoneme>'
        elif combined_sentences_token_list[i][0] == "Mobile" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m????ba??l">Mobile</phoneme>'
        elif combined_sentences_token_list[i][0] == "mobile" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m????ba??l">mobile</phoneme>'
    return combined_sentences_word_list

def moderate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Moderate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??d??r??e??t">Moderate</phoneme>'
        elif combined_sentences_token_list[i][0] == "moderate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??d??r??e??t">moderate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Moderate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??d??r??t">Moderate</phoneme>'
        elif combined_sentences_token_list[i][0] == "moderate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??d??r??t">moderate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Moderate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??d????re??t">Moderate</phoneme>'
        elif combined_sentences_token_list[i][0] == "moderate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??d????re??t">moderate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Moderate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??d??r??t">Moderate</phoneme>'
        elif combined_sentences_token_list[i][0] == "moderate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??d??r??t">moderate</phoneme>'
    return combined_sentences_word_list

def moped(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Moped" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??mo??pt">Moped</phoneme>'
        elif combined_sentences_token_list[i][0] == "moped" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??mo??pt">moped</phoneme>'
        elif combined_sentences_token_list[i][0] == "Moped" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??mo????p??d">Moped</phoneme>'
        elif combined_sentences_token_list[i][0] == "moped" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??mo????p??d">moped</phoneme>'

        elif combined_sentences_token_list[i][0] == "Moped" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??mo??pd">Moped</phoneme>'
        elif combined_sentences_token_list[i][0] == "moped" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??mo??pd">moped</phoneme>'
        elif combined_sentences_token_list[i][0] == "Moped" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m????p??d">Moped</phoneme>'
        elif combined_sentences_token_list[i][0] == "moped" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m????p??d">moped</phoneme>'
    return combined_sentences_word_list

def mouse(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Mouse" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ma??z">Mouse</phoneme>'
        elif combined_sentences_token_list[i][0] == "mouse" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ma??z">mouse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Mouse" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ma??s">Mouse</phoneme>'
        elif combined_sentences_token_list[i][0] == "mouse" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ma??s">mouse</phoneme>'
    return combined_sentences_word_list

def mouth(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Mouth" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ma????">Mouth</phoneme>'
        elif combined_sentences_token_list[i][0] == "mouth" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ma????">mouth</phoneme>'
        elif combined_sentences_token_list[i][0] == "Mouth" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ma????">Mouth</phoneme>'
        elif combined_sentences_token_list[i][0] == "mouth" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ma????">mouth</phoneme>'
    return combined_sentences_word_list

def mow(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Mow" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??mo??">Mow</phoneme>'
        elif combined_sentences_token_list[i][0] == "mow" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??mo??">mow</phoneme>'
        elif combined_sentences_token_list[i][0] == "Mow" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ma??">Mow</phoneme>'
        elif combined_sentences_token_list[i][0] == "mow" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ma??">mow</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately. (It seems to tokenize multiply as either a verb
#or comparative adjective (instead of adverb)) The POS was used instead of the TAG for the adverbs, as the first
#letters of the various adverb tags differ.
def multiply(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Multiply" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??lt????pla??">Multiply</phoneme>'
        elif combined_sentences_token_list[i][0] == "multiply" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??lt????pla??">multiply</phoneme>'
        elif combined_sentences_token_list[i][0] == "Multiply" and English_Phonetics == "American_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??lt??pli">Multiply</phoneme>'
        elif combined_sentences_token_list[i][0] == "multiply" and English_Phonetics == "American_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??lt??pli">multiply</phoneme>'

        elif combined_sentences_token_list[i][0] == "Multiply" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??lt????pla??">Multiply</phoneme>'
        elif combined_sentences_token_list[i][0] == "multiply" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??lt????pla??">multiply</phoneme>'
        elif combined_sentences_token_list[i][0] == "Multiply" and English_Phonetics == "British_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??lt??pli">Multiply</phoneme>'
        elif combined_sentences_token_list[i][0] == "multiply" and English_Phonetics == "British_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??m??lt??pli">multiply</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def number(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Number" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??m??r">Number</phoneme>'
        elif combined_sentences_token_list[i][0] == "number" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??m??r">number</phoneme>'
        elif combined_sentences_token_list[i][0] == "Number" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "VB"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??mb??r">Number</phoneme>'
        elif combined_sentences_token_list[i][0] == "number" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "VB"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??mb??r">number</phoneme>'

        elif combined_sentences_token_list[i][0] == "Number" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??m??">Number</phoneme>'
        elif combined_sentences_token_list[i][0] == "number" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??m??">number</phoneme>'
        elif combined_sentences_token_list[i][0] == "Number" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "VB"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??mb??">Number</phoneme>'
        elif combined_sentences_token_list[i][0] == "number" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "VB"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??n??mb??">number</phoneme>'
    return combined_sentences_word_list

def object(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Object" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??b??d????kt">Object</phoneme>'
        elif combined_sentences_token_list[i][0] == "object" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??b??d????kt">object</phoneme>'
        elif combined_sentences_token_list[i][0] == "Object" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??bd????kt">Object</phoneme>'
        elif combined_sentences_token_list[i][0] == "object" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??bd????kt">object</phoneme>'

        elif combined_sentences_token_list[i][0] == "Object" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??b??d????kt">Object</phoneme>'
        elif combined_sentences_token_list[i][0] == "object" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??b??d????kt">object</phoneme>'
        elif combined_sentences_token_list[i][0] == "Object" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????bd????kt">Object</phoneme>'
        elif combined_sentences_token_list[i][0] == "object" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????bd????kt">object</phoneme>'
    return combined_sentences_word_list

#Only in American English, as it is pronounced the same in British English.
def obligate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Obligate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????bl????ge??t">Obligate</phoneme>'
        elif combined_sentences_token_list[i][0] == "obligate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????bl????ge??t">obligate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Obligate" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????bl??g??t">Obligate</phoneme>'
        elif combined_sentences_token_list[i][0] == "obligate" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????bl??g??t">obligate</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def overage(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Overage" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??o??v??r??e??d??">Overage</phoneme>'
        elif combined_sentences_token_list[i][0] == "overage" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??o??v??r??e??d??">overage</phoneme>'
        elif combined_sentences_token_list[i][0] == "Overage" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??o??v??r??d??">Overage</phoneme>'
        elif combined_sentences_token_list[i][0] == "overage" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??o??v??r??d??">overage</phoneme>'

        elif combined_sentences_token_list[i][0] == "Overage" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????v??r??e??d??">Overage</phoneme>'
        elif combined_sentences_token_list[i][0] == "overage" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????v??r??e??d??">overage</phoneme>'
        elif combined_sentences_token_list[i][0] == "Overage" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????v??r??d??">Overage</phoneme>'
        elif combined_sentences_token_list[i][0] == "overage" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????v??r??d??">overage</phoneme>'
    return combined_sentences_word_list

#The POS was used instead of the TAG for the adverbs, as the first letters of the various adverb tags differ.
def overall(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Overall" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??o??v??r????l">Overall</phoneme>'
        elif combined_sentences_token_list[i][0] == "overall" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??o??v??r????l">overall</phoneme>'
        elif combined_sentences_token_list[i][0] == "Overall" and English_Phonetics == "American_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="o??v??r????l">Overall</phoneme>'
        elif combined_sentences_token_list[i][0] == "overall" and English_Phonetics == "American_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="o??v??r????l">overall</phoneme>'

        elif combined_sentences_token_list[i][0] == "Overall" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????v??r??????l">Overall</phoneme>'
        elif combined_sentences_token_list[i][0] == "overall" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????v??r??????l">overall</phoneme>'
        elif combined_sentences_token_list[i][0] == "Overall" and English_Phonetics == "British_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????v??r??????l">Overall</phoneme>'
        elif combined_sentences_token_list[i][0] == "overall" and English_Phonetics == "British_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????v??r??????l">overall</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
#The POS was used instead of the TAG for the adverbs, as the first letters of the various adverb tags differ.
def overhead(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Overhead" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??o??v??r??h??d">Overhead</phoneme>'
        elif combined_sentences_token_list[i][0] == "overhead" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??o??v??r??h??d">overhead</phoneme>'
        elif combined_sentences_token_list[i][0] == "Overhead" and English_Phonetics == "American_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="o??v??r??h??d">Overhead</phoneme>'
        elif combined_sentences_token_list[i][0] == "overhead" and English_Phonetics == "American_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="o??v??r??h??d">overhead</phoneme>'

        elif combined_sentences_token_list[i][0] == "Overhead" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????v????h??d">Overhead</phoneme>'
        elif combined_sentences_token_list[i][0] == "overhead" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????v????h??d">overhead</phoneme>'
        elif combined_sentences_token_list[i][0] == "Overhead" and English_Phonetics == "British_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????v????h??d">Overhead</phoneme>'
        elif combined_sentences_token_list[i][0] == "overhead" and English_Phonetics == "British_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????v????h??d">overhead</phoneme>'
    return combined_sentences_word_list

def overlook(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Overlook" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??o??v??r??l??k">Overlook</phoneme>'
        elif combined_sentences_token_list[i][0] == "overlook" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??o??v??r??l??k">overlook</phoneme>'
        elif combined_sentences_token_list[i][0] == "Overlook" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??o??v??r??l??k">Overlook</phoneme>'
        elif combined_sentences_token_list[i][0] == "overlook" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??o??v??r??l??k">overlook</phoneme>'

        elif combined_sentences_token_list[i][0] == "Overlook" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????v????l??k">Overlook</phoneme>'
        elif combined_sentences_token_list[i][0] == "overlook" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????v????l??k">overlook</phoneme>'
        elif combined_sentences_token_list[i][0] == "Overlook" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????v????l??k">Overlook</phoneme>'
        elif combined_sentences_token_list[i][0] == "overlook" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????v????l??k">overlook</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def overrun(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Overrun" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??o??v??r??r??n">Overrun</phoneme>'
        elif combined_sentences_token_list[i][0] == "overrun" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??o??v??r??r??n">overrun</phoneme>'
        elif combined_sentences_token_list[i][0] == "Overrun" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??o??v??r??r??n">Overrun</phoneme>'
        elif combined_sentences_token_list[i][0] == "overrun" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??o??v??r??r??n">overrun</phoneme>'

        elif combined_sentences_token_list[i][0] == "Overrun" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????v????r??n">Overrun</phoneme>'
        elif combined_sentences_token_list[i][0] == "overrun" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????v????r??n">overrun</phoneme>'
        elif combined_sentences_token_list[i][0] == "Overrun" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????v????r??n">Overrun</phoneme>'
        elif combined_sentences_token_list[i][0] == "overrun" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??????v????r??n">overrun</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def pedal(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Pedal" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "VB"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pedl">Pedal</phoneme>'
        elif combined_sentences_token_list[i][0] == "pedal" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "VB"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pedl">pedal</phoneme>'
        elif combined_sentences_token_list[i][0] == "Pedal" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pidl">Pedal</phoneme>'
        elif combined_sentences_token_list[i][0] == "pedal" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pidl">pedal</phoneme>'

        elif combined_sentences_token_list[i][0] == "Pedal" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "VB"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??d??l">Pedal</phoneme>'
        elif combined_sentences_token_list[i][0] == "pedal" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "VB"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??d??l">pedal</phoneme>'
        elif combined_sentences_token_list[i][0] == "Pedal" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pi??d??l">Pedal</phoneme>'
        elif combined_sentences_token_list[i][0] == "pedal" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pi??d??l">pedal</phoneme>'
    return combined_sentences_word_list

def perfect(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Perfect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="p??r??f??kt">Perfect</phoneme>'
        elif combined_sentences_token_list[i][0] == "perfect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="p??r??f??kt">perfect</phoneme>'
        elif combined_sentences_token_list[i][0] == "Perfect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??rf??kt">Perfect</phoneme>'
        elif combined_sentences_token_list[i][0] == "perfect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??rf??kt">perfect</phoneme>'

        elif combined_sentences_token_list[i][0] == "Perfect" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="p????f??kt">Perfect</phoneme>'
        elif combined_sentences_token_list[i][0] == "perfect" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="p????f??kt">perfect</phoneme>'
        elif combined_sentences_token_list[i][0] == "Perfect" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p????f??kt">Perfect</phoneme>'
        elif combined_sentences_token_list[i][0] == "perfect" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p????f??kt">perfect</phoneme>'
    return combined_sentences_word_list

def permit(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Permit" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="p??r??m??t">Permit</phoneme>'
        elif combined_sentences_token_list[i][0] == "permit" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="p??r??m??t">permit</phoneme>'
        elif combined_sentences_token_list[i][0] == "Permit" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??r??m??t">Permit</phoneme>'
        elif combined_sentences_token_list[i][0] == "permit" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??r??m??t">permit</phoneme>'

        elif combined_sentences_token_list[i][0] == "Permit" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="p????m??t">Permit</phoneme>'
        elif combined_sentences_token_list[i][0] == "permit" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="p????m??t">permit</phoneme>'
        elif combined_sentences_token_list[i][0] == "Permit" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p????m??t">Permit</phoneme>'
        elif combined_sentences_token_list[i][0] == "permit" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p????m??t">permit</phoneme>'
    return combined_sentences_word_list

def pervert(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Pervert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="p??r??v??rt">Pervert</phoneme>'
        elif combined_sentences_token_list[i][0] == "pervert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="p??r??v??rt">pervert</phoneme>'
        elif combined_sentences_token_list[i][0] == "Pervert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??r??v??rt">Pervert</phoneme>'
        elif combined_sentences_token_list[i][0] == "pervert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??r??v??rt">pervert</phoneme>'

        elif combined_sentences_token_list[i][0] == "Pervert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="p????v????t">Pervert</phoneme>'
        elif combined_sentences_token_list[i][0] == "pervert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="p????v????t">pervert</phoneme>'
        elif combined_sentences_token_list[i][0] == "Pervert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p????v????t">Pervert</phoneme>'
        elif combined_sentences_token_list[i][0] == "pervert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p????v????t">pervert</phoneme>'
    return combined_sentences_word_list

def polish(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Polish" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1] == "NNP":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??poul????">Polish</phoneme>'
        elif combined_sentences_token_list[i][0] == "Polish" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1] in ["VB", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??l????">Polish</phoneme>'
        elif combined_sentences_token_list[i][0] == "polish" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1] in ["VB", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??l????">polish</phoneme>'
        elif combined_sentences_token_list[i][0] == "Polish" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??poul????">Polish</phoneme>'
        elif combined_sentences_token_list[i][0] == "polish" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??poul????">polish</phoneme>'

        elif combined_sentences_token_list[i][0] == "Polish" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1] == "NNP":
                combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p????l????">Polish</phoneme>'
        elif combined_sentences_token_list[i][0] == "Polish" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1] in ["VB", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??l????">Polish</phoneme>'
        elif combined_sentences_token_list[i][0] == "polish" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1] in ["VB", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??l????">polish</phoneme>'
        elif combined_sentences_token_list[i][0] == "Polish" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p????l????">Polish</phoneme>'
        elif combined_sentences_token_list[i][0] == "polish" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p????l????">polish</phoneme>'
    return combined_sentences_word_list

def postulate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Postulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??st??????le??t">Postulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "postulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??st??????le??t">postulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Postulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??st????l??t">Postulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "postulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??st????l??t">postulate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Postulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??stj????le??t">Postulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "postulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??stj????le??t">postulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Postulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??stj??l??t">Postulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "postulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??stj??l??t">postulate</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def precedent(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Precedent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pr????si??d??nt">Precedent</phoneme>'
        elif combined_sentences_token_list[i][0] == "precedent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pr????si??d??nt">precedent</phoneme>'
        elif combined_sentences_token_list[i][0] == "Precedent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr??s??d??nt">Precedent</phoneme>'
        elif combined_sentences_token_list[i][0] == "precedent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr??s??d??nt">precedent</phoneme>'

        elif combined_sentences_token_list[i][0] == "Precedent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pri??sid??nt">Precedent</phoneme>'
        elif combined_sentences_token_list[i][0] == "precedent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pri??sid??nt">precedent</phoneme>'
        elif combined_sentences_token_list[i][0] == "Precedent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr??s??d??nt">Precedent</phoneme>'
        elif combined_sentences_token_list[i][0] == "precedent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr??s??d??nt">precedent</phoneme>'
    return combined_sentences_word_list

def precipitate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Precipitate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pri??s??p????te??t">Precipitate</phoneme>'
        elif combined_sentences_token_list[i][0] == "precipitate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pri??s??p????te??t">precipitate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Precipitate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pri??s??p??t??t">Precipitate</phoneme>'
        elif combined_sentences_token_list[i][0] == "precipitate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pri??s??p??t??t">precipitate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Precipitate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pr????s??p????te??t">Precipitate</phoneme>'
        elif combined_sentences_token_list[i][0] == "precipitate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pr????s??p????te??t">precipitate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Precipitate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pr????s??p??t??t">Precipitate</phoneme>'
        elif combined_sentences_token_list[i][0] == "precipitate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pr????s??p??t??t">precipitate</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def predicate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Predicate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr??d????ke??t">Predicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "predicate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr??d????ke??t">predicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Predicate" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr??d??k??t">Predicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "predicate" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr??d??k??t">predicate</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def premise(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Premise" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pr????ma??z">Premise</phoneme>'
        elif combined_sentences_token_list[i][0] == "premise" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pr????ma??z">premise</phoneme>'
        elif combined_sentences_token_list[i][0] == "Premise" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr??m??s">Premise</phoneme>'
        elif combined_sentences_token_list[i][0] == "premise" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr??m??s">premise</phoneme>'
    return combined_sentences_word_list

def present(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Present" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pr????z??nt">Present</phoneme>'
        elif combined_sentences_token_list[i][0] == "present" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pr????z??nt">present</phoneme>'
        elif combined_sentences_token_list[i][0] == "Present" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr??z??nt">Present</phoneme>'
        elif combined_sentences_token_list[i][0] == "present" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr??z??nt">present</phoneme>'
    return combined_sentences_word_list

def proceeds(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Proceeds" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pr????si??dz">Proceeds</phoneme>'
        elif combined_sentences_token_list[i][0] == "proceeds" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pr????si??dz">proceeds</phoneme>'
        elif combined_sentences_token_list[i][0] == "Proceeds" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pro??si??dz">Proceeds</phoneme>'
        elif combined_sentences_token_list[i][0] == "proceeds" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pro??si??dz">proceeds</phoneme>'
    return combined_sentences_word_list

def produce(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Produce" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pr????du??s">Produce</phoneme>'
        elif combined_sentences_token_list[i][0] == "produce" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pr????du??s">produce</phoneme>'
        elif combined_sentences_token_list[i][0] == "Produce" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr??du??s">Produce</phoneme>'
        elif combined_sentences_token_list[i][0] == "produce" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr??du??s">produce</phoneme>'

        elif combined_sentences_token_list[i][0] == "Produce" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pro????dus">Produce</phoneme>'
        elif combined_sentences_token_list[i][0] == "produce" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pro????dus">produce</phoneme>'
        elif combined_sentences_token_list[i][0] == "Produce" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pro????dus">Produce</phoneme>'
        elif combined_sentences_token_list[i][0] == "produce" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pro????dus">produce</phoneme>'
    return combined_sentences_word_list

def progress(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Progress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pro????gr??s">Progress</phoneme>'
        elif combined_sentences_token_list[i][0] == "progress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pro????gr??s">progress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Progress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr??gr??s">Progress</phoneme>'
        elif combined_sentences_token_list[i][0] == "progress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr??gr??s">progress</phoneme>'

        elif combined_sentences_token_list[i][0] == "Progress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pr??????r??s">Progress</phoneme>'
        elif combined_sentences_token_list[i][0] == "progress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pr??????r??s">progress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Progress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr??????r??s">Progress</phoneme>'
        elif combined_sentences_token_list[i][0] == "progress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr??????r??s">progress</phoneme>'
    return combined_sentences_word_list

def project(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Project" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pr????d????kt">Project</phoneme>'
        elif combined_sentences_token_list[i][0] == "project" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pr????d????kt">project</phoneme>'
        elif combined_sentences_token_list[i][0] == "Project" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr????d????kt">Project</phoneme>'
        elif combined_sentences_token_list[i][0] == "project" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr????d????kt">project</phoneme>'

        elif combined_sentences_token_list[i][0] == "Project" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pr????d????kt">Project</phoneme>'
        elif combined_sentences_token_list[i][0] == "project" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pr????d????kt">project</phoneme>'
        elif combined_sentences_token_list[i][0] == "Project" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr??d????kt">Project</phoneme>'
        elif combined_sentences_token_list[i][0] == "project" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr??d????kt">project</phoneme>'
    return combined_sentences_word_list

def proofread(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Proofread" and combined_sentences_token_list[i][1] in ["VB", "VBP", "VBZ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pru??f??ri??d">Proofread</phoneme>'
        elif combined_sentences_token_list[i][0] == "proofread" and combined_sentences_token_list[i][1] in ["VB", "VBP", "VBZ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pru??f??ri??d">proofread</phoneme>'
        elif combined_sentences_token_list[i][0] == "Proofread" and combined_sentences_token_list[i][1] not in ["VB", "VBP", "VBZ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pru??f??r??d">Proofread</phoneme>'
        elif combined_sentences_token_list[i][0] == "proofread" and combined_sentences_token_list[i][1] not in ["VB", "VBP", "VBZ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pru??f??r??d">proofread</phoneme>'
    return combined_sentences_word_list

#Only in British English, because the verb and noun are pronounced the same in American English.
def prospect(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Prospect" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pr????sp??kt">Prospect</phoneme>'
        elif combined_sentences_token_list[i][0] == "prospect" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pr????sp??kt">prospect</phoneme>'
        elif combined_sentences_token_list[i][0] == "Prospect" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr??sp??kt">Prospect</phoneme>'
        elif combined_sentences_token_list[i][0] == "prospect" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr??sp??kt">prospect</phoneme>'
    return combined_sentences_word_list

def protest(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Protest" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pro????t??st">Protest</phoneme>'
        elif combined_sentences_token_list[i][0] == "protest" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pro????t??st">protest</phoneme>'
        elif combined_sentences_token_list[i][0] == "Protest" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pro????t??st">Protest</phoneme>'
        elif combined_sentences_token_list[i][0] == "protest" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pro????t??st">protest</phoneme>'

        elif combined_sentences_token_list[i][0] == "Protest" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pr????t??st">Protest</phoneme>'
        elif combined_sentences_token_list[i][0] == "protest" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pr????t??st">protest</phoneme>'
        elif combined_sentences_token_list[i][0] == "Protest" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr????t??st">Protest</phoneme>'
        elif combined_sentences_token_list[i][0] == "protest" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pr????t??st">protest</phoneme>'
    return combined_sentences_word_list

def pussy(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Pussy" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??si">Pussy</phoneme>'
        elif combined_sentences_token_list[i][0] == "pussy" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??si">pussy</phoneme>'
        elif combined_sentences_token_list[i][0] == "Pussy" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pusi">Pussy</phoneme>'
        elif combined_sentences_token_list[i][0] == "pussy" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??pusi">pussy</phoneme>'

        elif combined_sentences_token_list[i][0] == "Pussy" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??s??">Pussy</phoneme>'
        elif combined_sentences_token_list[i][0] == "pussy" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??s??">pussy</phoneme>'
        elif combined_sentences_token_list[i][0] == "Pussy" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??s??">Pussy</phoneme>'
        elif combined_sentences_token_list[i][0] == "pussy" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??s??">pussy</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def putting(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Putting" and combined_sentences_token_list[i][3].lower() == "putt":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??t????">Putting</phoneme>'
        elif combined_sentences_token_list[i][0] == "putting" and combined_sentences_token_list[i][3].lower() == "putt":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??t????">putting</phoneme>'
        elif combined_sentences_token_list[i][0] == "Putting" and combined_sentences_token_list[i][3].lower() == "put":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??t????">Putting</phoneme>'
        elif combined_sentences_token_list[i][0] == "putting" and combined_sentences_token_list[i][3].lower() == "put":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??t????">putting</phoneme>'
    return combined_sentences_word_list

#As the different forms of the noun "raven" (as in "ravin" or as the bird) have different pronounciations,
#only the adjective and verb are included.
def raven(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Raven" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??r??v??n">Raven</phoneme>'
        elif combined_sentences_token_list[i][0] == "raven" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??r??v??n">raven</phoneme>'
        elif combined_sentences_token_list[i][0] == "Raven" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??re??v??n">Raven</phoneme>'
        elif combined_sentences_token_list[i][0] == "raven" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??re??v??n">raven</phoneme>'
    return combined_sentences_word_list

def read(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Read" and combined_sentences_token_list[i][1] in ["VB", "VBP", "VBZ", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri??d">Read</phoneme>'
        elif combined_sentences_token_list[i][0] == "read" and combined_sentences_token_list[i][1] in ["VB", "VBP", "VBZ", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri??d">read</phoneme>'
        elif combined_sentences_token_list[i][0] == "Read" and combined_sentences_token_list[i][1] not in ["VB", "VBP", "VBZ", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r??d">Read</phoneme>'
        elif combined_sentences_token_list[i][0] == "read" and combined_sentences_token_list[i][1] not in ["VB", "VBP", "VBZ", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r??d">read</phoneme>'
    return combined_sentences_word_list

def rebel(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Rebel" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????b??l">Rebel</phoneme>'
        elif combined_sentences_token_list[i][0] == "rebel" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????b??l">rebel</phoneme>'
        elif combined_sentences_token_list[i][0] == "Rebel" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??r??b??l">Rebel</phoneme>'
        elif combined_sentences_token_list[i][0] == "rebel" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??r??b??l">rebel</phoneme>'
    return combined_sentences_word_list

#As the "recall" verb form meaning "to remove from office" is pronounced differently from the other transitive verb forms in American English,
#only the noun is included in American English.
def recall(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Recall" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??k??l">Recall</phoneme>'
        elif combined_sentences_token_list[i][0] == "recall" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??k??l">recall</phoneme>'

        elif combined_sentences_token_list[i][0] == "Recall" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????k????l">Recall</phoneme>'
        elif combined_sentences_token_list[i][0] == "recall" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????k????l">recall</phoneme>'
        elif combined_sentences_token_list[i][0] == "Recall" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??k????l">Recall</phoneme>'
        elif combined_sentences_token_list[i][0] == "recall" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??k????l">recall</phoneme>'
    return combined_sentences_word_list

def recap(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Recap" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri??k??p">Recap</phoneme>'
        elif combined_sentences_token_list[i][0] == "recap" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri??k??p">recap</phoneme>'
        elif combined_sentences_token_list[i][0] == "Recap" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??k??p">Recap</phoneme>'
        elif combined_sentences_token_list[i][0] == "recap" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??k??p">recap</phoneme>'

        elif combined_sentences_token_list[i][0] == "Recap" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri????k??p">Recap</phoneme>'
        elif combined_sentences_token_list[i][0] == "recap" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri????k??p">recap</phoneme>'
        elif combined_sentences_token_list[i][0] == "Recap" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri????k??p">Recap</phoneme>'
        elif combined_sentences_token_list[i][0] == "recap" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri????k??p">recap</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def recess(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Recess" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????s??s">Recess</phoneme>'
        elif combined_sentences_token_list[i][0] == "recess" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????s??s">recess</phoneme>'
        elif combined_sentences_token_list[i][0] == "Recess" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ris??s">Recess</phoneme>'
        elif combined_sentences_token_list[i][0] == "recess" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ris??s">recess</phoneme>'

        elif combined_sentences_token_list[i][0] == "Recess" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????s??s">Recess</phoneme>'
        elif combined_sentences_token_list[i][0] == "recess" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????s??s">recess</phoneme>'
        elif combined_sentences_token_list[i][0] == "Recess" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??s??s">Recess</phoneme>'
        elif combined_sentences_token_list[i][0] == "recess" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??s??s">recess</phoneme>'
    return combined_sentences_word_list

#Only in British English, as the noun and adjective are pronounced the same in American English.
def recitative(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Recitative" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??r??s??t????ti??v">Recitative</phoneme>'
        elif combined_sentences_token_list[i][0] == "recitative" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??r??s??t????ti??v">recitative</phoneme>'
        elif combined_sentences_token_list[i][0] == "Recitative" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????sa??t??t??v">Recitative</phoneme>'
        elif combined_sentences_token_list[i][0] == "recitative" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????sa??t??t??v">recitative</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def recoil(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Recoil" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????k????l">Recoil</phoneme>'
        elif combined_sentences_token_list[i][0] == "recoil" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????k????l">recoil</phoneme>'
        elif combined_sentences_token_list[i][0] == "Recoil" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??k????l">Recoil</phoneme>'
        elif combined_sentences_token_list[i][0] == "recoil" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??k????l">recoil</phoneme>'

        elif combined_sentences_token_list[i][0] == "Recoil" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????k????l">Recoil</phoneme>'
        elif combined_sentences_token_list[i][0] == "recoil" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????k????l">recoil</phoneme>'
        elif combined_sentences_token_list[i][0] == "Recoil" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??k????l">Recoil</phoneme>'
        elif combined_sentences_token_list[i][0] == "recoil" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??k????l">recoil</phoneme>'
    return combined_sentences_word_list

def recollect(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Recollect" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??r??k????l??kt">Recollect</phoneme>'
        elif combined_sentences_token_list[i][0] == "recollect" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??r??k????l??kt">recollect</phoneme>'
        elif combined_sentences_token_list[i][0] == "Recollect" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??rek????lekt">Recollect</phoneme>'
        elif combined_sentences_token_list[i][0] == "recollect" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??rek????lekt">recollect</phoneme>'
    return combined_sentences_word_list

def record(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Record" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????k??rd">Record</phoneme>'
        elif combined_sentences_token_list[i][0] == "record" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????k??rd">record</phoneme>'
        elif combined_sentences_token_list[i][0] == "Record" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??r??k??rd">Record</phoneme>'
        elif combined_sentences_token_list[i][0] == "record" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??r??k??rd">record</phoneme>'

        elif combined_sentences_token_list[i][0] == "Record" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????k????d">Record</phoneme>'
        elif combined_sentences_token_list[i][0] == "record" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????k????d">record</phoneme>'
        elif combined_sentences_token_list[i][0] == "Record" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??r??k????d">Record</phoneme>'
        elif combined_sentences_token_list[i][0] == "record" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??r??k????d">record</phoneme>'
    return combined_sentences_word_list

#Only in American English, as the verb and noun are pronounced the same in British English.
#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def redress(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Redress" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????dr??s">Redress</phoneme>'
        elif combined_sentences_token_list[i][0] == "redress" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????dr??s">redress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Redress" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??dr??s">Redress</phoneme>'
        elif combined_sentences_token_list[i][0] == "redress" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??dr??s">redress</phoneme>'
    return combined_sentences_word_list

def refill(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Refill" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri??f??l">Refill</phoneme>'
        elif combined_sentences_token_list[i][0] == "refill" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri??f??l">refill</phoneme>'
        elif combined_sentences_token_list[i][0] == "Refill" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??f??l">Refill</phoneme>'
        elif combined_sentences_token_list[i][0] == "refill" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??f??l">refill</phoneme>'

        elif combined_sentences_token_list[i][0] == "Refill" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri????f??l">Refill</phoneme>'
        elif combined_sentences_token_list[i][0] == "refill" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri????f??l">refill</phoneme>'
        elif combined_sentences_token_list[i][0] == "Refill" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??f??l">Refill</phoneme>'
        elif combined_sentences_token_list[i][0] == "refill" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??f??l">refill</phoneme>'
    return combined_sentences_word_list

def refit(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Refit" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri??f??t">Refit</phoneme>'
        elif combined_sentences_token_list[i][0] == "refit" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri??f??t">refit</phoneme>'
        elif combined_sentences_token_list[i][0] == "Refit" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??f??t">Refit</phoneme>'
        elif combined_sentences_token_list[i][0] == "refit" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??f??t">refit</phoneme>'

        elif combined_sentences_token_list[i][0] == "Refit" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri????f??t">Refit</phoneme>'
        elif combined_sentences_token_list[i][0] == "refit" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri????f??t">refit</phoneme>'
        elif combined_sentences_token_list[i][0] == "Refit" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri????f??t">Refit</phoneme>'
        elif combined_sentences_token_list[i][0] == "refit" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri????f??t">refit</phoneme>'
    return combined_sentences_word_list

def reflex(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Reflex" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????fl??ks">Reflex</phoneme>'
        elif combined_sentences_token_list[i][0] == "reflex" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????fl??ks">reflex</phoneme>'
        elif combined_sentences_token_list[i][0] == "Reflex" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??fl??ks">Reflex</phoneme>'
        elif combined_sentences_token_list[i][0] == "reflex" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??fl??ks">reflex</phoneme>'

        elif combined_sentences_token_list[i][0] == "Reflex" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????fl??ks">Reflex</phoneme>'
        elif combined_sentences_token_list[i][0] == "reflex" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????fl??ks">reflex</phoneme>'
        elif combined_sentences_token_list[i][0] == "Reflex" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??fl??ks">Reflex</phoneme>'
        elif combined_sentences_token_list[i][0] == "reflex" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??fl??ks">reflex</phoneme>'
    return combined_sentences_word_list

def refund(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Refund" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????f??nd">Refund</phoneme>'
        elif combined_sentences_token_list[i][0] == "refund" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????f??nd">refund</phoneme>'
        elif combined_sentences_token_list[i][0] == "Refund" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??f??nd">Refund</phoneme>'
        elif combined_sentences_token_list[i][0] == "refund" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??f??nd">refund</phoneme>'

        elif combined_sentences_token_list[i][0] == "Refund" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????f??nd">Refund</phoneme>'
        elif combined_sentences_token_list[i][0] == "refund" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????f??nd">refund</phoneme>'
        elif combined_sentences_token_list[i][0] == "Refund" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri????f??nd">Refund</phoneme>'
        elif combined_sentences_token_list[i][0] == "refund" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri????f??nd">refund</phoneme>'
    return combined_sentences_word_list

def refuse(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Refuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????fjuz">Refuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "refuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????fjuz">refuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Refuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??r??fjus">Refuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "refuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??r??fjus">refuse</phoneme>'

        elif combined_sentences_token_list[i][0] == "Refuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????fju??z">Refuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "refuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????fju??z">refuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Refuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??r??fju??s">Refuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "refuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??r??fju??s">refuse</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def regenerate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Regenerate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????d????n????re??t">Regenerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "regenerate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????d????n????re??t">regenerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Regenerate" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????d????n??r??t">Regenerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "regenerate" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????d????n??r??t">regenerate</phoneme>'
    return combined_sentences_word_list

def regress(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Regress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????gr??s">Regress</phoneme>'
        elif combined_sentences_token_list[i][0] == "regress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????gr??s">regress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Regress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??rigr??s">Regress</phoneme>'
        elif combined_sentences_token_list[i][0] == "regress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??rigr??s">regress</phoneme>'

        elif combined_sentences_token_list[i][0] == "Regress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r??????r??s">Regress</phoneme>'
        elif combined_sentences_token_list[i][0] == "regress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r??????r??s">regress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Regress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri????r??s">Regress</phoneme>'
        elif combined_sentences_token_list[i][0] == "regress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri????r??s">regress</phoneme>'
    return combined_sentences_word_list

#As the verb may be pronounced either way in American English, only the noun was included.
def rehash(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Rehash" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??h????">Rehash</phoneme>'
        elif combined_sentences_token_list[i][0] == "rehash" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??h????">rehash</phoneme>'

        elif combined_sentences_token_list[i][0] == "Rehash" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri????h????">Rehash</phoneme>'
        elif combined_sentences_token_list[i][0] == "rehash" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri????h????">rehash</phoneme>'
        elif combined_sentences_token_list[i][0] == "Rehash" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri????h????">Rehash</phoneme>'
        elif combined_sentences_token_list[i][0] == "rehash" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri????h????">rehash</phoneme>'
    return combined_sentences_word_list

def reject(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Reject" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????d????kt">Reject</phoneme>'
        elif combined_sentences_token_list[i][0] == "reject" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????d????kt">reject</phoneme>'
        elif combined_sentences_token_list[i][0] == "Reject" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??rid????kt">Reject</phoneme>'
        elif combined_sentences_token_list[i][0] == "reject" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??rid????kt">reject</phoneme>'

        elif combined_sentences_token_list[i][0] == "Reject" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????d????kt">Reject</phoneme>'
        elif combined_sentences_token_list[i][0] == "reject" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????d????kt">reject</phoneme>'
        elif combined_sentences_token_list[i][0] == "Reject" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??d????kt">Reject</phoneme>'
        elif combined_sentences_token_list[i][0] == "reject" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??d????kt">reject</phoneme>'
    return combined_sentences_word_list

def relapse(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Relapse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????l??ps">Relapse</phoneme>'
        elif combined_sentences_token_list[i][0] == "relapse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????l??ps">relapse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Relapse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ril??ps">Relapse</phoneme>'
        elif combined_sentences_token_list[i][0] == "relapse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ril??ps">relapse</phoneme>'

        elif combined_sentences_token_list[i][0] == "Relapse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????l??ps">Relapse</phoneme>'
        elif combined_sentences_token_list[i][0] == "relapse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????l??ps">relapse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Relapse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri????l??ps">Relapse</phoneme>'
        elif combined_sentences_token_list[i][0] == "relapse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri????l??ps">relapse</phoneme>'
    return combined_sentences_word_list

def relay(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Relay" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????le??">Relay</phoneme>'
        elif combined_sentences_token_list[i][0] == "relay" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????le??">relay</phoneme>'
        elif combined_sentences_token_list[i][0] == "Relay" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??le??">Relay</phoneme>'
        elif combined_sentences_token_list[i][0] == "relay" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??le??">relay</phoneme>'

        elif combined_sentences_token_list[i][0] == "Relay" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????le??">Relay</phoneme>'
        elif combined_sentences_token_list[i][0] == "relay" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????le??">relay</phoneme>'
        elif combined_sentences_token_list[i][0] == "Relay" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??le??">Relay</phoneme>'
        elif combined_sentences_token_list[i][0] == "relay" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??le??">relay</phoneme>'
    return combined_sentences_word_list

def remake(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Remake" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri??me??k">Remake</phoneme>'
        elif combined_sentences_token_list[i][0] == "remake" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri??me??k">remake</phoneme>'
        elif combined_sentences_token_list[i][0] == "Remake" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??me??k">Remake</phoneme>'
        elif combined_sentences_token_list[i][0] == "remake" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??me??k">remake</phoneme>'

        elif combined_sentences_token_list[i][0] == "Remake" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri????me??k">Remake</phoneme>'
        elif combined_sentences_token_list[i][0] == "remake" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri????me??k">remake</phoneme>'
        elif combined_sentences_token_list[i][0] == "Remake" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri????me??k">Remake</phoneme>'
        elif combined_sentences_token_list[i][0] == "remake" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri????me??k">remake</phoneme>'
    return combined_sentences_word_list

def repatriate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Repatriate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri??pe??tri??e??t">Repatriate</phoneme>'
        elif combined_sentences_token_list[i][0] == "repatriate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri??pe??tri??e??t">repatriate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Repatriate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri??pe??tri??t">Repatriate</phoneme>'
        elif combined_sentences_token_list[i][0] == "repatriate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri??pe??tri??t">repatriate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Repatriate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri????p??tr????e??t">Repatriate</phoneme>'
        elif combined_sentences_token_list[i][0] == "repatriate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri????p??tr????e??t">repatriate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Repatriate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri????p??tr????t">Repatriate</phoneme>'
        elif combined_sentences_token_list[i][0] == "repatriate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri????p??tr????t">repatriate</phoneme>'
    return combined_sentences_word_list

def repent(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Repent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????p??nt">Repent</phoneme>'
        elif combined_sentences_token_list[i][0] == "repent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????p??nt">repent</phoneme>'
        elif combined_sentences_token_list[i][0] == "Repent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??rip??n">Repent</phoneme>'
        elif combined_sentences_token_list[i][0] == "repent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??rip??n">repent</phoneme>'

        elif combined_sentences_token_list[i][0] == "Repent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????p??nt">Repent</phoneme>'
        elif combined_sentences_token_list[i][0] == "repent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????p??nt">repent</phoneme>'
        elif combined_sentences_token_list[i][0] == "Repent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??p??nt">Repent</phoneme>'
        elif combined_sentences_token_list[i][0] == "repent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??p??nt">repent</phoneme>'
    return combined_sentences_word_list

def replay(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Replay" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri????ple??">Replay</phoneme>'
        elif combined_sentences_token_list[i][0] == "replay" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri????ple??">replay</phoneme>'
        elif combined_sentences_token_list[i][0] == "Replay" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri????ple??">Replay</phoneme>'
        elif combined_sentences_token_list[i][0] == "replay" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri????ple??">replay</phoneme>'

        elif combined_sentences_token_list[i][0] == "Replay" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri??plei">Replay</phoneme>'
        elif combined_sentences_token_list[i][0] == "replay" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri??plei">replay</phoneme>'
        elif combined_sentences_token_list[i][0] == "Replay" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??plei">Replay</phoneme>'
        elif combined_sentences_token_list[i][0] == "replay" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??plei">replay</phoneme>'
    return combined_sentences_word_list

def reprint(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Reprint" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri??pr??nt">Reprint</phoneme>'
        elif combined_sentences_token_list[i][0] == "reprint" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri??pr??nt">reprint</phoneme>'
        elif combined_sentences_token_list[i][0] == "Reprint" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??pr??nt">Reprint</phoneme>'
        elif combined_sentences_token_list[i][0] == "reprint" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??pr??nt">reprint</phoneme>'

        elif combined_sentences_token_list[i][0] == "Reprint" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri????pr??nt">Reprint</phoneme>'
        elif combined_sentences_token_list[i][0] == "reprint" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri????pr??nt">reprint</phoneme>'
        elif combined_sentences_token_list[i][0] == "Reprint" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri????pr??nt">Reprint</phoneme>'
        elif combined_sentences_token_list[i][0] == "reprint" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri????pr??nt">reprint</phoneme>'
    return combined_sentences_word_list

def rerun(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Rerun" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri??r??n">Rerun</phoneme>'
        elif combined_sentences_token_list[i][0] == "rerun" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri??r??n">rerun</phoneme>'
        elif combined_sentences_token_list[i][0] == "Rerun" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??r??n">Rerun</phoneme>'
        elif combined_sentences_token_list[i][0] == "rerun" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??r??n">rerun</phoneme>'

        elif combined_sentences_token_list[i][0] == "Rerun" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri????r??n">Rerun</phoneme>'
        elif combined_sentences_token_list[i][0] == "rerun" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri????r??n">rerun</phoneme>'
        elif combined_sentences_token_list[i][0] == "Rerun" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri????r??n">Rerun</phoneme>'
        elif combined_sentences_token_list[i][0] == "rerun" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri????r??n">rerun</phoneme>'
    return combined_sentences_word_list

def retake(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Retake" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri??te??k">Retake</phoneme>'
        elif combined_sentences_token_list[i][0] == "retake" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri??te??k">retake</phoneme>'
        elif combined_sentences_token_list[i][0] == "Retake" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??te??k">Retake</phoneme>'
        elif combined_sentences_token_list[i][0] == "retake" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??te??k">retake</phoneme>'

        elif combined_sentences_token_list[i][0] == "Retake" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri????te??k">Retake</phoneme>'
        elif combined_sentences_token_list[i][0] == "retake" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri????te??k">retake</phoneme>'
        elif combined_sentences_token_list[i][0] == "Retake" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri????te??k">Retake</phoneme>'
        elif combined_sentences_token_list[i][0] == "retake" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri????te??k">retake</phoneme>'
    return combined_sentences_word_list

#As different forms of the noun "retard" are pronounced differently in American English, only the verb is included.
def retard(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Retard" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????t????rd">Retard</phoneme>'
        elif combined_sentences_token_list[i][0] == "retard" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????t????rd">retard</phoneme>'

        elif combined_sentences_token_list[i][0] == "Retard" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????t????d">Retard</phoneme>'
        elif combined_sentences_token_list[i][0] == "retard" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="r????t????d">retard</phoneme>'
        elif combined_sentences_token_list[i][0] == "Retard" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??t????d">Retard</phoneme>'
        elif combined_sentences_token_list[i][0] == "retard" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??t????d">retard</phoneme>'
    return combined_sentences_word_list

def rewind(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Rewind" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri??wa??nd">Rewind</phoneme>'
        elif combined_sentences_token_list[i][0] == "rewind" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri??wa??nd">rewind</phoneme>'
        elif combined_sentences_token_list[i][0] == "Rewind" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??wa??nd">Rewind</phoneme>'
        elif combined_sentences_token_list[i][0] == "rewind" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri??wa??nd">rewind</phoneme>'

        elif combined_sentences_token_list[i][0] == "Rewind" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri????wa??nd">Rewind</phoneme>'
        elif combined_sentences_token_list[i][0] == "rewind" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ri????wa??nd">rewind</phoneme>'
        elif combined_sentences_token_list[i][0] == "Rewind" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri????wa??nd">Rewind</phoneme>'
        elif combined_sentences_token_list[i][0] == "rewind" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ri????wa??nd">rewind</phoneme>'
    return combined_sentences_word_list

def segment(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Segment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??gm??nt">Segment</phoneme>'
        elif combined_sentences_token_list[i][0] == "segment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??gm??nt">segment</phoneme>'
        elif combined_sentences_token_list[i][0] == "Segment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??gm??nt">Segment</phoneme>'
        elif combined_sentences_token_list[i][0] == "segment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??gm??nt">segment</phoneme>'

        elif combined_sentences_token_list[i][0] == "Segment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s??????m??nt">Segment</phoneme>'
        elif combined_sentences_token_list[i][0] == "segment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s??????m??nt">segment</phoneme>'
        elif combined_sentences_token_list[i][0] == "Segment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s????m??nt">Segment</phoneme>'
        elif combined_sentences_token_list[i][0] == "segment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s????m??nt">segment</phoneme>'
    return combined_sentences_word_list

def separate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Separate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??sep????reit">Separate</phoneme>'
        elif combined_sentences_token_list[i][0] == "separate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??sep????reit">separate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Separate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??sep??r??t">Separate</phoneme>'
        elif combined_sentences_token_list[i][0] == "separate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??sep??r??t">separate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Separate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??p????re??t">Separate</phoneme>'
        elif combined_sentences_token_list[i][0] == "separate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??p????re??t">separate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Separate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??p??r??t">Separate</phoneme>'
        elif combined_sentences_token_list[i][0] == "separate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??p??r??t">separate</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def skied(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Skied" and combined_sentences_token_list[i][1][:2] == "VB" and combined_sentences_token_list[i][3].lower() == "ski":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ski??d">Skied</phoneme>'
        elif combined_sentences_token_list[i][0] == "skied" and combined_sentences_token_list[i][1][:2] == "VB" and combined_sentences_token_list[i][3].lower() == "ski":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ski??d">skied</phoneme>'
        elif combined_sentences_token_list[i][0] == "Skied" and combined_sentences_token_list[i][1][:2] == "VB" and combined_sentences_token_list[i][3].lower() == "sky":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ska??d">Skied</phoneme>'
        elif combined_sentences_token_list[i][0] == "skied" and combined_sentences_token_list[i][1][:2] == "VB" and combined_sentences_token_list[i][3].lower() == "sky":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ska??d">skied</phoneme>'
    return combined_sentences_word_list

def sow(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Sow" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="so??">Sow</phoneme>'
        elif combined_sentences_token_list[i][0] == "sow" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="so??">sow</phoneme>'
        elif combined_sentences_token_list[i][0] == "Sow" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="sa??">Sow</phoneme>'
        elif combined_sentences_token_list[i][0] == "sow" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="sa??">sow</phoneme>'

        elif combined_sentences_token_list[i][0] == "Sow" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s????">Sow</phoneme>'
        elif combined_sentences_token_list[i][0] == "sow" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s????">sow</phoneme>'
        elif combined_sentences_token_list[i][0] == "Sow" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="sa??">Sow</phoneme>'
        elif combined_sentences_token_list[i][0] == "sow" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="sa??">sow</phoneme>'
    return combined_sentences_word_list

#Only in American English, as the noun and adjective are pronounced the same in British English.
#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def stabile(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Stabile" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ste?? bil">Stabile</phoneme>'
        elif combined_sentences_token_list[i][0] == "stabile" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ste?? bil">stabile</phoneme>'
        elif combined_sentences_token_list[i][0] == "Stabile" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ste??b??l">Stabile</phoneme>'
        elif combined_sentences_token_list[i][0] == "stabile" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??ste??b??l">stabile</phoneme>'
    return combined_sentences_word_list

def stipulate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Stipulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??st??pj????le??t">Stipulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "stipulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??st??pj????le??t">stipulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Stipulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??st??pj??l??t">Stipulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "stipulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??st??pj??l??t">stipulate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Stipulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??st??pj????le??t">Stipulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "stipulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??st??pj????le??t">stipulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Stipulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??st??pj??l??t">Stipulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "stipulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??st??pj??l??t">stipulate</phoneme>'
    return combined_sentences_word_list

def subject(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Subject" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s??b??d????kt">Subject</phoneme>'
        elif combined_sentences_token_list[i][0] == "subject" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s??b??d????kt">subject</phoneme>'
        elif combined_sentences_token_list[i][0] == "Subject" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??bd????kt">Subject</phoneme>'
        elif combined_sentences_token_list[i][0] == "subject" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??bd????kt">subject</phoneme>'
    return combined_sentences_word_list

#The POS was used instead of the TAG for the adverbs, as the first letters of the various adverb tags differ.
#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def supply(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Supply" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["VB", "NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s????pla??">Supply</phoneme>'
        elif combined_sentences_token_list[i][0] == "supply" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["VB", "NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s????pla??">supply</phoneme>'
        elif combined_sentences_token_list[i][0] == "Supply" and English_Phonetics == "American_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??pli">Supply</phoneme>'
        elif combined_sentences_token_list[i][0] == "supply" and English_Phonetics == "American_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??pli">supply</phoneme>'

        elif combined_sentences_token_list[i][0] == "Supply" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["VB", "NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s????pla??">Supply</phoneme>'
        elif combined_sentences_token_list[i][0] == "supply" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["VB", "NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s????pla??">supply</phoneme>'
        elif combined_sentences_token_list[i][0] == "Supply" and English_Phonetics == "British_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??pl??">Supply</phoneme>'
        elif combined_sentences_token_list[i][0] == "supply" and English_Phonetics == "British_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??pl??">supply</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
#Supposed in "was supposed to" is a modal verb and could be identified by the Spacy fine grained tag "MD" or if the following word is "to".
def supposed(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Supposed" and (combined_sentences_token_list[i][1][:2] == "MD" or combined_sentences_token_list[i+1][0].lower() == "to"):
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s????po??st">Supposed</phoneme>'
        elif combined_sentences_token_list[i][0] == "supposed" and (combined_sentences_token_list[i][1][:2] == "MD" or combined_sentences_token_list[i+1][0].lower() == "to"):
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s????po??st">supposed</phoneme>'
        elif combined_sentences_token_list[i][0] == "Supposed" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s????po??zd">Supposed</phoneme>'
        elif combined_sentences_token_list[i][0] == "supposed" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s????po??zd">supposed</phoneme>'
        elif combined_sentences_token_list[i][0] == "Supposed" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s????po??z(??)d">Supposed</phoneme>'
        elif combined_sentences_token_list[i][0] == "supposed" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s????po??z(??)d">supposed</phoneme>'
    return combined_sentences_word_list

def survey(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Survey" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s??r??ve??">Survey</phoneme>'
        elif combined_sentences_token_list[i][0] == "survey" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s??r??ve??">survey</phoneme>'
        elif combined_sentences_token_list[i][0] == "Survey" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??r??ve??">Survey</phoneme>'
        elif combined_sentences_token_list[i][0] == "survey" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??r??ve??">survey</phoneme>'

        elif combined_sentences_token_list[i][0] == "Survey" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s??????ve??">Survey</phoneme>'
        elif combined_sentences_token_list[i][0] == "survey" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s??????ve??">survey</phoneme>'
        elif combined_sentences_token_list[i][0] == "Survey" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s????ve??">Survey</phoneme>'
        elif combined_sentences_token_list[i][0] == "survey" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s????ve??">survey</phoneme>'
    return combined_sentences_word_list

def suspect(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Suspect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s????sp??kt">Suspect</phoneme>'
        elif combined_sentences_token_list[i][0] == "suspect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s????sp??kt">suspect</phoneme>'
        elif combined_sentences_token_list[i][0] == "Suspect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??s??p??kt">Suspect</phoneme>'
        elif combined_sentences_token_list[i][0] == "suspect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??s??p??kt">suspect</phoneme>'

        elif combined_sentences_token_list[i][0] == "Suspect" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s????sp??kt">Suspect</phoneme>'
        elif combined_sentences_token_list[i][0] == "suspect" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="s????sp??kt">suspect</phoneme>'
        elif combined_sentences_token_list[i][0] == "Suspect" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??sp??kt">Suspect</phoneme>'
        elif combined_sentences_token_list[i][0] == "suspect" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??sp??kt">suspect</phoneme>'
    return combined_sentences_word_list

def syndicate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Syndicate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??nd????ke??t">Syndicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "syndicate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??nd????ke??t">syndicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Syndicate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??nd??k??t">Syndicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "syndicate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??nd??k??t">syndicate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Syndicate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??nd????ke??t">Syndicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "syndicate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??nd????ke??t">syndicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Syndicate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??nd??k??t">Syndicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "syndicate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??s??nd??k??t">syndicate</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def tarry(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Tarry" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["VB", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??t??ri">Tarry</phoneme>'
        elif combined_sentences_token_list[i][0] == "tarry" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["VB", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??t??ri">tarry</phoneme>'
        elif combined_sentences_token_list[i][0] == "Tarry" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??t??ri">Tarry</phoneme>'
        elif combined_sentences_token_list[i][0] == "tarry" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??t??ri">tarry</phoneme>'

        elif combined_sentences_token_list[i][0] == "Tarry" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["VB", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??t??r??">Tarry</phoneme>'
        elif combined_sentences_token_list[i][0] == "tarry" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["VB", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??t??r??">tarry</phoneme>'
        elif combined_sentences_token_list[i][0] == "Tarry" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??t??r??">Tarry</phoneme>'
        elif combined_sentences_token_list[i][0] == "tarry" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??t??ri">tarry</phoneme>'
    return combined_sentences_word_list

#The nouns "tear" (liquid tear and tear in clothes) cannot be distinguished by Spacy, so phoneme substitutions will
#only take place if the fine-grained tag is "VB" (verb).
def tear(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Tear" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??t??r">Tear</phoneme>'
        elif combined_sentences_token_list[i][0] == "tear" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??t??r">tear</phoneme>'

        elif combined_sentences_token_list[i][0] == "Tear" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??t????">Tear</phoneme>'
        elif combined_sentences_token_list[i][0] == "tear" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??t????">tear</phoneme>'
    return combined_sentences_word_list

def torment(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Torment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="t??r??m??nt">Torment</phoneme>'
        elif combined_sentences_token_list[i][0] == "torment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="t??r??m??nt">torment</phoneme>'
        elif combined_sentences_token_list[i][0] == "Torment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??t??r??m??nt">Torment</phoneme>'
        elif combined_sentences_token_list[i][0] == "torment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??t??r??m??nt">torment</phoneme>'

        elif combined_sentences_token_list[i][0] == "Torment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="t??????m??nt">Torment</phoneme>'
        elif combined_sentences_token_list[i][0] == "torment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="t??????m??nt">torment</phoneme>'
        elif combined_sentences_token_list[i][0] == "Torment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??t????m??nt">Torment</phoneme>'
        elif combined_sentences_token_list[i][0] == "torment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??t????m??nt">torment</phoneme>'
    return combined_sentences_word_list

def transect(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Transect" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="tr??n??s??kt">Transect</phoneme>'
        elif combined_sentences_token_list[i][0] == "transect" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="tr??n??s??kt">transect</phoneme>'
        elif combined_sentences_token_list[i][0] == "Transect" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??tr??ns??kt">Transect</phoneme>'
        elif combined_sentences_token_list[i][0] == "transect" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??tr??ns??kt">transect</phoneme>'
    return combined_sentences_word_list

#Only for British English, since the verb and noun may be pronounced the same way in American English.
def transfer(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Transfer" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="tr??ns??f????">Transfer</phoneme>'
        elif combined_sentences_token_list[i][0] == "transfer" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="tr??ns??f????">transfer</phoneme>'
        elif combined_sentences_token_list[i][0] == "Transfer" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??tr??nsf????">Transfer</phoneme>'
        elif combined_sentences_token_list[i][0] == "transfer" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??tr??nsf????">transfer</phoneme>'
    return combined_sentences_word_list

def transplant(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Transplant" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="tr??ns??pl??nt">Transplant</phoneme>'
        elif combined_sentences_token_list[i][0] == "transplant" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="tr??ns??pl??nt">transplant</phoneme>'
        elif combined_sentences_token_list[i][0] == "Transplant" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??tr??ns??pl??nt">Transplant</phoneme>'
        elif combined_sentences_token_list[i][0] == "transplant" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??tr??ns??pl??nt">transplant</phoneme>'

        elif combined_sentences_token_list[i][0] == "Transplant" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="tr??ns??pl????nt">Transplant</phoneme>'
        elif combined_sentences_token_list[i][0] == "transplant" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="tr??ns??pl????nt">transplant</phoneme>'
        elif combined_sentences_token_list[i][0] == "Transplant" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??tr??ns??pl????nt">Transplant</phoneme>'
        elif combined_sentences_token_list[i][0] == "transplant" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??tr??ns??pl????nt">transplant</phoneme>'
    return combined_sentences_word_list

def transport(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Transport" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="tr??ns??p??rt">Transport</phoneme>'
        elif combined_sentences_token_list[i][0] == "transport" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="tr??ns??p??rt">transport</phoneme>'
        elif combined_sentences_token_list[i][0] == "Transport" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??tr??ns??p??rt">Transport</phoneme>'
        elif combined_sentences_token_list[i][0] == "transport" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??tr??ns??p??rt">transport</phoneme>'

        elif combined_sentences_token_list[i][0] == "Transport" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="tr??ns??p????t">Transport</phoneme>'
        elif combined_sentences_token_list[i][0] == "transport" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="tr??ns??p????t">transport</phoneme>'
        elif combined_sentences_token_list[i][0] == "Transport" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??tr??ns??p????t">Transport</phoneme>'
        elif combined_sentences_token_list[i][0] == "transport" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??tr??ns??p????t">transport</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def upset(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Upset" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["VB", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??s??t">Upset</phoneme>'
        elif combined_sentences_token_list[i][0] == "upset" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["VB", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??s??t">upset</phoneme>'
        elif combined_sentences_token_list[i][0] == "Upset" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????p??s??t">Upset</phoneme>'
        elif combined_sentences_token_list[i][0] == "upset" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????p??s??t">upset</phoneme>'

        elif combined_sentences_token_list[i][0] == "Upset" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["VB", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??s??t">Upset</phoneme>'
        elif combined_sentences_token_list[i][0] == "upset" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["VB", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??p??s??t">upset</phoneme>'
        elif combined_sentences_token_list[i][0] == "Upset" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????p??s??t">Upset</phoneme>'
        elif combined_sentences_token_list[i][0] == "upset" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="????p??s??t">upset</phoneme>'
    return combined_sentences_word_list

def use(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Use" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="juz">Use</phoneme>'
        elif combined_sentences_token_list[i][0] == "use" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="juz">use</phoneme>'
        elif combined_sentences_token_list[i][0] == "Use" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="jus">Use</phoneme>'
        elif combined_sentences_token_list[i][0] == "use" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="jus">use</phoneme>'

        elif combined_sentences_token_list[i][0] == "Use" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ju??z">Use</phoneme>'
        elif combined_sentences_token_list[i][0] == "use" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ju??z">use</phoneme>'
        elif combined_sentences_token_list[i][0] == "Use" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ju??s">Use</phoneme>'
        elif combined_sentences_token_list[i][0] == "use" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ju??s">use</phoneme>'
    return combined_sentences_word_list

#Supposed in "was supposed to" is a modal verb and could be identified by the Spacy fine grained tag "MD" or if the following word is "to".
def used(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Used" and (combined_sentences_token_list[i][1][:2] == "MD" or combined_sentences_token_list[i+1][0].lower() == "to"):
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ju??st">Used</phoneme>'
        elif combined_sentences_token_list[i][0] == "used" and (combined_sentences_token_list[i][1][:2] == "MD" or combined_sentences_token_list[i+1][0].lower() == "to"):
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ju??st">used</phoneme>'
        elif combined_sentences_token_list[i][0] == "Used" and combined_sentences_token_list[i][1][:2] in ["VB", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ju??zd">Used</phoneme>'
        elif combined_sentences_token_list[i][0] == "used" and combined_sentences_token_list[i][1][:2] in ["VB", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ju??zd">used</phoneme>'
    return combined_sentences_word_list

def wicked(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Wicked" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??w??kt">Wicked</phoneme>'
        elif combined_sentences_token_list[i][0] == "wicked" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??w??kt">wicked</phoneme>'
        elif combined_sentences_token_list[i][0] == "Wicked" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??w??k??d">Wicked</phoneme>'
        elif combined_sentences_token_list[i][0] == "wicked" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??w??k??d">wicked</phoneme>'
    return combined_sentences_word_list

#This is the heteronym entry that makes the most assumptions on the meaning of the word "wind".
#It is assumed that the noun "wind" designates the movement of air, and not the act of winding or state of being wound, or a single turn/bend.
#As different forms of the verb "wind" may be pronounced differently, only the phoneme for "??wa??nd" is substituted for "wind" in so far as "wind" is followed
#by "up". Caution is warranted here, as the other phoneme could be used before "up" as well.
def wind(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Wind" and combined_sentences_token_list[i][1][:2] == "VB" and combined_sentences_token_list[i+1][0].lower() == "up":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??wa??nd">Wind</phoneme>'
        elif combined_sentences_token_list[i][0] == "wind" and combined_sentences_token_list[i][1][:2] == "VB" and combined_sentences_token_list[i+1][0].lower() == "up":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??wa??nd">wind</phoneme>'
        elif combined_sentences_token_list[i][0] == "Wind" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??w??nd">Wind</phoneme>'
        elif combined_sentences_token_list[i][0] == "wind" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="??w??nd">wind</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def wound(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Wound" and combined_sentences_token_list[i][1][:3] == "VBD":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="wa??nd">Wound</phoneme>'
        elif combined_sentences_token_list[i][0] == "wound" and combined_sentences_token_list[i][1][:3] == "VBD":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="wa??nd">wound</phoneme>'
        elif combined_sentences_token_list[i][0] == "Wound" and combined_sentences_token_list[i][1][:2] in ["VB", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="wu??nd">Wound</phoneme>'
        elif combined_sentences_token_list[i][0] == "wound" and combined_sentences_token_list[i][1][:2] in ["VB", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="wu??nd">wound</phoneme>'
    return combined_sentences_word_list


#The "set_of_heteronyms_in_text" will be populated with the words in "combined_sentences_word_list" if they are present in either
#"heteronyms_list_American_English" or "heteronyms_list_American_English based"
set_of_heteronyms_in_text = set()
for word in combined_sentences_word_list:
    if English_Phonetics == "American_English" and word.capitalize() in heteronyms_list_American_English:
        set_of_heteronyms_in_text.add(word)
    elif English_Phonetics == "British_English" and word.capitalize() in heteronyms_list_British_English:
        set_of_heteronyms_in_text.add(word)

#This function appends spaces between elements of 'combined_sentences_word_list' if the last character of an element is alphabetic and the next element isn't "n't" (to prevent getting "do n't" instead of "don't", as Spacy tokenizes "don't" as "do" + "n't")
#and the first character of the next element is also alphabetic, or a bracket or starting quote sign (to avoid results such as 'word1(word2)'). It also appends spaces between elements of the list if the last character is not alphabetic, and the
#first character of the next element is alphabetic (to add a space after a comma, for example), but not if the first character of the next element is a bracket or a starting quote sign (to avoid
#results such as '( word'). Otherwise, it doesn't add any spaces.
def make_new_sentences(combined_sentences_word_list):
    combined_sentences_word_list_with_spaces = []
    for i in range(len(combined_sentences_word_list)-1):
        if combined_sentences_word_list[i][-1].isalpha() == True and combined_sentences_word_list[i+1]!= "n???t" and (combined_sentences_word_list[i+1][0].isalpha() == True or combined_sentences_word_list[i+1][0] in ['(', '[', '{', '???', "???", "<"]):
            combined_sentences_word_list_with_spaces.append(combined_sentences_word_list[i])
            combined_sentences_word_list_with_spaces.append(" ")
        elif combined_sentences_word_list[i][-1].isalpha() == False and combined_sentences_word_list[i][-1] not in ['(', '[', '{', '???', "???", "-"] and combined_sentences_word_list[i+1][0].isalpha() == True:
            combined_sentences_word_list_with_spaces.append(combined_sentences_word_list[i])
            combined_sentences_word_list_with_spaces.append(" ")
        else:
            combined_sentences_word_list_with_spaces.append(combined_sentences_word_list[i])
    combined_sentences_word_list_with_spaces.append(combined_sentences_word_list[-1])
    new_combined_sentences = "".join(combined_sentences_word_list_with_spaces)
    new_sentences = [sentence.strip() for sentence in re.split("===", new_combined_sentences) if sentence != '']
    return new_sentences

#Only pass 'text' and 'combined_sentences_token_list' in the heteronym functions if a heteronym was found in 'combined_sentences_word_list'
#If there are hyphens in the heteronym (ex: "co-ordinate"), they will be replaced with underscores (ex: "co_ordinate") for the function call.
sentence_index = 0
if len(set_of_heteronyms_in_text) > 0:
    for heteronym in set_of_heteronyms_in_text:
        #Since "import" is an internal python command, the function call needs to be different, hence the addition of "_heteronym"
        #to give the following function call: "import_heteronym(args)".
        if heteronym == "import":
            new_combined_sentences_word_list = eval(heteronym.lower() + "_heteronym")(combined_sentences_word_list, combined_sentences_token_list)
            new_sentences = make_new_sentences(new_combined_sentences_word_list)
        else:
            new_combined_sentences_word_list = eval(heteronym.lower())(combined_sentences_word_list, combined_sentences_token_list)
            new_sentences = make_new_sentences(new_combined_sentences_word_list)
    #Cycling through the "set_of_sentence_indices_with_heteronyms" to replace the original sentences in the whole text that contain heteronyms
    #with the corresponding "new_sentences" (after substitution of the SSML phoneme tags for the original heteronyms). Since the original sentence
    #indices come from a set, even if a sentence contains several different heteronyms, only one "index" will be used for the "whole_text.replace()"
    #methods per sentence containing heteronyms. Thus, the total number of sentences in the "set_of_sentence_indices_with_heteronyms" matches up with the
    #number of sentences in the "new_sentences".
    counter = 0
    for index in set_of_sentence_indices_with_heteronyms:
        sentences[index] = new_sentences[counter]
        counter+=1
#The updated sentences are joined without a space because the TTS rendition of acronyms would suffer from the addition of spaces in between the letters of the acronym.
#(The whole_text is split at "!", "?" or "." and the period could be part of an acronym such as "e.g." The absence of spaces in between new sentences and the previous
#punctuation mark does not seem to affect the TTS rendition in modern TTS websites.)
#A space is added after the punctuation mark if the length of the text following it is greater than one.
for i in range(len(sentences)-2):
    if sentences[i] not in ["!", "?", "\."] and len(sentences[i]) >= 1 and len(sentences[i+2]) > 1:
        sentences[i+2] = " " + sentences[i+2]
whole_text = "".join(sentences)

commas_semicolons_whole_text_after_modifications = whole_text.count(',') + whole_text.count(';')
#Calculating the relative percent increase in commas in the whole text after modifications.
if commas_semicolons_whole_text_before_modifications > 0:
    percent_increase_in_commas["Percent increase in commas in the whole text after modifications: "] = str(round((commas_semicolons_whole_text_after_modifications-commas_semicolons_whole_text_before_modifications)/commas_semicolons_whole_text_before_modifications*100)) + "%"
else:
    percent_increase_in_commas["Percent increase in commas in the whole text after modifications: "] = "There were no commas nor semicolons in the initial text and there are now " + str(commas_semicolons_whole_text_after_modifications) + " commas in the script after modifications."

#Selecting for potentially mispronounced capitalized words in whole_text who appear at least 4 times throughout the text.
for unknown_word in potentially_mispronounced_words:
    unknown_word_count = len(re.findall("[^\w]" + re.escape(unknown_word) + "[^\w]", whole_text))
    if unknown_word_count > 3 and len(unknown_word) > 1 :
        potentiallyMispronouncedWords_wordCounts[unknown_word] = unknown_word_count

#Calculating the "number_of_heteronym_substitutions" by subtracting the number of "<phoneme alphabet=" in the initial text from that of the final text.
final_phoneme_tag_count = whole_text.count("<phoneme alphabet=")
number_of_heteronym_substitutions = final_phoneme_tag_count-initial_phoneme_tag_count

#All of the data will be outputed in a single dictionary (entireData_dictionaries), whose sole key is mapped to a value consisting of a list of
#six dictionaries/lists/strings. The title of the individual dictionaries (sentencesManyCommas_sentenceIndex, sentencesFewCommas_sentenceIndex, potentiallyMispronouncedWords_wordCounts, percent_increase_in_commas) give insight as to the structure of the dictionaries: KeyNames_ValueName1ValueName2ValueName3.
entireData_dictionaries[0] = [sentencesManyCommas_sentenceIndex, sentencesFewCommas_sentenceIndex, potentiallyMispronouncedWords_wordCounts, percent_increase_in_commas, number_of_heteronym_substitutions, whole_text]

print(json.dumps(entireData_dictionaries, ensure_ascii=False))
